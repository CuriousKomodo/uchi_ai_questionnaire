import os
from typing import TypedDict, Annotated, Sequence, Dict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json

from connection.azure_client import AzureClient

# Load environment variables
load_dotenv()

os.environ.pop("SSL_CERT_FILE", None)

client = AzureClient()

# Define the state schema
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The conversation history"]
    customer_info: Annotated[dict, "Customer information extracted from conversation"]
    wants_to_signup: Annotated[bool, "Would the customer like to signup?"]


def property_agent(state: AgentState) -> Dict:
    """Agent that handles property search conversations."""
    messages = state["messages"]
    # Create the system prompt
    system_prompt = """
    You are an AI asistant for a startup called Uchi. You are here to helping customers find properties to buy. 
    Your role is to:
    1. Engage in natural conversation about property search
    2. Extract and track key information about the customer's needs
    3. Provide helpful information about the Uchi
    4. Detect if the customer wants to sign up
    5. If they wish to sign up, summarise all the key information in natural language to the customer and ask for their email
    6. Detect if something is wrong, e.g. user appears to be confused or asked to speak with a human, kindly ask if they like to email team@uchiai.co.uk
    7. Do not display the collected information as a dictionary inside the response. 
    
    Track the following information from the conversation:
    - motivation: str, why they want to buy
    - property_type: List[str], such as "apartment" and "house"
    - is_first_time_buyer: bool, whether they're first-time buyers
    - is_buying_alone: bool, whether they're buying alone or with someone
    - maximum_budget: int, in thousands (GBP)
    - num_bedrooms: int, minimum number of bedrooms
    - timeline: str, when are they expecting to buy the property, choose from "in 6 months", "in 12 months", "not sure"
    - preferred_location: str
    
    Feel free to add more fields if you get other information from the customer.
    Make sure they are all extracted before you ask the customer if they like to sign up with an email. 
    
    **Requirements on your tone**
    Keep responses friendly and conversational. Ask one question at a time. Greet the customer with their first name is given. 
    Avoid sales language and be helpful.
    
    **Product information about Uchi AI**
    Our mission is to help people find their dream homes stress-free. Zen mode. 
    Customer will be asked in 5 seconds on the chat to provide further details about their requirements & their lifestyle. 
    Once they sign up:
    - Receive LLM-powered personalised recommendation based on their needs
    - Comprehensive information about the property & neighborhood, such as local crime rates, schools, and commute times.
    - Auto-draft enquiry to real-estate agents 
    - AI consultation regarding financial advices & property valuation
    Our service is free. 
    
    **Structure of your response**
    Format your response as a JSON object with two fields:
    - "response": your conversational response to the user, keep "response" within 150 words, use line breaks like \n or bullet points  
    - "extracted_info": all the information you've extracted so far, including from the latest message
    - "wants_to_signup": boolean, whether the customer showed interest to sign up
    """
    
    # Convert messages to the format expected by the LLM
    formatted_messages = [
        {"role": "system", "content": system_prompt}
    ]
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        formatted_messages.append({"role": role, "content": msg["content"]})
    
    # Generate response
    response = client.get_chat_completion(messages)
    try:
        # Parse the response as JSON
        parsed_response = json.loads(response['content'])
        return {
            "response": parsed_response["response"].replace("\n", "<br>"),
            "customer_info": parsed_response["extracted_info"],
            "wants_to_signup": parsed_response["wants_to_signup"],
        }
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "response": response.content,
            "customer_info": state.get("customer_info", {})
        }

def get_response(messages: Sequence[BaseMessage], customer_info: Dict = {}) -> Dict:
    """Get a response from the agent for the given messages."""
    state = AgentState(
        messages=messages,
        customer_info=customer_info
    )
    return property_agent(state)


# Have another agent to extract all the fields from the conversation into a structure format
if __name__ == "__main__":
    # Example usage
    messages = [
        HumanMessage(content="I am looking for a property"),
        AIMessage(content="Hello! I'm Uchi AI, your personal property search assistant. What's your first name?"),
        HumanMessage(content="My name is John and I am buying for the first time"),
    ]
    result = get_response(messages)
    print("Response:", result["response"])
    print("Extracted Info:", result["customer_info"])