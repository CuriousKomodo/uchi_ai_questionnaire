import streamlit_survey as ss
import streamlit as st

from connection.firestore import FireStore

# https://olivierbinette-streamlit-surv-docs-streamlit-survey-docs-hu1jf8.streamlit.app/Advanced_Usage
survey = ss.StreamlitSurvey("User Preference")
st.header("Tell us about your preference 🏠")

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

if "form_results" not in st.session_state:
    st.session_state.form_results = {}

def on_submit():
    st.success("Submitted!")
    st.write("<h3>We will start the search. Stay tuned! ✨</h3>", unsafe_allow_html=True)
    firestore = FireStore()
    firestore.insert_submission(st.session_state.form_results)

survey = ss.StreamlitSurvey("Progress Bar Example")
pages = survey.pages(4, progress_bar=True, on_submit=lambda: on_submit())


with pages:
    if pages.current == 0:
        st.markdown("<h3>Section 1 - Basic filter</h3>", unsafe_allow_html=True)
        num_bedrooms = st.number_input("Minimum number of bedrooms", min_value=0, max_value=10, value=1)
        max_price = st.slider("Maximum price (in £1000)", min_value=100, max_value=1000, value=50)
        property_type = survey.multiselect("Type of property, select all that applies:", options=["House", "Apartment"])
        min_price = st.slider("Minimum lease year", min_value=0, max_value=900, value=150)
        preferred_locations = survey.multiselect("Preferred locations in London, select all that applies", options=["London"])  # TODO: maybe a dropdown is better
        st.session_state.form_results.update({
            "num_bedrooms": num_bedrooms,
            "max_price": max_price,
            "property_type": property_type,
            "min_price": min_price,
            "preferred_location": preferred_locations
        })
    elif pages.current == 1:
        st.markdown("<h3>Section 2 - Other filters</h3>", unsafe_allow_html=True)
        build_era = survey.multiselect("Era of build, select all that applies:", options=["Victorian/Georgian", "Modern"])
        refurbishment_needed = survey.multiselect("Maximum level of refurbishment required", options=["Low/Medium", "High"])
        has_private_parking = survey.checkbox("Has private parking")
        has_garden = survey.checkbox("Has garden")
        has_balcony = survey.checkbox("Has balcony")
        exclude_commercial_site = survey.checkbox("Exclude property above commercial sites")
        exclude_high_rise = survey.checkbox("Exclude property inside a high-rise building")
        min_energy_rating = st.select_slider("Requirement on minimum energy rating:", options=["A", "B", "C", "D", "E", "No requirement"])
        st.session_state.form_results.update({
            "build_era": build_era,
            "refurbishment_needed": refurbishment_needed,
            "has_private_parking": has_private_parking,
            "has_garden": has_garden,
            "has_balcony": has_balcony,
            "exclude_commercial_site": exclude_commercial_site,
            "exclude_high_rise": exclude_high_rise,
            "min_energy_rating": min_energy_rating
        })
        #crime rate/demographic,

    elif pages.current == 2:
        st.markdown("<h3>Section 3 - Tell us about your life</h3>", unsafe_allow_html=True)
        workplace_location = st.text_input("Where is your workplace? Leave blank if not applicable.", value="None")
        has_child = survey.selectbox("Do you have children or plan to have a child soon?", options=["Yes", "No"])
        has_pet = survey.selectbox("Do you have pets or plan to have a pet soon?", options=["Yes", "No"])
        hobbies = st.text_area("What are your hobbies?", value="I like to play tennis")
        st.session_state.form_results.update({
            "workplace_location": workplace_location,
            "has_child": has_child,
            "has_pet": has_pet,
            "hobbies": hobbies,
        })
    elif pages.current == 3:
        first_name = st.text_input("What's your first name?")
        email = st.text_input("Your email address for our weekly recommendation")
        st.session_state.form_results.update({"email": email, "first_name": first_name})
