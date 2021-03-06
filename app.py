import json
from re import U
from flask import Flask, render_template, request, redirect, url_for, flash, session
from gensim.utils import file_or_filename
from scipy.sparse import data
from werkzeug.utils import secure_filename
import os
import pymysql.cursors
# from base64 import encode

import speech_recognition as sr
from pythainlp.word_vector import sentence_vectorizer
from sklearn.metrics.pairwise import cosine_similarity

from datetime import datetime
import time
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


UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'wav'])

# connection database
connection = pymysql.connect( host='localhost',
                              user='root',
                              password='',
                              database='audiobooks',
                              charset='utf8')

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create class that acts as a countdown
def countdown(h, m, s):
 
    # Calculate the total number of seconds
    total_seconds = h * 3600 + m * 60 + s
 
    # While loop that checks if total_seconds reaches zero
    # If not zero, decrement total time by one second
    while total_seconds > 0:
 
        # Timer represents time left on countdown
        timer = datetime.timedelta(seconds = total_seconds)
        
        # Prints the time left on the timer
        print(timer, end="\r")
 
        # Delays the program one second
        time.sleep(1)
 
        # Reduces total time by one second
        total_seconds -= 1
 
    print("Bzzzt! The countdown is at zero seconds!")

with connection:

   # <---------------------------- NO SIGNIN ------------------------------------->

   # firt page
   @app.route('/')
   def Home():
      with connection.cursor() as cur:
         # cur.execute('select book_id, book_title, author, date_format(time,"%i:%s") as Minutes, book_img, category_id from books where reader IS NOT NULL ')
         cur.execute('SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, bk.category_id FROM books bk JOIN chapter cp ON bk.book_id = cp.book_id WHERE cp.reader IS NOT NULL AND cp.audio_file IS NOT NULL GROUP BY book_id')
         rows = cur.fetchall()
         return render_template('index.html', datas=rows)
            # return str(rows)

   # audiobook info
   @app.route('/audiobook-info/<string:id>')
   def audiobook_info(id):
      with connection.cursor() as cur:
         sql = 'SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, bk.description, bk.category_id, cp.chapter_id, cp.chapter FROM books bk JOIN chapter cp ON bk.book_id = cp.book_id WHERE bk.book_id = %s AND cp.audio_file IS NOT NULL'
         cur.execute(sql, [id])
         datas = cur.fetchall()
         return render_template('audiobook-info.html', datas = datas, id = id)
         # return row[0]
      # return id
   @app.route('/audiobook-player-<string:id>-<string:cp>')
   def audiobook_player(id, cp):
      with connection.cursor() as cur:
         sql = 'SELECT cp.chapter_id, cp.chapter, bk.book_title, cp.audio_file, bk.book_img FROM books bk JOIN chapter cp ON bk.book_id = cp.book_id WHERE cp.book_id = %s AND cp.audio_file IS NOT NULL'
         cur.execute(sql, [id])
         rows = cur.fetchall()
         # data = {'title: ' + row[1], 'author: ' + row[2], 'cover: ' + row[3]}
         return render_template('audiobook-player.html', datas = rows, cp = cp)

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
      try:
         if request.method == 'POST':
            session['email'] = request.form['email']
            # email = request.form['email']
            password = request.form['pass']
            auth.sign_in_with_email_and_password(session['email'], password)
            return redirect('reader-homepage')
         return render_template('reader-sign-in.html')
      except:
         return redirect(request.url)

   
   # <---------------------------- NO SIGNIN ------------------------------------->


   # <---------------------------- SIGNIN ------------------------------------->
   @app.route('/reader-homepage')
   def reader_homepage():
      if 'email' in session:
         with connection.cursor() as cur:
            cur.execute("SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, bk.category_id, cp.reader FROM books bk JOIN Chapter cp ON cp.book_id = bk.book_id WHERE cp.reader IS NULL GROUP BY book_id")
            # cur.execute("SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, bk.category_id FROM books bk WHERE bk.reader IS NULL")
               # cur.execute('select book_id, book_title, author, date_format(time,"%i:%s") as Minutes, book_img, category_id , email inner from books where reader = 0 ')
            rows = cur.fetchall()
            return render_template('reader.html', datas=rows, email={session["email"]})
               # return f'Logged in as {session["email"]}'
      return 'You are not logged in'
    


   
   @app.route('/reader-library/<string:email>')
   def reader_library(email):
      with connection.cursor() as cur:
         # cur.execute('select book_id, book_title, author, date_format(time,"%i:%s") as Minutes, book_img from books where reader = 4')
         cur.execute("SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, cp.chapter_id, us.email, cp.time_stamp FROM books bk JOIN chapter cp ON cp.book_id = bk.book_id JOIN users us ON cp.reader = us.user_id WHERE us.email = %s GROUP BY book_id", email)
         rows = cur.fetchall()
         return render_template('reader-library.html', datas=rows, email = email)

   # Re
   @app.route('/show-chapter-<string:id>-<string:email>')
   def reader_show_chapter(id, email):
      # try:
         with connection.cursor() as cur:
            sql = 'SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, bk.description, bk.category_id, cp.chapter_id, cp.chapter, cp.reader FROM books bk JOIN chapter cp ON bk.book_id = cp.book_id WHERE bk.book_id = %s'
            cur.execute(sql, [id])
            rows = cur.fetchall()
            # return rows[0]
            return render_template('reader-show-chapter.html', datas=rows, email=email)
      # except:
      #    with connection.cursor() as cur:
      #       sql = 'SELECT book_id, book_title, author, book_img, description, category_id FROM books WHERE book_id = %s'
      #       cur.execute(sql, [id])
      #       row = cur.fetchone()
      #       return render_template('reader-no-chapter.html', data=row, email=email)


   @app.route('/reserve-chapter-<string:reader>-<string:id>')
   def reserve_chapter(reader, id):

      h = int(0)
      m = int(0)
      s = int(5)
      date_now = datetime.now()

      with connection.cursor() as cur:
         sql = 'SELECT user_id FROM users WHERE email = %s'
         cur.execute(sql, reader)
         user = cur.fetchone()
         # return render_template('test.html', data=user)
         with connection.cursor() as cur:
            sql = "update chapter set reader = %s, time_stamp = %s where chapter_id = %s"
            cur.execute(sql, (user, date_now, id))
            connection.commit()
            return redirect(request.referrer)
      
      countdown(int(h), int(m), int(s))

   
   @app.route('/delete-chapter-<string:id>')
   def delete_book(id):
      with connection.cursor() as cur:
         sql = "update chapter cp set cp.reader = NULL, cp.audio_file = NULL where cp.chapter_id = %s"
         cur.execute(sql, id)
         connection.commit()
         return redirect(request.referrer)

   @app.route('/chapter-detail/<string:id>')
   def reader_add_chapter(id):
      with connection.cursor() as cur:
         sql = 'SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, bk.category_id, cp.chapter_id, cp.chapter FROM books bk JOIN chapter cp ON bk.book_id = cp.book_id WHERE cp.chapter_id = %s'
            # sql = 'SELECT book_id, book_title, author, book_img, category_id FROM books WHERE book_id = %s'
         cur.execute(sql, [id])
         row = cur.fetchone()
         return render_template('reader-chapter-detail.html', row=row)

   @app.route('/chapter-detail/read/<string:id>')
   def read(id):
      with connection.cursor() as cur:
         sql = 'SELECT bk.book_id, bk.book_title, bk.author, cp.chapter_id, cp.chapter, cp.content FROM books bk JOIN chapter cp ON bk.book_id = cp.book_id WHERE cp.chapter_id = %s'
            # sql = 'SELECT book_id, book_title, author, book_img, category_id FROM books WHERE book_id = %s'
         cur.execute(sql, [id])
         row = cur.fetchone()
      return render_template('reader-show-content.html', data=row)

   @app.route('/reserved-chapter-<string:id>-<string:email>')
   def reader_delete_book(id, email):
      # try:
         with connection.cursor() as cur:
            sql = 'SELECT bk.book_id, bk.book_title, bk.author, bk.book_img, bk.description, bk.category_id, cp.chapter_id, cp.chapter, us.email, cp.audio_file FROM books bk JOIN chapter cp ON bk.book_id = cp.book_id JOIN users us ON cp.reader = us.user_id WHERE bk.book_id = %s AND us.email = %s'
            cur.execute(sql, [id, email])
            rows = cur.fetchall()
            return render_template('reader-show-chapter-1.html', datas=rows)
      # except:
      #    return redirect('reader-homepage')


   # upload & speech to text & comparison similarity
   @app.route('/upload-<string:id>', methods=['POST'])
   def upload(id):

      transcript = ""
      
      if request.method == "POST":
         print("form data received")

         if "audio" not in request.files:
            return redirect(request.url)

         file = request.files["audio"]
         

         if file.filename == "":
            return redirect(request.url)
      
         

         # if file and allowed_file(file.filename):
         #    filename = secure_filename(file.filename)
         #    filePath = "./static/audios/" + filename
         #    file.save(filePath)

         if file:
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(file)
            with audioFile as source:
               data = recognizer.record(source)
            
               transcript = recognizer.recognize_google(data, language="th-TH", key=None)
            with connection.cursor() as cur:
               sql = "update chapter set google_value = %s where chapter_id = %s"
               cur.execute(sql, (transcript, id))
               connection.commit()
            with connection.cursor() as cur:
               sql = "select content, google_value from chapter where chapter_id = %s"
               cur.execute(sql, id)
               twoDatas = cur.fetchall()
               origin = sentence_vectorizer(twoDatas[0][0])
               google = sentence_vectorizer(twoDatas[0][1])
               similarity = cosine_similarity(origin, google)
               with connection.cursor() as cur:
                  sql = "update chapter set similarity = %s where chapter_id = %s"
                  cur.execute(sql, (similarity[0][0], id))
                  connection.commit()

         request.files["audio"].seek(0)
         if similarity >=0.85 and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filePath = "./static/audios/" + filename
            file.save(filePath)

            with connection.cursor() as cur:
               sql = "update chapter set audio_file = %s where chapter_id = %s"
               cur.execute(sql, (filename, id))
               connection.commit()
               return render_template('reader-file-passed.html', similarity=similarity[0][0])
                     # return "yes" + similarity
         else:
                  # return "No"
            return render_template('reader-file-failed.html', similarity=similarity[0][0])

              # return transcript + " " + id
         
      # return redirect(url_for('compare', file=file))
      # return transcript

      
   @app.route('/logout')
   def logout():
    # remove the email from the session if it's there
      session.pop('email', None)
      return redirect('/')

   # <---------------------------- SIGNIN ------------------------------------->


   # <---------------------------- ADMIN ------------------------------------->

   # sign in page
   @app.route('/admin', methods=['GET', 'POST'])
   def admin_page():
      try:
         if request.method == 'POST': 
            session['email'] = request.form['email']
            # email = request.form['email']
            password = request.form['pass']
            auth.sign_in_with_email_and_password(session['email'], password)
            
            
            return redirect('admin-homepage')
      except:
         return redirect(request.url)
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
      return render_template('admin-add-content.html', id=id)

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
            # no_reader = "NUll"
            sql="insert into `books` (`book_title`, `author`, `book_img`, `description` , `category_id`, `date`) values(%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(title, author, filename, description, category, now))
            connection.commit()
            cursor.close()
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
            flash("Update successful")
         return redirect(url_for('admin_homepage'))
         # return redirect('insert-content')

   # edit book page
   @app.route('/delete-book/<string:id>')
   def delete_book_page(id):
      with connection.cursor() as cur:
         sql = 'delete from books where book_id = %s'
         cur.execute(sql, [id])
         connection.commit()
         flash("Delete successful")
         return redirect(url_for('admin_homepage'))

   

   # add content (Chapter) process
   @app.route('/add-content/<string:id>', methods=['POST'])
   def addContent(id):
      if request.method == "POST":
         chapter = request.form['chapter']
         content = request.form['content']
         with connection.cursor() as cursor:
            sql = "insert into `chapter` (`chapter`, `content`, `book_id`) values(%s,%s,%s)"
            cursor.execute(sql, (chapter, content, id))
            connection.commit()
            return redirect(url_for('admin_homepage'))

   # <---------------------------- ADMIN ------------------------------------->

   

   if __name__ == "__main__":
      app.run(debug=True)
