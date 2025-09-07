import streamlit as st
import streamlit_survey as ss
from connection.firestore import FireStore
from utils import is_strong_password


def run_rental_survey():
    st.title("Let's find your perfect rental in London 🏠")

    # Get URL parameters
    params = st.query_params.to_dict()

    # Debug prints to see what parameters we're getting
    print("Debug: Received rental parameters:", params)

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

            renting_alone = survey.number_input(
                "Are many people are renting?",
                value=1
            )
            num_bedrooms = st.number_input(
                "Minimum number of bedrooms",
                min_value=0,
                max_value=10,
                value=1
            )
            max_monthly_rent = st.slider(
                "Maximum monthly rent in £ (for all the renters in total)",
                min_value=500,
                max_value=5000,
                value=1500
            )
            property_type = survey.multiselect(
                "Type of property, select all that applies:",
                options=["House", "Flat", "Studio"],
                default="Flat"
            )

            user_preference = st.text_area(
                "Tell us about all the desired features & requirements of your dream rental?",
                value="Bright light with good storage, modern kitchen"
            )
            st.session_state.form_results.update({
                "renting_alone": renting_alone,
                "num_bedrooms": num_bedrooms,
                "max_monthly_rent": max_monthly_rent,
                "property_type": property_type,
                "user_preference": user_preference,
            })

        elif pages.current == 1:
            st.markdown("<h3>Location preference & your lifestyle</h3>", unsafe_allow_html=True)
            timeline = survey.selectbox(
                "When do you want to move in?",
                options=["ASAP", "within 1 month", "within 3 months", "within 6 months", "flexible"],
                placeholder="within 3 months"
            )

            preferred_location = st.text_input(
                'Do you have a preferred location? i.e. "West London" or "Finsbury Park"',
                value="Hampstead Heath"
            )
            workplace_location = st.text_input(
                "What's the postcode of a place you frequently commute to, such as your workplace/school?",
                value="Liverpool Street"
            )
            has_child = survey.selectbox(
                "👶🏼Do you have children?",
                options=["Yes", "No"],
                index=1
            )
            school_types = []
            if has_child == "Yes":
                school_types = survey.multiselect(
                    "🏫Are you looking for nursery/schools? If yes, select all that applies.",
                    options=["Nursery", "Primary", "Secondary"],
                )

            has_pet = survey.selectbox(
                "Do you have pets? 🐾",
                options=["Yes", "No"],
                index=1
            )

            furnishing_preference = survey.selectbox(
                "Do you prefer furnished or unfurnished?",
                options=["Furnished", "Unfurnished", "Part furnished", "No preference"],
                index=3
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
                "furnishing_preference": furnishing_preference,
                "hobbies": hobbies,
            })
        elif pages.current == 2:
            st.markdown("<h3>Complete the registration</h3>", unsafe_allow_html=True)
            first_name = st.text_input(
                "What's your first name?",
            )
            email = st.text_input(
                "Enter your email",
            )
            password = st.text_input("Enter your password", type="password")
            password_confirm = st.text_input("Re-enter your password", type="password")
            password_error = None
            if password or password_confirm:
                if password != password_confirm:
                    password_error = "Passwords do not match."
                elif not is_strong_password(password):
                    password_error = "Password must be at least 8 characters."
            if password_error:
                st.error(password_error)

            st.session_state.form_results.update({
                "email": email,
                "first_name": first_name,
                "password": password if not password_error else None
            })