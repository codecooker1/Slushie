from os import environ
from flask import Flask, render_template, request, url_for, flash, redirect
from flask.cli import load_dotenv
from flask_mail import Mail, Message

from Models import Post, db

load_dotenv('.env')

app = Flask(__name__)

app.secret_key = str(environ.get('APP_SECRET_KEY'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///slushynotes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = environ.get('MAIL_USERNAME')

mail = Mail(app)

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

        msg = Message('Verify your SlushyNote!', recipients=[email])

        msg.body = f"Hello {name},\n\nYour note is almost live! Click the link below to verify and publish it:\n\n{verify_link}\n\n"
        msg.html = f"""
                <div style="font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #415462; line-height: 1.5; max-width: 600px; margin: 0 auto; padding: 20px;">

                    <h2 style="color: #111928; margin-top: 0; margin-bottom: 1rem; font-weight: 700;">Verify Your Note</h2>
                    <p style="margin-bottom: 1.5rem;">Hello <strong>{name}</strong>,</p>
                    <p style="margin-bottom: 2rem;">Your SlushyNote is almost live! Click the button below to verify your email and publish it to the world:</p>

                    <a href="{verify_link}" style="display: inline-block; background-color: #111928; color: #ffffff; padding: 0.75rem 1.5rem; border-radius: 0.25rem; text-decoration: none; font-weight: 600; margin-bottom: 2rem;">
                        Publish My Note
                    </a>

                    <br><br>
                    
                    Or, paste this link in your browser: {verify_link}

                </div>
                """

        mail.send(msg)

        flash("Click the link sent to your mail to verify your E-Mail and publish it.", "success")

        return redirect(url_for('home'))
    else:
        return render_template('create.html')

@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash('Note not found.', 'error')
        return redirect(url_for('home'))

    submitted_email = request.form.get('e-mail')
    submitted_token = request.form.get('verification')

    if request.method == 'POST':
        if not submitted_token:
            if submitted_email == post.email:
                flash('Now enter the code sent to your mail to delete!.', 'success')

                msg = Message('Delete Your SlushyNote!', recipients=[submitted_email])

                msg.body = f"Hello '{post.name}',\n\nYou requested to delete your note titled '{post.title}'.\n\nYour secure verification code is: {post.token}\n\nPaste this code on the website to permanently delete the note."
                msg.html = f"""
                                <div style="font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; color: #415462; line-height: 1.5; max-width: 600px; margin: 0 auto; padding: 20px;">

                                    <h2 style="color: #111928; margin-top: 0; margin-bottom: 1rem; font-weight: 700;">Delete Note Request</h2>
                                    <p style="margin-bottom: 2rem;">You requested to delete your SlushyNote. Here is a preview of what you are about to permanently delete:</p>

                                    <article style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 0.125rem 0.25rem rgba(16, 24, 40, 0.04);">

                                        <header style="border-bottom: 1px solid #e2e8f0; padding-bottom: 1rem; margin-bottom: 1rem;">
                                            <h3 style="margin: 0; color: #111928; font-size: 1.25rem; font-weight: 600;">{post.title}</h3>
                                            <div style="color: #64748b; font-size: 0.875rem; margin-top: 0.25rem;">
                                                By <strong>{post.name}</strong>
                                            </div>
                                        </header>

                                        <p style="margin: 0; color: #415462;">
                                            {post.content}
                                        </p>
                                    </article>
                                    <p style="margin-bottom: 1rem;">If you are sure you want to delete this, copy your secure verification code below:</p>

                                    <div style="background-color: #AF291D; color: #FAEEEB; padding: 0.75rem 1rem; border-radius: 0.25rem; text-align: center; font-size: 1.5rem; font-weight: 700; letter-spacing: 2px;">
                                        {post.token}
                                    </div>

                                    <p style="font-size: 0.75rem; color: #64748b; margin-top: 2rem;">If you didn't request this, you can safely ignore this email.</p>
                                </div>
                                """

                mail.send(msg)

                return render_template('delete.html', id=id, delete=True, email_value=submitted_email)
            else:
                flash('That email does not match the author of this note.', 'error')
                return render_template('delete.html', id=id, delete=False, email_value='')
        else:
            if submitted_email == post.email and submitted_token == post.token:
                db.session.delete(post)
                db.session.commit()
                flash('Your note has been securely deleted.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect verification code. Deletion failed.', 'error')
                return render_template('delete.html', id=id, delete=True, email_value=submitted_email)

    return render_template('delete.html', id=id, delete=False)

@app.route('/verify/<token>')
def verify(token):
    post = Post.query.filter_by(token=token).first()

    if post and not post.is_published:
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
