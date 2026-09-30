# YATZIV Decision — Premium V3

Streamlit MVP with a clean game-like mission-control flow.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud
Upload `app.py` and `requirements.txt` to the repository root and set Main file path to `app.py`.

## Data upload schema
Required columns: `חודש`, `הכנסות`, `הוצאות`
Recommended: `קניות`, `שכר`, `סוציאליות`

The built-in hummus-shop dataset is a manually normalized case study from the supplied 2022 P&L and is intended for product testing, not statutory reporting.
