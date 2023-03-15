import os
from flask import Flask, render_template, request, flash, redirect
from flask import url_for, session
from authlib.integrations.flask_client import OAuth
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
from psycopg2 import paramstyle
from werkzeug.security import generate_password_hash, check_password_hash
#from Tables import *
from Forms import *
#from flask_login import UserMixin
from flask import abort
#from flask_sqlalchemy import SQLAlchemy
from helpers import login_required


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'web50'


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def log():
    if session.get("user_id") is None:
        return render_template("auth.html")
    else:
        return redirect("/flights")

@app.route("/flights", methods=['GET'])
@login_required
def index():
    if request.method == 'GET':
        leer = text("SELECT * FROM flights ORDER BY id ASC")
        flights = db.execute(leer).fetchall()
        return render_template("index.html", flights=flights, options={"order": [[1, "asc"]]})
    '''if not request.method == 'GET':
        return render_template("404.html")'''



@app.route('/editar_registro', methods=['POST', 'GET'])
@login_required
def editar_registro():
    id_viaje = request.form.get('id')
    origen = request.form.get('origin')
    destino = request.form.get('destination')
    duracion = request.form.get('duration')
    if not origen or not destino or not duracion:
        abort(404)
    try:
        actualizar = text("UPDATE flights SET origin=:origen, destination=:destino, duration=:duracion WHERE id=:id")
        db.execute(actualizar, {'origen': origen, 'destino': destino, 'duracion': duracion, 'id': id_viaje})
        db.commit()
        db.close()
        return redirect("/flights")
    except Exception as e:
        db.rollback()
        print("Error")
        abort(404)

@app.route('/agregar_vuelo', methods=['POST', 'GET'])
@login_required
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
            return redirect("/flights")
        except Exception as e:
            db.rollback()
            print("Error")
            abort(404)

@app.route('/eliminar_vuelo', methods=['POST', 'GET'])
@login_required
def eliminar_vuelo():
    if request.method == 'POST':
        fid = request.form.get("id")
    if not fid:
      abort(404)
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
      return redirect("/flights")
    except Exception as e:
      db.rollback()
      print("Error: ", str(e))
      abort(404)

@app.route('/Auth')
def Auth():  
    return render_template("auth.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        rname = request.form.get("name")
        remail = request.form.get("email")
        rpassword = request.form.get("password")
        hashed_password = generate_password_hash(rpassword)

        if not rname or not remail or not rpassword:
            return render_template("/Auth")

        try:
            verificar_usuario = text("SELECT EXISTS(SELECT 1 FROM users WHERE name = :rname)")
            verificar_correo = text("SELECT EXISTS(SELECT 1 FROM users WHERE email = :remail)")
            res2 = db.execute(verificar_usuario, {"rname" :rname})
            res3 = db.execute(verificar_correo, {"remail" :remail})
            user_exists = res2.fetchone()[0]
            email_exists = res3.fetchone()[0]

            if user_exists or email_exists:
                return render_template("/Auth")
            
            agregar_usuario = text("INSERT INTO users (name, email, password) VALUES (:rname, :remail, :hashed_password)")
            db.execute(agregar_usuario, {"rname" :rname, "remail" :remail, "hashed_password" :hashed_password})
            db.commit()
            db.close()
            return redirect('/Auth')
        except Exception as e:
            db.rollback()
            print("Error: ", str(e))
            abort(404)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        lemail = request.form.get("email")
        lpassword = request.form.get("password")
    if not request.form.get("email") or not request.form.get("password"):
        return redirect(url_for("auth"))
    try:
        seleccionar_usuario = text("SELECT * FROM users WHERE email=:email")
        res = db.execute(seleccionar_usuario, {'email': lemail})
        print(res)
        user = res.fetchone()
        print(user)
        db.commit()
        db.close()
        if user and check_password_hash(user[3], lpassword):
            session["user_id"] = user[0]
            return redirect("/flights")
        else:
            error = "Correo electrónico o contraseña incorrecta"
            return render_template("auth.html", error=error)
    except Exception as e:
        db.rollback()
        print("Error: ", str(e))
        abort(404)


@app.route("/logout", methods=['POST', 'GET'])
@login_required
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")
