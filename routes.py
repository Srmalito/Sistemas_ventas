from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.forms import RegisterForm, LoginForm, ProductoForm, VentaForm, ClienteRegistroForm
from app.models import User, Producto, Cliente, Venta, DetalleVenta, Provincia, Distrito, Departamento
from app import db, bcrypt, login_manager
from flask_login import login_user, login_required, logout_user, current_user


main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('El correo ya está registrado.', 'warning')
            return render_template('register.html', form=form)
        
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw,
            rol=form.rol.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Cuenta creada exitosamente', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/productos')
@login_required
def productos():
    lista = Producto.query.all()
    return render_template('productos.html', productos=lista)

@main.route('/producto/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        try:
            precio = float(form.precio.data)
        except ValueError:
            flash('El precio debe ser un número válido (ej. 10.00)', 'danger')
            return render_template('producto_form.html', form=form, titulo='Nuevo Producto')
        producto = Producto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio=precio,
            stock=form.stock.data
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto creado correctamente', 'success')
        return redirect(url_for('main.productos'))
    return render_template('producto_form.html', form=form, titulo='Nuevo Producto')

@main.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)
    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.precio = form.precio.data
        producto.stock = form.stock.data
        db.session.commit()
        flash('Producto actualizado', 'success')
        return redirect(url_for('main.productos'))
    return render_template('producto_form.html', form=form, titulo='Editar Producto')

@main.route('/producto/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado', 'info')
    return redirect(url_for('main.productos'))

@main.route('/clientes')
@login_required
def clientes():
    lista = Cliente.query.all()
    return render_template('clientes.html', clientes=lista)

@main.route('/cliente/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    form = ClienteRegistroForm()

    if form.validate_on_submit():
        try:
            if not (form.departamento.data and form.provincia.data and form.distrito.data):
                flash("Debe seleccionar Departamento, Provincia y Distrito.", "warning")
                return render_template('cliente_form.html', form=form, titulo='Nuevo Cliente')

            nuevo = Cliente(
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                email=form.email.data,
                direccion=form.direccion.data,
                celular=form.celular.data,
                departamento_id=form.departamento.data.id,
                provincia_id=form.provincia.data.id,
                distrito_id=form.distrito.data.id,
                fecha_registro=form.fecha_registro.data
            ) 
            db.session.add(nuevo)
            db.session.commit()
            flash('Cliente registrado con éxito', 'success')
            return redirect(url_for('main.clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'danger')

    return render_template('cliente_form.html', form=form, titulo='Nuevo Cliente')


@main.route('/api/provincias')
def api_provincias():
    departamento_id = request.args.get('departamento_id', type=int)
    provincias = Provincia.query.filter_by(departamento_id=departamento_id).order_by(Provincia.nombre).all()
    return jsonify([{'id': p.id, 'nombre': p.nombre} for p in provincias])

@main.route('/api/distritos')
def api_distritos():
    provincia_id = request.args.get('provincia_id', type=int)
    distritos = Distrito.query.filter_by(provincia_id=provincia_id).order_by(Distrito.nombre).all()
    return jsonify([{'id': d.id, 'nombre': d.nombre} for d in distritos])


@main.route('/ventas')
@login_required
def ventas():
    lista = Venta.query.order_by(Venta.id.desc()).all()
    return render_template('ventas.html', ventas=lista)

@main.route('/venta/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    form = VentaForm()
    form.cliente_id.choices = [(c.id, f"{c.nombre} {c.apellido}") for c in Cliente.query.all()]
    productos = Producto.query.filter(Producto.stock > 0).all()

    if request.method == 'POST':
        carrito = request.form.getlist('producto_id')
        cantidades = request.form.getlist('cantidad')

        if carrito:
            venta = Venta(cliente_id=form.cliente_id.data, total=0)
            db.session.add(venta)
            db.session.flush()
            total = 0

            for pid, qty in zip(carrito, cantidades):
                if pid:
                    producto = Producto.query.get(int(pid))
                    cantidad = int(qty)
                    if cantidad > producto.stock:
                        flash(f"Stock insuficiente para {producto.nombre}", "danger")
                        return redirect(url_for('main.nueva_venta'))

                    subtotal = producto.precio * cantidad
                    detalle = DetalleVenta(
                        venta_id=venta.id,
                        producto_id=producto.id,
                        cantidad=cantidad,
                        subtotal=subtotal
                    )
                    producto.stock -= cantidad
                    db.session.add(detalle)
                    total += subtotal

            venta.total = total
            db.session.commit()
            flash('Venta registrada con éxito', 'success')
            return redirect(url_for('main.ventas'))

        flash('Debe seleccionar al menos un producto', 'warning')

    return render_template('venta_form.html', form=form, productos=productos)

@main.route('/venta/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_venta(id):
    venta = Venta.query.get_or_404(id)
    db.session.delete(venta)
    db.session.commit()
    flash('Venta eliminada con éxito', 'info')
    return redirect(url_for('main.ventas'))
