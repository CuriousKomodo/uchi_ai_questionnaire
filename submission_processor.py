import streamlit as st
import requests
import threading
from datetime import datetime
from typing import Dict, Any, List

from gif_service import GifService


class RecommendationProcessor:
    def __init__(self):
        self.url = st.secrets.get("CREATE_RECOMMENDATION_URL")
        self.git_service = GifService()
    
    def submit_and_wait(self, submission_id: str):
        """
        Submit data to external API and display results when ready
        """
        # Create placeholders for loading and results
        loading_placeholder = st.empty()
        results_placeholder = st.empty()
        
        # Show loading content
        with loading_placeholder.container():
            st.write("<h3>We are searching based on your preference ✨</h3>", unsafe_allow_html=True)
            st.info("🔄 This may take up to 10 seconds.")
            gif_url = self.git_service.get_working_hard_gif()
            st.image(gif_url, width=400)
        
        # Make the request in a separate thread
        result_container = {"result": None, "error": None}
        
        def make_request():
            try:
                payload = {
                    "submission_id": submission_id,
                    "days_added": 30,
                }
                
                response = requests.post(
                    self.url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result_container["result"] = response.json().get("matched_properties")
                else:
                    result_container["error"] = f"API error: {response.status_code}"
                    
            except Exception as e:
                result_container["error"] = str(e)
        
        # Start the request
        thread = threading.Thread(target=make_request)
        thread.start()
        thread.join()  # Wait for completion
        
        # Clear the loading content (including GIF)
        loading_placeholder.empty()
        
        # Display results
        with results_placeholder.container():
            if result_container["error"]:
                st.markdown(f"Looks like the search might take a little bit longer - we will send an email when it's ready!")
            else:
                self._display_results(result_container.get("result"))
    
    def _display_results(self, data: List[Dict[str, Any]]):
        """Display the API results"""
        
        # Handle the matched properties data structure
        if isinstance(data, list) and len(data) > 0:
            # This is the matched properties format
            properties = data
            num_properties = len(properties)
            
            # Show summary
            st.markdown(f"<h5>🎉Great news! We found {num_properties} properties that match your criteria</h5>", unsafe_allow_html=True)
            
            # Get the first (best) property for the matched criteria display
            best_property = properties[0]
            matched_criteria = best_property.get("matched_criteria", [])
            
            if matched_criteria:
                st.write("**Your requirements that were matched:**")

                for criterion in matched_criteria:
                    st.markdown(f"✅ {criterion}")
                
                # Show match percentage if available
                match_percentage = best_property.get("prop_property_criteria_matched", 0)
                if match_percentage:
                    st.write(f"**Match score:** {match_percentage:.1%}")
            
            # Add some spacing
            st.write("")

        else:
            st.markdown("<h5> We haven't found any suitable properties that got listed in the last 7 days. "
                        "But we will let you know as soon as possible. Please keep an eye for our weekly mailing list.📧 </h5>", unsafe_allow_html=True)

        # Link button to dashboard
        dashboard_url = st.secrets.get("DASHBOARD_URL", "https://your-dashboard.com")
        st.link_button(
            "🏠 Find out more",
            url=dashboard_url,
            type="primary",
            help="View detailed property information and schedule viewings"
        )