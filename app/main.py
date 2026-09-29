from fastapi import FastAPI
from . import models
from .database import Base, engine
from time import time
import psycopg2
from psycopg2.extras import RealDictCursor
from .routers import post, user, auth


app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
Base.metadata.create_all(bind=engine)

while True:
        try:
            conn =psycopg2.connect(host='localhost', database='fastapi',
                                    user='postgres', password='123', 
                                    cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            print("Database connected successfully")
            break
        except Exception as error:
            print("connection to database failed")
            print("Error:", error)
            time.sleep(2)

@app.get("/")
def home():
    return {"message": "Stock Portfolio API is running"}