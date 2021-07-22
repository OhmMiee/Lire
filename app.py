from flask import Flask, render_template
import pymysql

app = Flask(__name__)

# database
conn = pymysql.connect( host='localhost',
                        user='root',
                        password='',
                        database='audiobooks',)

@app.route('/')
def Home():
   time = "5.00"
   return render_template('index.html', data=time)

@app.route('/audiobook')
def audiobook_page():
   return "Hi"

if __name__ == "__main__":
    app.run(debug=True)