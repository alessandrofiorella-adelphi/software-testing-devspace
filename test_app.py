import pytest, datetime
from flask import template_rendered
# 1. Import your factory function from app.py
from app import create_app, db
from models import User, Build, Feedback, Response
import ctypes


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    # Set up application context for extensions like SQLAlchemy
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def captured_templates(app):
    """A fixture that listens to Flask signals and captures rendered templates."""
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


# --- Actual Tests ---

def test_homepage_template(client, captured_templates):
    # 1. Make the request to your target route (adjust "/" to your route path)
    response = client.get("/")

    # 2. Check that the request succeeded
    assert response.status_code == 200

    # 3. Assert exactly one template was rendered
    assert len(captured_templates) == 1

    # 4. Verify the template name
    template, context = captured_templates[0]
    assert template.name == "index.html"

def test_login_page(client, captured_templates):
    response = client.get("/login")

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "login.html"

def test_developer_access(client, captured_templates):
    response = client.post('/loggingIn', data={
        'username': 'alessandrofiorella@mail.adelphi.edu',
        'password': 'kitten654'
    }, follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "dev.html"

def test_tester_access(client, captured_templates):
    response = client.post('/loggingIn', data={
        'username': 'timothykravets@mail.adelphi.edu',
        'password': 'doggie321'
    }, follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "tester.html"

def test_login_fail(client, captured_templates):
    response = client.post('/loggingIn', data={
        'username': 'jondoe@hotmail.net',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200

    template, context = captured_templates[0]
    assert len(captured_templates) == 1
    assert template.name == "login.html"
    assert context.get('wrong_password') == "Invalid username or password!"

def test_logout_success(client, captured_templates):
    client.post('/loggingIn', data={
        'username': 'timothykravets@mail.adelphi.edu',
        'password': 'doggie321'
    })

    response = client.get("/logout", follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "index.html"

def test_good_build_creation(client, captured_templates):
    client.post('/loggingIn', data={
        'username': 'alessandrofiorella@mail.adelphi.edu',
        'password': 'kitten654'
    }, follow_redirects=True)

    response = client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Personal'
    }, follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 2

    template, context = captured_templates[1]
    assert template.name == "dev.html"

    build = db.session.execute(
        db.select(Build).filter_by(name='MySpace')
    ).scalar_one_or_none()

    assert build is not None
    assert build.description == 'Lorem ipsum dolor sit amet'
    assert build.instructions == 'Lorem ipsum dolor sit amet'
    assert build.link == 'https://en.wikipedia.org/wiki/Myspace'
    assert build.tag == 'Personal'

def test_bad_build_creation(client, captured_templates):
    client.post('/loggingIn', data={
        'username': 'alessandrofiorella@mail.adelphi.edu',
        'password': 'kitten654'
    }, follow_redirects=True)

    response = client.post('/uploadBuild', data={
        'buildName': "MySpace",
        'description': None,
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag' : 'Personal'
    }, follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 2

    template, context = captured_templates[-1]
    assert template.name == "dev.html"
    assert context["invalid_build"] == "Invalid build information!"

    build = db.session.execute(
        db.select(Build).filter_by(name='MySpace')
    ).scalar_one_or_none()

    assert build is None

def test_build_link_warning (client, captured_templates):
    client.post('/loggingIn', data={
        'username': 'timothykravets@mail.adelphi.edu',
        'password': 'doggie321'
    })

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Personal'
    })

    response = client.get('/')

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "index.html"

    assert b'onclick=' in response.data
    assert b'confirm(' in response.data
    assert b'https://en.wikipedia.org/wiki/Myspace' in response.data
    assert b'You are being redirected to an external website to access this build. Please exercise caution when downloading any programs/executables' in response.data

def test_comment_feedback (client, captured_templates):
    client.post('/loggingIn', data={
        'username': 'timothykravets@mail.adelphi.edu',
        'password': 'doggie321'
    })

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Personal'
    })

    response = client.post('/giveFeedback/1', data={
        'testTime': '2026-09-30',
        'comment': 'Lorem ipsum dolor sit amet',
    }, follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "index.html"

    feedback = db.session.execute(
        db.select(Feedback).filter_by(comment='Lorem ipsum dolor sit amet')
    ).scalar_one_or_none()

    assert feedback is not None
    assert feedback.date == datetime.date(2026, 9, 30)
    assert feedback.comment == 'Lorem ipsum dolor sit amet'
    assert feedback.buildId == 1
    assert feedback.testerId == 3

def test_accept_comment (client, captured_templates):
    client.post('/loggingIn', data={
        'username': 'timothykravets@mail.adelphi.edu',
        'password': 'doggie321'
    })

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Personal'
    })

    client.post('/giveFeedback/1', data={
        'testTime': '2026-09-30',
        'comment': 'Lorem ipsum dolor sit amet',
    })

    response = client.get('/dev')

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "dev.html"

    feedback = db.session.execute(
        db.select(Feedback).filter_by(comment='Lorem ipsum dolor sit amet')
    ).scalar_one_or_none()

    assert feedback is not None
    assert feedback.date == datetime.date(2026, 9, 30)
    assert feedback.comment == 'Lorem ipsum dolor sit amet'
    assert feedback.accepted == False
    assert feedback.buildId == 1
    assert feedback.testerId == 3

    client.post('/acceptFeedback/1', data={})

    assert feedback.accepted == True

