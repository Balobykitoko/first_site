from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)

# CONFIGURATION
# In a real app, keep the SECRET_KEY secret!
app.config['SECRET_KEY'] = 'dev-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INITIALIZE PLUGINS
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
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

# --- ROUTES ---

@app.route('/')
def home():
    all_questions = Question.query.all()
    return render_template('index.html', questions=all_questions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # Simple password check (for production, use password hashing!)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password.')
            
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    # Only allow the admin user to access this page
    if not current_user.is_admin:
        return "Access Denied: Admins Only", 403
    
    if request.method == 'POST':
        q_text = request.form.get('text')
        q_answer = request.form.get('answer')
        
        if q_text and q_answer:
            new_question = Question(text=q_text, correct_answer=q_answer)
            db.session.add(new_question)
            db.session.commit()
            flash('Question added successfully!')
            return redirect(url_for('admin'))
    
    # Get all questions to display in the admin table
    questions = Question.query.all()
    return render_template('admin.html', questions=questions)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- INITIALIZE DATABASE ---
# This creates the .db file and the admin user automatically
with app.app_context():
    db.create_all()
    # Create default admin if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin', 
            password='password123', 
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)