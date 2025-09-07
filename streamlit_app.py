import time
import uuid
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

from ui_components.buyer_survey import run_buyer_survey
from ui_components.renter_survey import run_rental_survey
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


def run_chat():
    st.title("🤖Chat with Uchi AI")

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("Hello! I am an <b>AI assistant</b> for Uchi. ", unsafe_allow_html=True)
        time.sleep(1)
        try:
            gif_url = st.session_state.gif_service.get_greeting_gif()
            st.image(gif_url, width=400)
        except Exception as e:
            print(str(e))

        time.sleep(1)
        greeting = "I heard you are looking for a home and would love to know more. First, what is your name ? 😊"
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
                session_id=st.session_state.session_id,
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
                    survey_url = f"{base_url}?page=for-buyer&{urlencode(params)}"
                    
                    # Show the register button with the survey URL
                    st.link_button("Finish your registration with us! ✨", url=survey_url, type="primary")
                except Exception as e:
                    st.error(f"Error processing customer information: {str(e)}")
                    # Create fallback URL for buyer form
                    base_url = st.secrets["BASE_URL"]
                    fallback_url = f"{base_url}?page=for-buyer"
                    st.link_button("Complete your registration with us. Sorry 😞", url=fallback_url, type="primary")

            except Exception as e:
                st.error(f"Error processing customer information: {str(e)}")


def main():
    initialize_session_state()
    
    # Get the current page from query parameters
    current_page = st.query_params.get("page", "")

    # Access rental form via: yourapp.com?page=for-rent
    # Access buyer form via: yourapp.com?page=for-buyer
    if current_page == "for-rent":
        run_rental_survey()
    elif current_page == "for-buyer":
        run_buyer_survey()
    else:
        run_chat()

if __name__ == "__main__":
    main()
