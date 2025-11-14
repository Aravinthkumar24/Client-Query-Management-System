import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
from datetime import datetime
import plotly.express as px  # <-- for donut chart

# ---------- MySQL Connection ----------
def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port="3306",
        user="ak",
        password="2401",  # change this
        database="client_query_db"
    )
# ---------- Utility Functions ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, hashed_password, role) VALUES (%s, %s, %s)",
            (username, hash_password(password), role),
        )
        conn.commit()
        st.success("✅ Registration Successful!")
    except mysql.connector.errors.IntegrityError:
        st.error("⚠️ Username already exists.")
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND hashed_password=%s",
        (username, hash_password(password)),
    )
    user = cursor.fetchone()
    conn.close()
    return user

def insert_query(mail, mobile, heading, desc):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO queries (mail_id, mobile_number, query_heading, query_description, query_created_time)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (mail, mobile, heading, desc, datetime.now()),
    )
    conn.commit()
    conn.close()
    st.success("✅ Query Submitted Successfully!")

def fetch_queries(status=None):
    conn = get_connection()
    query = "SELECT * FROM queries"
    if status and status != "All":
        query += f" WHERE status='{status}'"
    query += " ORDER BY query_created_time DESC"  # 👈 sort newest first
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def close_query(query_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE queries SET status='Closed', query_closed_time=%s WHERE query_id=%s",
        (datetime.now(), query_id),
    )
    conn.commit()
    conn.close()
    st.success(f"✅ Query ID {query_id} Closed Successfully!")

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Client Query Management System", layout="wide")
st.title("🧾 Client Query Management System")

# ---------- Sidebar Navigation ----------
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.page = "Login"

# If not logged in
if not st.session_state.user:
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Register":
        st.subheader("📝 Register New User")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Client", "Support"])
        if st.button("Register"):
            if username and password:
                register_user(username, password, role)
            else:
                st.warning("Please fill all fields.")

    elif choice == "Login":
        st.subheader("🔐 User Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.user = user
                if user["role"] == "Client":
                    st.session_state.page = "Client"
                elif user["role"] == "Support":
                    st.session_state.page = "Support"
                st.rerun()
            else:
                st.error("Invalid username or password.")

# ---------- After Login ----------
else:
    user = st.session_state.user
    st.sidebar.write(f"👋 Welcome, **{user['username']} ({user['role']})**")
    logout = st.sidebar.button("🚪 Logout")

    if logout:
        st.session_state.user = None
        st.session_state.page = "Login"
        st.rerun()

    # ----- Client Page -----
    if st.session_state.page == "Client" and user["role"] == "Client":
        st.header("📩 Submit a New Query")
        mail = st.text_input("Email ID")
        mobile = st.text_input("Mobile Number")
        heading = st.text_input("Query Heading")
        desc = st.text_area("Query Description")

        if st.button("Submit Query"):
            if mail and mobile and heading and desc:
                insert_query(mail, mobile, heading, desc)
            else:
                st.warning("Please fill all fields.")

        st.divider()
        st.subheader("📜 Your Queries")
        df = fetch_queries()
        st.dataframe(df)

        # ----- Support Page -----
    elif st.session_state.page == "Support" and user["role"] == "Support":
        st.header("🛠️ Support Dashboard")

        # ---- Donut Chart Section ----
        all_queries = fetch_queries()
        if not all_queries.empty:
            status_counts = all_queries['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']

            fig = px.pie(
                status_counts,
                names='Status',
                values='Count',
                hole=0.5,  # donut
                color_discrete_sequence=["#00cc96", "#ff6361"]
            )
            fig.update_layout(title_text="📊 Query Status Distribution", title_x=0.35)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No queries found yet.")

        st.divider()
        filter_status = st.selectbox("Filter by Status", ["All", "Open", "Closed"])
        df = fetch_queries(filter_status)
        st.dataframe(df)

        if not df.empty and "Open" in df["status"].values:
            open_ids = df[df["status"] == "Open"]["query_id"].tolist()
            selected_id = st.selectbox("Select Query ID to Close", open_ids)
            if st.button("Close Selected Query"):
                close_query(selected_id)
                # 🔁 Refresh dashboard instantly
                st.rerun()

    # ---------------- Resolution Time Analysis ----------------
    st.subheader("⏳ Resolution Time Analysis (Closed Queries Only)")

    closed_df = all_queries[all_queries['status'] == "Closed"].copy()
    if not closed_df.empty:
        closed_df['query_created_time'] = pd.to_datetime(closed_df['query_created_time'])
        closed_df['query_closed_time'] = pd.to_datetime(closed_df['query_closed_time'])

        closed_df['resolution_hours'] = (closed_df['query_closed_time'] - closed_df['query_created_time']).dt.total_seconds() / 3600

        avg_resolution = closed_df['resolution_hours'].mean()
        median_resolution = closed_df['resolution_hours'].median()

        st.metric("Average Resolution Time (hrs)", f"{avg_resolution:.2f}")
        st.metric("Median Resolution Time (hrs)", f"{median_resolution:.2f}")

        fig_res = px.histogram(
            closed_df,
            x='resolution_hours',
            nbins=20,
            title="Resolution Time Distribution (hours)",
            color_discrete_sequence=["#636EFA"]
        )
        st.plotly_chart(fig_res, use_container_width=True)
    else:
        st.info("No closed queries yet to calculate resolution times.")

    # ---------------- Support Load Over Time ----------------
    st.subheader("📌 Support Load Over Time (Open Queries)")

    open_df = all_queries[all_queries['status'] == "Open"].copy()
    if not open_df.empty:
        open_df['query_created_date'] = pd.to_datetime(open_df['query_created_time']).dt.date
        open_trend = open_df.groupby('query_created_date').size().reset_index(name='Open Queries')

        fig_load = px.bar(
            open_trend,
            x='query_created_date',
            y='Open Queries',
            title="Daily Open Query Load",
            color='Open Queries',
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_load, use_container_width=True)
    else:
        st.info("No open queries at the moment.")
