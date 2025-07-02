from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.forms import RegisterForm, LoginForm, ProductoForm, VentaForm, ClienteRegistroForm
from app.models import User, Producto, Cliente, Venta, DetalleVenta, Provincia, Distrito, Departamento
from app import db, bcrypt, login_manager
from flask_login import login_user, login_required, logout_user, current_user
from xhtml2pdf import pisa
from flask import make_response
from io import BytesIO
import qrcode
from flask import send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from app.models import Venta
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.models import Venta
from flask_login import login_required
from flask import Blueprint
from datetime import datetime
from app.forms import LoginForm  # Ajusta a tu estructura real

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
    now = datetime.now()

    # Saludo según la hora
    if now.hour < 12:
        saludo = "¡Buenos días!"
    elif now.hour < 18:
        saludo = "¡Buenas tardes!"
    else:
        saludo = "¡Buenas noches!"

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Login failed. Check email and password.', 'danger')

    return render_template('login.html', form=form, now=now , saludo=saludo)  

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


@main.route('/ventas/pdf')
@login_required
def ventas_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Historial de Ventas", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [["ID", "Cliente", "Fecha", "Productos", "Total (S/.)"]]

    ventas = Venta.query.order_by(Venta.id).all()
    for v in ventas:
        productos = ", ".join([
            f"{d.producto.nombre} x {d.cantidad}" for d in v.detalles
        ])
        fecha = v.fecha.strftime('%d/%m/%Y') if v.fecha else "N/A"
        data.append([
            str(v.id),
            v.cliente.nombre,
            fecha,
            productos,
            f"{v.total:.2f}"
        ])

    table = Table(data, colWidths=[30, 90, 70, 200, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.indigo),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="ventas_historial.pdf", mimetype='application/pdf')


@main.route('/boleta/<int:id>')
@login_required
def generar_boleta(id):
    venta = Venta.query.get_or_404(id)
    cliente = venta.cliente

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, height - 40, "Boleta de Venta")
    c.setFont("Helvetica", 10)
    c.drawString(30, height - 60, f"Boleta N°: {venta.id}")
    c.drawString(30, height - 75, f"Cliente: {cliente.nombre} {cliente.apellido}")
    c.drawString(30, height - 90, f"Email: {cliente.email}")
    c.drawString(30, height - 105, f"Celular: {cliente.celular}")

    y = height - 130
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y, "Producto")
    c.drawString(200, y, "Cantidad")
    c.drawString(270, y, "Subtotal")

    c.setFont("Helvetica", 10)
    for detalle in venta.detalles:
        y -= 15
        c.drawString(30, y, detalle.producto.nombre)
        c.drawString(200, y, str(detalle.cantidad))
        c.drawString(270, y, f"S/ {detalle.subtotal:.2f}")

    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y, f"Total: S/ {venta.total:.2f}")

    # Generar QR
    qr_data = f"Boleta #{venta.id} - Cliente: {cliente.nombre} - Total: S/ {venta.total:.2f}"
    qr_img = qrcode.make(qr_data)
    qr_io = BytesIO()
    qr_img.save(qr_io)
    qr_io.seek(0)
    c.drawImage(ImageReader(qr_io), width - 120, 40, 80, 80)

    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"boleta_{venta.id}.pdf", mimetype='application/pdf')


@main.route('/admin/usuarios')
@login_required
def usuarios():
    if current_user.rol != 'admin':
        flash('Acceso restringido solo para administradores', 'danger')
        return redirect(url_for('main.index'))

    lista = User.query.all()
    return render_template('usuarios.html', usuarios=lista)


@main.route('/admin/mensajes')
@login_required
def messages():
    if current_user.rol != 'admin':
        flash('Acceso restringido solo para administradores', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('mensajes.html')  # crea mensajes.html si no existe


