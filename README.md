# Farmer Credit Score Engine

**Transparent, Data-Driven Credit Scoring for the Unbanked**

[![CI](https://github.com/youruser/farmer-credit-score-engine/workflows/CI/badge.svg)](https://github.com/youruser/farmer-credit-score-engine/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)

---

## 📖 Table of Contents
- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [How It Works](#-how-it-works)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [ML Model & Scoring](#-ml-model--scoring)
- [Roadmap](#-roadmap)

---

## 🚩 The Problem

India's **146 million farmers** face a persistent credit gap of over **₹8 trillion**. Traditional credit scoring models fail rural borrowers because:

*   **No Credit History:** 70% of farmers are unbanked or lack formal credit records.
*   **Seasonal Income:** Cash flow is tied to unpredictable crop cycles, not monthly salaries.
*   **Collateral Dependency:** Banks rely heavily on land ownership, excluding tenant farmers.
*   **Opaque Processes:** Farmers rarely understand why a loan was rejected.

As a result, millions are forced to rely on informal money lenders charging **24-36% interest rates**.

---

## 💡 The Solution

The **Farmer Credit Score Engine** is a fintech platform designed to bridge this gap. It computes **fair, transparent, and data-driven credit scores (0-100)** by looking beyond bank statements.

We utilize **Alternative Data** to assess creditworthiness:
1.  **Agri Stack Data:** Land records, crop registry, and government database integration.
2.  **Satellite Imagery:** Real-time crop health monitoring using NDVI (Normalized Difference Vegetation Index).
3.  **Weather Patterns:** Historical rainfall data and anomaly detection to assess yield risk.
4.  **Digital Footprint:** UPI transactions, FPO memberships, and market access data.

---

## ⚙️ How It Works

1.  **Onboarding:** A Field Agent onboards a farmer using the **Offline-First Mobile App**, capturing basic details and land coordinates.
2.  **Data Ingestion:** The system automatically fetches satellite data, weather history, and land records for the farmer's location.
3.  **Scoring:**
    *   **Deterministic Model:** Calculates a baseline score using weighted rules.
    *   **ML Model (RandomForest):** Refines the score and identifies risk factors.
    *   **Explainability (SHAP):** Generates the "Top 3 Drivers" explaining *why* the score is what it is (e.g., "High crop health," "Consistent rainfall").
4.  **Decision:** The Bank Admin Dashboard displays the score, risk profile, and a **customized loan offer** with EMI plans aligned to the crop harvest cycle.

---

## ✨ Key Features

*   **✅ Explainable AI:** Unlike "black box" scores, we tell you *why*. Every score comes with human-readable reasons (e.g., "+ Good market access", "- High rainfall deficit").
*   **✅ Offline-First PWA:** The Field Agent app works without internet, syncing data when connectivity returns—crucial for remote villages.
*   **✅ Crop-Cycle Aligned Loans:** EMI plans are generated based on the specific crop's harvest time, reducing default risk.
*   **✅ Microservices Architecture:** Scalable, independent services for API, ML, and Frontend.
*   **✅ Production Ready:** Includes Docker Compose for local dev and Kubernetes manifests for cloud deployment.

---

## 🛠 Technology Stack

### Backend & ML
*   **FastAPI (Python):** High-performance async REST API.
*   **Celery & Redis:** Distributed task queue for background scoring and data fetching.
*   **Scikit-Learn:** RandomForest Regressor for credit scoring.
*   **SHAP:** For model explainability.
*   **PostgreSQL:** Primary relational database.

### Frontend
*   **React (Vite):** Fast, modern UI framework.
*   **Tailwind CSS:** Utility-first styling with a custom vibrant design system.
*   **PWA (Progressive Web App):** Service workers for offline capability.
*   **Recharts & Leaflet:** For data visualization and maps.

### Infrastructure
*   **Docker & Docker Compose:** Containerization.
*   **Kubernetes:** Orchestration for production.
*   **GitHub Actions:** CI/CD pipelines.
*   **Prometheus:** Metrics and monitoring.

---

## 🏗 Architecture

The system follows a microservices pattern:

```mermaid
graph TD
    Client[Field Agent App / Bank Dashboard] -->|HTTP/REST| API[API Service (FastAPI)]
    API -->|Read/Write| DB[(PostgreSQL)]
    API -->|Enqueue Tasks| Redis[(Redis)]
    
    Worker[Celery Worker] -->|Poll Tasks| Redis
    Worker -->|Fetch Data| MockAgri[Mock Agri Stack]
    Worker -->|Predict| ML[ML Model Service]
    Worker -->|Save Results| DB
    
    ML -->|Load Model| ModelArtifact[model.joblib]
```

---

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Node.js v18+ (for local frontend dev)
*   Python 3.9+ (for local backend dev)

### Option 1: Run with Docker (Recommended)

This will start the entire stack: API, Frontend, Dashboard, Database, Redis, and Worker.

```bash
# 1. Clone the repository
git clone https://github.com/youruser/farmer-credit-score-engine.git
cd farmer-credit-score-engine

# 2. Setup environment variables
cp .env.example .env

# 3. Start services
docker-compose up -d

# 4. Access the applications
# Frontend (Field Agent): http://localhost:3000
# Dashboard (Bank Admin): http://localhost:3001
# API Documentation:      http://localhost:8000/docs
```

### Option 2: Run Locally (No Docker)

See [RUN_WITHOUT_DOCKER.md](RUN_WITHOUT_DOCKER.md) for detailed instructions on running services individually.

---

## 📡 API Documentation

The API is fully documented using OpenAPI/Swagger. Once running, visit `http://localhost:8000/docs`.

**Key Endpoints:**
*   `POST /auth/login`: Authenticate users.
*   `POST /farmers`: Onboard a new farmer.
*   `GET /farmers/{id}/score`: Get the latest credit score.
*   `POST /loan/quote`: Calculate loan eligibility.

---

## 📊 ML Model & Scoring

We use a **RandomForest Regressor** trained on synthetic data that mimics real-world agricultural patterns.

**Top Features Influencing Score:**
1.  **NDVI Mean (15%):** Average crop health over the season.
2.  **Credit History (15%):** Past defaults or successful repayments.
3.  **Yield Estimation (12%):** Historical productivity of the land.
4.  **Transaction Frequency (10%):** Digital financial activity.

**Transparency:**
We use **SHAP (SHapley Additive exPlanations)** to decompose the score. If a farmer gets a score of 60, the system might say:
*   *Base Score: 50*
*   *+15 due to excellent crop health*
*   *-5 due to high rainfall deficit*

---

## 🗺 Roadmap

*   **Phase 1 (Current):** Pilot with synthetic data, basic ML model, and offline PWA.
*   **Phase 2:** Integrate real satellite data (Sentinel-2) and live weather APIs.
*   **Phase 3:** Multi-language support for field agents and SMS alerts for farmers.
*   **Phase 4:** Blockchain integration for immutable credit history records.

---

## 🤝 Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the farmers of India.**
