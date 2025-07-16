from pathlib import Path
import psycopg2
import pandas as pd
import streamlit as st
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


max_file_size = 10 * 1024 * 1024
hw_directory = Path(Path.cwd() / "hw_pages" / "homeworks")

if st.session_state.hw_authenticated and "hw_course" in st.session_state and "user_id" in st.session_state:

    conn = get_connection()
    st.title("Welcome")

    try:
        with conn.cursor() as cursor:
            # Secure user data fetch
            cursor.execute(
                sql.SQL("SELECT * FROM {} WHERE university_code = %s")
                .format(sql.Identifier(st.session_state.hw_course)),
                (st.session_state.user_id,)
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            # Secure current homework index
            cursor.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position DESC
                LIMIT 1
                """,
                (st.session_state.hw_course,)
            )
            hw_index = cursor.fetchone()[0]

        emoji_map = {
            ":x:": "❌",
            ":mag:": "🔍",
            ":arrows_clockwise:": "🔄",
            ":white_check_mark:": "✅"
        }

        df = pd.DataFrame(rows, columns=columns)
        for key, emoji in emoji_map.items():
            df.replace(key, emoji, inplace=True)
        st.table(df)

        if str(hw_index).isdigit():
            hw_name = f"{st.session_state.hw_course}_{st.session_state.user_id}_{hw_index}"

            with st.form("upload_form"):
                file = st.file_uploader("Select homework file", type=["pdf", "py", "png", "jpg"])

                if st.form_submit_button("Submit Homework"):
                    if file and hw_name:
                        file_size = file.getbuffer().nbytes
                        if file_size > max_file_size:
                            st.warning("File is too large. Please upload a file smaller than 10 MB.")
                        else:
                            file_ext = file.name.split('.')[-1]
                            file_path = hw_directory / f"{hw_name}.{file_ext}"
                            for old_file_path in hw_directory.glob(f"{hw_name}.*"):
                                old_file_path.unlink()
                            with open(file_path, "wb") as f:
                                f.write(file.getbuffer())

                            with conn.cursor() as cursor:
                                cursor.execute(
                                    sql.SQL("UPDATE {} SET {} = %s WHERE university_code = %s")
                                    .format(
                                        sql.Identifier(st.session_state.hw_course),
                                        sql.Identifier(hw_index)
                                    ),
                                    (":mag:", st.session_state.user_id)
                                )
                                conn.commit()

                            st.success("Homework submitted!")
                            st.rerun()
                    else:
                        st.warning("Please select a valid file")
        else:
            st.write("No homeworks yet!")

    except Error as e:
        conn.rollback()
        st.error("A database error occurred.")
        print("Database error:", e)
