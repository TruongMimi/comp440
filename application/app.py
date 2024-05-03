# We used PyMySQL its portabilty making it ideal for containerizing environments as we did in Docker.
# There is no  need to install additional libraries within the containers

# Order of demo: (REORG FUNCTIONS)
# 1. User sign up
# 2. User login


from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql, re
from collections import defaultdict
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 's3CretK3y'

# MySQL connection configuration
db_config = {
    'host': '192.168.86.61',
    'user': 'newuser',
    'password': 'new_password',
    'database': 'publication_listings',
    'cursorclass': pymysql.cursors.DictCursor
}

# Function to render login page upon navigating to the application
@app.route('/')
def index():
    return render_template('login.html')


# Function to render the homepage 
@app.route('/homepage')
def homepage():
    login_success = request.args.get('login_success', False)
    pub_mod_success = request.args.get('pub_mod_success', False)
    add_mod_success = request.args.get('add_mod_success', False)
    return render_template('homepage.html', login_success=login_success, pub_mod_success=pub_mod_success, add_mod_success=add_mod_success)


# Function the render the signup page with the respective errors that occurred from the main signup page
@app.route('/signup_page')
def signup_page():
    signup_failure = request.args.get('signup_failure', False)
    password_mismatch = request.args.get('password_mismatch', False)
    return render_template('index.html', Password_mismatch=password_mismatch, Signup_failure=signup_failure )


# Function to validate email format during user signup
def validate_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)

# Function for user sign up
@app.route('/signup', methods=['POST'])
def signup():
    try:
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        # This ensures that the password is not less than 6 characters
        if len(password) < 6:
            return render_template('signup.html', Password_error=True)
        
        # This validates the email format
        if not validate_email(email):
            return render_template('signup.html', Email_error=True)
            
        # This checks if the passwords match
        if password != confirmPassword:
            return render_template('signup.html', Password_mismatch=True)

        # This hashes the password to secure the password before inserting it into the database
        hashed_password = generate_password_hash(password)

        # This opens a connection to the database using the database settings specified 
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                # This queries the database to find if the email already exists
                sql = "SELECT * FROM Users WHERE Email = %s"
                cursor.execute(sql, (email,))
                existing_user = cursor.fetchone()

                # If the user exists, the signup page is rendered with a message indicating that the email already exists
                if existing_user:
                    return render_template('signup.html', Signup_failure=True)

                # If the email doesn't exist, insert the new user into the Users table
                sql_insert = "INSERT INTO Users (FirstName, LastName, Email, Password) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_insert, (firstName, lastName, email, hashed_password))
                connection.commit()

        except pymysql.Error as e:
            # This handles any database error that might have occurred
            flash("An error occurred. Please try again later.", "error")
            return redirect(url_for('signup_page'))

        finally:
            # This closes the database connection
            connection.close() 
        
    except Exception as e:
        # This handles any exceptions that might have occurred during the signup process
        flash('An error occurred during signup: {}'.format(str(e)), 'error')  # Flash error message

    return redirect(url_for('login', Signup_success=True))


# Function for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    signup_success = request.args.get('Signup_success', False)
   
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # This opens a connection to the database using the database settings specified 
        connection = pymysql.connect(**db_config)
        try:
             # This queries the database to find if the email enters exists in the database
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Users WHERE Email = %s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()

                if user:
                    # This checks if the user entered password matches the hashed password in the database
                    if check_password_hash(user['Password'], password):
                        # This stores the user ID in the session
                        session['user_id'] = user['ID']
                        return redirect(url_for('homepage', login_success=True))
                    else:
                        return render_template('login.html', Login_failure=True, Signup_success=signup_success)
                else:
                    return render_template('login.html', Login_failure=True, Signup_success=signup_success)
        finally:
            # This closes the database connection
            connection.close()
    return render_template('login.html', Signup_success=signup_success)


