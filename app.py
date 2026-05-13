import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import test_bot as bot

app = Flask(__name__)
app.secret_key = os.urandom(24)
DB_NAME = 'mindmate.db'


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL,
            tokens INTEGER DEFAULT 100
        )
    ''')
    conn.commit()
    conn.close()


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return route_function(*args, **kwargs)
    return wrapper


init_db()


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/about.html')
def about():
    return render_template('about.html')


@app.route('/login.html')
def login_page():
    return render_template('login.html')


@app.route('/choose-support.html')
@login_required
def choose_support():
    return render_template('choose-support.html')


@app.route('/ai-chat.html')
@login_required
def ai_chat():
    return render_template('ai-chat.html')


@app.route('/specialists.html')
def specialists():
    return render_template('specialists.html')


@app.route('/assessment.html')
def assessment():
    return render_template('assessment.html')


@app.route('/specialist-dashboard.html')
@login_required
def specialist_dash():
    return render_template('specialist-dashboard.html')


@app.route('/dashboard.html')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/store.html')
def store():
    return render_template('store.html')


@app.route('/booking.html')
@login_required
def booking():
    return render_template('booking.html')


@app.route('/chat-room.html')
@login_required
def chat_room():
    return render_template('chat-room.html')


@app.route('/specialist-profile.html')
def specialist_profile():
    return render_template('specialist-profile.html')


@app.route('/video-call.html')
@login_required
def video_call():
    return render_template('video-call.html')


@app.route('/contact.html')
def contact():
    return render_template('contact.html')


@app.route('/faq.html')
def faq():
    return render_template('faq.html')


@app.route('/privacy.html')
def privacy():
    return render_template('privacy.html')


@app.route('/terms.html')
def terms():
    return render_template('terms.html')


@app.route('/404.html')
def not_found_page():
    return render_template('404.html'), 404


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request.'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    action = data.get('action', '').strip()
    user_type = data.get('user_type', 'user').strip()

    if not email or not password or action not in ['login', 'signup']:
        return jsonify({'success': False, 'message': 'Please fill all required fields.'}), 400

    conn = get_db_connection()
    c = conn.cursor()

    if action == 'signup':
        try:
            hashed_pw = generate_password_hash(password)
            c.execute(
                "INSERT INTO users (email, password, user_type) VALUES (?, ?, ?)",
                (email, hashed_pw, user_type)
            )
            conn.commit()

            user_id = c.lastrowid
            session['user_id'] = user_id
            session['email'] = email
            session['user_type'] = user_type

            conn.close()
            return jsonify({
                'success': True,
                'message': 'Account created successfully!',
                'redirect': url_for('specialist_dash') if user_type == 'specialist' else url_for('choose_support')
            })

        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Email already exists.'}), 400

    c.execute("SELECT id, password, user_type FROM users WHERE email = ?", (email,))
    user_record = c.fetchone()
    conn.close()

    if user_record and check_password_hash(user_record['password'], password):
        session['user_id'] = user_record['id']
        session['email'] = email
        session['user_type'] = user_record['user_type']

        return jsonify({
            'success': True,
            'message': 'Logged in successfully!',
            'redirect': url_for('specialist_dash') if user_record['user_type'] == 'specialist' else url_for('choose_support')
        })

    return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401


@app.route('/api/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/api/session', methods=['GET'])
def get_session_data():
    if 'user_id' not in session:
        return jsonify({
            'logged_in': False
        })

    return jsonify({
        'logged_in': True,
        'user_id': session.get('user_id'),
        'email': session.get('email'),
        'user_type': session.get('user_type')
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    user_input = data.get('message', '').strip()
    if not user_input:
        return jsonify({'error': 'Empty message'}), 400

    cleaned = bot.clean_text(user_input)

    detected_ctx = bot.detect_context(cleaned, user_input)
    if detected_ctx != "general":
        bot.session_state["current_context"] = detected_ctx
        context = detected_ctx
    elif bot.session_state.get("current_context") in ["abuse"]:
        context = "abuse"
    else:
        context = bot.session_state.get("current_context", "general")

    emotion, confidence, probs = bot.classify_input(cleaned, user_input)
    risk = bot.analyze_risk(emotion, confidence, context, cleaned)
    response = bot.get_response(emotion, confidence, risk, context, cleaned, user_input)

    bot.conversation_history.append({
        "user": user_input,
        "bot": response,
        "emotion": emotion,
        "risk": risk
    })

    if len(bot.conversation_history) > bot.MAX_HISTORY:
        bot.conversation_history.pop(0)

    return jsonify({
        'response': response,
        'emotion': emotion,
        'risk': risk,
        'confidence': f"{confidence:.0%}"
    })


if __name__ == '__main__':
    bot.session_state["patient_name"] = "User"
    print("MindMate AI Server running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)