import os
from flask import Flask, render_template, request, flash, redirect
from flask import url_for
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
from psycopg2 import paramstyle

load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'web50'
#app.static_folder = 'statics\sass\style.css'

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    leer = text("SELECT * FROM flights ORDER BY id ASC")
    flights = db.execute(leer).fetchall()
    return render_template("index.html", flights=flights, options={"order": [[1, "asc"]]})

@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='statics/images/ico/mobilecheckintravelflightairplane_109781.ico')



@app.route('/editar_registro', methods=['POST'])
def editar_registro():
    # Recopila datos del formulario
    id_viaje = request.form.get('id')
    origen = request.form.get('origin')
    destino = request.form.get('destination')
    duracion = request.form.get('duration')
    # Valida datos del formulario
    #if not origen or not destino or not duracion:
        #flash('Todos los campos son requeridos', 'error')
        #return redirect(url_for('editar_registro', id=id_registro))
    # Actualiza registro en la base de datos
    try:
        actualizar = text("UPDATE flights SET origin=:origen, destination=:destino, duration=:duracion WHERE id=:id")
        db.execute(actualizar, {'origen': origen, 'destino': destino, 'duracion': duracion, 'id': id_viaje})
        db.commit()
        db.close()
        return redirect("/")
    except Exception as e:
        db.rollback()
        print("Error")
        return redirect("/")

@app.route('/agregar_vuelo', methods=['POST'])
def agregar_vuelo():
    if request.method == 'POST':
        if not request.form.get("origin") or not  request.form.get("destination") or not  request.form.get("duration"):
            return render_template("/")
        forigin = request.form.get("origin")
        fdestination = request.form.get("destination")
        fduration = request.form.get("duration")
        try:
            ingresar = text("INSERT INTO flights (origin, destination, duration) VALUES (:forigin,:fdestination,:fduration)")
            db.execute(ingresar, {"forigin" :forigin, "fdestination" :fdestination, "fduration" :fduration})
            db.commit()
            db.close()
            return redirect("/")
        except Exception as e:
            db.rollback()
            print("Error")
            return redirect("/")

@app.route('/eliminar_vuelo', methods=['POST'])
def eliminar_vuelo():
    if not request.form.get("origin") or not  request.form.get("destination") or not  request.form.get("duration"):
        return render_template("/")
    fid = request.form.get("id")
    try:
        eliminar = text("DELETE FROM flights WHERE id=:id")
        db.execute(eliminar, {'id': fid})
        db.commit()
        db.close()
        return redirect("/")
    except Exception as e:
        db.rollback()
        print("Error")
        return redirect("/")