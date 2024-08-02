from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
socketio = SocketIO(app)
db = SQLAlchemy(app)



class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# with app.app_context():
#     db.create_all()


@app.route('/')
def index():
    messages = Message.query.all()
    return render_template('index.html', messages=messages)


@socketio.on('message')
def handle_message(msg):
    new_message = Message(content=msg)
    db.session.add(new_message)
    db.session.commit()
    socketio.emit('message', msg)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)