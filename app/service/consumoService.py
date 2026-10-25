from model.consumo import Consumo
from config.db import db
from sqlalchemy import func, extract
from datetime import datetime
from service.alertaService import AlertaService

class ConsumoService:

    @staticmethod
    def crear_consumo(data, user_id):
        nuevo_consumo = Consumo(
            localidad=data['localidad'],
            barrio=data['barrio'],
            kw_consumo=data['kw_consumo'],
            fecha=data['fecha'],
            mes=data['mes'],
            user_id=user_id
        )
        if float(data['kw_consumo']) > 500:

            AlertaService.crear_alerta({

                "titulo": "Consumo elevado",

                "descripcion":
                    f"Se registró un consumo de "
                    f"{data['kw_consumo']} kWh",

                "tipo": "danger",

                "user_id": user_id
            })
        db.session.add(nuevo_consumo)
        db.session.commit()
        return {"success": True}

    @staticmethod
    def total_kwh(user_id):
        total = db.session.query(
            func.sum(Consumo.kw_consumo)
        ).filter(
            Consumo.user_id == user_id
        ).scalar()

        return float(total or 0)
    
    @staticmethod
    def consumo_mensual(user_id):
        resultados = db.session.query(
            Consumo.mes,
            func.sum(Consumo.kw_consumo)
        ).filter(
            Consumo.user_id == user_id
        ).group_by(
            Consumo.mes
        ).all()

        return [
            {"mes": r[0], "kwh": float(r[1] or 0)}
            for r in resultados
        ]
        
    @staticmethod
    def consumo_por_zona(user_id):
        resultados = db.session.query(
            Consumo.localidad,
            func.sum(Consumo.kw_consumo)
        ).filter(
            Consumo.user_id == user_id
        ).group_by(
            Consumo.localidad
        ).all()

        zonas = []
        for r in resultados:
            consumo_val = float(r[1] or 0)
            zonas.append({
                "nombre": r[0],
                "consumo": consumo_val,
                "capacidad": consumo_val + 200 
            })
        return zonas

    @staticmethod
    def obtener_consumos(user_id):
        return Consumo.query.filter_by(user_id=user_id).all()

    @staticmethod
    def obtener_consumo(id, user_id):
        return Consumo.query.filter_by(id=id, user_id=user_id).first()

    @staticmethod
    def ultimos_consumos(user_id):
        return Consumo.query.filter_by(user_id=user_id).order_by(Consumo.fecha.desc()).limit(10).all()
    
    
    @staticmethod
    def variacion_mensual(user_id):

        hoy = datetime.now()

        mes_actual = hoy.month
        año_actual = hoy.year

        if mes_actual == 1:
            mes_pasado = 12
            año_pasado = año_actual - 1
        else:
            mes_pasado = mes_actual - 1
            año_pasado = año_actual

        # TOTAL MES ACTUAL
        actual = db.session.query(
            func.sum(Consumo.kw_consumo)
        ).filter(
            Consumo.user_id == user_id,
            extract('month', Consumo.fecha) == mes_actual,
            extract('year', Consumo.fecha) == año_actual
        ).scalar() or 0

        # TOTAL MES PASADO
        pasado = db.session.query(
            func.sum(Consumo.kw_consumo)
        ).filter(
            Consumo.user_id == user_id,
            extract('month', Consumo.fecha) == mes_pasado,
            extract('year', Consumo.fecha) == año_pasado
        ).scalar() or 0

        actual = float(actual)
        pasado = float(pasado)

        if pasado == 0:
            return "0%"

        variacion = ((actual - pasado) / pasado) * 100

        return f"{round(variacion, 1)}%"
    
    @staticmethod
    def obtener_alertas(user_id):

        consumos = Consumo.query.filter(
            Consumo.user_id == user_id,
            Consumo.kw_consumo > 500
        ).all()

        alertas = []

        for c in consumos:

            alertas.append({
                "tipo": "danger",
                "titulo": "Consumo elevado",
                "desc": f"{c.kw_consumo} kWh registrados",
                "hora": c.fecha.strftime("%d/%m/%Y"),
                "zona": c.localidad
            })

        return alertas
    
    @staticmethod
    def obtener_mis_consumos(user_id):

        consumos = Consumo.query.filter_by(
            user_id=user_id
        ).order_by(
            Consumo.fecha.desc()
        ).all()

        return consumos
    
    @classmethod
    def eliminar_consumo(cls, id, user_id):
        try:
            consumo = Consumo.query.filter_by(id=id, user_id=user_id).first()
            
            if not consumo:
                return {"error": "El registro no existe o no tienes permisos para eliminarlo"}
            
            db.session.delete(consumo)
            db.session.commit()
            return {"success": "Consumo eliminado correctamente"}
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al eliminar en la base de datos: {str(e)}"}