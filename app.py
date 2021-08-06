from flask import Flask, render_template, request, redirect, flash, session, logging
# from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import pymysql

app = Flask(__name__)

# config MySQL
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'audiobooks'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
# mysql = MySQL(app)


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
      # return str(rows)

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

if __name__ == "__main__":
    app.run(debug=True) 