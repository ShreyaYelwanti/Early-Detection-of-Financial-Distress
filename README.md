# Early Detection of Financial Distress Using Machine Learning

## Project Overview

This project explores the use of Machine Learning techniques for the early detection of financial distress in companies.

It analyzes financial indicators and applies multiple machine learning algorithms to identify patterns associated with potential financial distress. Different models are implemented and compared to study their predictive performance.

The project also includes an interactive Streamlit-based demonstration application that allows users to enter financial information and explore the prediction workflow.

**Note:** The Streamlit application is an experimental demonstration and is not intended to provide actual financial assessments or support real-world financial decisions.

## Project Structure

```text
Early-Detection-of-Financial-Distress/
│
├── bankruptcy_demo/       # Interactive Streamlit demonstration
│   ├── app.py
│   ├── pages/
│   ├── assets/
│   └── requirements.txt
│
├── experiments/           # Machine learning experiments
│   ├── Step1.ipynb
│   ├── Step2.ipynb
│   ├── ...
│   ├── Step8.ipynb
│   ├── models/
│   ├── data/
│   └── results/
│
├── .gitignore
└── README.md
```

## Project Components

### 1. Machine Learning Experiments

- Data preprocessing and preparation.
- Implementation of multiple machine learning algorithms.
- Model training and evaluation.
- Comparison of different models based on their performance.
- Storage of trained models and experimental results.

### 2. Interactive Demonstration Application

A Streamlit-based application that provides an interactive interface where users can:

- Enter financial information.
- Explore the financial distress prediction workflow.
- View model comparisons and related results.

The application serves as a demonstration of the developed approach.

## Technologies Used

- Python
- Machine Learning
- Pandas and NumPy
- Scikit-learn
- XGBoost
- Streamlit
- Jupyter Notebook

## Running the Interactive Demo

### Step 1: Navigate to the demo directory

```bash
cd bankruptcy_demo
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the Streamlit application

```bash
streamlit run app.py
```

The application will open in your default web browser.

## Research and Experiments

The `experiments/` directory contains the Jupyter notebooks, datasets, trained models, and results used throughout the machine learning workflow.

These experiments demonstrate the implementation and comparison of different machine learning approaches for financial distress detection.

## Repository Contents

This repository contains the machine learning experimental workflow, model comparisons, research-related work, and an interactive demonstration application developed as part of the project.

