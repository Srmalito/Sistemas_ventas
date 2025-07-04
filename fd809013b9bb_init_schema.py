"""init schema

Revision ID: fd809013b9bb
Revises: 
Create Date: 2025-06-23 14:30:36.758274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd809013b9bb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('departamento',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nombre')
    )
    op.create_table('producto',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.Column('precio', sa.Float(), nullable=False),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=150), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=False),
    sa.Column('password', sa.String(length=150), nullable=False),
    sa.Column('rol', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('provincia',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('departamento_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['departamento_id'], ['departamento.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('distrito',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('provincia_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['provincia_id'], ['provincia.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cliente',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('apellido', sa.String(length=100), nullable=False),
    sa.Column('celular', sa.String(length=15), nullable=False),
    sa.Column('direccion', sa.String(length=200), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('fecha_registro', sa.Date(), nullable=True),
    sa.Column('departamento_id', sa.Integer(), nullable=False),
    sa.Column('provincia_id', sa.Integer(), nullable=False),
    sa.Column('distrito_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['departamento_id'], ['departamento.id'], ),
    sa.ForeignKeyConstraint(['distrito_id'], ['distrito.id'], ),
    sa.ForeignKeyConstraint(['provincia_id'], ['provincia.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('venta',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cliente_id', sa.Integer(), nullable=False),
    sa.Column('total', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['cliente_id'], ['cliente.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('detalle_venta',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('venta_id', sa.Integer(), nullable=False),
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('cantidad', sa.Integer(), nullable=False),
    sa.Column('subtotal', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], ),
    sa.ForeignKeyConstraint(['venta_id'], ['venta.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('detalle_venta')
    op.drop_table('venta')
    op.drop_table('cliente')
    op.drop_table('distrito')
    op.drop_table('provincia')
    op.drop_table('user')
    op.drop_table('producto')
    op.drop_table('departamento')
    # ### end Alembic commands ###
