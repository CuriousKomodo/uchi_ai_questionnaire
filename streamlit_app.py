import time
from typing import Dict, Tuple
import streamlit as st
import streamlit_survey as ss
from langchain_core.messages import AIMessage, HumanMessage
from langchain_agents import get_response
from customer_info_processor import CustomerInfoProcessor, CustomerInfo
from gif_service import GifService
from connection.firestore import FireStore
from submission_processor import RecommendationProcessor
from urllib.parse import parse_qs, urlencode
from utils import is_strong_password


def initialize_session_state():
    """Initialize session state variables."""
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

def run_chat():
    st.title("🤖Chat with Uchi AI")

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("Hello! I am an <b>AI assistant</b> for Uchi.", unsafe_allow_html=True)
        time.sleep(1)
        try:
            gif_url = st.session_state.gif_service.get_greeting_gif()
            st.image(gif_url, width=400)
        except Exception as e:
            print(str(e))

        time.sleep(1)
        greeting = "What is your name ? And what brought you here today? 😊"
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Hi, how can I help you today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            if "@" in str(prompt) or "sign up" in str(prompt):
                st.session_state.wants_to_signup = True
            st.markdown(prompt, unsafe_allow_html=True)

        with st.chat_message("assistant"):
            new_state = get_response(
                messages=st.session_state.messages,
                customer_info=st.session_state.customer_info,
                wants_to_signup=st.session_state.wants_to_signup,
            )
            response = new_state["response"]
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.customer_info = new_state["customer_info"]
            if not st.session_state.wants_to_signup:
                st.session_state.wants_to_signup = new_state.get("wants_to_signup", False)
            st.markdown(response, unsafe_allow_html=True)

        # If user wants to sign up, process the conversation and show signup button
        if st.session_state.wants_to_signup:
            try:
                # Show celebration GIF
                with st.chat_message("assistant"):
                    try:
                        gif_url = st.session_state.gif_service.get_celebration_gif()
                        st.image(gif_url, width=400)
                        st.markdown("Great! Let's finish your registration, give me 2 seconds...")
                    except Exception as e:
                        print(f"Error displaying GIF: {str(e)}")

                # Convert messages to BaseMessage format
                base_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        base_messages.append(HumanMessage(content=msg["content"]))
                    else:
                        base_messages.append(AIMessage(content=msg["content"]))

                # Process the conversation
                try:
                    customer_info = st.session_state.info_processor.process_conversation(base_messages)
                    st.session_state.customer_info = customer_info
                    
                    # Generate URL parameters for the survey
                    params = {
                        "name": customer_info.get("first_name", ""),
                        "email": customer_info.get("email", ""),
                        "has_child": str(customer_info.get("has_children", False)).lower(),
                        "has_pet": "false",
                        "preferred_location": customer_info.get("preferred_location", ""),
                        "additional_notes": customer_info.get("additional_notes", ""),
                        "motivation": customer_info.get("motivation", ""),
                        "timeline": customer_info.get("timeline", ""),
                        "property_type": customer_info.get("property_type", "apartment"),
                        "num_bedrooms": str(customer_info.get("number_of_rooms", 1)),
                        "max_price": str(customer_info.get("maximum_budget", 50))
                    }
                    
                    # Create the survey URL
                    base_url = st.secrets["BASE_URL"]
                    survey_url = f"{base_url}?page=preferences&{urlencode(params)}"
                    
                    # Show the register button with the survey URL
                    st.link_button("Finish your registration with us! ✨", url=survey_url, type="primary")
                except Exception as e:
                    st.error(f"Error processing customer information: {str(e)}")
                    st.link_button("Complete your registration with us. Sorry 😞", url=survey_url, type="primary")

            except Exception as e:
                st.error(f"Error processing customer information: {str(e)}")

def run_survey():
    st.title("Let's find your dream home in London 🏠")
    
    # Get URL parameters
    params = st.query_params.to_dict()
    
    # Debug prints to see what parameters we're getting
    print("Debug: Received parameters:", params)
    
    survey = ss.StreamlitSurvey("User Preference")
    pages = survey.pages(3, progress_bar=True, on_submit=lambda: on_submit())

    def on_submit():
        # Save to Firestore
        firestore = FireStore(credential_info=st.secrets["firestore_credentials"])
        submission_id = firestore.insert_submission(st.session_state.form_results)
        
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

def main():
    initialize_session_state()
    
    # Get the current page from query parameters
    current_page = st.query_params.get("page", "")
    
    if current_page == "preferences":
        run_survey()
    else:
        run_chat()

if __name__ == "__main__":
    main()
