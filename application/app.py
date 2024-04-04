from flask import Flask, request, render_template, redirect, url_for, jsonify, flash
import mysql.connector

app = Flask(__name__)

# Set the secret key for the application
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# db connection settings
db_config = {
    'user': '', # need to set up a user to access DB
    'password': '', # need to set up a password for the user
    'host': '', # need to find what my host ip address is
    'database': 'publication_listings',
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)