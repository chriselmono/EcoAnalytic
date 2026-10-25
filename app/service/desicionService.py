import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from model.consumo import Consumo


class MLService:
    """Entrena y clasifica el consumo promedio registrado por localidad."""

    # Umbrales mensuales iniciales para hogares de Bogotá (kWh).
    UMBRALES = ((600, "Bajo"), (1000, "Medio"), (1500, "Alto"))
    COLUMNAS = ["Localidad", "Consumo_Promedio"]

    def __init__(self):
        procesador = ColumnTransformer(
            [("localidad", OneHotEncoder(handle_unknown="ignore"), ["Localidad"])],
            remainder="passthrough",
        )
        self.modelo = Pipeline([
            ("variables", procesador),
            ("arbol", DecisionTreeClassifier(max_depth=4, random_state=42)),
        ])
        self.entrenado = False

    @classmethod
    def clasificar_consumo(cls, consumo_kwh):
        for limite, categoria in cls.UMBRALES:
            if consumo_kwh <= limite:
                return categoria
        return "Extremo"

    @staticmethod
    def obtener_promedios_por_localidad():
        filas = (
            Consumo.query.with_entities(Consumo.localidad, Consumo.kw_consumo)
            .all()
        )
        if not filas:
            return pd.DataFrame(columns=MLService.COLUMNAS)

        datos = pd.DataFrame(filas, columns=["Localidad", "Consumo_kWh"])
        datos["Consumo_kWh"] = pd.to_numeric(datos["Consumo_kWh"], errors="coerce")
        datos = datos.dropna(subset=["Localidad", "Consumo_kWh"])
        promedios = (
            datos.groupby("Localidad", as_index=False)["Consumo_kWh"]
            .mean()
            .rename(columns={"Consumo_kWh": "Consumo_Promedio"})
        )
        return promedios

    def entrenar_desde_base(self):
        localidades = self.obtener_promedios_por_localidad()
        if localidades.empty:
            self.entrenado = False
            return {
                "success": False,
                "mensaje": "No hay consumos válidos en la base de datos.",
            }

        localidades["Categoria"] = localidades["Consumo_Promedio"].map(
            self.clasificar_consumo
        )
        self.modelo.fit(localidades[self.COLUMNAS], localidades["Categoria"])
        self.entrenado = True

        return {
            "success": True,
            "localidades_entrenadas": len(localidades),
            "resultados": [
                {
                    "localidad": fila.Localidad,
                    "consumo_promedio_kwh": round(float(fila.Consumo_Promedio), 2),
                    "categoria": fila.Categoria,
                }
                for fila in localidades.itertuples(index=False)
            ],
        }

    def predecir_localidades(self):
        if not self.entrenado:
            return {
                "success": False,
                "mensaje": "Primero debes entrenar el modelo.",
            }

        localidades = self.obtener_promedios_por_localidad()
        if localidades.empty:
            return {
                "success": False,
                "mensaje": "No hay consumos válidos en la base de datos.",
            }

        predicciones = self.modelo.predict(localidades[self.COLUMNAS])
        probabilidades = self.modelo.predict_proba(localidades[self.COLUMNAS])
        return {
            "success": True,
            "resultados": [
                {
                    "localidad": fila.Localidad,
                    "consumo_promedio_kwh": round(float(fila.Consumo_Promedio), 2),
                    "categoria": str(prediccion),
                    "probabilidades": {
                        str(clase): round(float(prob) * 100, 2)
                        for clase, prob in zip(self.modelo.classes_, probs)
                    },
                }
                for fila, prediccion, probs in zip(
                    localidades.itertuples(index=False), predicciones, probabilidades
                )
            ],
        }
