from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterUserForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///auth_exercise"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, first_name, last_name, email)
        db.session.commit()
        
        session['username'] = username
        flash(f"Welcome {username}, you have now been registered", 'success')
        return redirect(f"/users/{username}")
    else:
        return render_template('create_new_user.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = username
            flash(f"Welcome back {username}, good to see you again!", 'success')
            return redirect(f"/users/{username}")
        else:
            form.username.errors = ['Invalid username/password']
       
    return render_template('login.html', form=form)


@app.route('/users/<username>')
def secret_page(username):
    user = User.query.get(username)
    comments = user.feedback
    if "username" not in session:
        flash("Please login first")
        return redirect('/login')
    return render_template('user_details.html', username = user.username, email = user.email, first_name = user.first_name, last_name = user.last_name, comments=comments)

    

# @app.route('/users/<username>/feedback/add')
# def add_feedback(username):
#     user = User.query.get(username)

#     form = FeedbackForm(obj=feedback)



@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):

    """Delete user and redirect to login"""
    user = User.query.get(username)
    if user and 'username' in session:
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        return redirect('/')
    else:
        flash("You don't have permission to delete", info)
        return redirect('/')


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_content(username):
    """Show add-feedback form and process it."""
    form = FeedbackForm()

    # if session['username'] == username:
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(
            title=title,
            content=content,
            username=username
        )
        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")
        
    else:
        return render_template('add_content.html', form=form)

    



@app.route('/feedback/<int:id>/update', methods=['GET', 'POST'])
def update_feedback(id):
   
    feedback = Feedback.query.get(id)

    form = FeedbackForm(obj=feedback)
    
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(f"/users/{feedback.username}")

    return render_template('feedback_edit.html', form=form, feedback=feedback)


@app.route('/feedback/<int:id>/delete')
def delete_comment(id):
    feedback = Feedback.query.get(id)
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{feedback.username}')


@app.route('/logout')
def user_logout():
    session.pop('username')
    flash('Hope to see you again soon!', 'info')
    return redirect('/login')



