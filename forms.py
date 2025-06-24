from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.fields import DateField
from app.models import Departamento, Provincia, Distrito
from datetime import datetime

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    rol = SelectField('Rol', choices=[('usuario', 'Usuario'), ('admin', 'Admin')])
    submit = SubmitField('Crear cuenta')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    precio = FloatField('Precio', validators=[DataRequired(), NumberRange(min=50)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Guardar')

class VentaForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Registrar Venta')

class ClienteRegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    direccion = StringField('Dirección', validators=[DataRequired()])
    celular = StringField('Celular', validators=[DataRequired()])

    departamento = QuerySelectField('Departamento', get_label='nombre', allow_blank=False, get_pk=lambda x: x.id)
    provincia = QuerySelectField('Provincia', get_label='nombre', allow_blank=False, get_pk=lambda x: x.id)
    distrito = QuerySelectField('Distrito', get_label='nombre', allow_blank=False, get_pk=lambda x: x.id)

    fecha_registro = DateField('Fecha de Registro', default=datetime.utcnow, format='%Y-%m-%d')
    submit = SubmitField('Registrar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.departamento.query = Departamento.query.order_by(Departamento.nombre).all()
        self.provincia.query = Provincia.query.order_by(Provincia.nombre).all()
        self.distrito.query = Distrito.query.order_by(Distrito.nombre).all()