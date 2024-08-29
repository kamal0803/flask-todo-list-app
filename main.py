from flask import Flask, render_template, request, redirect, url_for
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import TextAreaField, SubmitField, StringField, PasswordField
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
app.config['SECRET_KEY'] = 'my-secret-key'
Bootstrap5(app)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

todo_list_items = []


class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField(label='Log In')

class Login(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()

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
        name = form.name.data
        email = form.email.data
        password = form.password.data

        new_login = Login(name=name, email=email, password=password)
        db.session.add(new_login)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("login.html", form=form)


if __name__ == '__main__':
    app.run()