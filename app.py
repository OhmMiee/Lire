from flask import Flask, render_template,request,redirect,url_for, flash
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import pymysql.cursors
from base64 import encode
import speech_recognition as sr


from pythainlp.word_vector import sentence_vectorizer
from sklearn.metrics.pairwise import cosine_similarity


from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

# database
connection = pymysql.connect( host='localhost',
                              user='root',
                              password='',
                              database='audiobooks',
                              charset='utf8')

UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS  

with connection:
   @app.route('/')
   def Home():
      with connection.cursor() as cur:
         cur.execute('select book_title, author, date_format(time,"%i:%s") as Minutes, book_img from books')
         rows = cur.fetchall()
         return render_template('index.html', datas=rows)
            # return str(rows)


   @app.route('/admin')
   def admin_page():
      return render_template('admin.html')

   @app.route('/upload')
   def upload_page():
      return render_template('upload.html');

   # @app.route('/insert', methods=['POST'])
   # def insert():
   #    if request.method == "POST":
         

   #       if 'imagefile' not in request.files:
   #          flash('No file part')
   #          return redirect(request.url)

   #       imagefile = request.files['imagefile']
   #       now = datetime.now()

   #       if imagefile.filename == '':
   #          flash('No image selected for uploading')
   #          return redirect(request.url)
         

   #       if imagefile and allowed_file(imagefile.filename):
   #          filename = secure_filename(imagefile.filename)
   #          imagefile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
         
   #          #print('upload_image filename: ' + filename)
   #          flash('Image successfully uploaded and displayed below')
   #          return filename

   #       category=request.form['category']
   #       bookname=request.form['bookname']
   #       authorname=request.form['authorname']
   #       story=request.form['story']
   #       with connection.cursor() as cursor:
   #          sql="insert into 'books'('category','book_img','book_file','book_name','Author','story') values(%s,%s,%s,%s,%s,%s)"
   #          cursor.execute(sql,(category, imagefile, bookfile, bookname , authorname, story))
   #          connection.commit()

   @app.route('/sign-up')
   def signUpPage():
      return render_template('signUp.html')

   class signUpForm(Form):
      first_name = StringField('First Name', [validators.Length(min=1, max=50)])
      last_name  = StringField('Last Name', [validators.Length(min=1, max=50)])
      email  = StringField('Email', [validators.Length(min=6, max=50)])
      password  = PasswordField('Password', [
         validators.DataRequired(),
         validators.EqualTo('confirm', message='Passwords do not match')
      ])
      confirm = PasswordField('Confirm Password')

   @app.route('/ign-up', methods=['POST'])
   def signUp():
      form = signUpForm(request.form)
      if request.method == 'POST' and form.validate():
         return render_template('signUp.html')
      return render_template('signUp.html', form=form)
         # fName = request.form['fName']
         # lName = request.form['lName']
         # email = request.form['email']
         # passW = request.form['pass']
         # with conn.cursor() as cursor:
         #    sql = 'insert into `users` ()'

   @app.route('/book-unknown')
   def audiobook_page():
      return render_template('book-upload.html')

   @app.route('/upload', methods=['POST'])
   def upload():

      # return file.filename

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
               sql = "update chapter set google_value = %s where chapter_id = 0"
               cur.execute(sql, transcript)
               connection.commit()
      # return render_template("book-upload.html", transcript=transcript)
      return redirect('process')
      # return transcript

   @app.route('/process')
   def compare():
      with connection.cursor() as cur:
         sql = "select origin, google_value from chapter"
         cur.execute(sql)
         twoDatas = cur.fetchall()
         origin = sentence_vectorizer(twoDatas[0][0])
         google = sentence_vectorizer(twoDatas[0][1])
         similarity = cosine_similarity(origin, google)
         return render_template('process.html', data = similarity)

   if __name__ == "__main__":
      app.run(debug=True)
