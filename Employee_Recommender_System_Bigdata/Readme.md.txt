
# 👩‍💼 Employee Behavior Recommender System

A behavioral analytics system designed to monitor employee activity, detect anomalies, and recommend secure access patterns using big data tools and machine learning.

---

## 📋 Project Overview

**Secure Sense** is a Spark-powered behavioral monitoring and recommender system. It analyzes employee logins, HTTP activity, and file access logs to detect suspicious behavior and recommend secure work patterns. The system integrates anomaly detection and collaborative filtering to not only flag risks but guide employees toward safer actions.

---

## 🧠 Key Features

- 🔐 **Behavioral Monitoring**:
  - Tracks login patterns, file accesses, and web activity
- ⚠️ **Anomaly Detection**:
  - Identifies login time anomalies, malicious URLs, and rare file access
  - Isolation Forest and statistical profiling
- 🤝 **Recommendations**:
  - Suggests files and URLs based on collaborative behavior
  - ALS-based collaborative filtering in PySpark
- 📊 **Dashboard Visualization**:
  - Power BI dashboard for live activity tracking

---

## 🏗️ Project Structure

```
employee-behavior-recommender/
├── data/                      # Sample input datasets
│   ├── login_info_sample.csv
│   ├── http_info_sample.csv
│   └── employee_details_sample.csv
├── notebooks/                 # PySpark data analysis and modeling
│   ├── Group10_1.ipynb
│   └── Group10_2.ipynb
├── report/                    # Final project report
│   └── Final_group10_report.pdf
├── dashboards/                # (Optional) Power BI exports/screenshots
│   └── powerbi_dashboard.png
└── README.md
```

---

## 🛠️ Tools & Tech

- ⚙️ **PySpark** for scalable data processing
- 📁 CSV-based user activity and metadata
- 📊 Power BI for real-time visualization
- 🧪 Isolation Forest for anomaly detection
- 🤖 ALS collaborative filtering in PySpark

---

## 💻 Sample Use Case

**Scenario**:  
A user logs in at odd hours, accesses files from a different department, and clicks on unverified URLs.  
The system:

- Flags these as anomalies
- Logs metadata (time, type, severity)
- Recommends secure files and trusted URLs based on similar employees

---

## 📌 Future Improvements

- Real-time stream processing via Kafka
- Email alerting for policy violations
- Role-based access recommendations

---

## 🙋‍♂️ Author

**Evakattu Muni Eshwar**  
🎓 M.S. in Artificial Intelligence, San Jose State University  
🔗 [LinkedIn](https://www.linkedin.com/in/evakattumunieshwar) | [GitHub](https://github.com/munieshwar16)

---

> 🔒 _“Detect early. Recommend safely. Empower securely.”_
