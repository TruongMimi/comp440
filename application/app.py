# add error handling and messages to tell the user that stuff was successful
# year in search is broken

# add author and keywords to add publication section
# Change the button for add publication

# 9.13 Design and implement a publication-listing service. 
# The service should permit entering of information about publications, such as title, authors, year, where the publication appeared, and pages. 
# Authors should be a separate entity with attributes such as name, institution, department, email, address, and home page. 
# Your application should support multiple views on the same data. For instance, you should provide all publications by a given author (sorted by year, for example), or all publications by authors from a given institution or department. 
# You should also support search by keywords, on the overall database as well as within each of the views.
# add functionality to delete and modify and maybe keep a copy if they want to undo

from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
from collections import defaultdict
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 's3CretK3y'  # Set a secret key for session management

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
    return render_template('login.html')

@app.route('/homepage')
def homepage():
    login_success = request.args.get('login_success', False)
    return render_template('homepage.html', login_success=login_success)

@app.route('/signup_page')
def signup_page():
    signup_failure = request.args.get('signup_failure', False)
    password_mismatch = request.args.get('password_mismatch', False)
    return render_template('index.html', Password_mismatch=password_mismatch, Signup_failure=signup_failure )


@app.route('/login', methods=['GET', 'POST'])
def login():
    signup_success = request.args.get('Signup_success', False)
    login_failure = request.args.get('Login_failure', False)
   
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the database to find user by email
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Users WHERE Email = %s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()

                if user:
                    # Check if the entered password matches the hashed password in the database
                    if check_password_hash(user['Password'], password):
                        # Store user ID in session
                        session['user_id'] = user['ID']
                        return redirect(url_for('homepage', login_success=True))
                    else:
                        return render_template('login.html', Login_failure=True, Signup_success=signup_success)
                else:
                    return render_template('login.html', Login_failure=True, Signup_success=signup_success)
        finally:
            connection.close()

    return render_template('login.html', Signup_success=signup_success)



