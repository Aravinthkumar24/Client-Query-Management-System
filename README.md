# Client-Query-Management-System
**Client Query Management System:** Developed a Python-MySQL Streamlit app for managing client support queries. Features include secure login, real-time query submission, and a dashboard for tracking and closing queries. Used Pandas for data cleaning, analysis, and visualization to monitor trends and resolution times.

🚀 Features
👤 User Authentication

Register new users (Client / Support)

Secure login with SHA-256 password hashing

📩 Client Portal

Submit new queries

View history of submitted queries

🛠 Support Dashboard

View all queries

Filter by: All / Open / Closed

Close queries with one click

Donut chart showing query status distribution

📊 Analytics

Resolution time calculation

Resolution histogram

Daily open-query load analysis


📦 Installation
1. Clone the repository
git clone <repo-link>
cd client-query-management

2. Install dependencies
pip install -r requirements.txt

3. Create MySQL Database
CREATE DATABASE client_query_db;

USE client_query_db;

CREATE TABLE users (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE,
  hashed_password VARCHAR(255),
  role ENUM('Client','Support')
);

CREATE TABLE queries (
  query_id INT PRIMARY KEY AUTO_INCREMENT,
  mail_id VARCHAR(100),
  mobile_number VARCHAR(20),
  query_heading VARCHAR(255),
  query_description TEXT,
  status ENUM('Open','Closed') DEFAULT 'Open',
  query_created_time DATETIME,
  query_closed_time DATETIME NULL
);

4. Update credentials in code
Edit:
host="127.0.0.1"
user="ak"
password="2401"
database="client_query_db"

▶ Run the Application
streamlit run main.py

📁 Project Structure
.
├── main.py
├── requirements.txt
└── README.md

🔒 Security

Password hashing with SHA-256

Parameterized SQL queries

Role-based interface access

🧩 Screenshots

Login Page

Client Query Form

Support Dashboard

Visual Analytics

