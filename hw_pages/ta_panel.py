from pathlib import Path
import psycopg2
import pandas as pd
import streamlit as st
from PIL import Image
from psycopg2 import sql
from streamlit_pdf_viewer import pdf_viewer


# Use st.cache_resource to ensure single DB connection
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        database=st.secrets["database"]["name"],
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"]
    )


if st.session_state.hw_authenticated == "TA":

    overview_tab, review_tab, operation_tab = st.tabs(["Overview", "Review", "operation"])

    hw_directory = Path(Path.cwd() / "hw_pages" / "homeworks")
    archived_dir = Path(Path.cwd() / "hw_pages" / "old")

    conn = get_connection()

    with overview_tab:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            courses = [row[0] for row in cursor.fetchall()]

        for course in courses:
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("SELECT * FROM {};").format(sql.Identifier(course)))
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

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

    with review_tab:
        def hw_next():
            st.session_state.current = st.session_state.current + 1

        def hw_prev():
            st.session_state.current = max(st.session_state.current - 1, 0)

        def hw_accept(this_university_code):
            with conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("UPDATE {} SET {} = %s WHERE university_code = %s")
                    .format(
                        sql.Identifier(st.session_state.course_to_review),
                        sql.Identifier(st.session_state.homework_index_to_review)
                    ),
                    (":white_check_mark:", this_university_code)
                )
                conn.commit()

        def hw_retry(this_university_code):
            with conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("UPDATE {} SET {} = %s WHERE university_code = %s")
                    .format(
                        sql.Identifier(st.session_state.course_to_review),
                        sql.Identifier(st.session_state.homework_index_to_review)
                    ),
                    (":arrows_clockwise:", this_university_code)
                )
                conn.commit()

        st.session_state.course_to_review = st.selectbox("What course?", courses, key="course_review")

        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position DESC LIMIT 1
                """), (st.session_state.course_to_review,))
            st.session_state.homework_index_to_review = cursor.fetchone()[0]

        if str(st.session_state.homework_index_to_review).isdigit():
            with conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("""
                        SELECT * FROM {} WHERE {} SIMILAR TO %s
                    """)
                    .format(
                        sql.Identifier(st.session_state.course_to_review),
                        sql.Identifier(st.session_state.homework_index_to_review)
                    ),
                    ('(:mag:%|:arrows_clockwise:%)',)
                )
                submissions_to_review = cursor.fetchall()

            if "current" not in st.session_state:
                st.session_state.current = 0

            if submissions_to_review:
                if st.session_state.current >= len(submissions_to_review):
                    st.session_state.current = 0

                each_submission = submissions_to_review[st.session_state.current]
                f_name, l_name, university_code = each_submission[:3]
                file_name = f"{st.session_state.course_to_review}_{university_code}_{st.session_state.homework_index_to_review}"

                col_info, col_preview = st.columns([2, 10])
                with col_info:
                    st.text(f"date = {st.session_state.homework_index_to_review}")
                    st.text(f"{f_name} {l_name}")
                    st.text(f"{university_code}")

                    col_nav_next, col_nav_prev = st.columns([1, 1])
                    with col_nav_next:
                        st.button(":arrow_forward:", on_click=hw_next, key="next_btn",
                                  disabled=st.session_state.current == len(submissions_to_review) - 1)
                    with col_nav_prev:
                        st.button(":arrow_backward:", on_click=hw_prev, key="prev_btn",
                                  disabled=st.session_state.current == 0)

                    st.button("Accepted ✅", on_click=hw_accept, args=(university_code,), key="acc_btn")
                    st.button("Needs more work 🔄", on_click=hw_retry, args=(university_code,), key="ret_btn")

                with col_preview:
                    if Path(hw_directory / f"{file_name}.pdf").exists():
                        st.write("Mode: PDF")

                        with open(Path(hw_directory / f"{file_name}.pdf"), "rb") as f:
                            pdf_data = f.read()

                        pdf_viewer(input=pdf_data, width=700)

                    elif Path(hw_directory / f"{file_name}.png").exists():
                        st.write("Mode: IMG")
                        image = Image.open(Path(hw_directory / f"{file_name}.png"))
                        st.image(image, use_container_width=True)

                    elif Path(hw_directory / f"{file_name}.jpg").exists():
                        st.write("Mode: IMG")
                        image = Image.open(Path(hw_directory / f"{file_name}.jpg"))
                        st.image(image, use_container_width=True)

                    elif Path(hw_directory / f"{file_name}.jpeg").exists():
                        st.write("Mode: IMG")
                        image = Image.open(Path(hw_directory / f"{file_name}.jpeg"))
                        st.image(image, use_container_width=True)

                    elif Path(hw_directory / f"{file_name}.py").exists():
                        st.write("Mode: PY")
                        with open(Path(hw_directory / f"{file_name}.py")) as f:
                            st.code(f.read(), language='python')

                    else:
                        if Path(hw_directory / f"{file_name}.*").exists():
                            st.warning("File Available but preview not available")
                        else:
                            st.warning("Preview not available")

            else:
                st.write("Nothing to review")

        else:
            st.write("Nothing to review")

    with operation_tab:

        def new_hw():
            with conn.cursor() as cursor:
                new_index = str(int(st.session_state.homework_index_to_op) + 1) if st.session_state.homework_index_to_op.isdigit() else '1'
                if int(new_index) > 1:
                    old_index = str(int(new_index) - 1)
                    cursor.execute(
                        sql.SQL("SELECT * FROM {} WHERE {} SIMILAR TO %s")
                        .format(
                            sql.Identifier(st.session_state.course_to_op),
                            sql.Identifier(old_index)
                        ),
                        ('(:mag:%|:arrows_clockwise:%|:white_check_mark:)',)
                    )
                    for sub in cursor.fetchall():
                        uni_code = sub[2]
                        for file_path in hw_directory.glob(f"{st.session_state.course_to_op}_{uni_code}_{old_index}.*"):
                            file_path.rename(archived_dir / file_path.name)

                cursor.execute(
                    sql.SQL("ALTER TABLE {} ADD {} TEXT")
                    .format(
                        sql.Identifier(st.session_state.course_to_op),
                        sql.Identifier(new_index)
                    )
                )
                conn.commit()
                cursor.execute(
                    sql.SQL("UPDATE {} SET {} = %s WHERE {} IS NULL")
                    .format(
                        sql.Identifier(st.session_state.course_to_op),
                        sql.Identifier(new_index),
                        sql.Identifier(new_index)
                    ), (":x:",)
                )
                conn.commit()

        def drop_hw():
            with conn.cursor() as cursor:
                if not str(st.session_state.homework_index_to_op).isdigit():
                    st.error("No homeworks to drop")
                    return
                old_index = st.session_state.homework_index_to_op
                cursor.execute(
                    sql.SQL("SELECT * FROM {} WHERE {} SIMILAR TO %s")
                    .format(
                        sql.Identifier(st.session_state.course_to_op),
                        sql.Identifier(old_index)
                    ),
                    ('(:mag:%|:arrows_clockwise:%|:white_check_mark:)',)
                )
                for sub in cursor.fetchall():
                    uni_code = sub[2]
                    for file_path in hw_directory.glob(f"{st.session_state.course_to_op}_{uni_code}_{old_index}.*"):
                        file_path.unlink()

                cursor.execute(
                    sql.SQL("ALTER TABLE {} DROP {}")
                    .format(
                        sql.Identifier(st.session_state.course_to_op),
                        sql.Identifier(old_index)
                    )
                )
                conn.commit()

        st.session_state.course_to_op = st.selectbox("What course?", courses, key="course_op")
        st.text(f"Operating on {st.session_state.course_to_op}")

        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position DESC LIMIT 1
                """), (st.session_state.course_to_op,))
            st.session_state.homework_index_to_op = cursor.fetchone()[0]

        st.text(f"Last column is {st.session_state.homework_index_to_op}")

        st.button("Add new Homework", on_click=new_hw)
        st.button("Drop homework", on_click=drop_hw)
