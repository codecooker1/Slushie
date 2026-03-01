import uuid
from hmac import new
from os import environ

from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy

from Models import Post, db

app = Flask(__name__)

app.secret_key = str(environ.get('APP_SECRET_KEY'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///slushynotes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    posts = Post.query.filter_by(is_published=True).order_by(Post.pub_date.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        title = request.form.get('title')
        email = request.form.get('e-mail')
        content = request.form.get('content')

        post = Post()
        post.create(title, name, email, content)

        verify_link = url_for('verify', token=post.token, _external=True)

        print(verify_link)

        return redirect(url_for('home'))
    else:
        return render_template('create.html')

@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash('Note not found.', 'error')
        return redirect(url_for('home'))

    if request.method == 'POST':
        submitted_email = request.form.get('e-mail')
        submitted_token = request.form.get('verification')

        if not submitted_token:
            if submitted_email == post.email:
                flash('Email verified! Now enter your secure deletion code.', 'success')
                return render_template('delete.html', id=id, step=2, email_value=submitted_email)
            else:
                flash('That email does not match the author of this note.', 'error')
                return render_template('delete.html', id=id, step=1, email_value='')
        else:
            if submitted_email == post.email and submitted_token == post.token:
                db.session.delete(post)
                db.session.commit()
                flash('Your note has been securely deleted.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect verification code. Deletion failed.', 'error')
                return render_template('delete.html', id=id, step=2, email_value=submitted_email)

    #db.session.delete(post)
    #db.session.commit()
    return redirect(url_for('home'))

@app.route('/verify/<token>')
def verify(token):
    # Search the database for a post with this exact token
    post = Post.query.filter_by(token=token).first()

    if post and not post.is_published:
        # Mark as published and save the changes to the database
        post.is_published = True
        db.session.commit()

        flash('Awesome! Your note is now live.', 'success')
    elif post and post.is_published:
        flash('This note has already been published.', 'success')
    else:
        flash('Invalid or expired verification link.', 'error')

    return redirect(url_for('home'))

@app.route('/note/<id>')
def note(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash('Note not found.', 'error')
        return redirect(url_for('home'))

    return render_template('note.html', post=post)

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
