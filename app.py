from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import mysql.connector
import random
import os
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# MySQL connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    for _ in range(30):
        try:
            conn = mysql.connector.connect(
                host=os.environ["DB_HOST"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                database=os.environ["DB_NAME"],
            )
            cursor = conn.cursor()
            with open("init.sql") as f:
                for statement in f.read().split(";"):
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
            conn.commit()
            yield
            cursor.close()
            conn.close()
            break
        except mysql.connector.Error:
            time.sleep(1)
   

SECRET_NUMBER = random.randint(1, 100)
attempts = 0

def get_scores():
    cursor.execute(
        "SELECT username, attempts FROM scores ORDER BY attempts ASC LIMIT 10"
    )
    return cursor.fetchall()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "scores": get_scores(),
            "message": ""
        }
    )


@app.post("/guess", response_class=HTMLResponse)
def guess(request: Request, username: str = Form(...), number: int = Form(...)):
    global SECRET_NUMBER
    global attempts

    attempts += 1
    message = ""

    if number < SECRET_NUMBER:
        message = "Too low!"
    elif number > SECRET_NUMBER:
        message = "Too high!"
    else:
        cursor.execute(
            "INSERT INTO scores (username, attempts) VALUES (%s, %s)",
            (username, attempts)
        )
        db.commit()

        message = f"Correct! You guessed it in {attempts} attempts."

        SECRET_NUMBER = random.randint(1, 100)
        attempts = 0

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "scores": get_scores(),
            "message": message
        }
    )