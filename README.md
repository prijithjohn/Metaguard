# 🛡️ MetaGuard

### Enterprise Data Governance & Risk Intelligence Platform

MetaGuard is a Django-based platform that analyzes datasets for **data quality, metadata insights, sensitive information (PII), and risk classification**. It helps organizations identify governance issues before datasets are used for analytics or AI systems.

---

## 🚀 Live Demo

👉 [Click here to view Demo](https://metaguard-ig1v.onrender.com)

> Upload a dataset and see real-time governance, PII detection, and risk scoring in action.

---

## 🚀 Features

* 📂 CSV & JSON Dataset Upload
* ⚡ Asynchronous Processing with Celery & Redis
* 📊 Metadata Extraction
* 📈 Data Quality Scoring
* 🔒 PII & Sensitive Data Detection
* 🚨 Risk Classification Engine
* 📄 PDF Governance Reports
* 📉 Interactive Analytics Dashboard

---

## 🏗️ Architecture

```text
User
 ↓
Django
 ↓
Redis
 ↓
Celery Workers
 ↓
Metadata Analysis
Quality Analysis
PII Detection
 ↓
PostgreSQL
 ↓
Dashboard & PDF Reports
```

---

## 🛠️ Tech Stack

| Layer      | Technology       |
| ---------- | ---------------- |
| Backend    | Django 5         |
| Database   | PostgreSQL       |
| Queue      | Celery           |
| Broker     | Redis            |
| Processing | Pandas, NumPy    |
| Reports    | ReportLab        |
| Frontend   | Bootstrap 5      |
| Deployment | Railway / Docker |

---

## ⚙️ Run Locally

```bash
git clone https://github.com/prijithjohn/Metaguard.git

cd Metaguard

pip install -r requirements.txt

python manage.py migrate

redis-server

celery -A metaguard_project worker --loglevel=info --pool=solo

python manage.py runserver
```

---

## ⭐ Highlights

* Handles datasets up to 1GB
* Detects 13+ PII patterns
* Real-time dashboard analytics
* Background processing using Celery & Redis
* Production-ready deployment architecture

---

## 👨‍💻 Author

**Prijith John**

GitHub: https://github.com/prijithjohn

LinkedIn: https://www.linkedin.com/in/prijith-john-dev
