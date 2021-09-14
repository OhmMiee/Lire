from flask import Flask, render_template, request, redirect, url_for, flash, session, logging
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import pymysql.cursors
# from base64 import encode

import speech_recognition as sr
from pythainlp.word_vector import sentence_vectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------- Firebase Authentication ------------------- #

import pyrebase
config = {
    "apiKey": "AIzaSyAUFHpJ0PYyvIsd1oAoTPHSxkMyRNBaY5E",
    "authDomain": "lire-8e80d.firebaseapp.com",
    "projectId": "lire-8e80d",
    "databaseURL" : "",
    "storageBucket": "lire-8e80d.appspot.com",
    "messagingSenderId": "387969776204",
    "appId": "1:387969776204:web:52ce111c12acd0bc5952e9",
    "measurementId": "G-JLJG2BDC51"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# -------------------- Firebase Authentication ------------------- #

# from wtforms import Form, StringField, TextAreaField, PasswordField, validators
# from passlib.hash import sha256_crypt

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# connection database
connection = pymysql.connect( host='localhost',
                              user='root',
                              password='',
                              database='audiobooks',
                              charset='utf8')

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

with connection:

   # <---------------------------- NO SIGNIN ------------------------------------->

   # firt page
   @app.route('/')
   def Home():
      with connection.cursor() as cur:
         cur.execute('select book_id, book_title, author, date_format(time,"%i:%s") as Minutes, book_img, category_id from books where reader != 0')
         rows = cur.fetchall()
         return render_template('index.html', datas=rows)
            # return str(rows)

   # audiobook info
   @app.route('/audiobook-info/<string:id>')
   def audiobook_info(id):
      with connection.cursor() as cur:
         sql = 'select book_id, book_title, author, book_img, description, category_id from books where book_id = %s'
         cur.execute(sql, [id])
         row = cur.fetchone()
         return render_template('audiobook-info.html', data = row)
         # return row[0]
      # return id


   # sign up  
   @app.route('/sign-up', methods=['GET', 'POST'])
   def signUpPage():
      unsuccesful = 'try again'
      if request.method == 'POST':
        fName = request.form['fName']
        lName = request.form['lName']
        email = request.form['email']
        password = request.form['pass']
        with connection.cursor() as cur:
            sql="insert into `users` (`f_name`, `l_name`, `email`) values(%s,%s,%s)"
            cur.execute(sql,(fName, lName, email))
            connection.commit()
        try:
            auth.create_user_with_email_and_password(email, password)
            return 'sign up successful' + 'br' + email + 'br' + fName + ' ' + lName 
        except:
            return render_template('sign-up.html', us=unsuccesful)
      return render_template('sign-up.html')

   # sign up  
   @app.route('/sign-in', methods=['POST'])
   def signIn():
    





      

      return render_template('login.html')

   
   # <---------------------------- NO SIGNIN ------------------------------------->


   # <---------------------------- SIGNIN ------------------------------------->


   @app.route('/book-unknown')
   def audiobook_page():
      return render_template('book-upload.html')

   # upload & speech to text 
   @app.route('/upload', methods=['POST'])
   def upload():

      transcript = ""
      
      if request.method == "POST":
         print("form data received")

         if "inputfile" not in request.files:
            return redirect(request.url)

         file = request.files["inputfile"]
         if file.filename == "":
            return redirect(request.url)

         if file:
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(file)
            with audioFile as source:
               data = recognizer.record(source)
            transcript = recognizer.recognize_google(data, language="th-TH", key=None)
            with connection.cursor() as cur:
               sql = "update chapter set content = %s where chapter_id = 0"
               cur.execute(sql, transcript)
               connection.commit()
      # return render_template("book-upload.html", transcript=transcript)
      return redirect('process')
      # return transcript

   # comparison similarity
   @app.route('/process')
   def compare():
      with connection.cursor() as cur:
         sql = "select content, google_value from chapter"
         cur.execute(sql)
         twoDatas = cur.fetchall()
         origin = sentence_vectorizer(twoDatas[0][0])
         google = sentence_vectorizer(twoDatas[0][1])
         similarity = cosine_similarity(origin, google)
         return render_template('process.html', data = similarity)

   # <---------------------------- SIGNIN ------------------------------------->


   # <---------------------------- ADMIN ------------------------------------->

   # sign in page
   @app.route('/admin')
   def admin_page():
      return render_template('admin.html')

   # admin homepage
   @app.route('/admin-homepage')
   def admin_homepage():
      with connection.cursor() as cur:
         cur.execute('select book_id, book_title, author from books')
         rows = cur.fetchall()
         return render_template('admin-homepage.html', datas=rows)

   # book's summary 
   @app.route('/summary/<string:id>')
   def summary_page(id):
      with connection.cursor() as cur:
         # cur.execute("select book_title, author, category, book_img from books where book_id = %s inner join chapter ON books.chapter_id = chapter.chapter_id" , [id])
         cur.execute("select book_title, author, category_name, description, book_img from books inner join category ON books.category_id = category.category_id where book_id = %s", [id])
         result = cur.fetchone()
         return render_template('admin-summary-book.html', book=result)
         # return 

   # add centent page (Chapter)
   @app.route('/summary/insert_content')
   def add_content_page():
      return render_template('admin-add-content.html')

   # add book page
   @app.route('/insert-book')
   def insert_book_page():
      return render_template('admin-add-book.html')

   # add book process
   @app.route('/add-book', methods=['POST'])
   def addBook():
      if request.method == "POST":

         category = request.form['category']
         title = request.form['title']
         author = request.form['author']
         description = request.form['description']
            
         if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
         file = request.files['file']
         now = datetime.now()
         if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
         if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed below')
            # return render_template('admin-add-book.html', filename=filename)
         else:
            flash('Allowed image types are - png, jpg, jpeg, gif')
            return redirect(request.url)
        
         with connection.cursor() as cursor:
            no_reader = 0
            sql="insert into `books` (`book_title`, `author`, `reader`, `book_img`, `description` , `category_id`, `date`) values(%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(title, author, no_reader, filename, description, category, now))
            connection.commit()
         # return redirect('insert-content')
         return redirect('admin-homepage')

   # add content (Chapter) process
   @app.route('/summary/add-content', methods=['POST'])
   def addContent():
      if request.method == "POST":
         chapter = request.form['chapter']
         content = request.form['content']
         with connection.cursor() as cursor:
            sql = "insert into `chapter` (`chapter`, `content`) values(%s,%s)"
            cursor.execute(sql, (chapter, content))
            connection.commit()
            return chapter + ' ' + content

   # <---------------------------- ADMIN ------------------------------------->


   if __name__ == "__main__":
      app.run(debug=True)
