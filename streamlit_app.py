import streamlit_survey as ss
import streamlit as st

from connection.firestore import FireStore

# https://olivierbinette-streamlit-surv-docs-streamlit-survey-docs-hu1jf8.streamlit.app/Advanced_Usage
survey = ss.StreamlitSurvey("User Preference")
st.header("Let's find your dream home in London 🏠")

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

if "form_results" not in st.session_state:
    st.session_state.form_results = {}

def on_submit():
    st.success("Submitted!")
    st.write("<h3>We will start the search. Stay tuned! ✨</h3>", unsafe_allow_html=True)
    firestore = FireStore(credential_info=st.secrets["firestore_credentials"])
    firestore.insert_submission(st.session_state.form_results)

survey = ss.StreamlitSurvey("Progress Bar Example")
pages = survey.pages(3, progress_bar=True, on_submit=lambda: on_submit())


with pages:
    if pages.current == 0:
        st.markdown("<h3>Getting started</h3>", unsafe_allow_html=True)
        num_bedrooms = st.number_input("Minimum number of bedrooms", min_value=0, max_value=10, value=1)
        max_price = st.slider("Maximum price (in £1000)", min_value=100, max_value=1000, value=50)
        property_type = survey.multiselect("Type of property, select all that applies:", options=["House", "Apartment"])
        min_lease_year = st.slider("Minimum lease year", min_value=0, max_value=900, value=150)
        user_preference = st.text_area("Tell us about the desired features of your dream home?", value="Bright light with good storage")
        # preferred_locations = survey.multiselect("Preferred locations in London, select all that applies", options=["London"])  # TODO: maybe a dropdown is better
        st.session_state.form_results.update({
            "num_bedrooms": num_bedrooms,
            "max_price": max_price,
            "property_type": property_type,
            "min_lease_year": min_lease_year,
            "user_preference": user_preference
            # "preferred_location": preferred_locations
        })

    elif pages.current == 1:
        st.markdown("<h3>Tell us about your life</h3>", unsafe_allow_html=True)
        workplace_location = st.text_input("Where is the postcode of your workplace? Leave blank if not applicable.", value="")
        has_child = survey.selectbox("Do you have children or plan to have a child soon?", options=["Yes", "No"])
        has_pet = survey.selectbox("Do you have pets or plan to have a pet soon?", options=["Yes", "No"])
        hobbies = st.text_area("What are your hobbies?", value="E.g. I like to play tennis")
        st.session_state.form_results.update({
            "workplace_location": workplace_location,
            "has_child": has_child,
            "has_pet": has_pet,
            "hobbies": hobbies,
        })
    elif pages.current == 2:
        st.markdown("<h3>Complete the registration</h3>", unsafe_allow_html=True)
        first_name = st.text_input("What's your first name?")
        email = st.text_input("Enter your email")
        password = st.text_input("Enter your password")
        st.session_state.form_results.update({
            "email": email,
            "first_name": first_name,
            "password": password
        })


# if __name__ == '__main__':
#     import sys
#     from streamlit.web import cli as stcli
#
#     # For local debug
#     sys.argv = ["streamlit", "run", "streamlit_app.py"]
#     sys.exit(stcli.main())