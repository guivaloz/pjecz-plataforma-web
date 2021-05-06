"""
Sentencias, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Sentencia(db.Model, UniversalMixin):
    """Sentencia"""

    # Nombre de la tabla
    __tablename__ = "sentencias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column("autoridad", db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)
    sentencia = db.Column(db.String(256), index=True, nullable=False)
    expediente = db.Column(db.String(256), index=True, nullable=False)
    es_paridad_genero = db.Column(db.Boolean, nullable=False, default=False)
    archivo = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(512), nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<Sentencia {self.archivo}>"