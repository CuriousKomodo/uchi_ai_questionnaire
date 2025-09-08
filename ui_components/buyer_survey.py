import streamlit as st
import streamlit_survey as ss
from connection.firestore import FireStore
from utils import is_strong_password


def run_buyer_survey():
    st.title("Let's find your dream home to buy in London 🏠")

    # Get URL parameters
    params = st.query_params.to_dict()

    # Debug prints to see what parameters we're getting
    print("Debug: Received parameters:", params)

    survey = ss.StreamlitSurvey("User Preference")
    pages = survey.pages(3, progress_bar=True, on_submit=lambda: on_submit())

    def on_submit():
        # Save to Firestore
        firestore = FireStore(credential_info=st.secrets["firestore_credentials"])
        submission_data = st.session_state.form_results.copy()
        submission_data["listing_type"] = "buy"
        submission_data["session_id"] = get_param("chat_session_id")
        submission_id = firestore.insert_submission(submission_data)

        # Show immediate feedback
        st.success("Submitted!")

        st.session_state.recommendation_processor.submit_and_wait(submission_id)

    # Helper function to get customer info value with default
    def get_param(key, default=None):
        value = params.get(key)
        if value is None or value == "None":
            return default
        if key == "property_type":
            mapping = {
                "both": ["House", "Apartment"],
                "apartment": ["Apartment"],
                "house": ["House"]
            }
            return mapping.get(value.lower(), [])
        if key == "has_child":
            key_words = ["baby", "child", "son", "daughter", "family", "kid"]
            if any([kw in str(value).lower() for kw in key_words]):
                return True
        return value

    with pages:
        if pages.current == 0:
            st.markdown("<h3>Tell us what you are looking for?</h3>", unsafe_allow_html=True)
            if get_param("name"):
                st.markdown(f"Hello {get_param('name')}, let's get you signed up.")

            motivation = st.text_area(
                "What is your reason for buying a property?",
                value=get_param("motivation", "")
            )
            buying_alone = survey.selectbox(
                "Are you buying alone?",
                options=["Yes", "No"],
                placeholder="Yes" if get_param("is_buying_alone", True) else "No"
            )
            num_bedrooms = st.number_input(
                "Minimum number of bedrooms",
                min_value=0,
                max_value=10,
                value=int(get_param("num_bedrooms", 2))
            )
            max_price = st.slider(
                "Maximum price (in £1000)",
                min_value=100,
                max_value=1000,
                value=int(get_param("max_price", 500))
            )
            property_type = survey.multiselect(
                "Type of property, select all that applies:",
                options=["House", "Apartment"],
                default=get_param("property_type", "Apartment")
            )
            min_lease_year = None
            if "Apartment" in property_type:
                min_lease_year = st.slider(
                    "Minimum lease year",
                    min_value=0,
                    max_value=900,
                    value=150
                )
            user_preference = st.text_area(
                "Tell us about all the desired features & requirements of your dream home?",
                value=get_param("additional_notes", "Bright light with good storage")
            )
            st.session_state.form_results.update({
                "motivation": motivation,
                "buying_alone": buying_alone,
                "num_bedrooms": num_bedrooms,
                "max_price": max_price,
                "property_type": property_type,
                "min_lease_year": min_lease_year,
                "user_preference": user_preference,
            })

        elif pages.current == 1:
            st.markdown("<h3>Location preference & your lifestyle</h3>", unsafe_allow_html=True)
            timeline = survey.selectbox(
                "When do you expect to complete the buy? i.e. the exchange date?",
                options=["in 6 months", "in 12 months", "not sure"],
                placeholder=get_param("timeline", "in 12 months")
            )

            preferred_location = st.text_input(
                'Do you have a preferred location? i.e. "West London" or "Finsbury Park"',
                value=get_param("preferred_location", "London")
            )
            workplace_location = st.text_input(
                "What's the postcode of a place you frequently commute to, such as your workplace/school?",
                value=get_param("preferred_location", ""),
            )
            has_child = survey.selectbox(
                "👶🏼Do you have children or plan to have a child soon?",
                options=["Yes", "No"],
                index=0 if get_param("has_child") == "true" else 1
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
                index=1
            )
            hobbies = st.text_area(
                "What are your hobbies? 🎾🛍️",
                value="E.g. I like to play tennis"
            )
            st.session_state.form_results.update({
                "school_types": school_types,
                "preferred_location": preferred_location,
                "timeline": timeline,
                "workplace_location": workplace_location,
                "has_child": has_child,
                "has_pet": has_pet,
                "hobbies": hobbies,
            })
        elif pages.current == 2:
            st.markdown("<h3>Complete the registration</h3>", unsafe_allow_html=True)
            first_name = st.text_input(
                "What's your first name?",
                value=get_param("name", "")
            )
            email = st.text_input(
                "Enter your email",
                value=get_param("email", "")
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
