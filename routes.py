from flask import request, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from models import User, Build

# Home route
# A route is a URL pattern that is mapped to
def register_routes(app, db, bcrypt):
    @app.route('/')
    def home():
        builds = Build.query.all()
        return render_template('index.html', builds = builds), 200

    @app.route('/login')
    def login():
        return render_template('login.html'), 200

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/dev')
    @login_required
    def dev():
        builds = Build.query.filter_by(developerID=current_user.uid).all()
        return render_template('dev.html', builds=builds), 200

    @app.route('/uploadBuild', methods=['GET', 'POST'])
    @login_required
    def uploadBuild():
        if request.method == 'GET':
            return render_template('dev.html', invalid_build = "Invalid build information!"), 200
        elif request.method == 'POST':
            name = request.form.get('buildName')
            description = request.form.get('description')
            instructions = request.form.get('instructions')
            link = request.form.get('link')

            build = Build(name, description, instructions, link, current_user.uid)
            db.session.add(build)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                return redirect(url_for('uploadBuild'))

            return redirect(url_for('dev'))

    @app.route('/tester')
    @login_required
    def tester():
        return render_template('tester.html'), 200

    @app.route('/loggingIn', methods=['GET', 'POST'])
    def loggingIn():
        if request.method == 'GET':
            return render_template('login.html', wrong_password = "Invalid username or password!"), 200
        elif request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')

            user = User.query.filter(User.username == username).first()

            if not user or not bcrypt.check_password_hash(user.password_hash, password):
                return redirect(url_for('loggingIn'))

            login_user(user)
            if current_user.is_dev:
                return redirect(url_for('dev'))
            else:
                return redirect(url_for('tester'))

    @app.route('/comment/<int:id>', methods=['GET', 'POST'])
    @login_required
    def comment(id):
        return render_template('comment.html'), 200

    @app.route('/giveFeedback', methods=['GET', 'POST'])
    @login_required
    def giveFeedback():
        if request.method == 'GET':
            return render_template('comment.html'), 200
        elif request.method == 'POST':
            testTime = request.form.get('testTime')
            feedback = request.form.get('feedback')

            return redirect(url_for('home'))