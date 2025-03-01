from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

db.init_app(app)

# Create tables
# with app.app_context():
#     db.create_all()


@app.route('/')
def home():
    books = Book.query.order_by(Book.title).all()
    return render_template('home.html', books=books)


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')
    if keyword:
        # Search in title containing the keyword
        books = Book.query.filter(Book.title.like(f'%{keyword}%')).all()
        if not books:
            flash(f'No books found matching "{keyword}"', 'info')
    else:
        books = Book.query.all()

    return render_template('home.html', books=books, keyword=keyword)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date'] or None
        date_of_death = request.form['date_of_death'] or None

        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(new_author)

        try:
            db.session.commit()
            flash('Author added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding author: {str(e)}', 'danger')

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year'] or None
        author_id = request.form['author_id']

        new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
        db.session.add(new_book)

        try:
            db.session.commit()
            flash('Book added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding book: {str(e)}', 'danger')

    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    try:
        # Check if this is the author's last book
        author = Author.query.get(book.author_id)
        author_books_count = Book.query.filter_by(author_id=book.author_id).count()

        # Delete the book
        db.session.delete(book)

        # If this was the author's last book, delete the author too
        if author_books_count == 1:
            db.session.delete(author)
            flash(f'Book and author {author.name} deleted as this was their only book', 'success')
        else:
            flash('Book deleted successfully!', 'success')

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting book: {str(e)}', 'danger')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)