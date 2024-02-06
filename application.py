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

#This app.route is used for the main page
@app.route("/", methods=['GET', 'POST'])
def index():

    #When the method is GET, it renders the page without showing any book results, just shows the search bar.
    if request.method == 'GET':
        user_login = request.args.get('user_login', default=False)
        username=None
        if 'username' in session:
            user_login = True
            username = session['username']
        #The login status is included to modify the navbar to show if a user is logged in.
        return render_template("index.html", user_login=user_login, username=username)
    
    #If the method is POST, this means that a search was submitted, so it queries the result from the database
    #and returns and displays them in a table
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
            #With a successful search, the resulting books are returned to the index.html template
            return render_template("index.html", books=books, user_login=user_login, username=username)
        else: 
            #If the search was empty, it returns the home page with just the search bar displayed
            return render_template("index.html", user_login=user_login, username=username)


#Logs out the user and removes them from the session array
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

#Used to login a user and add them to the user database
@app.route("/login", methods=['GET','POST'])
def login():
    #If a user tries to access the login page will already logged in, they will be redirected to their profile
    if 'username' in session:
        return redirect(url_for('user'))

    #If the method is GET it renders the login page
    if request.method == 'GET':
        return render_template("login.html")
    else:
        #If the method is POST it will try to register a new user
        username = request.form.get('username')
        password = request.form.get('password')

        #Hashing the password for security
        password_hash = sha256(password.encode('utf-8')).hexdigest()

        #Creating the query and sending it to the database
        query = "SELECT COUNT(*) FROM users WHERE username = '{}' and password_hash = '{}' ".format(username, password_hash)
        result = db.execute(text(query)).fetchall()
        
        #If the user login fulfills the conditions, it will redirect to the user page
        if (result[0][0] == 1):
            session['username'] = username
            return redirect(url_for('user'))
        else:
            #If the login does not fulfill the conditions, it will stay on the login page and display an error.
            flash('Incorrect username or password.')
            return redirect(url_for('login'))


@app.route("/register", methods = ['GET', 'POST'])
def register():
    #If a user tries to access the register page will already logged in, they will be redirected to their profile
    if 'username' in session:
        return redirect(url_for('user'))

    #If the method is GET it will render the register page
    if request.method == 'GET':
        
        return render_template('register.html')
    else: #If the method is POST it will try to register a new user
        
        username = request.form.get('username')
        password = request.form.get('password')
        passwordCheck = request.form.get('passwordCheck')

        #If the password is different from the password check it will return to the register page
        if (password != passwordCheck):
            return redirect(url_for('register'))
        else:
            #If the password == passwordCheck it will try to register the user
            query = "SELECT COUNT(*) FROM users WHERE username = '{}' ".format(username)
            result = db.execute(text(query)).fetchall()
            
            if (result[0][0] == 0):
                password_hash = sha256(password.encode('utf-8')).hexdigest()
                query = "INSERT INTO users (username, password_hash) VALUES ('{}', '{}')".format(username, password_hash)
                db.execute(text(query))
                db.commit()
                #If the registration was successful, it redirects to the main page
                return redirect(url_for('index'))
            else:
                #If the registration is not successful it will flash an error and return to the register page
                flash('Username already exists.')
                return redirect(url_for('register'))



#Page for the profile of the user showing all of their reviews.
@app.route("/user")
def user():
    #If the user is logged in it will display the user page
    if 'username' in session:
        username = session['username']

        queryR = "SELECT * FROM  reviews WHERE reviewer_name= '{}' ".format(username)
        reviews = db.execute(text(queryR)).fetchall()
        return render_template("user.html", username=username, reviews=reviews)
    else:
        #If the user is not logged in it redirects to the login page
        return redirect(url_for('login'))
    

#Page to display the results after clicking on a book from a successful search
@app.route("/bookShow", methods=['GET', 'POST'])
def bookShow():
    isbn = request.args.get("isbn")

    if request.method == 'GET':
        if isbn is None: #If the ISBN is not provided, the page redirects to search again.
            return redirect(url_for('index'))
        else:
            #If an ISBN is provided, the page redirects to show the details and reviews of the book.
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
        #If the method is POST, and the user is logged in, a review will be added to the table and displayed
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
        else: #If the user is not logged in and tries to make a review, the user is redirected to the login page
            return redirect(url_for('login'))







#Running the app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)



