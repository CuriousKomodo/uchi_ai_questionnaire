import time
from typing import Dict, Tuple
import streamlit as st
import streamlit_survey as ss
from langchain_core.messages import AIMessage, HumanMessage
from langchain_agents import get_response
from customer_info_processor import CustomerInfoProcessor, CustomerInfo
from gif_service import GifService
from connection.firestore import FireStore
from urllib.parse import parse_qs

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "customer_info" not in st.session_state:
        st.session_state.customer_info = {}
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False
    if "wants_to_signup" not in st.session_state:
        st.session_state.wants_to_signup = False
    if "info_processor" not in st.session_state:
        st.session_state.info_processor = CustomerInfoProcessor()
    if "gif_service" not in st.session_state:
        st.session_state.gif_service = GifService()
    if "show_survey" not in st.session_state:
        st.session_state.show_survey = False
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "form_results" not in st.session_state:
        st.session_state.form_results = {}

def run_chat():
    st.title("🤖Chat with Uchi AI")

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("Hello! I am an <b>AI assistant</b> for Uchi. It's my first day at work", unsafe_allow_html=True)
        time.sleep(1)
        try:
            gif_url = st.session_state.gif_service.get_greeting_gif()
            st.image(gif_url, width=400)
        except Exception as e:
            print(str(e))

        time.sleep(1)
        with st.chat_message("assistant"):
            st.markdown("What is your name ? And what brought you here today? 😊")

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
            st.markdown(prompt)

        with st.chat_message("assistant"):
            new_state = get_response(
                messages=st.session_state.messages,
                customer_info=st.session_state.customer_info
            )
            response = new_state["response"]
            st.session_state.messages.append({"role": "assistant", "content": response})
            if not st.session_state.wants_to_signup:
                st.session_state.wants_to_signup = new_state.get("wants_to_signup", False)
            st.markdown(response)

        # If user wants to sign up, process the conversation and show signup button
        if st.session_state.wants_to_signup:
            try:
                # Show celebration GIF
                with st.chat_message("assistant"):
                    try:
                        gif_url = st.session_state.gif_service.get_celebration_gif()
                        st.image(gif_url, width=400)
                        st.markdown("🎉 Great! Let's get you registered!")
                    except Exception as e:
                        print(f"Error displaying GIF: {str(e)}")

                # Convert messages to BaseMessage format
                base_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        base_messages.append(HumanMessage(content=msg["content"]))
                    else:
                        base_messages.append(AIMessage(content=msg["content"]))

                try:
                    customer_info = st.session_state.info_processor.process_conversation(base_messages)
                    st.session_state.customer_info = customer_info
                    if st.button("Register with us ✨", type="primary"):
                        st.session_state.show_survey = True
                        st.rerun()
                except Exception as e:
                    st.error(f"Error processing customer information: {str(e)}")

            except Exception as e:
                st.error(f"Error processing customer information: {str(e)}")

def run_survey():
    st.title("Let's find your dream home in London 🏠")
    
    survey = ss.StreamlitSurvey("User Preference")
    pages = survey.pages(3, progress_bar=True, on_submit=lambda: on_submit())

    def on_submit():
        st.success("Submitted!")
        st.write("<h3>We will start the search. Stay tuned! ✨</h3>", unsafe_allow_html=True)
        firestore = FireStore(credential_info=st.secrets["firestore_credentials"])
        firestore.insert_submission(st.session_state.form_results)
        st.session_state.form_submitted = True

    # Helper function to get customer info value with default
    def get_customer_info(key, default=None):
        if key == "property_type":
            mapping = {
                "both": ["House", "Apartment"],
                "apartment": ["Apartment"],
                "house": ["House"]
            }
            return mapping.get(key.lower())
        return st.session_state.customer_info.get(key, default)

    with pages:
        if pages.current == 0:
            st.markdown("<h3>Tell us what you are looking for?</h3>", unsafe_allow_html=True)
            if get_customer_info("first_name"):
                st.markdown(f"Hello {get_customer_info('first_name')}, let's get you signed up.")

            motivation = st.text_area(
                "What is your reason for buying a property?",
                value=get_customer_info("motivation", "")
            )
            num_bedrooms = st.number_input(
                "Minimum number of bedrooms", 
                min_value=0, 
                max_value=10, 
                value=int(get_customer_info("number_of_rooms", 2))
            )
            max_price = st.slider(
                "Maximum price (in £1000)", 
                min_value=100, 
                max_value=1000, 
                value=int(get_customer_info("maximum_budget", 500))
            )
            property_type = survey.multiselect(
                "Type of property, select all that applies:", 
                options=["House", "Apartment"],
                default=[get_customer_info("property_type", "Apartment")]
            )
            min_lease_year = None
            if "Apartment" in property_type:
                min_lease_year = st.slider(
                    "Minimum lease year for the apartment",
                    min_value=0,
                    max_value=900,
                    value=150
                )
            user_preference = st.text_area(
                "Tell us about the desired features of your dream home?", 
                value=get_customer_info("additional_notes", "Bright light with good storage")
            )
            st.session_state.form_results.update({
                "motivation": motivation,
                "num_bedrooms": num_bedrooms,
                "max_price": max_price,
                "property_type": property_type,
                "min_lease_year": min_lease_year,
                "user_preference": user_preference,
            })

        elif pages.current == 1:
            st.markdown("<h3>Location preference & your lifestyle</h3>", unsafe_allow_html=True)
            timeline = st.text_input(
                'When do you expect to complete the buy? i.e. the exchange date?',
                value=get_customer_info("timeline", "within 12 months")
            )
            preferred_location = st.text_input(
                'Do you have a preferred location? i.e. "West London" or "Finsbury Park"',
                value=get_customer_info("preferred_location", "London")
            )
            workplace_location = st.text_input(
                "What's the postcode of a place you frequently commute to, such as your workplace/school?",
                value=get_customer_info("preferred_location", ""),
            )
            has_child = survey.selectbox(
                "Do you have children or plan to have a child soon?", 
                options=["Yes", "No"],
                index=0 if get_customer_info("is_buying_alone", False) else 1
            )
            has_pet = survey.selectbox(
                "Do you have pets or plan to have a pet soon?", 
                options=["Yes", "No"],
                index=1
            )
            hobbies = st.text_area(
                "What are your hobbies?", 
                value="E.g. I like to play tennis"
            )
            st.session_state.form_results.update({
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
                value=get_customer_info("first_name", "")
            )
            email = st.text_input(
                "Enter your email",
                value=get_customer_info("email", "")
            )
            password = st.text_input("Enter your password")
            st.session_state.form_results.update({
                "email": email,
                "first_name": first_name,
                "password": password
            })

def main():
    initialize_session_state()
    
    if st.session_state.show_survey:
        run_survey()
    else:
        run_chat()

if __name__ == "__main__":
    main()
