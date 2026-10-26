from datetime import datetime

from sqlalchemy import extract, func

from config.db import db
from model.consumo import Consumo
from service.alertaService import AlertaService


class ConsumoService:
    @staticmethod
    def _parsear_periodo(periodo):
        if not periodo:
            raise ValueError("Selecciona el mes y año facturados.")

        try:
            return datetime.strptime(periodo, "%Y-%m").date().replace(day=1)
        except (TypeError, ValueError):
            raise ValueError("El periodo debe tener formato año-mes (AAAA-MM).")

    @classmethod
    def crear_consumo(cls, data, user_id):
        periodo = cls._parsear_periodo(data.get("periodo_consumo"))
        nuevo_consumo = Consumo(
            localidad=data["localidad"],
            barrio=data["barrio"],
            kw_consumo=data["kw_consumo"],
            periodo_consumo=periodo,
            estrato=data.get("estrato") or None,
            personas_vivienda=data.get("personas_vivienda") or None,
            user_id=user_id,
        )
        if float(data["kw_consumo"]) > 500:
            AlertaService.crear_alerta(
                {
                    "titulo": "Consumo elevado",
                    "descripcion": (
                        f"Se registró un consumo de {data['kw_consumo']} kWh"
                    ),
                    "tipo": "danger",
                    "user_id": user_id,
                }
            )
        db.session.add(nuevo_consumo)
        db.session.commit()
        return {"success": True}

    @staticmethod
    def total_kwh(user_id=None):
        consulta = db.session.query(func.sum(Consumo.kw_consumo))
        if user_id is not None:
            consulta = consulta.filter(Consumo.user_id == user_id)
        return float(consulta.scalar() or 0)

    @staticmethod
    def consumo_mensual(user_id=None):
        consulta = db.session.query(
            Consumo.periodo_consumo,
            func.sum(Consumo.kw_consumo),
        ).filter(Consumo.periodo_consumo.isnot(None))
        if user_id is not None:
            consulta = consulta.filter(Consumo.user_id == user_id)

        resultados = (
            consulta.group_by(Consumo.periodo_consumo)
            .order_by(Consumo.periodo_consumo)
            .all()
        )
        return [
            {
                "mes": periodo.strftime("%Y-%m"),
                "kwh": float(kwh or 0),
            }
            for periodo, kwh in resultados
        ]

    @staticmethod
    def consumo_por_zona(user_id=None):
        consulta = db.session.query(
            Consumo.localidad,
            func.sum(Consumo.kw_consumo),
        )
        if user_id is not None:
            consulta = consulta.filter(Consumo.user_id == user_id)

        resultados = consulta.group_by(Consumo.localidad).all()
        zonas = []
        for nombre, consumo in resultados:
            consumo_val = float(consumo or 0)
            zonas.append(
                {
                    "nombre": nombre,
                    "consumo": consumo_val,
                }
            )
        return zonas

    @staticmethod
    def obtener_consumos(user_id):
        return Consumo.query.filter_by(user_id=user_id).all()

    @staticmethod
    def obtener_consumo(id, user_id):
        return Consumo.query.filter_by(id=id, user_id=user_id).first()

    @staticmethod
    def ultimos_consumos(user_id=None):
        consulta = Consumo.query
        if user_id is not None:
            consulta = consulta.filter(Consumo.user_id == user_id)
        return (
            consulta.order_by(Consumo.periodo_consumo.desc())
            .limit(10)
            .all()
        )

    @staticmethod
    def variacion_mensual(user_id=None):
        hoy = datetime.now()
        mes_actual = hoy.month
        año_actual = hoy.year
        if mes_actual == 1:
            mes_pasado = 12
            año_pasado = año_actual - 1
        else:
            mes_pasado = mes_actual - 1
            año_pasado = año_actual

        filtros_actuales = [
            extract("month", Consumo.periodo_consumo) == mes_actual,
            extract("year", Consumo.periodo_consumo) == año_actual,
        ]
        filtros_pasados = [
            extract("month", Consumo.periodo_consumo) == mes_pasado,
            extract("year", Consumo.periodo_consumo) == año_pasado,
        ]
        if user_id is not None:
            filtros_actuales.append(Consumo.user_id == user_id)
            filtros_pasados.append(Consumo.user_id == user_id)

        actual = (
            db.session.query(func.sum(Consumo.kw_consumo))
            .filter(*filtros_actuales)
            .scalar()
            or 0
        )
        pasado = (
            db.session.query(func.sum(Consumo.kw_consumo))
            .filter(*filtros_pasados)
            .scalar()
            or 0
        )

        actual = float(actual)
        pasado = float(pasado)
        if pasado == 0:
            return "0%"

        variacion = ((actual - pasado) / pasado) * 100
        return f"{round(variacion, 1)}%"

    @staticmethod
    def obtener_alertas(user_id=None):
        consulta = Consumo.query.filter(Consumo.kw_consumo > 500)
        if user_id is not None:
            consulta = consulta.filter(Consumo.user_id == user_id)
        consumos = consulta.order_by(Consumo.periodo_consumo.desc()).all()

        return [
            {
                "tipo": "danger",
                "titulo": "Consumo elevado",
                "desc": f"{consumo.kw_consumo} kWh registrados",
                "hora": (
                    consumo.periodo_consumo.strftime("%Y-%m")
                    if consumo.periodo_consumo
                    else "Periodo no registrado"
                ),
                "zona": consumo.localidad,
            }
            for consumo in consumos
        ]

    @staticmethod
    def obtener_mis_consumos(user_id):
        return (
            Consumo.query.filter_by(user_id=user_id)
            .order_by(Consumo.periodo_consumo.desc())
            .all()
        )

    @classmethod
    def eliminar_consumo(cls, id, user_id):
        try:
            consumo = Consumo.query.filter_by(id=id, user_id=user_id).first()
            if not consumo:
                return {
                    "error": "El registro no existe o no tienes permisos para eliminarlo"
                }

            db.session.delete(consumo)
            db.session.commit()
            return {"success": "Consumo eliminado correctamente"}
        except Exception as error:
            db.session.rollback()
            return {"error": f"Error al eliminar en la base de datos: {error}"}
