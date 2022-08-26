from flask import Flask
from flask import request
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author.to_dict(),
            "text": self.text
        }


# Resources: Author

@app.route("/authors")
def get_authors():
    quotes = QuoteModel.query.all()
    return [quote.to_dict() for quote in quotes]


@app.route("/authors/<int:author_id>")
def get_author_by_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        return f"Author with id={author_id} not found", 404
    return author.to_dict()


@app.route("/authors", methods=["POST"])
def create_author():
    author_data = request.json
    author = AuthorModel(author_data["name"])
    db.session.add(author)
    db.session.commit()
    return author.to_dict(), 201


@app.route("/authors/<int:author_id>", methods=["PUT"])
def edit_author(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        return f"Author with id {author_id} not found.", 404

    new_data = request.json
    for key in new_data.keys():
        setattr(author, key, new_data[key])

    db.session.commit()
    return author.to_dict()


@app.route("/authors/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        return f"Author with id {author_id} not found.", 404
    db.session.delete(author)
    db.session.commit()
    return author.to_dict(), 201


# Resources: Quote

@app.route("/quotes")
# object --> dict --> JSON
def get_quotes():
    quotes = QuoteModel.query.all()
    quotes_dict = []
    for quote in quotes:
        quotes_dict.append(quote.to_dict())
    return quotes_dict


@app.route("/quotes/<int:id>")
def get_quote_by_id(id):
    quote = QuoteModel.query.get(id)
    if quote:
        return quote.to_dict()
    return f"Quote with id {id} not found.", 404


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_quote(author_id):
    author = AuthorModel.query.get(author_id)
    new_quote = request.json
    q = QuoteModel(author, new_quote["text"])
    db.session.add(q)
    db.session.commit()
    return q.to_dict(), 201


@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        return f"Quote with id {id} not found.", 404

    new_data = request.json
    for key in new_data.keys():
        setattr(quote, key, new_data[key])

    db.session.commit()
    return quote.to_dict()


@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete_quote(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        return f"Quote with id {id} not found.", 404
    db.session.delete(quote)
    db.session.commit()
    return quote.to_dict(), 201


if __name__ == "__main__":
    app.run(debug=True)
