from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import login_user, LoginManager, login_required, logout_user, UserMixin, current_user
from sqlalchemy.orm import relationship


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# to track users logins
login_manager = LoginManager()
login_manager.init_app(app)

# charger un utilisateur à partir de la base de données en utilisant son identifiant
# loading the current user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    comments = relationship("Comment", back_populates="comment_author")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_author = relationship("User", back_populates="comments")


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def get_all_comments():
    # Fetch all the comments from the database
    all_messages = Comment.query.all()
    if not hasattr(get_all_comments, 'is_called'):
        # First time the function is called
        setattr(get_all_comments, 'is_called', True)
        user = None
    else:
        user = current_user
    if request.method == 'POST':
        # Get the comment from the form
        comment = request.form['comment']
        # Check if the comment already exists with the same submission time
        existing_message = next(
            (m for m in all_messages if m.content == comment and m.timestamp == request.form['timestamp']), None)

        if existing_message:
            return redirect(url_for('index'))

        # Add the comment to the database
        print(current_user)
        new_message = Comment(content=comment, comment_author=current_user)
        db.session.add(new_message)
        db.session.commit()

        # Redirect the user back to the homepage
        return redirect(url_for('get_all_comments'))

    return render_template('index.html', messages=all_messages, current_user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].upper()

        user = User.query.filter_by(username=username).first()
        # user doesn't exist
        if not user:
            flash("User does not exist, please try again.")
        else:
            login_user(user)
            return redirect(url_for('get_all_comments'))
    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_comments'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].upper()
        if User.query.filter_by(username=username).first():
            flash("Pseudo unavailable,already taken.")
            return redirect(url_for('login'))
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('get_all_comments'))
    return render_template('register.html')


@app.route('/sama')
def secret():
    users = User.query.all()
    return render_template('secrets.html',users=users)


if __name__ == '__main__':
    app.run(debug=True)
