"""
Listas de Acuerdos, formularios
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ListaDeAcuerdoNewForm(FlaskForm):
    """ Formulario Lista de Acuerdo """

    distrito = SelectField("Distrito", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    autoridad = SelectField("Autoridad", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    fecha = DateField("Fecha", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    archivo = FileField("Archivo", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class ListaDeAcuerdoEditForm(FlaskForm):
    """ Formulario Lista de Acuerdo """

    fecha = DateField("Fecha", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")
