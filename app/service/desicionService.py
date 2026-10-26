import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from model.consumo import Consumo


class MLService:
    """Pronostica el consumo mensual agregado por localidad y barrio."""

    COLUMNAS_CATEGORICAS = ["Localidad", "Barrio", "Mes_Numero"]
    COLUMNAS_NUMERICAS = [
        "Consumo_Lag_1",
        "Consumo_Lag_2",
        "Consumo_Lag_3",
    ]
    COLUMNAS = COLUMNAS_CATEGORICAS + COLUMNAS_NUMERICAS
    NUM_MESES_HISTORICOS = 3

    def __init__(self):
        procesador = ColumnTransformer(
            [
                (
                    "categoricas",
                    OneHotEncoder(handle_unknown="ignore"),
                    self.COLUMNAS_CATEGORICAS,
                )
            ],
            remainder="passthrough",
        )
        self.modelo = Pipeline(
            [
                ("variables", procesador),
                (
                    "bosque",
                    RandomForestRegressor(
                        n_estimators=300,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        )
        self.entrenado = False
        self.ultimo_periodo_entrenamiento = None

    @staticmethod
    def _obtener_historial_mensual():
        """Agrupa los reportes de todos los usuarios por zona y mes calendario."""
        filas = (
            Consumo.query.with_entities(
                Consumo.localidad,
                Consumo.barrio,
                Consumo.kw_consumo,
                Consumo.fecha,
                Consumo.fecha_registro,
            )
            .all()
        )
        if not filas:
            return pd.DataFrame(
                columns=["Localidad", "Barrio", "Periodo", "Consumo_kWh"]
            )

        datos = pd.DataFrame(
            filas,
            columns=[
                "Localidad",
                "Barrio",
                "Consumo_kWh",
                "Fecha",
                "Fecha_Registro",
            ],
        )
        datos["Consumo_kWh"] = pd.to_numeric(
            datos["Consumo_kWh"], errors="coerce"
        )
        # fecha representa el periodo de consumo; fecha_registro sirve de respaldo
        # para registros antiguos que no tengan fecha de consumo.
        datos["Fecha"] = pd.to_datetime(datos["Fecha"], errors="coerce")
        datos["Fecha_Registro"] = pd.to_datetime(
            datos["Fecha_Registro"], errors="coerce"
        )
        datos["Fecha_Consumo"] = datos["Fecha"].fillna(datos["Fecha_Registro"])
        datos = datos.dropna(
            subset=["Localidad", "Barrio", "Consumo_kWh", "Fecha_Consumo"]
        )
        if datos.empty:
            return pd.DataFrame(
                columns=["Localidad", "Barrio", "Periodo", "Consumo_kWh"]
            )

        datos["Localidad"] = datos["Localidad"].astype(str).str.strip()
        datos["Barrio"] = datos["Barrio"].astype(str).str.strip()
        datos = datos[
            (datos["Localidad"] != "")
            & (datos["Barrio"] != "")
            & (datos["Consumo_kWh"] >= 0)
        ]
        datos["Periodo"] = datos["Fecha_Consumo"].dt.to_period("M")
        return (
            datos.groupby(
                ["Localidad", "Barrio", "Periodo"], as_index=False
            )["Consumo_kWh"]
            .mean()
            .sort_values(["Localidad", "Barrio", "Periodo"])
            .reset_index(drop=True)
        )

    @classmethod
    def _crear_muestras_entrenamiento(cls, historial):
        """Cada muestra usa los tres meses consecutivos previos para estimar el siguiente."""
        muestras = []
        llaves_zona = ["Localidad", "Barrio"]

        for (localidad, barrio), grupo in historial.groupby(llaves_zona):
            serie = grupo.set_index("Periodo")["Consumo_kWh"].sort_index()
            for indice in range(cls.NUM_MESES_HISTORICOS, len(serie)):
                periodo_objetivo = serie.index[indice]
                periodos_previos = [
                    periodo_objetivo - desplazamiento
                    for desplazamiento in range(1, cls.NUM_MESES_HISTORICOS + 1)
                ]
                if not all(periodo in serie.index for periodo in periodos_previos):
                    continue

                muestra = {
                    "Localidad": localidad,
                    "Barrio": barrio,
                    "Mes_Numero": str(periodo_objetivo.month),
                    "Consumo_Lag_1": float(serie.loc[periodos_previos[0]]),
                    "Consumo_Lag_2": float(serie.loc[periodos_previos[1]]),
                    "Consumo_Lag_3": float(serie.loc[periodos_previos[2]]),
                    "Consumo_Objetivo": float(serie.loc[periodo_objetivo]),
                }
                muestras.append(muestra)

        return pd.DataFrame(muestras)

    def entrenar_desde_base(self):
        historial = self._obtener_historial_mensual()
        if historial.empty:
            self.entrenado = False
            return {
                "success": False,
                "mensaje": "No hay consumos con localidad, barrio y fecha válidos.",
            }

        muestras = self._crear_muestras_entrenamiento(historial)
        if len(muestras) < 3:
            self.entrenado = False
            return {
                "success": False,
                "mensaje": (
                    "Se requieren al menos tres ejemplos de entrenamiento. "
                    "Cada ejemplo necesita tres meses consecutivos previos y "
                    "el consumo del mes siguiente por localidad y barrio."
                ),
                "ejemplos_disponibles": len(muestras),
            }

        self.modelo.fit(muestras[self.COLUMNAS], muestras["Consumo_Objetivo"])
        self.entrenado = True
        self.ultimo_periodo_entrenamiento = str(historial["Periodo"].max())

        return {
            "success": True,
            "ejemplos_entrenamiento": len(muestras),
            "zonas_entrenadas": int(
                historial[["Localidad", "Barrio"]].drop_duplicates().shape[0]
            ),
            "ultimo_mes_con_datos": self.ultimo_periodo_entrenamiento,
        }

    def predecir_localidades(self, filtros=None):
        if not self.entrenado:
            return {
                "success": False,
                "mensaje": "Primero debes entrenar el modelo.",
            }

        historial = self._obtener_historial_mensual()
        if historial.empty:
            return {
                "success": False,
                "mensaje": "No hay consumos válidos en la base de datos.",
            }

        filtros = filtros or {}
        localidades = filtros.get("localidad")
        barrios = filtros.get("barrio")
        if localidades:
            valores = localidades if isinstance(localidades, (list, tuple, set)) else [localidades]
            historial = historial[historial["Localidad"].isin(valores)]
        if barrios:
            valores = barrios if isinstance(barrios, (list, tuple, set)) else [barrios]
            historial = historial[historial["Barrio"].isin(valores)]

        resultados = []
        for (localidad, barrio), grupo in historial.groupby(["Localidad", "Barrio"]):
            serie = grupo.set_index("Periodo")["Consumo_kWh"].sort_index()
            periodo_base = serie.index[-1]
            periodos_previos = [
                periodo_base - desplazamiento
                for desplazamiento in range(self.NUM_MESES_HISTORICOS - 1, -1, -1)
            ]
            if not all(periodo in serie.index for periodo in periodos_previos):
                continue

            periodo_objetivo = periodo_base + 1
            fila = pd.DataFrame(
                [
                    {
                        "Localidad": localidad,
                        "Barrio": barrio,
                        "Mes_Numero": str(periodo_objetivo.month),
                        "Consumo_Lag_1": float(serie.loc[periodos_previos[2]]),
                        "Consumo_Lag_2": float(serie.loc[periodos_previos[1]]),
                        "Consumo_Lag_3": float(serie.loc[periodos_previos[0]]),
                    }
                ]
            )
            estimacion = max(0.0, float(self.modelo.predict(fila[self.COLUMNAS])[0]))
            resultados.append(
                {
                    "localidad": localidad,
                    "barrio": barrio,
                    "mes_predicho": str(periodo_objetivo),
                    "consumo_estimado_kwh": round(estimacion, 2),
                    "ultimo_consumo_mensual_kwh": round(
                        float(serie.loc[periodo_base]), 2
                    ),
                }
            )

        if not resultados:
            return {
                "success": False,
                "mensaje": (
                    "No hay zonas que cumplan los filtros y tengan tres meses "
                    "consecutivos de historial."
                ),
            }

        return {"success": True, "resultados": resultados}
