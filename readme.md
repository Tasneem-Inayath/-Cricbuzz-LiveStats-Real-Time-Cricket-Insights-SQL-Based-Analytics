# -Cricbuzz-LiveStats-Real-Time-Cricket-Insights-SQL-Based-Analytics
A comprehensive cricket analytics dashboard that integrates live data from the Cricbuzz API with a SQL database to create an interactive web application. The platform should deliver: ⚡ Real-time match updates 📊 Detailed player statistics 🔍 SQL-driven analytics 🛠️ Full CRUD operations for data management

# 🏏 Cricbuzz LiveStats  
### *Real-Time Cricket Insights & SQL-Based Analytics*

---

## 📌 Introduction
Cricket fans love real-time insights!  
**Cricbuzz LiveStats** is a Streamlit-based web app that combines **live match tracking** and **SQL-powered analytics** for cricket enthusiasts.

---

## 🛠 Tech Stack
- **Frontend:** Streamlit  
- **Backend:** Python  
- **Database:** MySQL (via `mysql-connector-python`)  
- **Modules:** Pandas, Datetime, MySQL Connector  

---

## 🚀 Features
- 📱 **Live Matches Page** – Real-time score updates & highlights  
- 🗄 **CRUD Operations Page** – Manage teams, players, and matches  
- 📊 **SQL Queries Page** – Execute and view analytics  
- 🏆 **Top Stats Page** – Leaderboards & insights  
- 🏠 **Homepage** – Easy navigation  

---

## 📂 Folder Structure
```
project/
│── app.py                # Main entry point
│── queries.py            # SQL query functions
│── README.md             # Project Documentation
│── .gitignore
│
├── pages/                # Streamlit Pages
│   ├── homepage.py
│   ├── live_matches_ui.py
│   ├── crud_operations.py
│   ├── sql_queries.py
│   ├── top_stats.py
│
├── utils/                # Helper Functions
│   ├── match_helpers.py
│   ├── queries_funcs.py
│   ├── stat_helpers.py
│
└── notebooks/            # Jupyter Notebooks
```

---

## 💻 Installation & Setup

1. **Clone the repository**
```bash
git clone <your-repo-link>
cd Cricbuzz-LiveStats
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **MySQL Database Setup**
   - Create a MySQL database (e.g., `cricketdb`)  
   - Import the SQL schema if available  
   - Update `app.py` with your MySQL credentials

5. **Run the Streamlit app**
```bash
streamlit run app.py
```

---

## 📝 Sample SQL Queries
```sql
-- Top 5 run scorers
SELECT player_name, SUM(runs) AS total_runs
FROM player_stats
GROUP BY player_name
ORDER BY total_runs DESC
LIMIT 5;

-- Head-to-head team stats (last 3 years)
SELECT LEAST(team1_id, team2_id) AS team_a,
       GREATEST(team1_id, team2_id) AS team_b,
       COUNT(*) AS total_matches
FROM matches
WHERE match_date >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
GROUP BY team_a, team_b;
```

---

## 📸 UI Snapshots
- Homepage  
<img width="1904" height="972" alt="Screenshot 2025-09-30 000844" src="https://github.com/user-attachments/assets/f6aebde7-0df1-4185-9582-9f9573c50e0c" />

<img width="1881" height="982" alt="Screenshot 2025-09-30 001221" src="https://github.com/user-attachments/assets/af94ab13-f47e-4213-83d1-0632a5ba8458" />


<img width="1893" height="982" alt="Screenshot 2025-09-30 001246" src="https://github.com/user-attachments/assets/61fb1968-f5eb-4b8d-b49f-7108b0a68780" />

<img width="1919" height="983" alt="Screenshot 2025-09-30 001307" src="https://github.com/user-attachments/assets/c4f746f1-7e4e-4267-a7e7-17d7e0bcbeab" />
<img width="1893" height="988" alt="Screenshot 2025-09-30 001355" src="https://github.com/user-attachments/assets/e5566608-7480-4428-b08f-fa5c8778b571" />
<img width="1885" height="974" alt="Screenshot 2025-09-30 001511" src="https://github.com/user-attachments/assets/5c316b71-cee0-4b50-b511-9191876be7a0" />
<img width="1873" height="970" alt="Screenshot 2025-09-30 001541" src="https://github.com/user-attachments/assets/bf36b3b3-6bf9-43bf-8283-a5da1b3b6960" />

<img width="1907" height="863" alt="Screenshot 2025-09-30 001556" src="https://github.com/user-attachments/assets/d86cdbe0-7d33-4a00-bdfd-3c86e3b4a783" />


<img width="1874" height="960" alt="Screenshot 2025-09-30 001626" src="https://github.com/user-attachments/assets/e9f034b2-f31e-42c4-a4dd-e520c6975014" />









---

## ⚡ Challenges
- Managing real-time data refresh in Streamlit  
- Writing optimized SQL queries in MySQL  
- Smooth CRUD operations integration  

---

## 🔮 Future Enhancements
- Integration with a **live cricket API** for real-time match data  
- **AI/ML-based predictions** for player & team performance  
- Enhanced **visualizations** with charts & dashboards  

---

## ✅ Conclusion
- Built with **Python + MySQL + Streamlit**  
- Hands-on experience with **database queries** & **real-time analytics**  
- Real-world use case for cricket data enthusiasts  

---

