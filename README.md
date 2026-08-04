# 🚀 MetaGuard

**Enterprise Data Governance & Risk Intelligence Platform**

MetaGuard is a production-ready Django application that helps organizations analyze uploaded datasets by extracting metadata, detecting Personally Identifiable Information (PII), evaluating data quality, classifying risk, and generating governance reports.

🌐 **Live Demo:** https://metaguard-hc0k.onrender.com

---

## ✨ Features

- 📂 Upload and validate CSV/JSON datasets
- 🔍 Metadata extraction and schema analysis
- 🛡️ PII detection and risk classification
- 📊 Data quality analysis and scoring
- 📄 Automated governance PDF reports
- ⚡ Background processing with Celery & Redis

---

## 🏗️ Architecture

```text
Client
   │
   ▼
Gunicorn
   │
   ▼
Django
 ├── PostgreSQL
 └── Redis
      │
      ▼
 Celery Worker
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|--------|------------|
| Backend | Django 5 |
| Database | PostgreSQL |
| Task Queue | Celery + Redis |
| Data Processing | Pandas |
| Reports | ReportLab |
| Server | Gunicorn |
| Containerization | Docker & Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | Render |

---

## 📸 Screenshots

> Add screenshots here:

- Dashboard
- Dataset Upload
- Data Quality Report
- Governance Report

---

## ⚙️ Run Locally

```bash
git clone https://github.com/prijithjohn/Metaguard.git

cd Metaguard

cp .env.example .env

docker compose up --build
```

The application will be available at:

```
http://localhost:8001
```

---

## 🚀 Deployment

MetaGuard is containerized using Docker and deployed on Render with PostgreSQL, Redis, and GitHub Actions for continuous integration.

---

## 🎯 Future Improvements

- NGINX Reverse Proxy
- Kubernetes Deployment
- Terraform Infrastructure
- Prometheus & Grafana Monitoring
- AWS S3 File Storage

---

## 💡 Skills Demonstrated

- Django Backend Development
- REST API Design
- PostgreSQL
- Celery & Redis
- Docker & Docker Compose
- CI/CD with GitHub Actions
- Production Deployment
- Data Processing with Pandas

---

## 👨‍💻 Author

**Prijith John**

- GitHub: https://github.com/prijithjohn
- LinkedIn: linkedin.com/in/prijith-john-dev

If you found this project interesting, consider giving it a ⭐.
