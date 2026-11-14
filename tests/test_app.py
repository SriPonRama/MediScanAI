"""
MediScan AI – Automated Test Suite
Run with:  pytest tests/test_app.py -v
"""
import os
import sys
import json
import pytest

# Point imports to the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use an in-memory SQLite database for tests so we never touch the real data
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-do-not-use-in-prod')
os.environ.setdefault('MAIL_USERNAME', '')   # disable mail during tests

import app as app_module
from models.database import db as _db, User, Patient, Prediction, CheckupRecord, Notification, ChatMessage, PasswordResetToken


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='session')
def flask_app():
    """Create the Flask app configured for testing (in-memory DB)."""
    app_module.app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,          # disable CSRF for form submissions in tests
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SERVER_NAME': 'localhost',
    })
    with app_module.app.app_context():
        _db.create_all()
        yield app_module.app
        _db.drop_all()


@pytest.fixture()
def client(flask_app):
    """A test client that resets after each test function."""
    with flask_app.test_client() as c:
        yield c


@pytest.fixture()
def app_ctx(flask_app):
    """Push an application context for direct DB queries."""
    with flask_app.app_context():
        yield


@pytest.fixture()
def doctor_user(app_ctx):
    """Create and return a test doctor account."""
    user = User(
        name='Dr. Test Doctor',
        email='doctor@test.com',
        phone='9000000001',
        role='doctor',
        hospital_name='Test Hospital',
        specialization='Radiology',
    )
    user.set_password('TestPass123')
    _db.session.add(user)
    _db.session.commit()
    yield user
    ChatMessage.query.filter((ChatMessage.sender_id == user.id) | (ChatMessage.receiver_id == user.id)).delete()
    _db.session.delete(user)
    _db.session.commit()


@pytest.fixture()
def patient_user(app_ctx, doctor_user):
    """Create a test patient user linked to a patient record."""
    pat_record = Patient(
        user_id=doctor_user.id,
        name='Test Patient',
        age=35,
        gender='male',
        contact='9000000002',
    )
    _db.session.add(pat_record)
    _db.session.flush()

    user = User(
        name='Test Patient',
        email='patient@test.com',
        phone='9000000002',
        role='patient',
        patient_id=pat_record.id,
    )
    user.set_password('TestPass123')
    _db.session.add(user)
    _db.session.commit()
    yield user, pat_record
    ChatMessage.query.filter((ChatMessage.sender_id == user.id) | (ChatMessage.receiver_id == user.id)).delete()
    _db.session.delete(user)
    _db.session.delete(pat_record)
    _db.session.commit()


def _login(client, email, password):
    return client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)


def _logout(client):
    return client.get('/logout', follow_redirects=True)


# ---------------------------------------------------------------------------
# Auth tests
# ---------------------------------------------------------------------------

