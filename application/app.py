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


# @app.route('/search', methods=['GET', 'POST'])
# def search():
#     if request.method == 'POST':
#         # Handle search form submission and database query here
#         search_field = request.form['search_field']
#         search_query = request.form['search_query']

#         # Perform database query based on search query and field
#         connection = pymysql.connect(**db_config)
#         try:
#             with connection.cursor() as cursor:
#                 if search_field == 'Author':
#                     # Search by author name
#                     sql = "SELECT p.* FROM Publication p INNER JOIN Author a ON p.ID = a.Publication_id WHERE a.FirstName LIKE %s OR a.LastName LIKE %s"
#                     cursor.execute(sql, ('%' + search_query + '%', '%' + search_query + '%'))
#                 elif search_field == 'Keywords':
#                     # Search by keywords
#                     sql = "SELECT p.* FROM Publication p INNER JOIN Keywords k ON p.ID = k.Publication_Pub_ID WHERE k.Keyword LIKE %s"
#                     cursor.execute(sql, ('%' + search_query + '%',))
#                 else:
#                     # Search by other fields in Publication table
#                     sql = f"SELECT * FROM Publication WHERE {search_field} LIKE %s"
#                     cursor.execute(sql, ('%' + search_query + '%',))
#                 results = cursor.fetchall()
#         finally:
#             connection.close()  # Close database connection

#         # Render search results page with the retrieved data
#         return render_template('search_results.html', search_query=search_query, results=results)
#     else:
#         # Render the search form page
#         return render_template('search.html')


# Edit to search for author name, insitution - should list publications per author
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

        return redirect('/')  # Redirect to the homepage after adding publication
    else:
        return render_template('add_publication.html')  # Render the add publication form page

if __name__ == '__main__':
    app.run(debug=True)
