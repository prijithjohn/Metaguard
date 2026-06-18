# MetaGuard

MetaGuard is a lightweight data governance and data quality inspection tool built with Django. It supports dataset ingestion (CSV and JSON), metadata extraction, quality scoring, sensitive data discovery, and PDF reporting.

## Project Overview
- Ingest datasets (CSV/JSON)
- Extract column-level metadata
- Compute data quality scores
- Discover sensitive columns (PII) and compute risk
- Dashboard with KPIs and charts
- PDF report generation for executive summaries

## Business Problem
Organizations need an accessible tool to evaluate data quality and detect sensitive information during dataset intake. MetaGuard provides quick operational visibility for data stewards and governance teams.

## Architecture (Mermaid)
```mermaid
flowchart LR
  Upload[User Upload (CSV/JSON)] --> Backend[MetaGuard Django App]
  Backend -->|store| Media[Media Storage]
  Backend -->|process| Services[Metadata / Quality / Governance Services]
  Services --> DB[(Database)]
  Backend -->|render| Frontend[Bootstrap Templates]
  Backend -->|export| PDF[ReportLab PDF]
```

## Database Schema
- `Dataset` — metadata and file pointer
- `DatasetColumn` — column-level metadata
- `QualityReport` — quality metrics and score
- `SensitiveDataReport` / `SensitiveField` — sensitive findings

## Features
- Upload CSV or JSON datasets
- Metadata extraction (data types, nulls, uniques)
- Quality scoring algorithm with configurable weights
- Sensitive data discovery (emails, SSN, PAN, Aadhaar, IFSC, UPI, phone, DOB, salary, address heuristics)
- Dashboard with KPIs and charts
- PDF report generation

## Installation
1. Create virtualenv and install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
2. Configure environment variables (see `.env.example`)
3. Apply migrations
```bash
python manage.py migrate
```
4. Run development server
```bash
python manage.py runserver
```

## Usage
- Access dashboard: http://127.0.0.1:8000/dashboard/
- Upload dataset: http://127.0.0.1:8000/datasets/upload/

## Future Enhancements
- Background processing for large datasets (Celery/RQ)
- Virus scanning on uploads
- User authentication and role-based access control
- Export to additional formats and richer PDF reports
