🏏 Cricket Analytics Dashboard

An interactive Streamlit dashboard for exploring cricket data, tracking live matches, visualizing top stats, and performing database operations.

📱 Features

🏠 Home Page → Quick navigation and project overview

📊 SQL Analytics → 25 predefined SQL queries, custom query execution, CSV download, and visualizations

📡 Live Matches → Real-time match updates, player scorecards, match summary

🏆 Top Stats → Leaderboards, player comparisons, season trends

📝 CRUD Operations → Add, edit, and manage players and matches with auto-clear inputs

💼 Business Use Cases

📺 Sports Media → Real-time updates & analysis for commentary teams

🎮 Fantasy Cricket → Player form & stats for team selection

📈 Analytics Firms → Performance trend analysis & insights

🎓 Education → SQL practice & database operations with real-world data

🎲 Sports Prediction → Historical & venue-specific performance analysis

⚙️ Installation

Clone the repository:

git clone https://github.com/your-username/cricket-analytics-dashboard.git
cd cricket-analytics-dashboard


Create a virtual environment (recommended):

python -m venv .venv
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate       # Windows


Install dependencies:

pip install -r requirements.txt

🚀 Run the App
streamlit run app.py


The dashboard will open in your browser.

📂 Project Structure
.
├── app.py                  # Main entry (Home Page)
├── pages/                  # Other Streamlit pages
│   ├── 1_SQL_Analytics.py
│   ├── 2_Live_Matches.py
│   ├── 3_Top_Stats.py
│   └── 4_CRUD_Operations.py
├── cricket_fresh.db        # SQLite database
├── queries.py              # Predefined SQL queries
├── requirements.txt        # Dependencies
└── README.md               # Documentation

🛠️ Tech Stack

Streamlit → Frontend & UI

SQLite → Database

Pandas → Data handling

Matplotlib / Altair → Visualizations

Requests API → Live match data

✨ Built with ❤️ by Tasneem