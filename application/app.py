
# add error handling and messages to tell the user that stuff was successful

# 9.13 Design and implement a publication-listing service. 
# The service should permit entering of information about publications, such as title, authors, year, where the publication appeared, and pages. 
# Authors should be a separate entity with attributes such as name, institution, department, email, address, and home page. 
# Your application should support multiple views on the same data. For instance, you should provide all publications by a given author (sorted by year, for example), or all publications by authors from a given institution or department. 
# You should also support search by keywords, on the overall database as well as within each of the views.
# add functionality to delete and modify and maybe keep a copy if they want to undo

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

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

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

    return render_template('homepage.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Handle search form submission and database query here
        search_field = request.form['search_field']
        search_query = request.form['search_query']

        # Perform database query based on search query and field
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                if search_field == 'Author':
                    # Search by author name
                    sql = "SELECT p.*, GROUP_CONCAT(DISTINCT CONCAT(a.FirstName, ' ', a.LastName) SEPARATOR ', ') AS Authors, GROUP_CONCAT(DISTINCT k.Keyword SEPARATOR ', ') AS Keywords " \
                          "FROM Publication p " \
                          "LEFT JOIN Author a ON p.ID = a.Publication_id " \
                          "LEFT JOIN Keywords k ON p.ID = k.Publication_id " \
                          "WHERE a.FirstName LIKE %s OR a.LastName LIKE %s " \
                          "GROUP BY p.ID"
                    cursor.execute(sql, ('%' + search_query + '%', '%' + search_query + '%'))
                elif search_field == 'Keywords':
                    # Search by keywords
                    sql = "SELECT p.*, GROUP_CONCAT(DISTINCT CONCAT(a.FirstName, ' ', a.LastName) SEPARATOR ', ') AS Authors, GROUP_CONCAT(DISTINCT k.Keyword SEPARATOR ', ') AS Keywords " \
                          "FROM Publication p " \
                          "LEFT JOIN Author a ON p.ID = a.Publication_id " \
                          "LEFT JOIN Keywords k ON p.ID = k.Publication_id " \
                          "WHERE k.Keyword LIKE %s " \
                          "GROUP BY p.ID"
                    cursor.execute(sql, ('%' + search_query + '%',))
                else:
                    # Search by other fields in Publication table
                    sql = "SELECT p.*, GROUP_CONCAT(DISTINCT CONCAT(a.FirstName, ' ', a.LastName) SEPARATOR ', ') AS Authors, GROUP_CONCAT(DISTINCT k.Keyword SEPARATOR ', ') AS Keywords " \
                          "FROM Publication p " \
                          "LEFT JOIN Author a ON p.ID = a.Publication_id " \
                          "LEFT JOIN Keywords k ON p.ID = k.Publication_id " \
                          f"WHERE {search_field} LIKE %s " \
                          "GROUP BY p.ID"
                    cursor.execute(sql, ('%' + search_query + '%',))
                results = cursor.fetchall()
                # Close database connection

        finally:
            connection.close()  # Close database connection

        # Render search results page with the retrieved data
        return render_template('search_results.html', search_query=search_query, results=results)
    else:
        # Render the search form page
        return render_template('search.html')

@app.route('/add_publication', methods=['GET', 'POST'])
def add_publication():
    if request.method == 'POST':
        # Get form data
        title = request.form['title']
        date_published = request.form['date_published']
        pages = request.form['pages']
        doi = request.form['doi']
        link = request.form['link']

        # Insert publication into Publication table
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                # Execute the SQL command to insert the publication into the Publication table
                sql = "INSERT INTO Publication (Title, DatePublished, Pages, DOI, Link) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (title, date_published, pages, doi, link))
            connection.commit()  # Commit changes to the database
        finally:
            connection.close()  # Close database connection

        return redirect('/homepage')  # Redirect to the homepage after adding publication
    else:
        return render_template('add_publication.html')  # Render the add publication form page

if __name__ == '__main__':
    app.run(debug=True)
