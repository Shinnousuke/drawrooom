import sqlite3
import random
import time
import os

# ------------------- Database Setup ------------------- #
DB_NAME = "drawroomm.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code TEXT NOT NULL UNIQUE,
            created_by INTEGER NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS room_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# Call it once when app starts
initialize_db()

# ------------------- Register User ------------------- #
def register_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        return False, "Email already exists"

    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True, "User registered"

# ------------------- Login User ------------------- #
def login_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result and password == result["password_hash"]:
        return True, (result["username"], result["id"])
    return False, "Invalid email or password"

# ------------------- Generate Unique Room Code ------------------- #
def generate_unique_room_code():
    conn = get_db_connection()
    cursor = conn.cursor()
    while True:
        code = str(random.randint(1000, 9999))
        cursor.execute("SELECT id FROM rooms WHERE room_code = ?", (code,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return code

# ------------------- Create Room with Retry ------------------- #
def create_room_auto(user_id, retries=3, delay=2):
    for attempt in range(retries):
        try:
            room_code = generate_unique_room_code()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO rooms (room_code, created_by) VALUES (?, ?)", (room_code, user_id))
            conn.commit()
            return True, room_code
        except Exception as e:
            conn.rollback()
            if "database is locked" in str(e).lower() and attempt < retries - 1:
                print(f"Retrying ({attempt+1}/{retries}) due to lock...")
                time.sleep(delay)
            else:
                raise
        finally:
            cursor.close()
            conn.close()
    raise Exception("Failed to create room after multiple retries.")

# ------------------- Join Room ------------------- #
def join_room(room_code, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM rooms WHERE room_code = ?", (room_code,))
    room = cursor.fetchone()
    if room:
        room_id = room["id"]
        cursor.execute("INSERT INTO room_members (room_id, user_id) VALUES (?, ?)", (room_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, room_id
    return False, "Room not found"
