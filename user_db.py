import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import tweepy

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_subscribed INTEGER DEFAULT 0,
        linkedin_token TEXT,
        twitter_token TEXT,
        facebook_token TEXT,
        instagram_token TEXT
    )''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                  (username, generate_password_hash(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row and check_password_hash(row[0], password):
        return True
    return False

def subscribe_user(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET is_subscribed = 1 WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def save_social_token(username, platform, token):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(f'UPDATE users SET {platform}_token = ? WHERE username = ?', (token, username))
    conn.commit()
    conn.close()

def get_social_token(username, platform):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(f'SELECT {platform}_token FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def get_twitter_api(user_token, user_token_secret):
    consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
    consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, user_token, user_token_secret)
    return tweepy.API(auth)

def post_to_twitter(user_token, user_token_secret, content):
    api = get_twitter_api(user_token, user_token_secret)
    api.update_status(content)

# Helper to split stored twitter token into access_token and access_token_secret
def get_twitter_tokens(username):
    token = get_social_token(username, 'twitter')
    if token and ':' in token:
        access_token, access_token_secret = token.split(':', 1)
        return access_token, access_token_secret
    return None, None
