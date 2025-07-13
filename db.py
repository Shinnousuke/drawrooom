import mysql.connector
import random
import time

# ------------------- Database Connection ------------------- #
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",  # Your MySQL password
        database="drawrooom"
    )

# ------------------- Register User ------------------- #
def register_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return False, "Email already exists"

    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
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
    cursor.execute("SELECT id, username, password_hash FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result and password == result[2]:  # plaintext for now
        user_id = result[0]
        username = result[1]
        return True, (username, user_id)  # ✅ return in correct order
    return False, "Invalid email or password"

# ------------------- Generate Unique Room Code ------------------- #
def generate_unique_room_code():
    conn = get_db_connection()
    cursor = conn.cursor()
    while True:
        code = str(random.randint(1000, 9999))
        cursor.execute("SELECT id FROM rooms WHERE room_code = %s", (code,))
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
            cursor.execute("INSERT INTO rooms (room_code, created_by) VALUES (%s, %s)", (room_code, user_id))
            conn.commit()
            return True, room_code
        except mysql.connector.errors.DatabaseError as e:
            conn.rollback()
            if "Lock wait timeout" in str(e) and attempt < retries - 1:
                print(f"Retrying ({attempt+1}/{retries}) due to lock timeout...")
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
    cursor.execute("SELECT id FROM rooms WHERE room_code = %s", (room_code,))
    room = cursor.fetchone()
    if room:
        room_id = room[0]
        cursor.execute("INSERT INTO room_members (room_id, user_id) VALUES (%s, %s)", (room_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, room_id
    return False, "Room not found"
