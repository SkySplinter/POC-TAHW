import streamlit as st
import psycopg2
from psycopg2 import sql, Error


@st.cache_resource
def get_connection():
    return psycopg2.connect(
        database=st.secrets["database"]["name"],
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"]
    )


conn = get_connection()

with conn.cursor() as cursor:
    cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """)
    login_options = [row[0] for row in cursor.fetchall()]


def authenticate(role, user, password):
    try:
        with conn.cursor() as cursor:
            if role == "admin":
                cursor.execute(
                    "SELECT name FROM admin WHERE name = %s AND password = crypt(%s, password)",
                    (user, password)
                )
                fetched = cursor.fetchone()

                if fetched:
                    st.success(f"Logged in as {user}")
                    st.session_state.hw_authenticated = "TA"
                else:
                    st.error("Wrong username or password")

            else:
                if password == f"Student?{user}":
                    # Protect against SQL injection in table name using sql.Identifier
                    cursor.execute(
                        sql.SQL("SELECT university_code FROM {} WHERE university_code = %s")
                        .format(sql.Identifier(role)),
                        (user,)
                    )
                    fetched = cursor.fetchone()

                    if fetched:
                        st.success(f"Logged in as {user}")
                        st.session_state.hw_authenticated = True
                        st.session_state.hw_course = role
                        st.session_state.user_id = user
                    else:
                        st.error("Wrong username or password")
                else:
                    st.error("Wrong username or password")

    except Error as e:
        st.error("A database error occurred.")
        conn.rollback()
        print("Database error:", e)


if st.session_state.hw_authenticated is False:

    with st.container(border=True):

        st.header("Login")
        role = st.selectbox("Role", login_options)
        user_id = st.text_input("ID")
        password = st.text_input("Password", type="password")

        st.button("LOGIN", on_click=authenticate, kwargs={
            "role": role,
            "user": user_id,
            "password": password
        })
