import string
import random
import base64
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Using SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
db = SQLAlchemy(app)


class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(50), unique=True, nullable=False)
    identifier = db.Column(db.String(50), unique=True, nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        identifier = generate_identifier()
        short_url = base64.urlsafe_b64encode(identifier.encode()).decode()[:6]

        url_entry = URLMapping(original_url=original_url,
                               short_url=short_url, identifier=identifier)
        db.session.add(url_entry)
        db.session.commit()

        short_url = url_for('redirect_to_original',
                            identifier=identifier, _external=True)
        return render_template('index.html', short_url=short_url)

    return render_template('index.html')


@app.route('/<identifier>')
def redirect_to_original(identifier):
    url_mapping = URLMapping.query.filter_by(identifier=identifier).first()
    if url_mapping:
        return redirect(url_mapping.original_url)
    else:
        return redirect(url_for('index'))


def generate_identifier():
    characters = string.ascii_letters + string.digits
    identifier = ''.join(random.choice(characters) for _ in range(6))
    return identifier


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
# the short link have to be copied and pasted into a search bar of a browser