def test_signup_page (client, captured_templates):
    response = client.get("/signup")

    # 2. Check that the request succeeded
    assert response.status_code == 200

    # 3. Assert exactly one template was rendered
    assert len(captured_templates) == 1

    # 4. Verify the template name
    template, context = captured_templates[0]
    assert template.name == "signup.html"

def test_account_creation (client, captured_templates):
    client.post('/createAccount', data={
        'fname': 'David',
        'lname': 'Chays',
        'username' : 'davidchays@mail.adelphi.edu',
        'password' : 'husky987'
    })

    response = client.post('/loggingIn', data={
        'username': 'davidchays@mail.adelphi.edu',
        'password': 'husky987'
    }, follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "tester.html"

def test_respond_to_feedback (client, captured_templates):
    client.post('/loggingIn', data={
        'username': 'timothykravets@mail.adelphi.edu',
        'password': 'doggie321'
    })

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Personal'
    })

    client.post('/giveFeedback/1', data={
        'testTime': '2026-09-30',
        'comment': 'Lorem ipsum dolor sit amet',
    })

    response = client.post('respond/1', data = {
        'responseTime': '2026-10-01',
        'comment': 'Lorem ipsum dolor sit amet',
    }, follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "tester.html" or template.name == "dev.html"

    response = db.session.execute(
        db.select(Response).filter_by(comment='Lorem ipsum dolor sit amet')
    ).scalar_one_or_none()

    assert response is not None
    assert response.date == datetime.date(2026, 10, 1)
    assert response.comment == 'Lorem ipsum dolor sit amet'
    assert response.feedbackId == 1
    assert response.userId == 3

def test_verify_account(client, captured_templates):
    client.post('/loggingIn', data={
        'username': 'timothykravets@mail.adelphi.edu',
        'password': 'doggie321'
    })

    user = db.session.execute(
        db.select(User).filter_by(username='timothykravets@mail.adelphi.edu')
    ).scalar_one_or_none()

    assert user.verified == False

    response = client.get('/verify', follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]

    assert template.name == "dev.html" or template.name == "tester.html"

    assert user.verified == True

def test_creation_and_bad_verification(client, captured_templates):
    client.post('/createAccount', data={
        'fname': 'Timothy',
        'lname': 'Kravets',
        'username': 'timkravets@gmail.com',
        'password': 'luna18'
    })

    response = client.post('/loggingIn', data={
        'username': 'timkravets@gmail.com',
        'password': 'luna18'
    }, follow_redirects=True)

    user = db.session.execute(
        db.select(User).filter_by(username='timkravets@gmail.com')
    ).scalar_one_or_none()

    assert user.verified == False

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "tester.html"

    response = client.get('/verify', follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 2

    template, context = captured_templates[1]

    assert template.name == "dev.html" or template.name == "tester.html"

    assert user.verified == False

def test_crash(client, captured_templates):
    client.application.config['TESTING'] = False
    response = client.get('/crash')

    assert response.status_code == 500

    assert len(captured_templates) == 0

def test_good_tag(client, captured_templates):
    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Personal'
    })

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Professional'
    })

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Educational'
    })

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Personal'
    })

    builds = db.session.execute(db.select(Build)).scalars().all()
    for build in builds:
        assert build.tag == "Educational" or build.tag == "Personal" or build.tag == "Professional"

def test_good_tag(client, captured_templates):
    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Personal'
    })

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Professional'
    })

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'Educational'
    })

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://en.wikipedia.org/wiki/Myspace',
        'tag': 'All of them'
    })

    builds = db.session.execute(db.select(Build)).scalars().all()
    for build in builds:
        assert build.tag == "Educational" or build.tag == "Personal" or build.tag == "Professional"

def test_edit_build_success(client, captured_templates):
    client.post('/loggingIn', data={
        'username': 'alessandrofiorella@mail.adelphi.edu',
        'password': 'kitten654'
    }, follow_redirects=True)

    client.post('/uploadBuild', data={
        'buildName': 'MySpace',
        'description': 'Lorem ipsum dolor sit amet',
        'instructions': 'Lorem ipsum dolor sit amet',
        'link': 'https://wikipedia.org',
        'tag': 'Personal'
    }, follow_redirects=True)

    captured_templates.clear()

    response = client.post('/editBuild/1', data={
        'buildName': 'MySpace Evolved',
        'description': 'Updated project description details text',
        'instructions': 'Updated build testing execution steps guide',
        'link': 'https://wikipedia.org_modified',
        'tag': 'Professional'
    }, follow_redirects=True)

    assert response.status_code == 200

    assert len(captured_templates) == 1

    template, context = captured_templates[0]
    assert template.name == "dev.html"

    updated_build = db.session.execute(
        db.select(Build).filter_by(id=1)
    ).scalar_one_or_none()

    assert updated_build is not None
    assert updated_build.name == 'MySpace Evolved'
    assert updated_build.description == 'Updated project description details text'
    assert updated_build.instructions == 'Updated build testing execution steps guide'
    assert updated_build.link == 'https://wikipedia.org_modified'
    assert updated_build.tag == 'Professional'
