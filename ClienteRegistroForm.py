# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Departamento, Provincia, Distrito

class ClienteRegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    celular = StringField('Celular', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    direccion = StringField('Dirección', validators=[DataRequired()])

    departamento = QuerySelectField(
        'Departamento',
        query_factory=lambda: Departamento.query.order_by(Departamento.nombre).all(),
        get_label='nombre',
        allow_blank=True
    )

    provincia = QuerySelectField(
        'Provincia',
        query_factory=lambda: Provincia.query.order_by(Provincia.nombre).all(),
        get_label='nombre',
        allow_blank=True
    )

    distrito = QuerySelectField(
        'Distrito',
        query_factory=lambda: Distrito.query.order_by(Distrito.nombre).all(),
        get_label='nombre',
        allow_blank=True
    )

    submit = SubmitField('Registrar')