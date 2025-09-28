import streamlit as st

st.title("🏏 Cricbuzz LiveStats")
st.markdown("Welcome to your all-in-one cricket Analytics Dashboard 🏏")

st.write("Get live updates, explore player statistics, run SQL queries, and manage your own records!")

st.markdown("---")

col1,col2,col3,col4 = st.columns(4)

with col1:
    st.subheader("Live Matches")
    st.write("Catch real-time scores and matche details.")
    if st.button("Go to Live Matches"):
        st.switch_page("pages/live_matches_ui.py")
with col2:
    st.subheader("📊 Top Stats")
    st.write("View batting and bowling leaders.")
    if st.button("Go to Top Stats"):
        st.switch_page("pages/top_stats.py")

with col3:
    st.subheader("🛠️ SQL Queries")
    st.write("Run custom SQL queries on match data.")
    if st.button("Go to SQL Queries"):
        st.switch_page("pages/sql_queries.py")
with col4:
    st.subheader("✍️ CRUD Operations")
    st.write("Add, update, or delete player stats.")
    if st.button("Go to CRUD Operations"):
        st.switch_page("pages/crud_operations.py")

st.subheader("📱 About This Dashboard")
st.info("""
**Home Page:**
- Welcome overview of Cricket Dashboard  
- Navigation to all modules (SQL, Live, Top Stats, CRUD)  
- Shortcuts for quick access  
- Project description & usage guide  
- Contact / About section  
""") 
st.markdown("---")
st.caption("⚡ Powered by Cricbuzz API & Streamlit | Designed for Cricket Fans ❤️")



        
