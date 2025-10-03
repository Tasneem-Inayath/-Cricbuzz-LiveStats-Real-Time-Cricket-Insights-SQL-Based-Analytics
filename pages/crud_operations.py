import streamlit as st
import mysql.connector
from datetime import datetime, date
import decimal
import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.db_connection import get_connection

# -------------------
# MySQL Connection
# -------------------
@st.cache_resource
def get_conn():
    return get_connection()

conn = get_conn()

cursor = conn.cursor(dictionary=True)

# -------------------
# Helper Functions
# -------------------
def get_tables():
    """Return a list of all table names in the current database."""
    cursor.execute("SHOW TABLES;")
    results = cursor.fetchall()
    # grab the first value from each row dict
    return [list(r.values())[0] for r in results] #type:ignore

def get_columns(table):
    """Return a list of (column_name, column_type) for a table."""
    cursor.execute(f"DESCRIBE {table};")
    return [(col['Field'], col['Type']) for col in cursor.fetchall()]#type:ignore

def get_primary_key(table):
    """Return a list of primary key column names for a table."""
    cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name='PRIMARY';")
    return [row['Column_name'] for row in cursor.fetchall()]#type:ignore

def format_value_for_insert(val):
    """Convert Python values to proper MySQL insert format."""
    if isinstance(val, decimal.Decimal):
        return float(val)
    if isinstance(val, date):
        return val.strftime("%Y-%m-%d")
    return val

def input_widget(col, col_type, value=None, disabled=False):
    """Return appropriate Streamlit input widget based on column type."""
    col_type_lower = col_type.lower()
    
    if "int" in col_type_lower or "bigint" in col_type_lower:
        return st.number_input(col, value=value if value is not None else 0, step=1, disabled=disabled)
    elif "decimal" in col_type_lower or "float" in col_type_lower:
        val = float(value) if isinstance(value, decimal.Decimal) else (value if value is not None else 0.0)
        return st.number_input(col, value=val, format="%.2f", disabled=disabled)
    elif "date" in col_type_lower:
        from datetime import datetime, date
        if value is None or not isinstance(value, date):
            value = datetime.today()
        return st.date_input(col, value=value, disabled=disabled)
    else:
        return st.text_input(col, value=str(value) if value is not None else "", disabled=disabled)

# -------------------
# CRUD Dashboard
# -------------------
st.title("⚡ Dynamic CRUD Dashboard - CricketDB")

tables = get_tables()
selected_table = st.selectbox("Select Table", tables)

columns = get_columns(selected_table)
col_types = {c[0]: c[1] for c in columns}
primary_keys = get_primary_key(selected_table)

crud_action = st.radio("Select Action", ["Create", "Read", "Update", "Delete"])

# -------------------
# READ
# -------------------
if crud_action == "Read":
    st.subheader(f"📖 View {selected_table}")
    try:
        cursor.execute(f"SELECT * FROM {selected_table} LIMIT 100;")
        results = cursor.fetchall()
        if results:
            st.table(results)
        else:
            st.warning("⚠️ No data found.")
    except mysql.connector.Error as e:
        st.error(f"❌ Error: {e}")

# -------------------
# CREATE
# -------------------
elif crud_action == "Create":
    st.subheader(f"➕ Add New Row to {selected_table}")
    new_values = {col: input_widget(col, col_type) for col, col_type in columns}

    if st.button("Add Row"):
        try:
            keys = ", ".join(new_values.keys())#type:ignore
            placeholders = ", ".join(["%s"] * len(new_values))
            vals = tuple(format_value_for_insert(v) for v in new_values.values())
            cursor.execute(f"INSERT INTO {selected_table} ({keys}) VALUES ({placeholders})", vals)
            conn.commit()
            st.success("✅ Row added successfully!")
        except mysql.connector.Error as e:
            st.error(f"❌ Error: {e}")

# -------------------
# UPDATE
# -------------------
elif crud_action == "Update":
    st.subheader(f"✏️ Update Row in {selected_table}")
    try:
        cursor.execute(f"SELECT * FROM {selected_table}")
        all_rows = cursor.fetchall()
        if not all_rows:
            st.warning("⚠️ No rows available to update.")
        else:
            options = [" | ".join(str(r[k]) for k in primary_keys) for r in all_rows]#type:ignore
            selected_index = st.selectbox("Select row to update", range(len(options)), format_func=lambda x: options[x])
            selected_row = all_rows[selected_index]

            updated_values = {}
            for col, col_type in columns:
                if col in primary_keys:
                    continue  # Skip primary key
                updated_values[col] = input_widget(col, col_type, selected_row[col])#type:ignore

            if st.button("Update Row"):
                try:
                    set_clause = ", ".join(f"{k}=%s" for k in updated_values.keys())
                    pk_clause = " AND ".join(f"{k}=%s" for k in primary_keys)
                    vals = tuple(format_value_for_insert(v) for v in updated_values.values())
                    vals += tuple(selected_row[k] for k in primary_keys)#type:ignore
                    cursor.execute(f"UPDATE {selected_table} SET {set_clause} WHERE {pk_clause}", vals)
                    conn.commit()
                    st.success("✅ Row updated successfully!")
                except mysql.connector.Error as e:
                    st.error(f"❌ Error: {e}")
    except mysql.connector.Error as e:
        st.error(f"❌ Error: {e}")

# -------------------
# DELETE
# -------------------
elif crud_action == "Delete":
    st.subheader(f"🗑️ Delete Row from {selected_table}")
    try:
        cursor.execute(f"SELECT * FROM {selected_table}")
        all_rows = cursor.fetchall()
        if not all_rows:
            st.warning("⚠️ No rows available to delete.")
        else:
            options = [" | ".join(str(r[k]) for k in primary_keys) for r in all_rows]#type:ignore
            selected_index = st.selectbox("Select row to delete", range(len(options)), format_func=lambda x: options[x])
            selected_row = all_rows[selected_index]

            if st.button("Delete Row"):
                try:
                    pk_clause = " AND ".join(f"{k}=%s" for k in primary_keys)
                    cursor.execute(f"DELETE FROM {selected_table} WHERE {pk_clause}", tuple(selected_row[k] for k in primary_keys))#type:ignore
                    conn.commit()
                    st.success("✅ Row deleted successfully!")
                except mysql.connector.Error as e:
                    st.error(f"❌ Error: {e}")
    except mysql.connector.Error as e:
        st.error(f"❌ Error: {e}")
st.subheader("🛠️ About CRUD Operations")
st.info("""
**CRUD Operations Page:**
- Create, Read, Update, and Delete records  
- Manage players, teams, and matches data  
- Form-based interface for easy data entry  
- Validation to prevent errors  
- Immediate reflection of changes in the database
""")
def back_to_home():
    if st.button("🏠 Back to Home Page"):
        st.switch_page("pages/homepage.py")  
back_to_home()