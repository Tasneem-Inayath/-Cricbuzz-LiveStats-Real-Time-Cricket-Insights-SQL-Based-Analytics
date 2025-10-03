import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import queries as q
import streamlit as st
import mysql.connector
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.db_connection import get_connection
# -------------------
# PAGE SETUP
# -------------------
st.set_page_config(
    page_title="Cricket SQL Analytics",
    page_icon="📊",
    layout="wide"
)
st.title("📊 Cricket SQL Analytics")
st.header("🪄 Database Query Questions")

# -------------------
# MYSQL CONNECTION
# -------------------
@st.cache_resource
conn = get_connection() #type:ignore

# -------------------
# RUN QUERY FUNCTION
# -------------------
def run_query(conn, sql):
    """Execute SQL and return results + columns"""
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return columns, rows
    except Exception as e:
        st.error(f"❌ SQL Error: {e}")
        return [], []

# -------------------
# PREDEFINED QUERIES
# -------------------
import queries as q
queries = q.queries_json

st.markdown("---")
st.header("🔎 Predefined SQL Questions")

query_keys = list(queries.keys())
selected_question = st.selectbox(
    "Select a predefined question:",
    options=query_keys,
    index=0
)

selected_query_obj = queries[selected_question]

# ------------------- Check if selected query is a nested dict -------------------
if isinstance(selected_query_obj, dict):
    # Show sub-query selectbox
    selected_subquery = st.selectbox(
        "Select a sub-query:",
        options=list(selected_query_obj.keys())
    )
    sql_to_run = selected_query_obj[selected_subquery]

    with st.expander("🔍 View SQL Query"):
        st.code(sql_to_run, language="sql")

    if st.button("▶️ Execute Sub-Query"):
        cols, rows = run_query(conn, sql_to_run)
        if rows:
            st.success("✅ Query executed successfully!")
            st.table([dict(zip(cols, r)) for r in rows])
        else:
            st.warning("⚠️ Query returned no results.")

# ------------------- Normal single SQL query -------------------
else:
    sql_to_run = selected_query_obj

    with st.expander("🔍 View SQL Query"):
        st.code(sql_to_run, language="sql")

    if st.button("▶️ Execute Predefined Query"):
        cols, rows = run_query(conn, sql_to_run)
        if rows:
            st.success("✅ Query executed successfully!")
            st.table([dict(zip(cols, r)) for r in rows])
        else:
            st.warning("⚠️ Query returned no results.")

# -------------------
# CUSTOM QUERY
# -------------------
st.markdown("---")
st.header("💻 Execute Custom SQL Query")

user_query = st.text_area(
    "Type your SQL query here:",
    height=150,
    placeholder="e.g., SELECT * FROM players LIMIT 10;"
)

if st.button("▶️ Run Custom Query"):
    if user_query.strip() == "":
        st.warning("⚠️ Please enter a SQL query to execute.")
    else:
        cols, rows = run_query(conn, user_query)
        if rows:
            st.success("✅ Query executed successfully!")
            st.table([dict(zip(cols, r)) for r in rows])
        else:
            st.warning("⚠️ Query returned no results.")

# -------------------
# DATABASE INFO
# -------------------
def get_table_info(conn):
    """Get all tables and their columns"""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [t[0] for t in cursor.fetchall()]
    table_dict = {}
    for t in tables:
        cursor.execute(f"DESCRIBE {t};")
        table_dict[t] = [row[0] for row in cursor.fetchall()]
    return table_dict

with st.expander("📁 Database Tables & Columns"):
    tables_info = get_table_info(conn)
    for t, cols in tables_info.items():
        with st.expander(f"Table: {t}"):
            st.write(cols)

st.markdown("---")
st.header("📱 About This Dashboard")
st.markdown("""
**SQL Analytics Page:**
- 25 predefined SQL questions
- Searchable dropdown & query execution
- Custom SQL query execution
- Interactive table display
- Table structure visualization
""")
def back_to_home():
    if st.button("🏠 Back to Home Page"):
        st.switch_page("pages/homepage.py")  
back_to_home()

