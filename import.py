import os
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcd-1234'
os.environ["DATABASE_URL"] = "postgresql://postgres:paul@localhost/ENGO551"
os.environ["FLASK_ENV"] = "development"
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session_cache"


Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    query = "COPY books FROM 'C:\\Users\\pauld\\Desktop\\ENGO551\\project1\\books.csv' WITH DELIMITER ',' CSV HEADER"
    db.execute(text(query))
    db.commit()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)