import time
import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_agents import get_response
from urllib.parse import parse_qs, urlencode
from langfuse import get_client, observe

langfuse_client = get_client()

def run_chat():
    st.title("🤖Chat with Uchi AI - For Buyers")

    if not st.session_state.get("session_id"):
        st.session_state["session_id"] = str(uuid.uuid4())

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(
                "Hello! I am an <b>AI assistant</b> for Uchi. I'm here to help you find your perfect home to buy! ",
                unsafe_allow_html=True)
        time.sleep(1)
        try:
            gif_url = st.session_state.gif_service.get_greeting_gif()
            st.image(gif_url, width=400)
        except Exception as e:
            print(str(e))

        time.sleep(1)
        greeting = "I heard you are looking for a home to buy and would love to know more. First, what is your name ? 😊"
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
            langfuse_client.flush()
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
                        "max_price": str(customer_info.get("maximum_budget", 50)),
                        "chat_session_id": st.session_state.session_id,
                    }

                    # Create the survey URL - redirect to same page with form parameter
                    base_url = st.secrets["BASE_URL"]
                    survey_url = f"{base_url}/for-buy?form=true&{urlencode(params)}"

                    # Show the register button with the survey URL
                    st.link_button("Finish your registration with us! ✨", url=survey_url, type="primary")
                except Exception as e:
                    st.error(f"Error processing customer information: {str(e)}")
                    # Create fallback URL for buyer form
                    base_url = st.secrets["BASE_URL"]
                    fallback_url = f"{base_url}/for-buy?form=true"
                    st.link_button("Complete your registration with us. Sorry our GPT agent forgot the details 😞", url=fallback_url, type="primary")

            except Exception as e:
                st.error(f"Error processing customer information: {str(e)}")
