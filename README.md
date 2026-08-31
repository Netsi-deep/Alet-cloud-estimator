# Alet Cloud Resource Cost & Usage Estimator

A full-stack web application designed for estimating cloud resource costs (vCPU, RAM, Storage, and SMS volume) on Alet Cloud infrastructure. It features a modern, responsive UI with real-time calculations, dark/light mode, and server-side professional PDF quotation generation.

---

## 🚀 Features
- **Interactive Estimator:** Dynamic range sliders for vCPU Cores, RAM, NVMe Storage, and Monthly SMS volume with real-time cost updates.
- **Billing Cycles:** Seamless switching between Hourly, Monthly, and Yearly pricing structures.
- **Server-Side PDF Generation:** Generates branded, professional PDF quotations instantly using ReportLab.
- **Dark/Light Theme Support:** Clean user-toggleable interface themes built with Tailwind CSS.
- **Cloud Ready:** Containerized using Docker for scalable and reliable cloud deployments.

---

## 🛠️ Tech Stack
- **Frontend:** HTML5, Tailwind CSS (CDN), JavaScript (ES6+)
- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **PDF Engine:** ReportLab
- **Containerization:** Docker (`python:3.11-slim`)
- **Deployment:** Alet Cloud Platform

---

## 📁 Project Structure

```text
alet-estimator/
│
├── main.py            # FastAPI backend application & PDF generation logic
├── index.html         # Main user interface frontend
├── script.js          # Frontend interactivity, API fetch calls, and theme handling
├── style.css          # Custom CSS styles and Tailwind configurations
├── Dockerfile         # Container build instructions for Alet Cloud
├── logo-icon.png      # AletCloud branding asset
└── README.md          # Project documentation
```
## ⚙️ Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Netsi-deep/Alet-cloud-estimator.git](https://github.com/Netsi-deep/Alet-cloud-estimator.git)
   cd Alet-cloud-estimator

2.  **Install dependencies:**
 ```bash
   pip install fastapi uvicorn pydantic reportlab
   ```

3.  **Run the FastAPI development server:**
Bash
uvicorn main:app --reload --port 8000
4.  **Access the application:**
Open your browser and navigate to http://localhost:8000.
## 🐳 Docker Deployment

**To build and run the container locally:**
Bash

docker build -t alet-cloud-estimator .
docker run -p 8000:8000 alet-cloud-estimator

## 🌐 Live Deployment Link

    Alet Cloud Instance: https://alet-estim.app.aletcloud.com