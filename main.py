from flask import Flask, render_template, request, redirect, url_for, flash
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from wtforms.validators import DataRequired
from wtforms import TextAreaField, SubmitField, StringField, PasswordField
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Integer, String, Text

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
app.config['SECRET_KEY'] = 'my-secret-key'
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

todo_list_items = []


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField(label='Log In')

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign Up')

class User(UserMixin, db.Model):
    __tablename__ = "users"
    # Parent
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)

    todolists = relationship("ToDoList", back_populates="author")
class ToDoList(db.Model):
    __tablename__="todolists"

    #Child
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task: Mapped[str] = mapped_column(String(250), nullable=False)
    due_date = db.Column(db.DateTime)

    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="todolists")

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        
        todo_text = request.form['todo_text']
        todo_list_items.append(todo_text)

        return render_template("index.html", todo_list_items=todo_list_items)
    return render_template("index.html", todo_list_items=todo_list_items)

@app.route("/delete")
def delete():

    index = request.args.get('index')
    del todo_list_items[int(index)]

    return redirect(url_for('home'))

@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        check_user = db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none()

        if check_user: #user exists
            print("User exists")

            if check_password_hash(pwhash=check_user.password, password=password): #login is successful
                print("Log In success")
                login_user(check_user)
                return redirect(url_for('home'))

            else: #login failed as password is incorrect
                print("Log In failed")
                flash('<span class="sign-up"> Password incorrect, please try again</span>', category='error')
                return redirect(url_for('login'))

        else: # user doesn't exists, route them to sign up telling they need to sign up first
            print("User doesn't exists")
            flash('<span class="sign-up">This email ID doesnt exists, please consider <a href="/sign_up">signing up</a> first</span>')

    return render_template("login.html", form=form)

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():

    form = SignUpForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        encrypted_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(name=name, email=email, password=encrypted_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for('home'))

    return render_template("signup.html", form=form)

if __name__ == '__main__':
    app.run(debug=True)