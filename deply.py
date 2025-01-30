import streamlit as st
import pandas as pd
import pickle
import boto3
import io
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Initialize AWS S3 client
s3_client = boto3.client('s3')

# Define your S3 bucket name and model file names
bucket_name = 'your-s3-bucket-name'
random_forest_model_key = 'models/random_forest_model.pkl'
logistic_model_key = 'models/regression_model.pkl'

# Function to load model from S3
def load_model_from_s3(bucket, key):
    try:
        # Retrieve the model file from S3
        s3_object = s3_client.get_object(Bucket=bucket, Key=key)
        model_data = s3_object['Body'].read()
        model = pickle.load(io.BytesIO(model_data))
        return model
    except Exception as e:
        st.error(f"Error loading model from S3: {e}")
        raise

# Load models from S3
try:
    random_forest_model = load_model_from_s3(bucket_name, random_forest_model_key)
    logistic_model = load_model_from_s3(bucket_name, logistic_model_key)
except Exception as e:
    st.error(f"Error loading models: {e}")
    raise

# Set page configuration
st.set_page_config(
    page_title="Bank Stability Dashboard",
    page_icon="📊",
    layout="wide"
)

# Styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8f9fa;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.15);
    }
    .stMetric {
        color: #007bff;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .sidebar-header {
        font-size: 22px;
        font-weight: bold;
        color: #007bff;
        margin-bottom: 10px;
    }
    .sidebar-label {
        font-size: 20px;
        color: #333333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.title("Bank Stability Dashboard")
st.markdown("Track and assess your bank's stability using advanced metrics.")

# Sidebar for inputs
st.sidebar.markdown('<div class="sidebar-header">🔧 Input Metrics</div>', unsafe_allow_html=True)

bank_name = st.sidebar.text_input("Bank Name", "Your Bank")

capital_adequacy = st.sidebar.slider("Capital Adequacy Ratio (%)", min_value=0.0, max_value=25.0, value=10.0, step=0.1)
non_performing_loans = st.sidebar.slider("Non-Performing Loans Ratio (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.1)
loan_to_deposit = st.sidebar.slider("Loan-to-Deposit Ratio (%)", min_value=50.0, max_value=120.0, value=85.0, step=0.1)
net_interest_margin = st.sidebar.slider("Net Interest Margin (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.1)

# Button to calculate stability
if st.sidebar.button("Calculate Stability"):
    try:
        # Ensure inputs are valid
        if capital_adequacy is None or non_performing_loans is None or loan_to_deposit is None or net_interest_margin is None:
            st.error("Please make sure all inputs are filled out.")
        else:
            # Calculate Stability Score
            stability_score = (
                (capital_adequacy / 8.0) * 25 +
                (1 - non_performing_loans / 15.0) * 25 +
                (1 - abs(loan_to_deposit - 80) / 40) * 25 +
                (net_interest_margin / 5.0) * 25
            )
            status = "Stable" if stability_score >= 75 else ("At Risk" if stability_score >= 50 else "Unstable")

            # Metrics Summary
            st.subheader("Metrics Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Capital Adequacy", f"{capital_adequacy:.1f}%", ">= 8% ideal")
            col2.metric("Non-Performing Loans", f"{non_performing_loans:.1f}%", "Lower is better")
            col3.metric("Loan-to-Deposit", f"{loan_to_deposit:.1f}%", "75%-85% ideal")
            col4.metric("Net Interest Margin", f"{net_interest_margin:.1f}%", "Higher is better")

            # Recommendations
            st.subheader("Recommendations")
            if stability_score < 50:
                st.error(f"{bank_name} is in a critical condition. Immediate intervention is required.")
            elif stability_score < 75:
                st.warning(f"{bank_name} shows moderate risk. Focus on improving key metrics.")
            else:
                st.success(f"{bank_name} is performing well. Keep up the good work!")

            # Display Stability Score
            st.markdown(f"*Overall Stability Score*: {stability_score:.2f}")
            st.markdown(f"*Status*: {status}")
    except ValueError as e:
        st.error(f"Error calculating stability: {e}")
        st.error("Please check the input values.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

# Footer
st.markdown("---")
st.caption("Bank stability analysis powered by Streamlit.")
