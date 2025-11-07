import streamlit as st
from db_functions import *


# Page setup
st.set_page_config(layout="wide")  # FULL width layout

# Reduce sidebar width & tighten spacing
st.markdown(
    """
    <style>
        /* Reduce sidebar width */
        [data-testid="stSidebar"] {
            width: 200px;
        }

        /* Reduce gap between sidebar and main section */
        [data-testid="stSidebar"], .css-1d391kg {
            padding-top: 0px !important;
        }

        /* Remove excessive top padding in main area */
        .block-container {
            padding-top: 1rem; 
            padding-left: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================================================
# Sidebar
st.sidebar.title("Inventory Management Dashboard")
option = st.sidebar.radio("Select Options", ['Basic Information', 'Operational Tasks'])

# Main Title
st.title("📊 Inventory & Supply Chain Dashboard")

# Database connection
db = connected_to_db()
cursor = db.cursor(dictionary=True)

#--------------------- Basic Information Page -----------------------
if option == "Basic Information":
    st.subheader("📌 Key Business Metrics")

    # Fetch KPI dictionary (any length)
    basic_info = get_basic_info(cursor)

    metric_names = list(basic_info.keys())
    total_metrics = len(metric_names)

    # Display metrics in rows of 3
    for i in range(0, total_metrics, 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < total_metrics:
                label = metric_names[i + j]
                value = basic_info[label]
                cols[j].metric(label, value)

    st.markdown("---")  # Nice divider
