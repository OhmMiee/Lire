from flask import Flask, render_template
webApp = Flask(__name__)
	
@webApp.route('/')
def Home():
   return render_template('index.html')