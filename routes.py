import os

from flask import request, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from models import User, Build, Feedback, Response

import datetime

# Home route
# A route is a URL pattern that is mapped to
def register_routes(app, db, bcrypt):
    @app.route('/')
    def home():
        builds = Build.query.all()
        return render_template('index.html', builds = builds), 200

    @app.route('/personal')
    def personal():
        builds = Build.query.filter_by(tag="Personal").all()
        return render_template('index.html', builds=builds), 200

    @app.route('/professional')
    def professional():
        builds = Build.query.filter_by(tag="Professional").all()
        return render_template('index.html', builds=builds), 200

    @app.route('/educational')
    def educational():
        builds = Build.query.filter_by(tag="Educational").all()
        return render_template('index.html', builds=builds), 200

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
        if current_user.is_dev:
            builds = Build.query.filter_by(developerID=current_user.uid).all()
            allFeedback = []
            rejected = False
            accepted = False
            for build in builds:
                feedback = Feedback.query.filter_by(buildId=build.id).all()
                allFeedback += feedback
                for elem in feedback:
                    if elem.rejected:
                        rejected = True
                    if elem.accepted:
                        accepted = True
            return render_template('dev.html', builds=builds, feedback = allFeedback, rejected = rejected, accepted = accepted), 200
        return redirect(url_for('tester'))

    @app.route('/uploadBuild', methods=['GET', 'POST'])
    @login_required
    def uploadBuild():
        if request.method == 'GET':
            return render_template('dev.html', invalid_build = "Invalid Build Information!"), 200
        elif request.method == 'POST':
            name = request.form.get('buildName')
            description = request.form.get('description')
            instructions = request.form.get('instructions')
            link = request.form.get('link')
            tag = request.form.get('tag').title()

            if tag == "Personal" or tag == "Professional" or tag == "Educational":
                build = Build(name, description, instructions, link, tag, current_user.uid)
                db.session.add(build)
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    return redirect(url_for('uploadBuild'))
            else:
                print("Invalid tag!")
                return redirect(url_for('dev'))

            return redirect(url_for('dev'))

    @app.route('/tester')
    @login_required
    def tester():
        builds = Build.query.all()
        allFeedback = []
        allBuilds = []
        for build in builds:
            feedback = Feedback.query.filter_by(testerId=current_user.uid, buildId=build.id).all()
            if feedback:
                allBuilds.append(build)
                allFeedback += feedback
        return render_template('tester.html', builds = allBuilds, feedback = allFeedback), 200

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
        build = Build.query.filter_by(id = id).first()
        return render_template('comment.html', build=build), 200

    @app.route('/giveFeedback/<int:id>', methods=['GET', 'POST'])
    @login_required
    def giveFeedback(id):
        if request.method == 'GET':
            build = Build.query.filter_by(id=id).first()
            return render_template('comment.html', build=build), 200
        elif request.method == 'POST':
            testTime = datetime.date.fromisoformat(request.form.get('testTime'))
            comment = request.form.get('comment')
            feedback = Feedback(testTime, comment, id, current_user.uid)
            db.session.add(feedback)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                return redirect(url_for('giveFeedback', id=id))

            return redirect(url_for('home'))

    @app.route('/acceptFeedback/<int:id>', methods=['GET', 'POST'])
    @login_required
    def acceptFeedback(id):
        if request.method == 'GET':
            return redirect(url_for('dev'))
        elif request.method == 'POST':
            feedback = Feedback.query.filter_by(id=id).first()
            feedback.accepted = True
            feedback.rejected = False
            db.session.commit()
            return redirect(url_for('dev'))

    @app.route('/rejectFeedback/<int:id>', methods=['GET', 'POST'])
    @login_required
    def rejectFeedback(id):
        if request.method == 'GET':
            return redirect(url_for('dev'))
        elif request.method == 'POST':
            feedback = Feedback.query.filter_by(id=id).first()
            feedback.rejected = True
            feedback.accepted = False
            db.session.commit()
            return redirect(url_for('dev'))

    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        if current_user.is_dev:
            return redirect(url_for('dev'))
        else:
            return redirect(url_for('tester'))

    @app.route('/signup', methods=['GET'])
    def signup():
        return render_template('signup.html')

    @app.route('/deleteBuild/<int:id>', methods=['GET', 'POST'])
    @login_required
    def deleteBuild(id):
        if request.method == 'GET':
            return redirect(url_for('dev'))
        elif request.method == 'POST':
            build = Build.query.filter_by(id=id).first()
            feedbacks = Feedback.query.filter_by(buildId=id).all()
            for feedback in feedbacks:
                db.session.delete(feedback)
            db.session.delete(build)
            try:
                db.session.commit()
                print("Successfully Deleted Build " + str(id))
            except Exception:
                db.session.rollback()
                return redirect(url_for('deleteBuild', id=id))
            return redirect(url_for('dev'))

    @app.route('/createAccount', methods=['GET', 'POST'])
    def createAccount():
        if request.method == 'GET':
            return render_template('signup.html', wrong_password = "Invalid Account Creation. Username may already exist"), 200
        elif request.method == 'POST':
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            username = request.form.get('username')
            password = request.form.get('password')

            user = User(fname, lname, username, bcrypt.generate_password_hash(password).decode('utf-8'), False)
            db.session.add(user)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Account creation error:", e)
                return redirect(url_for('createAccount'))

            return redirect(url_for('login'))

    @app.route('/respond/<int:id>', methods=['GET', 'POST'])
    @login_required
    def respond(id):
        feedback = Feedback.query.filter_by(id=id).first()
        return render_template('respond.html', feedback=feedback), 200

    @app.route('/giveResponse/<int:id>', methods=['GET', 'POST'])
    @login_required
    def giveResponse(id):
        if request.method == 'GET':
            return redirect(url_for('dev'))
        elif request.method == 'POST':
            responseTime = datetime.date.fromisoformat(request.form.get('responseTime'))
            comment = request.form.get('comment')

            response = Response(responseTime, comment, id, current_user.uid)
            db.session.add(response)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                return redirect(url_for('respond', id=id))

            return redirect(url_for('dev'))

    @app.route('/verify', methods=['GET', 'POST'])
    @login_required
    def verify():
        email = current_user.username
        print(email)
        if (email[-3:] == "edu"):
            current_user.verified = True
            current_user.is_dev = True
            db.session.commit()
            db.session.refresh(current_user)
        else:
            print("Not Verified")

        return redirect(url_for('dev'))

    @app.route('/crash', methods=['GET', 'POST'])
    def crash():
        raise SystemError("BOOOOOO!!!!")

    @app.route('/editBuild/<int:id>', methods=['GET', 'POST'])
    @login_required
    def editBuild(id):
        if request.method == 'GET':
            return redirect(url_for('dev'))
        elif request.method == 'POST':
            build = Build.query.filter_by(id=id).first()
            name = request.form.get('buildName')
            desc = request.form.get('description')
            instructions = request.form.get('instructions')
            link = request.form.get('link')
            tag = request.form.get('tag').title()

            build.name = name
            build.description = desc
            build.instructions = instructions
            build.link = link
            if tag == "Personal" or tag == "Professional" or tag == "Educational":
                build.tag = tag
            else:
                print("Invalid tag!")
                return redirect(url_for('dev'))

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                return redirect(url_for('editBuild', id=id))

            return redirect(url_for('dev'))