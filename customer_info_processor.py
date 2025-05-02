from typing import TypedDict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.environ['SSL_CERT_FILE'] = "/etc/ssl/cert.pem"

# Define the structured schema for customer information
class CustomerInfo(TypedDict):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    motivation: str
    is_first_time_buyer: bool
    is_buying_alone: bool
    preferred_location: str
    maximum_budget: int
    property_type: str
    number_of_rooms: int
    timeline: str
    additional_notes: Optional[str]

class CustomerInfoProcessor:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4")
        
    def process_conversation(self, messages: List[BaseMessage]) -> CustomerInfo:
        """Process the conversation and extract structured customer information."""
        system_prompt = """
        You are an information extraction agent for Uchi AI. Your task is to extract structured customer information from the conversation.
        
        Extract the following information and format it as a JSON object:
        {
            "first_name": str,  # Customer's first name
            "last_name": str,   # Customer's last name
            "email": str,       # Customer's email address
            "motivation": str,  # Why they want to buy a property
            "is_first_time_buyer": bool,  # Whether they're first-time buyers
            "is_buying_alone": bool,      # Whether they're buying alone or with someone
            "preferred_location": str,     # Their preferred location/area
            "maximum_budget": int,           # Their maximum budget in thousands GBP
            "property_type": str,          # Are they looking for "apartment", a "house" or "both"?
            "number_of_rooms": int,          # Minimum number of rooms 
            "timeline": str,             # When are they looking to buy?
            "additional_notes": str        # Any additional requirements about the property
        }
        
        Rules:
        1. If any information is missing, use null for that field
        2. Ensure all required fields are present
        3. Format dates and numbers consistently
        4. Clean and normalize text data
        5. Validate email format if present
        """
        
        # Convert messages to the format expected by the LLM
        formatted_messages = [
            {"role": "system", "content": system_prompt}
        ]
        for msg in messages:
            role = "user" if msg.type == "human" else "assistant"
            formatted_messages.append({"role": role, "content": msg.content})
        
        # Generate response
        response = self.llm.invoke(formatted_messages)
        
        try:
            # Parse the response as JSON
            customer_info = json.loads(response.content)
            return CustomerInfo(**customer_info)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse customer information from conversation due to {str(e)}")

    def generate_signup_url(self, customer_info: CustomerInfo) -> str:
        """Generate a signup URL with the customer information as parameters."""
        base_url = os.getenv("UCHI_SIGNUP_URL")
        params = {
            "motivation": customer_info["motivation"],
            "is_first_time_buyer": str(customer_info["is_first_time_buyer"]).lower(),
            "is_buying_alone": str(customer_info["is_buying_alone"]).lower(),
            "preferred_location": customer_info["preferred_location"],
            "maximum_budget": int(customer_info["maximum_budget"]),
            "property_type": customer_info["property_type"],
            "num_bedrooms": int(customer_info["number_of_rooms"]),
            "timeline": customer_info["timeline"],
            "additional_notes": customer_info["additional_notes"]
        }

        if customer_info.get("additional_notes"):
            params["additional_notes"] = customer_info["additional_notes"]
        
        # Create URL with parameters
        param_strings = [f"{k}={v}" for k, v in params.items()]
        return f"{base_url}?{'&'.join(param_strings)}" 