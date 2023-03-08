import csv
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("flights.csv")
    reader = csv.reader(f)
    for origin, destination, duration in reader:
        consulta = text("INSERT INTO flights (origin, destination, duration) VALUES (:origin, :destination, :duration)")
        db.execute(consulta, {"origin": origin, "destination": destination, "duration": duration})
        print(consulta)
        print("hola")
        
    db.commit()
    
if __name__ == "__main__":
    main()