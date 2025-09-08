import time
import uuid
import streamlit as st

from customer_info_processor import CustomerInfoProcessor, CustomerInfo
from gif_service import GifService
from connection.firestore import FireStore
from submission_processor import RecommendationProcessor
from ui_components.buyer_chat import run_chat
from ui_components.buyer_survey import run_buyer_survey
from utils import is_strong_password


def initialize_session_state():
    """Initialize session state variables."""
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
        print(st.session_state["session_id"])
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "customer_info" not in st.session_state:
        st.session_state.customer_info = {}
    if "wants_to_signup" not in st.session_state:
        st.session_state.wants_to_signup = False
    if "info_processor" not in st.session_state:
        st.session_state.info_processor = CustomerInfoProcessor()
    if "gif_service" not in st.session_state:
        st.session_state.gif_service = GifService()
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "form_results" not in st.session_state:
        st.session_state.form_results = {}
    if "submission_processor" not in st.session_state:
        st.session_state.recommendation_processor = RecommendationProcessor()



def main():
    # Hide sidebar completely with CSS
    st.markdown(
        """
        <style>
            .css-1d391kg {display: none;}
            .st-emotion-cache-1d391kg {display: none;}
            .css-1cypcdb {display: none;}
            .st-emotion-cache-1cypcdb {display: none;}
            section[data-testid="stSidebar"] {display: none;}
            .stSidebar {display: none;}
            div[data-testid="collapsedControl"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    initialize_session_state()
    
    # Check if we should show the form or chat
    show_form = st.query_params.get("form", "") == "true"
    
    if show_form:
        run_buyer_survey()
    else:
        run_chat()


if __name__ == "__main__":
    main()
