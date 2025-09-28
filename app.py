import streamlit as st

st.set_page_config(page_title="Live Cricket Scores", page_icon="🏏",layout="wide",initial_sidebar_state="expanded")

st.sidebar.title("🏏 CricBuzz LiveStats")
st.sidebar.markdown("Select a section")

pages = {
    "Home":"pages/homepage.py",
    "Live Matches":"pages/live_matches_ui.py",
    "Top Stats":"pages/top_stats.py",
    "Sql Queries":"pages/sql_queries.py",
    "Crud Operations":"pages/crud_operations.py"

}
choice = st.sidebar.selectbox("Navigation", list(pages.keys()),index=0)
# if choice == "home":
#     import pages.homepage as home
#     home.show()

# elif choice == "live matches":
#     import pages.live_matches as live
#     live.show()
# elif choice == "top stats":
#     import pages.top_stats as top
#     top.show()      
# elif choice == "sql queries":
#     import pages.sql_queries as sql
#     sql.show()
# elif choice == "crud operations":
#     import pages.crud_operations as crud
#     crud.show()

page_file = pages[choice]
with open(page_file, "r", encoding="utf-8") as f:
    code = f.read()
exec(code)