import os
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from hashlib import sha256

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


@app.route("/", methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        user_login = request.args.get('user_login', default=False)
        username=None
        if 'username' in session:
            user_login = True
            username = session['username']

        return render_template("index.html", user_login=user_login, username=username)
    else:
        search = request.form.get('search')
        search_type = request.form.get('search_type')

        user_login = request.args.get('user_login', default=False)
        username=None
        if 'username' in session:
            user_login = True
            username = session['username']

        if search:
            query = "SELECT * FROM books WHERE {} ILIKE '{}%' ".format(search_type, search)
            print(query)
            books = db.execute(text(query)).fetchall()
            print(books)
            return render_template("index.html", books=books, user_login=user_login, username=username)
        else:
            return render_template("index.html", user_login=user_login, username=username)



@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/login", methods=['GET','POST'])
def login():
    if 'username' in session:
        return redirect(url_for('user'))


    if request.method == 'GET':
        return render_template("login.html")
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = sha256(password.encode('utf-8')).hexdigest()
        query = "SELECT COUNT(*) FROM users WHERE username = '{}' and password_hash = '{}' ".format(username, password_hash)
        result = db.execute(text(query)).fetchall()
        
        if (result[0][0] == 1):
            session['username'] = username
            return redirect(url_for('user'))
        else:
            flash('Incorrect username or password.')
            return redirect(url_for('login'))


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('user'))

    if request.method == 'GET':
        
        return render_template('register.html')
    else:
        
        username = request.form.get('username')
        password = request.form.get('password')
        passwordCheck = request.form.get('passwordCheck')

        if (password != passwordCheck):
            return redirect(url_for('register'))
        else:
            query = "SELECT COUNT(*) FROM users WHERE username = '{}' ".format(username)
            result = db.execute(text(query)).fetchall()
            
            if (result[0][0] == 0):
                password_hash = sha256(password.encode('utf-8')).hexdigest()
                query = "INSERT INTO users (username, password_hash) VALUES ('{}', '{}')".format(username, password_hash)
                db.execute(text(query))
                db.commit()
                return redirect(url_for('index'))
            else:
                flash('Username already exists.')
                return redirect(url_for('register'))




@app.route("/user")
def user():
    if 'username' in session:
        username = session['username']

        queryR = "SELECT * FROM  reviews WHERE reviewer_name= '{}' ".format(username)
        reviews = db.execute(text(queryR)).fetchall()
        return render_template("user.html", username=username, reviews=reviews)
    else:
        return redirect(url_for('login'))
    


@app.route("/bookShow", methods=['GET', 'POST'])
def bookShow():
    isbn = request.args.get("isbn")

    if request.method == 'GET':
        if isbn is None:
            return redirect(url_for('index'))
        else:
            queryR = "SELECT * FROM  reviews WHERE isbn = '{}' ".format(isbn)
            queryB = "SELECT * FROM books WHERE isbn = '{}' ".format(isbn)
            reviews = db.execute(text(queryR)).fetchall()
            book_detail = db.execute(text(queryB)).fetchall()


            user_login = request.args.get('user_login', default=False)
            username=None
            if 'username' in session:
                user_login = True
                username = session['username']

        return render_template('bookShow.html', reviews=reviews, book_detail=book_detail[0], user_login=user_login, username=username)
    else:
        if 'username' in session:
            isbn = request.args.get("isbn")
            queryB = "SELECT * FROM books WHERE isbn = '{}' ".format(isbn)
            
            book_detail = db.execute(text(queryB)).fetchall()
            print(book_detail[0].isbn)
            reviewer_name = session['username']
            review_description = request.form.get('review')

            query = "INSERT INTO reviews (title, author, description, reviewer_name, isbn) VALUES ( '{}', '{}', '{}', '{}', '{}' ) ON CONFLICT (reviewer_name, title) DO UPDATE SET description = EXCLUDED.description".format(book_detail[0].title, book_detail[0].author, review_description, reviewer_name, book_detail[0].isbn)
            print(text(query))
            db.execute(text(query))
            db.commit()

            queryR = "SELECT * FROM  reviews WHERE isbn = '{}' ORDER BY review_id DESC".format(isbn)
            reviews = db.execute(text(queryR)).fetchall()


            user_login = request.args.get('user_login', default=False)
            username=None
            if 'username' in session:
                user_login = True
                username = session['username']


            return render_template('bookShow.html', reviews=reviews, book_detail=book_detail[0], user_login=user_login, username=username)
        else:
            return redirect(url_for('login'))








if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)