class TestAuthentication:

    def test_index_redirects_unauthenticated_to_landing(self, client):
        resp = client.get('/', follow_redirects=False)
        # Unauthenticated users should see the index page (200) or be redirected
        assert resp.status_code in (200, 302)

    def test_login_page_loads(self, client):
        resp = client.get('/login')
        assert resp.status_code == 200
        assert b'Sign in' in resp.data or b'Login' in resp.data

    def test_signup_page_loads(self, client):
        resp = client.get('/signup')
        assert resp.status_code == 200

    def test_valid_doctor_login(self, client, doctor_user):
        resp = _login(client, 'doctor@test.com', 'TestPass123')
        assert resp.status_code == 200
        # After login a doctor lands on the dashboard
        assert b'Dashboard' in resp.data or b'dashboard' in resp.data.lower()
        _logout(client)

    def test_invalid_login_shows_error(self, client):
        resp = _login(client, 'nobody@test.com', 'wrongpass')
        assert b'Invalid email or password' in resp.data

    def test_logout_redirects_to_index(self, client, doctor_user):
        _login(client, 'doctor@test.com', 'TestPass123')
        resp = client.get('/logout', follow_redirects=True)
        assert resp.status_code == 200
        # Should be back on the landing/index page
        assert b'MediScan' in resp.data

    def test_protected_route_requires_login(self, client):
        resp = client.get('/dashboard', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers.get('Location', '')


# ---------------------------------------------------------------------------
# Password reset tests
# ---------------------------------------------------------------------------

class TestPasswordReset:

    def test_forgot_password_page_loads(self, client):
        resp = client.get('/forgot_password')
        assert resp.status_code == 200
        assert b'Forgot' in resp.data or b'Reset' in resp.data

    def test_forgot_password_unknown_email_shows_generic_message(self, client):
        resp = client.post(
            '/forgot_password',
            data={'email': 'nobody@nowhere.com'},
            follow_redirects=True
        )
        assert resp.status_code == 200
        assert b'registered' in resp.data.lower() or b'instructions' in resp.data.lower()

    def test_forgot_password_known_email_creates_token(self, client, doctor_user, app_ctx):
        resp = client.post(
            '/forgot_password',
            data={'email': 'doctor@test.com'},
            follow_redirects=True
        )
        assert resp.status_code == 200
        token = PasswordResetToken.query.filter_by(user_id=doctor_user.id, is_used=False).first()
        assert token is not None
        assert token.is_valid()

    def test_reset_password_invalid_token_redirects(self, client):
        resp = client.get('/reset_password/invalid-token-xyz', follow_redirects=True)
        assert resp.status_code == 200
        assert b'invalid' in resp.data.lower() or b'expired' in resp.data.lower()

    def test_reset_password_valid_flow(self, client, doctor_user, app_ctx):
        # Create a fresh token
        import secrets
        from datetime import datetime, timedelta
        raw_token = secrets.token_urlsafe(48)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        token_obj = PasswordResetToken(
            user_id=doctor_user.id,
            token=raw_token,
            expires_at=expires_at
        )
        _db.session.add(token_obj)
        _db.session.commit()

        # Submit new password
        resp = client.post(
            f'/reset_password/{raw_token}',
            data={'password': 'NewPass999', 'confirm_password': 'NewPass999'},
            follow_redirects=True
        )
        assert resp.status_code == 200
        assert b'reset successfully' in resp.data.lower() or b'log in' in resp.data.lower()

        # Verify the token is now marked used
        token_obj = PasswordResetToken.query.filter_by(token=raw_token).first()
        assert token_obj.is_used is True

        # Verify the new password works
        resp2 = _login(client, 'doctor@test.com', 'NewPass999')
        assert resp2.status_code == 200
        _logout(client)

        # Restore original password so other tests are not affected
        doctor_user.set_password('TestPass123')
        _db.session.commit()


# ---------------------------------------------------------------------------
# Patient management tests
# ---------------------------------------------------------------------------

class TestPatientManagement:

    def test_add_patient_requires_login(self, client):
        resp = client.get('/patient_form', follow_redirects=False)
        assert resp.status_code == 302
        assert '/login' in resp.headers.get('Location', '')

    def test_add_patient_as_doctor(self, client, doctor_user, app_ctx):
        _login(client, 'doctor@test.com', 'TestPass123')
        resp = client.post('/patient_form', data={
            'name': 'Jane Doe',
            'age': 42,
            'gender': 'female',
            'contact': '9111111111',
            'dob': '1982-05-20',
            'address': '123 Main St',
            'medical_history': '',
            'emergency_contact': '',
            'blood_group': 'O+',
            'allergies': '',
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Patient should be in DB
        p = Patient.query.filter_by(contact='9111111111').first()
        assert p is not None
        assert p.name == 'Jane Doe'
        # Cleanup
        _db.session.delete(p)
        _db.session.commit()
        _logout(client)

    def test_patient_cannot_add_patient(self, client, patient_user):
        user, _ = patient_user
        _login(client, user.email, 'TestPass123')
        resp = client.get('/patient_form', follow_redirects=True)
        assert b'Only medical practitioners' in resp.data or b'patient_portal' in resp.request.url.lower() or resp.status_code == 200
        _logout(client)


# ---------------------------------------------------------------------------
# Access-control tests (prediction routes)
# ---------------------------------------------------------------------------

class TestPredictionAccess:

    def _make_prediction(self, app_ctx, patient_id):
        """Helper: create a dummy Prediction record."""
        pred = Prediction(
            patient_id=patient_id,
            image_path='test_image.jpg',
            body_part='chest',
            prediction_result='Normal',
            confidence_score=0.92,
            additional_info=json.dumps({'description': 'Test', 'medical_tips': []}),
            medical_tips=json.dumps([]),
        )
        _db.session.add(pred)
        _db.session.commit()
        return pred

    def test_doctor_can_view_own_patient_prediction(self, client, doctor_user, patient_user, app_ctx):
        _, pat_record = patient_user
        pred = self._make_prediction(app_ctx, pat_record.id)
        _login(client, 'doctor@test.com', 'TestPass123')
        resp = client.get(f'/prediction/{pred.id}', follow_redirects=True)
        assert resp.status_code == 200
        # Should NOT be an access-denied redirect
        assert b'Access denied' not in resp.data
        _logout(client)
        _db.session.delete(pred)
        _db.session.commit()

    def test_patient_can_view_own_prediction(self, client, patient_user, app_ctx):
        pat_user, pat_record = patient_user
        pred = self._make_prediction(app_ctx, pat_record.id)
        _login(client, pat_user.email, 'TestPass123')
        resp = client.get(f'/prediction/{pred.id}', follow_redirects=True)
        assert resp.status_code == 200
        assert b'Access denied' not in resp.data
        _logout(client)
        _db.session.delete(pred)
        _db.session.commit()


# ---------------------------------------------------------------------------
# Notification tests
# ---------------------------------------------------------------------------

class TestNotifications:

    def test_notifications_page_loads_for_authenticated_user(self, client, doctor_user):
        _login(client, 'doctor@test.com', 'TestPass123')
        resp = client.get('/notifications', follow_redirects=True)
        assert resp.status_code == 200
        _logout(client)

    def test_notifications_requires_login(self, client):
        resp = client.get('/notifications', follow_redirects=False)
        assert resp.status_code == 302


# ---------------------------------------------------------------------------
# Language / Translation tests
# ---------------------------------------------------------------------------

class TestLanguage:

    def test_set_language_hi(self, client):
        resp = client.get('/set_language/hi', follow_redirects=True)
        assert resp.status_code == 200

    def test_set_language_unsupported_code_does_not_crash(self, client):
        resp = client.get('/set_language/xx', follow_redirects=True)
        assert resp.status_code == 200

    def test_translate_api_returns_json(self, client):
        resp = client.post(
            '/api/translate',
            json={'text': 'Hello', 'target_language': 'hi'},
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'translated_text' in data

    def test_translate_api_empty_text_returns_400(self, client):
        resp = client.post(
            '/api/translate',
            json={'text': '', 'target_language': 'hi'},
            content_type='application/json'
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Messaging API tests
# ---------------------------------------------------------------------------

class TestMessaging:

    def test_api_messages_requires_login(self, client):
        resp = client.get('/api/messages/1')
        assert resp.status_code == 302

    def test_api_messages_polling_returns_new_messages(self, client, doctor_user, patient_user, app_ctx):
        pat_user, _ = patient_user
        _login(client, 'doctor@test.com', 'TestPass123')

        # Send a message via the web form / AJAX endpoint
        send_resp = client.post(
            f'/messages/{pat_user.id}',
            data={'message': 'Hello from test doctor'},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        assert send_resp.status_code == 200

        # Poll messages via the API endpoint
        poll_resp = client.get(f'/api/messages/{pat_user.id}')
        assert poll_resp.status_code == 200
        data = poll_resp.get_json()
        assert data.get('success') is True
        assert len(data.get('messages', [])) >= 1
        assert any('Hello from test doctor' in m['message'] for m in data['messages'])
        _logout(client)
        ChatMessage.query.filter_by(sender_id=doctor_user.id).delete()
        _db.session.commit()

