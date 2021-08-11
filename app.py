from flask import Flask, render_template
# import pymysql

app = Flask(__name__)

# database
# conn = pymysql.connect( host='localhost',
#                         user='root',
#                         password='',
#                         database='audiobooks',)

# @app.route('/')
# def Home():
#    with conn:
#       cur = conn.cursor()
#       cur.execute('select book_title, author, date_format(time,"%i:%s") as Minutes, book_img from books')
#       rows = cur.fetchall()
#       return render_template('index.html', datas=rows)

@app.route('/audiobook')
def audiobook_page():
   return render_template('admin.html')

if __name__ == "__main__":
    app.run(debug=True) 