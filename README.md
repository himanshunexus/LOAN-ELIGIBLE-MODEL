# Loan Eligibility Predictor

A Django web app that predicts whether a loan applicant is eligible using a trained machine learning model.

---

## Overview

Users fill out a loan form. The app returns one of three decisions:

- Approved
- Rejected
- Under Review

The model is a Random Forest classifier trained on the Kaggle Loan Prediction dataset. It runs entirely inside a scikit-learn Pipeline saved as a single file.

---

## Tech Stack

- Django
- Python
- scikit-learn
- pandas
- Vanilla JavaScript
- Custom CSS


## Folder Structure

loan_project/
├── predictor/
│   ├── ml_model/
│   │   └── loan_pipeline.pkl
│   ├── templates/
│   │   └── predictor/
│   │       └── index.html
│   ├── forms.py
│   ├── urls.py
│   └── views.py
├── loan_project/
│   ├── settings.py
│   └── urls.py
├── train_pipeline.py
└── manage.py


## Setup

1. Clone the repo.

2. Create and activate a virtual environment.

3. Install dependencies.

   pip install django pandas scikit-learn joblib numpy

4. Train the model.

   Place loan_data.csv in the root folder and run:

   python train_pipeline.py

5. Copy the model into the Django app.

   mkdir -p predictor/ml_model
   cp loan_pipeline.pkl predictor/ml_model/

6. Run migrations.

   python manage.py migrate

7. Start the server.

   python manage.py runserver

   Visit http://127.0.0.1:8000


## How It Works

Training happens offline in train_pipeline.py. The Django app only loads the saved model and makes predictions.

The API uses probability thresholds:

- probability >= 0.65   -> Approved
- probability <= 0.35   -> Rejected
- 0.35 < probability < 0.65 -> Under Review


## API

POST /api/predict/

Request body:

{
  "Gender": "Male",
  "Married": "Yes",
  "Dependents": 0,
  "Education": "Graduate",
  "Self_Employed": "No",
  "ApplicantIncome": 5000,
  "CoapplicantIncome": 2000,
  "LoanAmount": 150,
  "Loan_Amount_Term": 360,
  "Credit_History": 1.0,
  "Property_Area": "Urban"
}

Response:

{
  "decision": "Approved",
  "confidence": 92.4,
  "probability": 0.924,
  "message": "High confidence approval."
}


## Model Performance

- Accuracy: 82.9%
- F1 Score: 0.859
- Recall (Not Eligible): 65.8%
- Recall (Eligible): 90.6%


## Notes

- Do not train the model inside Django views.
- The model expects the exact column order and names used during training.
- Frontend uses fetch API and plain CSS.
