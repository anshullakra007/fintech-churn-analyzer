# 💸 FinTech Customer Churn & Impact Analyzer

Welcome to the **FinTech Customer Churn & Impact Analyzer**, a full-stack, AI-powered analytics dashboard built entirely in Python. This project bridges the gap between raw data and actionable operational intelligence by analyzing the direct impact of technical payment gateway failures on customer retention and revenue.

---

## 🚀 Live Demo
**[Access the Live Streamlit Dashboard on Render](https://fintech-churn-analyzer.onrender.com)**

---

## 🧠 Project Overview

This repository contains the end-to-end pipeline for the project, broken down into four major phases:

1. **Synthetic Data Engineering (`ml/generate_and_train.py`)**
   - Injected a custom metric (`failed_transactions_last_30_days`) into standard banking churn datasets to mirror the effects of a faulty payment reconciliation system.
   - Trained a Random Forest classifier to predict churn probabilities.
2. **Exploratory Data Analysis (`ml/eda.py`)**
   - Extracted hard business metrics proving the massive cost of technical debt (e.g., ~$314M in Revenue at Risk).
   - Generated professional Seaborn visualizations correlating transaction failures with churn rates (`ml/eda_visualizations/`).
3. **The Business Dashboard (`app.py`)**
   - Built a lightweight, interactive Streamlit frontend natively in Python.
   - Features real-time KPI generation, interactive Plotly distribution charts, and a dynamic table surfacing the Top 50 'High-Risk' customers for collections intervention.
4. **AI-Driven Root Cause Analysis**
   - Integrated the **Google Gemini SDK**.
   - The dashboard dynamically captures the active KPI metrics and prompts the Gemini LLM to generate instant Executive Summaries and Operational Recommendations simulating live alerts.
5. **Phase 5: AI-Powered Customer Recovery & ROI Simulator (New! ✨)**
   - **Intervention ROI Simulator**: A sidebar module allowing operations to calculate the exact Net Revenue saved against the cost of a retention offer.
   - **Targeted Outreach**: Select any customer from the High-Risk table to instantly generate a hyper-personalized, context-aware retention email using Gemini tailored to that specific customer's exact balance, age, and failure frequency.

---

## 🛠️ Technology Stack

- **Data Pipeline**: Python, Pandas, Numpy, Scikit-learn, Joblib
- **Exploratory Analysis**: Seaborn, Matplotlib
- **Frontend Dashboard**: Streamlit, Plotly
- **AI Integration**: Google Generative AI (Gemini 1.5 Flash API)
- **Deployment**: Render Web Services

---

## 💻 Local Setup Instructions

If you wish to run the dashboard locally on your machine, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/anshullakra007/fintech-churn-analyzer.git
cd fintech-churn-analyzer
```

### 2. Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the AI (Gemini API)
To enable the AI Root Cause Analysis feature, you must provide your own Gemini API key.
```bash
export GEMINI_API_KEY="your-google-gemini-api-key"
```

### 5. Run the Application
```bash
streamlit run app.py
```
The application will instantly launch in your default web browser at `http://localhost:8501`.

---

*Architected and developed with autonomous agentic CI/CD deployment pipelines.*
