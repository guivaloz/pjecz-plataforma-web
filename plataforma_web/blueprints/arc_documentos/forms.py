"""
Archivo Documentos, formularios
"""
from flask_wtf import FlaskForm
from datetime import date
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_juzgados_extintos.models import ArcJuzgadoExtinto

from lib.safe_string import EXPEDIENTE_REGEXP


def juzgados_extintos_opciones():
    """Opciones para select"""
    return ArcJuzgadoExtinto.query.filter_by(estatus="A").order_by(ArcJuzgadoExtinto.clave).all()


class ArcDocumentoNewArchivoForm(FlaskForm):
    """Formulario nuevo Documento"""

    expediente = StringField("Núm. Expediente (999/año)", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1900, date.today().year)])
    juzgado_id = SelectField("Instancia", coerce=int, validate_choice=False, validators=[DataRequired()])
    actor = StringField("Actor(es)", validators=[DataRequired(), Length(max=256)])
    demandado = StringField("Demandado(s)", validators=[Optional(), Length(max=256)])
    juicio = StringField("Juicio", validators=[Optional(), Length(max=128)])
    juzgado_origen = QuerySelectField("Instancia de Origen", query_factory=juzgados_extintos_opciones, get_label="nombre", validators=[Optional()], allow_blank=True)
    tipo = SelectField("Tipo de Documento", coerce=int, validate_choice=False, validators=[DataRequired()])
    ubicacion = SelectField("Ubicación", choices=ArcDocumento.UBICACIONES, validators=[DataRequired()])
    tipo_juzgado = SelectField("Tipo de Instancia", choices=ArcDocumento.TIPO_JUZGADOS, validators=[DataRequired()])
    # Campos opcionales para la bitácora o historial
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    notas = TextAreaField("Notas", validators=[Optional(), Length(max=256)])
    crear = SubmitField("Crear")


class ArcDocumentoNewSolicitanteForm(FlaskForm):
    """Formulario nuevo Documento"""

    expediente = StringField("Núm. Expediente (999/año)", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1900, date.today().year)])
    juzgado_readonly = StringField("Instancia")
    actor = StringField("Actor(es)", validators=[DataRequired(), Length(max=256)])
    demandado = StringField("Demandado(s)", validators=[Optional(), Length(max=256)])
    juicio = StringField("Juicio", validators=[Optional(), Length(max=128)])
    juzgado_origen = QuerySelectField("Instancia de Origen", query_factory=juzgados_extintos_opciones, get_label="nombre", validators=[Optional()], allow_blank=True)
    tipo = SelectField("Tipo de Documento", coerce=int, validate_choice=False, validators=[DataRequired()])
    ubicacion_readonly = StringField("Ubicación")
    tipo_juzgado = SelectField("Tipo de Instancia", choices=ArcDocumento.TIPO_JUZGADOS, validators=[DataRequired()])
    # Campos opcionales para la bitácora o historial
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    notas = TextAreaField("Notas", validators=[Optional(), Length(max=256)])
    crear = SubmitField("Crear")


class ArcDocumentoEditArchivoForm(FlaskForm):
    """Formulario modificar Documento"""

    expediente = StringField("Núm. Expediente (999/año)", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1900, date.today().year)])
    juzgado_id = SelectField("Instancia", coerce=int, validate_choice=False, validators=[DataRequired()])
    actor = StringField("Actor(es)", validators=[DataRequired(), Length(max=256)])
    demandado = StringField("Demandado(s)", validators=[Optional(), Length(max=256)])
    juicio = StringField("Juicio", validators=[Optional(), Length(max=128)])
    juzgado_origen = QuerySelectField("Instancia de Origen", query_factory=juzgados_extintos_opciones, get_label="nombre", validators=[Optional()], allow_blank=True)
    tipo = SelectField("Tipo de Documento", coerce=int, validate_choice=False, validators=[DataRequired()])
    ubicacion = SelectField("Ubicación", choices=ArcDocumento.UBICACIONES, validators=[DataRequired()])
    tipo_juzgado = SelectField("Tipo de Instancia", choices=ArcDocumento.TIPO_JUZGADOS, validators=[DataRequired()])
    # Campos opcionales para la bitácora o historial
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    notas = TextAreaField("Notas", validators=[Optional(), Length(max=256)])
    observaciones = TextAreaField("Motivo", validators=[DataRequired(), Length(min=5, max=256)])
    guardar = SubmitField("Guardar")


class ArcDocumentoEditSolicitanteForm(FlaskForm):
    """Formulario modificar Documento"""

    expediente = StringField("Núm. Expediente (999/año)", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1900, date.today().year)])
    juzgado_readonly = StringField("Instancia")
    actor = StringField("Actor(es)", validators=[DataRequired(), Length(max=256)])
    demandado = StringField("Demandado(s)", validators=[Optional(), Length(max=256)])
    juicio = StringField("Juicio", validators=[Optional(), Length(max=128)])
    juzgado_origen = QuerySelectField("Instancia de Origen", query_factory=juzgados_extintos_opciones, get_label="nombre", validators=[Optional()], allow_blank=True)
    tipo = SelectField("Tipo de Documento", coerce=int, validate_choice=False, validators=[DataRequired()])
    ubicacion_readonly = StringField("Ubicación")
    tipo_juzgado = SelectField("Tipo de Instancia", choices=ArcDocumento.TIPO_JUZGADOS, validators=[DataRequired()])
    # Campos opcionales para la bitácora o historial
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    notas = TextAreaField("Notas", validators=[Optional(), Length(max=256)])
    observaciones = TextAreaField("Motivo", validators=[DataRequired(), Length(min=5, max=256)])
    guardar = SubmitField("Guardar")


class ArcDocumentoEditNoUbicacionForm(FlaskForm):
    """Formulario modificar Documento"""

    expediente = StringField("Núm. Expediente (999/año)", validators=[DataRequired(), Length(max=16), Regexp(EXPEDIENTE_REGEXP)])
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1900, date.today().year)])
    juzgado_id = SelectField("Instancia", coerce=int, validate_choice=False, validators=[DataRequired()])
    actor = StringField("Actor(es)", validators=[DataRequired(), Length(max=256)])
    demandado = StringField("Demandado(s)", validators=[Optional(), Length(max=256)])
    juicio = StringField("Juicio", validators=[Optional(), Length(max=128)])
    juzgado_origen = QuerySelectField("Instancia de Origen", query_factory=juzgados_extintos_opciones, get_label="nombre", validators=[Optional()], allow_blank=True)
    tipo = SelectField("Tipo de Documento", coerce=int, validate_choice=False, validators=[DataRequired()])
    ubicacion_readonly = StringField("Ubicación")
    tipo_juzgado = SelectField("Tipo de Instancia", choices=ArcDocumento.TIPO_JUZGADOS, validators=[DataRequired()])
    # Campos opcionales para la bitácora o historial
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    notas = TextAreaField("Notas", validators=[Optional(), Length(max=256)])
    observaciones = TextAreaField("Motivo", validators=[DataRequired(), Length(min=5, max=256)])
    guardar = SubmitField("Guardar")