@app.route('/signup', methods=['POST'])
def signup():
 
    # Get form data
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']
    password = request.form['password']
    confirmPassword = request.form['confirmPassword']

    # Check if passwords match
    if password != confirmPassword:
        return render_template('signup.html', Password_mismatch=True)

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Check if the email already exists
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Execute SQL query to check if the email exists
            sql = "SELECT * FROM Users WHERE Email = %s"
            cursor.execute(sql, (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                return render_template('signup.html', Signup_failure=True)

            # If the email doesn't exist, insert the new user into the Users table
            sql_insert = "INSERT INTO Users (FirstName, LastName, Email, Password) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql_insert, (firstName, lastName, email, hashed_password))
            connection.commit()

    except pymysql.Error as e:
        # Handle database errors
        flash("An error occurred. Please try again later.", "error")
        return redirect(url_for('signup_page'))

    finally:
        connection.close()  # Close database connection

    return redirect(url_for('login', Signup_success=True))





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
        authors = request.form['authors']  # Assuming the authors are entered as a single string separated by commas
        keywords = request.form['keywords']  # Assuming the authors are entered as a single string separated by commas

        # Insert publication into Publication table
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                # Execute the SQL command to insert the publication into the Publication table
                sql = "INSERT INTO Publication (Title, DatePublished, Pages, DOI, Link) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (title, date_published, pages, doi, link))
                publication_id = cursor.lastrowid  # Get the ID of the newly inserted publication

                # Insert authors into Author table
                authors_list = [author.strip() for author in authors.split(',')]  # Split authors by comma and remove leading/trailing whitespace
                for author in authors_list:
                    sql = "INSERT INTO Author (Publication_id, FirstName, LastName) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (publication_id, author.split()[0], ' '.join(author.split()[1:])))  # Split author into first name and last name
                    
                 # Split keywords input string into individual keywords
                keywords = request.form['keywords'].split(',')

                # Insert keywords into Keywords table
                for keyword in keywords:
                    sql = "INSERT INTO Keywords (Publication_id, Keyword) VALUES (%s, %s)"
                    cursor.execute(sql, (publication_id, keyword.strip()))

            connection.commit()  # Commit changes to the database
        finally:
            connection.close()  # Close database connection

        return redirect('/homepage')  # Redirect to the homepage after adding publication
    else:
        return render_template('add_publication.html')  # Render the add publication form page


@app.route('/modify_publication/<int:publication_id>', methods=['GET', 'POST'])
def modify_publication(publication_id):
    if request.method == 'POST':
        # Get form data
        title = request.form['title']
        date_published = request.form['date_published']
        pages = request.form['pages']
        doi = request.form['doi']
        link = request.form['link']
        authors = request.form['authors']  # Assuming the authors are entered as a single string separated by commas
        keywords = request.form['keywords']  # Assuming the authors are entered as a single string separated by commas

        # Update publication in Publication table
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                # Execute the SQL command to update the publication in the Publication table
                sql = "UPDATE Publication SET Title = %s, DatePublished = %s, Pages = %s, DOI = %s, Link = %s WHERE ID = %s"
                cursor.execute(sql, (title, date_published, pages, doi, link, publication_id))

                # Delete existing authors and keywords
                sql_delete_authors = "DELETE FROM Author WHERE Publication_id = %s"
                cursor.execute(sql_delete_authors, (publication_id,))
                sql_delete_keywords = "DELETE FROM Keywords WHERE Publication_id = %s"
                cursor.execute(sql_delete_keywords, (publication_id,))

                # Insert authors into Author table
                if authors.strip():  # Check if the author's name is not empty
                    author_parts = authors.split()
                    if len(author_parts) == 1:
                        first_name = author_parts[0]
                        last_name = ""  # Set last name to empty if only one name is provided
                    else:
                        first_name = author_parts[0]
                        last_name = ' '.join(author_parts[1:])  # Join all parts after the first one as the last name
                    sql_insert_author = "INSERT INTO Author (Publication_id, FirstName, LastName) VALUES (%s, %s, %s)"
                    cursor.execute(sql_insert_author, (publication_id, first_name, last_name))


                # Split keywords input string into individual keywords
                keywords_list = [keyword.strip() for keyword in keywords.split(',')]  # Split keywords by comma and remove leading/trailing whitespace

                # Insert keywords into Keywords table
                for keyword in keywords_list:
                    sql_insert_keyword = "INSERT INTO Keywords (Publication_id, Keyword) VALUES (%s, %s)"
                    cursor.execute(sql_insert_keyword, (publication_id, keyword))

            connection.commit()  # Commit changes to the database
        finally:
            connection.close()  # Close database connection

        return redirect(url_for('homepage'))  # Redirect to the homepage after modifying publication
    else:
        # Retrieve publication details from the database
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                # Execute the SQL command to retrieve publication details
                sql = "SELECT * FROM Publication WHERE ID = %s"
                cursor.execute(sql, (publication_id,))
                publication = cursor.fetchone()
                # Get authors
                sql_authors = "SELECT FirstName, LastName FROM Author WHERE Publication_id = %s"
                cursor.execute(sql_authors, (publication_id,))
                authors = cursor.fetchall()
                # Get keywords
                sql_keywords = "SELECT Keyword FROM Keywords WHERE Publication_id = %s"
                cursor.execute(sql_keywords, (publication_id,))
                keywords = cursor.fetchall()
        finally:
            connection.close()  # Close database connection

        return render_template('modify_publication.html', publication=publication, authors=authors, keywords=keywords)
    
    
# Define a function to retrieve publication details from the database
def get_publication_details(publication_id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command to retrieve publication details
            sql = "SELECT * FROM Publication WHERE ID = %s"
            cursor.execute(sql, (publication_id,))
            publication = cursor.fetchone()
            if publication:
                # Get authors
                sql_authors = "SELECT FirstName, LastName FROM Author WHERE Publication_id = %s"
                cursor.execute(sql_authors, (publication_id,))
                authors = cursor.fetchall()
                publication['Authors'] = authors
                # Get keywords
                sql_keywords = "SELECT Keyword FROM Keywords WHERE Publication_id = %s"
                cursor.execute(sql_keywords, (publication_id,))
                keywords = cursor.fetchall()
                publication['Keywords'] = keywords
            return publication
    finally:
        connection.close()  # Close database connection

# Define a function to restore a deleted publication
def restore_publication(publication_details):
    # Retrieve publication details
    title = publication_details['Title']
    date_published = publication_details['DatePublished']
    pages = publication_details['Pages']
    doi = publication_details['DOI']
    link = publication_details['Link']
    authors = publication_details['Authors']
    keywords = publication_details['Keywords']
    
    # Insert publication into Publication table
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command to insert the publication into the Publication table
            sql_insert_publication = "INSERT INTO Publication (Title, DatePublished, Pages, DOI, Link) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql_insert_publication, (title, date_published, pages, doi, link))
            publication_id = cursor.lastrowid  # Get the ID of the newly inserted publication

            # Insert authors into Author table
            for author in authors:
                first_name, last_name = author['FirstName'], author['LastName']
                sql_insert_author = "INSERT INTO Author (Publication_id, FirstName, LastName) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert_author, (publication_id, first_name, last_name))

            # Insert keywords into Keywords table
            for keyword in keywords:
                keyword = keyword['Keyword']
                sql_insert_keyword = "INSERT INTO Keywords (Publication_id, Keyword) VALUES (%s, %s)"
                cursor.execute(sql_insert_keyword, (publication_id, keyword))

        connection.commit()  # Commit changes to the database
    finally:
        connection.close()  # Close database connection


# Dictionary to store temporarily deleted publications
deleted_publications = defaultdict(list)



@app.route('/delete_publication/<int:publication_id>', methods=['POST'])
def delete_publication(publication_id):
    # Retrieve publication details before deletion
    publication_details = get_publication_details(publication_id)
    
    # Delete associated keywords first
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Delete keywords associated with the publication
            sql_delete_keywords = "DELETE FROM Keywords WHERE Publication_id = %s"
            cursor.execute(sql_delete_keywords, (publication_id,))
        
        connection.commit()  # Commit changes to the database
    finally:
        connection.close()  # Close database connection
    
    # Delete associated authors
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Delete authors associated with the publication
            sql_delete_authors = "DELETE FROM Author WHERE Publication_id = %s"
            cursor.execute(sql_delete_authors, (publication_id,))
        
        connection.commit()  # Commit changes to the database
    finally:
        connection.close()  # Close database connection
    
    # Now, delete the publication from the Publication table
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # Execute the SQL command to delete the publication from the Publication table
            sql_delete_publication = "DELETE FROM Publication WHERE ID = %s"
            cursor.execute(sql_delete_publication, (publication_id,))
        
        connection.commit()  # Commit changes to the database
    finally:
        connection.close()  # Close database connection

    # Store the deleted publication details temporarily
    deleted_publications[publication_id] = publication_details

    return render_template('delete_success.html', publication_id=publication_id)  # Render delete success page


# Add a route for confirming the deletion
@app.route('/confirm_delete_publication/<int:publication_id>', methods=['GET', 'POST'])
def confirm_delete_publication(publication_id):
    # Retrieve publication details from the database
    publication_details = get_publication_details(publication_id)
    if not publication_details:
        abort(404)  # Publication not found, return 404 error

    return render_template('confirm_delete_publication.html', publication_id=publication_id)

# Add a route for undoing the delete
@app.route('/undo_delete_publication/<int:publication_id>', methods=['POST'])
def undo_delete_publication(publication_id):
    # Retrieve the deleted publication details from the temporary storage
    publication_details = deleted_publications.pop(publication_id, None)
    
    if publication_details:
        # Restore the deleted publication
        restore_publication(publication_details)
    
    return render_template('undo_delete_success.html') # Redirect to the homepage after undoing delete


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
