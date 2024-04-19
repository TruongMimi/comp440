from flask import Flask, render_template, request, redirect
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

    return render_template('search.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Handle search form submission and database query here
        search_query = request.form['search_query']

        # Perform database query based on search query
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Publication WHERE Title LIKE %s OR DatePublished LIKE %s"
                cursor.execute(sql, ('%' + search_query + '%', '%' + search_query + '%'))
                results = cursor.fetchall()
        finally:
            connection.close()  # Close database connection

        # Render search results page with the retrieved data
        return render_template('search_results.html', search_query=search_query, results=results)
    else:
        # Render the search form page
        return render_template('search.html')

@app.route('/author/<int:author_id>')
def author(author_id):
    # Handle retrieving author's publications from the database
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command to retrieve author's information and publications
            sql_author_info = "SELECT * FROM Author WHERE ID = %s"
            cursor.execute(sql_author_info, (author_id,))
            author_info = cursor.fetchone()

            sql_author_publications = "SELECT * FROM Publication WHERE ID IN (SELECT Publication_id FROM Author WHERE ID = %s)"
            cursor.execute(sql_author_publications, (author_id,))
            author_publications = cursor.fetchall()
    finally:
        connection.close()  # Close database connection

    # Render author publications page with the retrieved data
    return render_template('author.html', author_info=author_info, author_publications=author_publications)

if __name__ == '__main__':
    app.run(debug=True)
