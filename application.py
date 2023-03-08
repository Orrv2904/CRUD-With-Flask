import os
from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
from psycopg2 import paramstyle

load_dotenv()

app = Flask(__name__)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    leer = text("SELECT * FROM flights ORDER BY id ASC")
    flights = db.execute(leer).fetchall()
    return render_template("index.html", flights=flights)