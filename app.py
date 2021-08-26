from flask import Flask, render_template,request,redirect,url_for, flash
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import pymysql

app = Flask(__name__)

# database
conn = pymysql.connect( host='localhost',
                        user='root',
                        password='',
                        database='testingdb',)

UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS  

@app.route('/')
def Home():
   with conn:
      cur = conn.cursor()
      cur.execute('select book_title, author, date_format(time,"%i:%s") as Minutes, book_img from books')
      rows = cur.fetchall()
      return render_template('index.html', datas=rows)

@app.route('/audiobook')
def audiobook_page():
   return render_template('admin.html')

@app.route('/upload')
def upload_page():
   return render_template('upload.html');

@app.route('/insert', methods=['POST'])
def insert():
   if request.method == "POST":
      

      if 'imagefile' not in request.files:
         flash('No file part')
         return redirect(request.url)

      imagefile = request.files['imagefile']
      now = datetime.now()

      if imagefile.filename == '':
         flash('No image selected for uploading')
         return redirect(request.url)
      

      if imagefile and allowed_file(imagefile.filename):
         filename = secure_filename(imagefile.filename)
         imagefile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      
         #print('upload_image filename: ' + filename)
         flash('Image successfully uploaded and displayed below')
         return filename

      category=request.form['category']
      bookname=request.form['bookname']
      authorname=request.form['authorname']
      story=request.form['story']
      with conn.cursor() as cursor:
         sql="insert into 'books'('category','book_img','book_file','book_name','Author','story') values(%s,%s,%s,%s,%s,%s)"
         cursor.execute(sql,(category, imagefile, bookfile, bookname , authorname, story))
         conn.commit()

   
   
   
   

   
if __name__ == "__main__":
    app.run(debug=True) 
