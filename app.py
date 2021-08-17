from flask import Flask, render_template,request,redirect,url_for
import pymysql

app = Flask(__name__)

# database
conn = pymysql.connect( host='localhost',
                        user='root',
                        password='',
                        database='audiobooks',)

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
      category=request.form['category']
      imagefile=request.form['imagefile']
      bookfile=request.form['bookfile']
      bookname=request.form['bookname']
      authorname=request.form['authorname']
      story=request.form['story']
     
      with conn.cursor() as cursor:
         sql="insert into 'books'('category','book_img','book_file','book_name','Author','story') values(%s,%s,%s,%s,%s,%s)"
         cursor.execute(sql,(category, imagefile, bookfile, bookname , authorname, story))
         conn.commit()
   
   return redirect(url_for('upload'))

if __name__ == "__main__":
    app.run(debug=True) 
