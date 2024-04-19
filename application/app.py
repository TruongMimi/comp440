from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

# MySQL connection configuration
db_config = {
    'host': 'localhost',
    'user': 'newuser',
    'password': 'new_password',
    'database': 'publication_listings',
    'cursorclass': pymysql.cursors.DictCursor
}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    # Get form data
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    address = request.form['address']
    email = request.form['email']

    # Insert user into Users table
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command to insert the user into the Users table
            sql = "INSERT INTO Users (FirstName, LastName, Address, Email) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (firstName, lastName, address, email))
        connection.commit()  # Commit changes to the database
    finally:
        connection.close()  # Close database connection

    return 'User signed up successfully!'

if __name__ == '__main__':
    app.run(debug=True)