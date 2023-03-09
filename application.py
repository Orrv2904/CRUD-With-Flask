import os
from flask import Flask, render_template, request, flash, redirect
from flask import url_for, session
from authlib.integrations.flask_client import OAuth
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
from psycopg2 import paramstyle

load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'web50'

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    '''if request.method == 'POST':'''
    leer = text("SELECT * FROM flights ORDER BY id ASC")
    flights = db.execute(leer).fetchall()
    return render_template("index.html", flights=flights, options={"order": [[1, "asc"]]})
    '''if not request.method == 'GET':
        return render_template("404.html")'''



@app.route('/editar_registro', methods=['POST'])
def editar_registro():
    id_viaje = request.form.get('id')
    origen = request.form.get('origin')
    destino = request.form.get('destination')
    duracion = request.form.get('duration')
    if not origen or not destino or not duracion:
        return redirect("/Not_Found")
    try:
        actualizar = text("UPDATE flights SET origin=:origen, destination=:destino, duration=:duracion WHERE id=:id")
        db.execute(actualizar, {'origen': origen, 'destino': destino, 'duracion': duracion, 'id': id_viaje})
        db.commit()
        db.close()
        return redirect("/")
    except Exception as e:
        db.rollback()
        print("Error")
        return redirect("/Not_Found")

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
            return redirect("/Not_Found")

@app.route('/eliminar_vuelo', methods=['POST'])
def eliminar_vuelo():
    if request.method == 'POST':
        fid = request.form.get("id")
    if not fid:
      return redirect("/Not_Found")
    try:
      # Verifica si el ID del vuelo está presente en la tabla 'flights'
      resultado = text("SELECT id FROM flights WHERE id=:id")
      db.execute(resultado, {'id': fid}).fetchone()
      if resultado is None:
        return redirect("/")
            
      # Elimina el vuelo de la tabla 'flights'
      eliminar = text("DELETE FROM flights WHERE id=:id")
      db.execute(eliminar, {'id': fid})
      db.commit()
      db.close()
      return redirect("/")
    except Exception as e:
      db.rollback()
      print("Error: ", str(e))
      return redirect("/Not_Found")

@app.route('/Not_Found')
def Not_Found():
    return render_template("404.html")

@app.route('/Auth')
def Auth():
    return render_template("auth.html")