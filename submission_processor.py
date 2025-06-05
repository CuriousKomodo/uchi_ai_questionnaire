import streamlit as st
import requests
import threading
from datetime import datetime
from typing import Dict, Any, List


class RecommendationProcessor:
    def __init__(self):
        self.url = st.secrets.get("CREATE_RECOMMENDATION_URL")
    
    def submit_and_wait(self, submission_data: Dict[str, Any]):
        """
        Submit data to external API and display results when ready
        """
        # Show loading state
        with st.spinner("🔄 Processing your submission... This may take up to 10 seconds."):
            placeholder = st.empty()
            
            # Make the request in a separate thread
            result_container = {"result": None, "error": None}
            
            def make_request():
                try:
                    payload = {
                        "data": submission_data,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    response = requests.post(
                        self.url,
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=30
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
            
            # Display results
            placeholder.empty()
            
            if result_container["error"]:
                st.error(f"❌ Error: {result_container['error']}")
            else:
                self._display_results(result_container.get("result"))
    
    def _display_results(self, data: List[Dict[str, Any]]):
        """Display the API results"""
        st.success("✅ Processing completed!")
        
        # Handle the matched properties data structure
        if isinstance(data, list) and len(data) > 0:
            # This is the matched properties format
            properties = data
            num_properties = len(properties)
            
            # Show summary
            st.subheader(f"🎉 Great news! We found {num_properties} properties that match your criteria")
            
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
            st.markdown("<h5> Your personal recommendations will be shown on the dashboard.")

        # Link button to dashboard
        dashboard_url = st.secrets.get("DASHBOARD_URL", "https://your-dashboard.com")
        st.link_button(
            "🏠 Find out more",
            url=dashboard_url,
            type="primary",
            help="View detailed property information and schedule viewings"
        )