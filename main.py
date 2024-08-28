from flask import Flask, render_template, request, redirect, url_for
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import TextAreaField, SubmitField
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
app.config['SECRET_KEY'] = 'my-secret-key'
Bootstrap5(app)

todo_list_items = []

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


if __name__ == '__main__':
    app.run()