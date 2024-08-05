from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    # Fetch all the comments from the database
    messages = Message.query.all()

    if request.method == 'POST':
        # Get the comment from the form
        comment = request.form['comment']
        # Check if the comment already exists with the same submission time
        existing_message = next(
            (m for m in messages if m.content == comment and m.timestamp == request.form['timestamp']), None)

        if existing_message:
            return redirect(url_for('index'))

        # Add the comment to the database
        new_message = Message(content=comment)
        db.session.add(new_message)
        db.session.commit()

        # Redirect the user back to the homepage
        return redirect(url_for('index'))



    # Render the template and pass the list of comments
    return render_template('index.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=True)