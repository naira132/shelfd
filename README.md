# 📚 Shelfd — Digital Bookshelf & OCR Reading Tracker

> A modern full-stack web application for tracking reading progress, capturing book quotes via OCR scan, and protecting users from plot spoilers.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)

---

## 🌟 Key Features

* **Interactive Reading Progress Tracker:** Visual page sliders and automated status transitions (`Want to Read` ➔ `Currently Reading` ➔ `Completed`).
* **OCR Quote Scanning:** Upload or photograph book pages to extract quote text automatically using PyTesseract.
* **Spoiler Protection Engine:** Backend middleware dynamically redacts community notes and quotes if they exceed a user's current reading page.
* **S3-Compatible Media Storage:** Store book covers and quote scans using local MinIO storage.

---

## 🛠️ Tech Stack

### **Backend**
* **Framework:** Python / FastAPI
* **Database & ORM:** PostgreSQL + SQLAlchemy & Alembic (Database Migrations)
* **Data Validation:** Pydantic V2
* **Storage & OCR:** MinIO (S3 API) + PyTesseract

### **Frontend**
* **Framework:** React (TypeScript) + Vite
* **Styling:** Tailwind CSS
* **Icons & State:** Lucide React, Native React Hooks

### **Infrastructure**
* **Containerization:** Docker & Docker Compose

---

## 🚀 Quick Start (Local Setup)

### **Prerequisites**
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### **1. Clone Repository**
```bash
git clone [https://github.com/your-username/shelfd.git](https://github.com/your-username/shelfd.git)
cd shelfd
```
