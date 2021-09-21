from flask import Flask, render_template, request, redirect, url_for, flash, session
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
   "apiKey": "AIzaSyAkQY5UT9aye5C0XZSfhCulbuWgXd43YO4",
   "authDomain": "learn-firebase-8568d.firebaseapp.com",
   "projectId": "learn-firebase-8568d",
   "databaseURL" : "",
   "storageBucket": "learn-firebase-8568d.appspot.com",
   "messagingSenderId": "724149410398",
   "appId": "1:724149410398:web:2f9e49bec32ab7e42a72cf",
   "measurementId": "G-SLKJDS5F50"
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
   @app.route('/reader-sign-up', methods=['GET', 'POST'])
   def signUpPage():
      unsuccesful = 'try again'
      if request.method == 'POST':
        fName = request.form['fName']
        lName = request.form['lName']
        email = request.form['email']
        password = request.form['pass']
        
        try:
            with connection.cursor() as cur:
               sql="insert into `users` (`f_name`, `l_name`, `email`) values(%s,%s,%s)"
               cur.execute(sql,(fName, lName, email))
               connection.commit()
               auth.create_user_with_email_and_password(email, password)
               return redirect('reader-sign-in')
        except:
            return render_template('reader-sign-up.html', us=unsuccesful)
      return render_template('reader-sign-up.html')
      

   # sign up  
   @app.route('/reader-sign-in', methods=['GET', 'POST'])
   def signInPage():
      if request.method == 'POST':
         session['email'] = request.form['email']
         # email = request.form['email']
         password = request.form['pass']
         auth.sign_in_with_email_and_password(session['email'], password)
         # with connection.cursor() as cur:
         #    cur.execute("SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, us.email FROM books bk INNER JOIN users us on bk.reader = us.user_id WHERE bk.reader = 0")
         #    # cur.execute('select book_id, book_title, author, date_format(time,"%i:%s") as Minutes, book_img, category_id , email inner from books where reader = 0 ')
         #    rows = cur.fetchall()
         #    return render_template('reader.html', datas=rows, email=email)
         return redirect('reader-homepage')
      return render_template('reader-sign-in.html')

   
   # <---------------------------- NO SIGNIN ------------------------------------->


   # <---------------------------- SIGNIN ------------------------------------->
   @app.route('/reader-homepage')
   def reader_homepage():
      if 'email' in session:
         with connection.cursor() as cur:
            cur.execute("SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, us.email FROM books bk INNER JOIN users us on bk.reader = us.user_id WHERE bk.reader = 0")
            # cur.execute('select book_id, book_title, author, date_format(time,"%i:%s") as Minutes, book_img, category_id , email inner from books where reader = 0 ')
            rows = cur.fetchall()
            return render_template('reader.html', datas=rows, email={session["email"]})
            # return f'Logged in as {session["email"]}'
      return 'You are not logged in'


   
   @app.route('/reader-library/<string:id>')
   def reader_library(id):
      with connection.cursor() as cur:
         # cur.execute('select book_id, book_title, author, date_format(time,"%i:%s") as Minutes, book_img from books where reader = 4')
         cur.execute("SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, us.email FROM books bk INNER JOIN users us ON bk.reader = us.user_id WHERE us.email = %s", [id[2:-2]])
         rows = cur.fetchall()
         # return render_template('reader.html', datas=rows)
         return render_template('reader-library.html', datas=rows)
         # return id
         # return id[2:-2]

   @app.route('/show-chapter-<string:id>')
   def reader_show_chapter(id):
      try:
         with connection.cursor() as cur:
            sql = 'SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, bk.description, bk.category_id, cp.chapter_id, cp.chapter FROM books bk JOIN chapter cp ON bk.book_id = cp.book_id WHERE bk.book_id = %s'
            cur.execute(sql, [id])
            rows = cur.fetchall()
            return render_template('reader-show-chapter.html', datas=rows)
      except:
         with connection.cursor() as cur:
            sql = 'SELECT book_id, book_title, author, book_img, description, category_id FROM books WHERE book_id = %s'
            cur.execute(sql, [id])
            row = cur.fetchone()
            return render_template('reader-no-chapter.html', data=row)

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
         if similarity >=0.85:
            return render_template('passed.html')
         else:
            return render_template('failed.html')   
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
         # cur.execute('select book_id, book_title, author from books')
         sql = "SELECT bk.book_id, bk.book_title, bk.author, ct.category_name FROM books bk INNER JOIN category ct on bk.category_id = ct.category_id ORDER BY bk.book_id"
         cur.execute(sql)
         rows = cur.fetchall()
         return render_template('admin-homepage.html', datas=rows, i = 0)

   # book's summary 
   @app.route('/summary/<string:id>')
   def summary_page(id):
      try:
         with connection.cursor() as cur:
         # cur.execute("select book_title, author, category, book_img from books where book_id = %s inner join chapter ON books.chapter_id = chapter.chapter_id" , [id])
         # cur.execute("select book_title, author, category_name, description, book_img, chapter.chapter from books inner join category on books.category_id = category.category_id right join chapter on books.book_id = chapter.book_id where book_id = %s", [id])
            cur.execute("SELECT bk.book_id, bk.book_title, bk.author, ct.category_name, bk.description, bk.book_img, cp.chapter FROM books bk INNER JOIN category ct on bk.category_id = ct.category_id RIGHT JOIN chapter cp on bk.book_id = cp.book_id WHERE bk.book_id = %s", [id])
            result = cur.fetchall()
            return render_template('admin-summary-book.html', book=result, cp = 'Chapter')
      except:
         with connection.cursor() as cur:
            cur.execute("SELECT bk.book_id, bk.book_title, bk.author, ct.category_name, bk.description, bk.book_img FROM books bk INNER JOIN category ct on bk.category_id = ct.category_id WHERE bk.book_id = %s", [id])
            result = cur.fetchall()
            return render_template('admin-summary-book.html', book=result, cp = 'No Chapter')

   # add centent page (Chapter)
   @app.route('/summary/insert_content/<string:id>')
   def add_content_page(id):
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
            # flash('Image successfully uploaded and displayed below')
            # return render_template('admin-add-book.html', filename=filename)
         else:
            flash('Allowed image types are - png, jpg, jpeg, gif')
            return redirect(request.url)
        
         with connection.cursor() as cursor:
            no_reader = 0
            sql="insert into `books` (`book_title`, `author`, `reader`, `book_img`, `description` , `category_id`, `date`) values(%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(title, author, no_reader, filename, description, category, now))
            connection.commit()
            flash("Add successful")
            return redirect('admin-homepage')
         # return redirect('insert-content')

   # edit book page
   @app.route('/update-book/<string:id>')
   def update_book_page(id):
      with connection.cursor() as cur:
         sql = 'SELECT bk.book_id, bk.book_title, bk.author, ct.category_id, bk.description, bk.book_img FROM books bk INNER JOIN category ct on bk.category_id = ct.category_id WHERE bk.book_id = %s'
         cur.execute(sql, [id])
         row = cur.fetchone()
         return render_template('admin-edit-book.html', book=row)

   # edit book process
   @app.route('/update-book/edit-book-<string:id>', methods=['POST'])
   def editBook(id):
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
            # flash('Image successfully uploaded and displayed below')
            # return render_template('admin-add-book.html', filename=filename)
         else:
            flash('Allowed image types are - png, jpg, jpeg, gif')
            return redirect(request.url)
        
         with connection.cursor() as cursor:
            no_reader = 0
            sql="update books set book_title = %s, author = %s , reader = %s , book_img = %s, description = %s, category_id = %s, date = %s where book_id = %s"
            cursor.execute(sql,(title, author, no_reader, filename, description, category, now, id))
            connection.commit()
         return redirect(url_for('admin_homepage'))
         # return redirect('insert-content')

   # edit book page
   @app.route('/delete-book/<string:id>')
   def delete_book_page(id):
      with connection.cursor() as cur:
         sql = 'delete from books WHERE book_id = %s'
         cur.execute(sql, [id])
         connection.commit()
         return redirect(url_for('admin_homepage'))

   

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