# Function for searching the publications table with the specified parameters
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # This gets the search parameters of the field to be searched and what to search for
        search_field = request.form['search_field']
        search_query = request.form['search_query']

        # This opens a connection to the database using the database settings specified 
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                # This puts together a query that will join the publication, author, and keyword tables and search for the matching author from the user specified parameter 
                if search_field == 'Author':
                    # This query searches for the matching author name
                    if ' ' in search_query:
                        # Split the search query into first name and last name
                        first_name, last_name = search_query.split(' ')
                        # Construct the SQL query to search for both first and last name
                        author_sql = "SELECT DISTINCT Publication_id FROM Author WHERE FirstName LIKE %s AND LastName LIKE %s"
                        cursor.execute(author_sql, ('%' + first_name + '%', '%' + last_name + '%'))
                    else:
                        # Construct the SQL query to search for either first name or last name
                        author_sql = "SELECT DISTINCT Publication_id FROM Author WHERE FirstName LIKE %s OR LastName LIKE %s"
                        cursor.execute(author_sql, ('%' + search_query + '%', '%' + search_query + '%'))
                    publication_ids = [row['Publication_id'] for row in cursor.fetchall()]

                else:
                    # Search by other fields in Publication table
                    sql = "SELECT DISTINCT ID FROM Publication WHERE {} LIKE %s".format(search_field)
                    cursor.execute(sql, ('%' + search_query + '%',))
                    publication_ids = [row['ID'] for row in cursor.fetchall()]


                # Fetch author details for each publication
                author_details = {}
                for publication_id in publication_ids:
                    author_sql = "SELECT DISTINCT FirstName, LastName, Institution, Department, Email, Homepage FROM Author WHERE Publication_id = %s"
                    cursor.execute(author_sql, (publication_id,))
                    authors = cursor.fetchall()
                    author_details[publication_id] = authors


                # Fetch keyword details for each publication
                keyword_details = {}
                for publication_id in publication_ids:
                    keyword_sql = "SELECT DISTINCT Keyword FROM Keywords WHERE Publication_id = %s"
                    cursor.execute(keyword_sql, (publication_id,))
                    keywords = [row['Keyword'] for row in cursor.fetchall()]
                    keyword_details[publication_id] = keywords

                # Fetch publication details with ordering by DatePublished DESC
                publication_sql = "SELECT * FROM Publication WHERE ID IN ({}) ORDER BY DatePublished DESC".format(','.join(['%s'] * len(publication_ids)))
                cursor.execute(publication_sql, publication_ids)
                results = cursor.fetchall()

                # Combine results with author and keyword details
                for publication in results:
                    publication_id = publication['ID']
                    publication['Authors'] = author_details.get(publication_id, [])
                    publication['Keywords'] = keyword_details.get(publication_id, [])

        finally:
            connection.close()  # Close database connection
        print(results)
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
        authors = request.form.getlist('authors[]') 
        author_details = request.form.getlist('author_details[]') 
        keywords = request.form['keywords'] 

        # Insert publication into Publication table
        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cursor:
                # Execute the SQL command to insert the publication into the Publication table
                sql = "INSERT INTO Publication (Title, DatePublished, Pages, DOI, Link) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (title, date_published, pages, doi, link))
                publication_id = cursor.lastrowid  # Get the ID of the newly inserted publication

                # Insert authors into Author table
                for i, author in enumerate(authors):
                    # Get author details if available
                    institution = author_details[i * 5].strip() if len(author_details) > i * 5 else None
                    department = author_details[i * 5 + 1].strip() if len(author_details) > i * 5 + 1 else None
                    email = author_details[i * 5 + 2].strip() if len(author_details) > i * 5 + 2 else None
                    homepage = author_details[i * 5 + 3].strip() if len(author_details) > i * 5 + 3 else None

                    sql = "INSERT INTO Author (Publication_id, FirstName, LastName, Institution, Department, Email, Homepage) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (publication_id, author.split()[0], ' '.join(author.split()[1:]), institution, department, email, homepage))
                    
                 # Split keywords input string into individual keywords
                keywords = request.form['keywords'].split(',')

                # Insert keywords into Keywords table
                for keyword in keywords:
                    sql = "INSERT INTO Keywords (Publication_id, Keyword) VALUES (%s, %s)"
                    cursor.execute(sql, (publication_id, keyword.strip()))

            connection.commit()  # Commit changes to the database
        finally:
            connection.close()  # Close database connection

        return render_template('homepage.html', add_mod_success=True)  # Redirect to the homepage after adding publication
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

        return redirect(url_for('homepage', pub_mod_success=True))  # Redirect to the homepage after modifying publication
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)