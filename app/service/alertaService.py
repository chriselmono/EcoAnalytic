from model.alerta import Alerta
from config.db import db

ADVERTENCIA = 200
RIESGO = 270.50


class AlertaService:

    @staticmethod
    def crear_alerta(kw_consumo: float, user_id: int, id: int):
        
        kw = float(kw_consumo)
        
        # ALERTA DE PELIGRO (RIESGO => 270)
        if kw >= RIESGO:
            return AlertaService.crear_alerta({
                "titulo": "Elevado consumo Detectado",
                "descripcion": (
                    f"Registraste {kw} kWh este mes, superando el límite "
                    f"crítico de {RIESGO} kWh. "
                    "Debes reducir tu consumo de inmediato para evitar "
                    "sobrecostos y un impacto ambiental elevado. "
                    "Esta alerta se resolverá automáticamente cuando tu "
                    "próximo registro esté por debajo del límite."
                ),
                "tipo": "danger",
                "user_id": user_id,
                "id": id
            })
            
        # ADVERTENCIA POSIBLE RIESGO (ADVERTENCIA =>210)
        if kw >= ADVERTENCIA:
            return AlertaService.crear_alerta({
                "titulo": "Consumo por encima del promedio",
                "descripcion": (
                    f"Registraste {kw} kWh este mes, superando el límite "
                    f"recomendado de {ADVERTENCIA} kWh. "
                    "Considera reducir el uso de electrodomésticos de alto "
                    "consumo. Esta alerta se resolverá cuando tu próximo "
                    "registro esté dentro del rango normal."
                ),
                "tipo": "warning",
                "user_id": user_id,
                "id": id
        })
            
            # SI NO HAY ALERTAS PORFA AYUDAR
            AlertaService.resolver_alertas_pendientes(user_id)
            return None
            
        # alerta = Alerta(
        #     titulo=data['titulo'],
        #     descripcion=data['descripcion'],
        #     tipo=data['tipo'],
        #     user_id=data['user_id'],
        #     consumo_id=data.get('consumo_id')
        # )

        # db.session.add(alerta)
        # db.session.commit()

        # return alerta
    
    @staticmethod
    def crear_alerta(data: dict):
        alerta = Alerta(
            titulo=data['titulo'],
            descripcion=data['descripcion'],
            tipo=data['tipo'],
            user_id=data['user_id'],
            consumo_id=data.get('consumo_id')
        )
        db.session.add(alerta)
        db.session.commit()
        return alerta
        
        
    # NUEVO
    @staticmethod
    def obtener_alertas_usuario(user_id: int):
        return (
            Alerta.query
            .filter_by(user_id=user_id)
            .order_by(Alerta.fecha_creacion.desc())
            .all()
        )
        
    
    @staticmethod
    def obtener_alertas_pendientes(user_id: int):
        return (
            Alerta.query
            .filter_by(user_id=user_id, estado='pendiente')
            .order_by(Alerta.fecha_creacion.desc())
            .all()
        )

# ES NUEVO
    @staticmethod
    def marcar_resuelta(alerta_id: int, user_id: int):
        alerta = Alerta.query.filter_by(
            id=alerta_id,
            user_id=user_id
        ).first()

        if not alerta:
            return {"error": "Alerta no encontrada o sin permisos"}

        alerta.estado = 'resuelta'
        db.session.commit()
        return {"success": "Alerta marcada como resuelta"}
        
        
        
        
    @staticmethod
    def resolver_alertas_pendientes(user_id: int):
        alertas = Alerta.query.filter_by(
            user_id=user_id,
            estado='pendiente'
        ).all()

        for alerta in alertas:
            alerta.estado = 'resuelta'

        db.session.commit()

# HECHO
    @staticmethod
    def obtener_alertas_usuario(user_id):

        return Alerta.query.filter_by(
            user_id=user_id
        ).order_by(
            Alerta.fecha_creacion.desc()
        ).all()


    @staticmethod
    def marcar_resuelta(id):

        alerta = Alerta.query.get(id)

        if alerta:

            alerta.estado = 'resuelta'

            db.session.commit()