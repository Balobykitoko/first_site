from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# DATABASE MODELS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ROUTES
@app.route('/')
def home():
    questions = Question.query.all()
    return render_template('index.html', questions=questions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid login!')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return "Access Denied", 403
    if request.method == 'POST':
        new_q = Question(text=request.form.get('text'), correct_answer=request.form.get('answer'))
        db.session.add(new_q)
        db.session.commit()
        flash('Question Added!')
    return render_template('admin.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Create the database tables
with app.app_context():
    db.create_all()
    # Create an admin user if none exists
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', password='password123', is_admin=True)
        db.session.add(admin_user)
        db.session.commit()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)