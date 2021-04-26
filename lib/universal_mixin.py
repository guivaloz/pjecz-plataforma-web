"""
UniversalMixin define las columnas y métodos comunes de todos los modelos
"""
from sqlalchemy.sql import func
from hashids import Hashids
from plataforma_web.extensions import db

hashids = Hashids(salt="this is my salt 1", min_length=16)


class UniversalMixin(object):
    """ Columnas y métodos comunes a todas las tablas """

    creado = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    modificado = db.Column(db.DateTime, onupdate=func.now(), server_default=func.now())
    estatus = db.Column(db.String(1), server_default="A", nullable=False)

    def delete(self):
        """ Eliminar registro """
        if self.estatus == "A":
            self.estatus = "B"
            return self.save()
        return None

    def recover(self):
        """ Recuperar registro """
        if self.estatus == "B":
            self.estatus = "A"
            return self.save()
        return None

    def save(self):
        """ Guardar registro """
        db.session.add(self)
        db.session.commit()
        return self

    def encode_id(self):
        """ Convertir el ID de entero a cadena """
        return hashids.encode(self.id)

    @classmethod
    def decode_id(cls, id_encoded):
        """ Convertir el ID de entero a cadena """
        return hashids.decode(id_encoded)[0]
