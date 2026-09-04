from django import forms


class LoanEligibilityForm(forms.Form):
    Gender = forms.ChoiceField(choices=[("Male", "Male"), ("Female", "Female")])
    Married = forms.ChoiceField(choices=[("Yes", "Yes"), ("No", "No")])
    Dependents = forms.IntegerField(min_value=0, max_value=3)
    Education = forms.ChoiceField(
        choices=[("Graduate", "Graduate"), ("Not Graduate", "Not Graduate")]
    )
    Self_Employed = forms.ChoiceField(choices=[("Yes", "Yes"), ("No", "No")])
    ApplicantIncome = forms.FloatField(min_value=0)
    CoapplicantIncome = forms.FloatField(min_value=0)
    LoanAmount = forms.FloatField(min_value=0)
    Loan_Amount_Term = forms.FloatField(min_value=0)
    Credit_History = forms.ChoiceField(choices=[("1.0", "Good"), ("0.0", "Bad")])
    Property_Area = forms.ChoiceField(
        choices=[("Urban", "Urban"), ("Semiurban", "Semiurban"), ("Rural", "Rural")]
    )
