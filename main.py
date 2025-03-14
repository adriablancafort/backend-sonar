from fastapi import FastAPI
from data import artists

app = FastAPI()

@app.get("/artists")
def read_activities():
    return artists