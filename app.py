from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./devspace.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['USER'] = 'admin'
    app.config['PASSWORD'] = 'badadminpassword'
    app.secret_key = 'webby'

    db.init_app(app)

    # LoginManager is used for user session management for users in flask applications.
    # we still need to create user logic for routes, password hashing, etc.
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.session_protection = "strong"

    # prevent circular imports by importing here
    from models import User, Build
    # When a user is logged in, this callback is used to reload the user object from the user ID stored in the session.
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect(url_for('login'))

    # Bcrypt is used for hashing passwords before storing them in the database.
    # Password hashing is the process of converting a plaintext password into a fixed-length string of characters, known as a hash, using a one-way cryptographic algorithm
    # password hashing is crucial for security, as it ensures that even if the database is compromised, the actual passwords are not exposed.
    bcrypt = Bcrypt(app)

    # prevent circular imports by importing here
    from routes import register_routes
    register_routes(app, db, bcrypt)

    migrate = Migrate(app, db)

    with app.app_context():
        db.create_all()
        # Manually creates an admin user.  Does not run if one already exists.
        if not db.session.execute(
                db.select(User)
        ).first():
            admin = User(
                fname = "Admin",
                lname = "Istrator",
                username=app.config["USER"],
                password_hash=bcrypt.generate_password_hash(app.config["PASSWORD"]).decode('utf-8'),
                is_dev=True,
            )
            db.session.add(admin)

            developer = User(
                fname="Alessandro",
                lname="Fiorella",
                username="alessandrofiorella@mail.adelphi.edu",
                password_hash=bcrypt.generate_password_hash("kitten654").decode('utf-8'),
                is_dev=True,
            )
            db.session.add(developer)

            tester = User(
                fname="Tim",
                lname="Kravets",
                username="timothykravets@mail.adelphi.edu",
                password_hash=bcrypt.generate_password_hash("doggie321").decode('utf-8'),
                is_dev=False,
            )
            db.session.add(tester)
            db.session.commit()
            db.close_all_sessions()

    return app

