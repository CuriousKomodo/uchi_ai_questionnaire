import time
import uuid
from datetime import datetime

import streamlit as st
import streamlit_survey as ss
from connection.firestore import FireStore
from submission_processor import RecommendationProcessor
from utils import is_strong_password, convert_date_to_datetime


def initialize_session_state():
    """Initialize session state variables."""
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    if "form_results" not in st.session_state:
        st.session_state.form_results = {}
    if "recommendation_processor" not in st.session_state:
        st.session_state.recommendation_processor = RecommendationProcessor()


SUPPORTED_METADATA_TAGS = [
    "has private parking",
    "has garden",
    "open kitchen",
    "modern interior",
    "modern kitchen",
    "modern bathroom",
    "close to public transport",
    "near nursery school",
    "near primary school",
    "near secondary school",
    "near supermarket",
    "near park",
    "low crime neighbourhood",
    "high income neighbourhood",
    "smoker friendly",
    "pet friendly"
]

def run_rental_survey():
    st.title("Let's find your perfect rental in London 🏠")
    
    survey = ss.StreamlitSurvey("Rental Preference")
    pages = survey.pages(3, progress_bar=True, on_submit=lambda: on_submit())

    def on_submit():
        # Save to Firestore
        firestore = FireStore(credential_info=st.secrets["firestore_credentials"])
        submission_data = st.session_state.form_results.copy()
        submission_data["listing_type"] = "rent"
        submission_id = firestore.insert_submission(submission_data)
        
        # Show immediate feedback
        st.success("Submitted!")

        st.session_state.recommendation_processor.submit_and_wait(submission_id)

    with pages:
        if pages.current == 0:
            st.markdown("<h3>Tell us what you are looking for?</h3>", unsafe_allow_html=True)
            num_bedrooms = st.number_input(
                "Number of beds",
                min_value=0, 
                max_value=10, 
                value=1
            )
            max_monthly_rent = st.number_input(
                "Maximum monthly rent in £ (excluding bills)",
                min_value=0,
                max_value=5000, 
                value=2000
            )
            let_type = survey.selectbox(
                "Let length",
                options=["Long term", "Short term"],
                index=0  # "No preference"
            )
            furnishing_preference = survey.selectbox(
                "Do you prefer furnished or unfurnished?",
                options=["Furnished", "Part Furnished", "Unfurnished", "No preference"],
                index=2  # "No preference"
            )
            timeline = st.date_input(
                "When do you want to move in?",
                datetime.now().date()
            )
            property_type = survey.multiselect(
                "Type of property, select all that applies:",
                options=["House", "Apartment", "Room"],
                default=["Apartment"]
            )
            st.session_state.form_results.update({
                "num_bedrooms": num_bedrooms,
                "max_monthly_rent": max_monthly_rent,
                "let_type": let_type,
                "property_type": property_type,
                "timeline": convert_date_to_datetime(timeline),
                "furnishing_preference": furnishing_preference,
            })

        elif pages.current == 1:
            st.markdown("<h3>Location preference & your lifestyle</h3>", unsafe_allow_html=True)

            preferred_location = st.text_input(
                'Do you have preferred locations? Separate multiple locations by ",". E.g. West London,Finsbury Park',
                value="London"
            )
            workplace_location = st.text_input(
                "What's the postcode of a place you frequently commute to, such as your workplace/school?",
                value=""
            )
            user_preference_tags = survey.multiselect(
                "Quick select ⚡ all the preferences that applies",
                options=SUPPORTED_METADATA_TAGS,
                placeholder="Select from our most common preferences :)"
            )

            if user_preference_tags:
                badges = " ".join([
                    f'<span style="background-color:#eef2ff;color:#1f3a8a;padding:4px 8px;border-radius:999px;margin-right:6px;margin-bottom:6px;display:inline-block;font-size:12px;">{t}</span>'
                    for t in user_preference_tags
                ])
                st.markdown(badges, unsafe_allow_html=True)

            user_preference = st.text_area(
                "Tell us about any additional features & requirements of your dream rental?",
                value="Bright light with good storage, modern kitchen"
            )

            has_child = survey.selectbox(
                "👶🏼Do you have children or plan to have a child soon?",
                options=["Yes", "No"],
                index=1  # "No"
            )
            school_types = []
            if has_child == "Yes":
                # Are you looking for schools?
                school_types = survey.multiselect(
                    "🏫Are you looking for nursery/schools? If yes, select all that applies.",
                    options=["Nursery", "Primary", "Secondary"],
                )

            has_pet = survey.selectbox(
                "Do you have pets or plan to have a pet soon? 🐾",
                options=["Yes", "No"],
                index=1  # "No"
            )
            
            hobbies = st.text_area(
                "What are your hobbies? 🎾🛍️",
                value="E.g. I like to play tennis"
            )
            st.session_state.form_results.update({
                "school_types": school_types,
                "user_preference": user_preference,
                "preferred_location": preferred_location,
                "workplace_location": workplace_location,
                "user_preference_tags": user_preference_tags,
                "has_child": has_child,
                "has_pet": has_pet,
                "hobbies": hobbies,
            })
        elif pages.current == 2:
            st.markdown("<h3>Complete the registration</h3>", unsafe_allow_html=True)
            first_name = st.text_input(
                "What's your first name?",
                value=""
            )
            email = st.text_input(
                "Enter your email",
                value=""
            )
            password = st.text_input("Enter your password", type="password")
            password_confirm = st.text_input("Re-enter your password", type="password")
            password_error = None
            if password or password_confirm:
                if password != password_confirm:
                    password_error = "Passwords do not match."
                elif not is_strong_password(password):
                    password_error = "Password must be at least 8 characters, include upper and lower case letters, a number."
            if password_error:
                st.error(password_error)
            
            st.session_state.form_results.update({
                "email": email,
                "first_name": first_name,
                "password": password if not password_error else None
            })


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
    run_rental_survey()


if __name__ == "__main__":
    main()
