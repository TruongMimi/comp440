from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

# MySQL connection configuration
db_config = {
    'host': 'localhost',
    'user': 'newuser',
    'password': 'new_password',
    'database': 'publication_listings',
    'cursorclass': pymysql.cursors.DictCursor  # Use dictionary cursor for easy access to query results
}

# Routes
@app.route('/')
def index():
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Publication")
        publications = cursor.fetchall()
    connection.close()
    return render_template('index.html', publications=publications)

@app.route('/authors/<author_id>')
def author_publications(author_id):
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Author WHERE author_ID = %s", (author_id,))
        author = cursor.fetchone()
    connection.close()
    return render_template('author_publications.html', author=author)

@app.route('/search')
def search():
    query = request.args.get('q')
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Publication WHERE Title LIKE %s", ('%' + query + '%',))
        publications = cursor.fetchall()
    connection.close()
    return render_template('search_results.html', query=query, publications=publications)

if __name__ == '__main__':
    app.run(debug=True)