import json
from pathlib import Path

import joblib
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Dependencies: pip install Django joblib pandas scikit-learn


MODEL_PATH = Path(__file__).resolve().parent / "ml_model" / "loan_pipeline.pkl"
try:
    pipeline = joblib.load(MODEL_PATH)
    model_load_error = None
except Exception as exc:
    pipeline = None
    model_load_error = exc

FEATURE_COLUMNS = [
    "Gender",
    "Married",
    "Dependents",
    "Education",
    "Self_Employed",
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_History",
    "Property_Area",
]


def index(request):
    return render(request, "predictor/index.html")


def _error(message, status):
    return JsonResponse({"error": message}, status=status)


def _validate_payload(payload):
    required = set(FEATURE_COLUMNS)
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    allowed = {
        "Gender": {"Male", "Female"},
        "Married": {"Yes", "No"},
        "Education": {"Graduate", "Not Graduate"},
        "Self_Employed": {"Yes", "No"},
        "Property_Area": {"Urban", "Semiurban", "Rural"},
    }
    for field, choices in allowed.items():
        if payload[field] not in choices:
            raise ValueError(f"Invalid value for {field}")

    try:
        dependents = int(payload["Dependents"])
        numeric_values = {
            field: float(payload[field])
            for field in (
                "ApplicantIncome",
                "CoapplicantIncome",
                "LoanAmount",
                "Loan_Amount_Term",
                "Credit_History",
            )
        }
    except (TypeError, ValueError):
        raise ValueError("Numeric fields must contain valid numbers") from None

    if not 0 <= dependents <= 3:
        raise ValueError("Dependents must be between 0 and 3")
    if numeric_values["Credit_History"] not in {0.0, 1.0}:
        raise ValueError("Credit_History must be 0.0 or 1.0")
    if any(value < 0 for value in numeric_values.values() if value != numeric_values["Credit_History"]):
        raise ValueError("Income, loan, and term values cannot be negative")

    return {
        "Gender": payload["Gender"],
        "Married": payload["Married"],
        "Dependents": dependents,
        "Education": payload["Education"],
        "Self_Employed": payload["Self_Employed"],
        **numeric_values,
        "Property_Area": payload["Property_Area"],
    }


@csrf_exempt
def predict_api(request):
    if request.method != "POST":
        return _error("Only POST requests are supported.", 405)

    try:
        payload = json.loads(request.body)
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object")
        values = _validate_payload(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _error("Request body must contain valid JSON.", 400)
    except ValueError as exc:
        return _error(str(exc), 400)

    if pipeline is None:
        return _error("The loan prediction model is unavailable.", 500)

    try:
        frame = pd.DataFrame([values], columns=FEATURE_COLUMNS)
        probabilities = pipeline.predict_proba(frame)
        classes = list(getattr(pipeline, "classes_", []))
        eligible_index = classes.index("Eligible") if "Eligible" in classes else classes.index(1)
        eligible_probability = float(probabilities[0][eligible_index])
        if eligible_probability >= 0.65:
            decision = "Approved"
            message = "Your application shows a strong likelihood of eligibility."
        elif eligible_probability <= 0.35:
            decision = "Rejected"
            message = "The application does not currently meet the model's eligibility threshold."
        else:
            decision = "Under Review"
            message = "Your application falls into the review range and may need further assessment."
        confidence = round(max(eligible_probability, 1 - eligible_probability) * 100, 1)
        return JsonResponse({
            "decision": decision,
            "confidence": confidence,
            "probability": round(eligible_probability, 4),
            "message": message,
        })
    except Exception:
        return _error("We could not evaluate this application right now.", 500)
