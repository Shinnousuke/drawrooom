import streamlit as st
from streamlit_drawable_canvas import st_canvas
import db  # Your backend file (make sure it has `join_room()` and `create_room_auto()`)

# ---------------------- Page Config ---------------------- #
st.set_page_config(page_title="DrawRoom", layout="wide")

# ------------------ Initialize Session ------------------- #
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.session_state.user_id = 0
    st.session_state.room_code = ''
    st.session_state.in_game = False

# ---------------------- Login Page ----------------------- #
def show_login():
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        success, result = db.login_user(email, password)

        if success:
            username, user_id = result
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_id = user_id
            st.success(f"Logged in as {username}")
            st.rerun()
        else:
            st.error(result)

# --------------------- Register Page --------------------- #
def show_register():
    st.title("Register")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        success, message = db.register_user(username, email, password)

        if success:
            st.success("Registered successfully! Please log in.")
        else:
            st.error(message)

# --------------------- DrawRoom Page --------------------- #
def show_drawroom():
    if st.session_state.in_game:
        show_game_canvas()
        return

    st.title(f"Welcome, {st.session_state.username}")
    st.subheader("Create or Join a Room")

    col1, col2 = st.columns(2)

    # ----- Create Room ----- #
    with col1:
        st.markdown("### Create a New Room")
        if st.button("Create Room"):
            try:
                success, room_code = db.create_room_auto(st.session_state.user_id)
                if success:
                    st.session_state.room_code = room_code
                    st.session_state.in_game = True
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to create room: {e}")

    # ----- Join Room ----- #
    with col2:
        join_code = st.text_input("Enter Room Code to Join")

        if st.button("Join Room"):
            try:
                success, message = db.join_room(join_code, st.session_state.user_id)
                if success:
                    st.session_state.room_code = join_code
                    st.session_state.in_game = True  # 🚀 Enter canvas mode
                    st.rerun()  # 🔁 Switch immediately
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"Failed to join room: {e}")

    # ----- Logout ----- #
    if st.button("Log Out"):
        for key in ['logged_in', 'username', 'user_id', 'room_code', 'in_game']:
            st.session_state[key] = False if key == 'logged_in' else ''
        st.rerun()

# --------------------- Full-Screen Game Canvas --------------------- #
def show_game_canvas():
    st.markdown(
        f"<h2 style='text-align: center;'>🎮 Room: {st.session_state.room_code} | Player: {st.session_state.username}</h2>",
        unsafe_allow_html=True
    )

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.3)",
        stroke_width=3,
        stroke_color="#00FFAA",
        background_color="#000000",
        width=1280,
        height=700,
        drawing_mode="freedraw",
        key="full_screen_canvas"
    )

    if st.button("❌ Exit Game"):
        st.session_state.in_game = False
        st.session_state.room_code = ''
        st.rerun()

# ----------------------- Routing ------------------------- #
menu = st.sidebar.radio("Navigate", ["Login", "Register", "DrawRoom"])

if not st.session_state.logged_in:
    if menu == "Login":
        show_login()
    elif menu == "Register":
        show_register()
    else:
        st.warning("Please log in to access the DrawRoom.")
else:
    show_drawroom()
