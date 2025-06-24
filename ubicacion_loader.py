# scripts/ubicacion_loader.py

import csv
import os
import sys

# Agrega la ruta raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Departamento, Provincia, Distrito

app = create_app()

with app.app_context():
    csv_path = os.path.join('data', 'ubicacion_peru.csv')
    if not os.path.exists(csv_path):
        print(f"❌ No se encontró el archivo: {csv_path}")
        sys.exit(1)

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        total_distritos = 0
        nuevos_departamentos = 0
        nuevos_provincias = 0

        for row in reader:
            dep_nombre = row['departamento'].strip().title()
            prov_nombre = row['provincia'].strip().title()
            dist_nombre = row['distrito'].strip().title()


            departamento = Departamento.query.filter_by(nombre=dep_nombre).first()
            if not departamento:
                departamento = Departamento(nombre=dep_nombre)
                db.session.add(departamento)
                db.session.flush()
                nuevos_departamentos += 1

            provincia = Provincia.query.filter_by(nombre=prov_nombre, departamento_id=departamento.id).first()
            if not provincia:
                provincia = Provincia(nombre=prov_nombre, departamento=departamento)
                db.session.add(provincia)
                db.session.flush()
                nuevos_provincias += 1

            distrito = Distrito.query.filter_by(nombre=dist_nombre, provincia_id=provincia.id).first()
            if not distrito:
                distrito = Distrito(nombre=dist_nombre, provincia=provincia)
                db.session.add(distrito)
                total_distritos += 1

        db.session.commit()

    print(f"✔ Departamentos nuevos: {nuevos_departamentos}")
    print(f"✔ Provincias nuevas: {nuevos_provincias}")
    print(f"✔ Distritos nuevos: {total_distritos}")
