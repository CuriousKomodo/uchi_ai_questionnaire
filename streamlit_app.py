import streamlit as st


def main():
    st.set_page_config(
        page_title="Uchi AI - Find Your Perfect Home", 
        page_icon="🏠",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Hide sidebar completely with CSS
    st.markdown(
        """
        <style>
            .css-1d391kg {display: none;}
            .st-emotion-cache-1d391kg {display: none;}
            .css-1cypcdb {display: none;}
            .st-emotion-cache-1cypcdb {display: none;}
            section[data-testid="stSidebar"] {display: none;}
            .stSidebar {display: none;}
            div[data-testid="collapsedControl"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Main landing page
    st.title("🏠 Welcome to Uchi AI")
    st.markdown("### Find your perfect home in London with AI assistance")
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Uchi AI** helps you discover your ideal home in London. Whether you're looking to buy or rent, 
        our AI assistant will guide you through the process and match you with properties that fit your needs.
        
        Choose your journey below:
        """)
        
        # Action buttons
        col_buy, col_rent = st.columns(2)
        
        with col_buy:
            st.markdown("#### 🏡 **For Buyers**")
            st.markdown("Chat with our AI to find homes to purchase")
            if st.button("Start Buying Journey", key="buyer", type="primary", use_container_width=True):
                st.switch_page("pages/for-buy.py")
        
        with col_rent:
            st.markdown("#### 🏠 **For Renters**") 
            st.markdown("Find rental properties that match your lifestyle")
            if st.button("Start Rental Search", key="renter", type="secondary", use_container_width=True):
                st.switch_page("pages/for-rent.py")
    
    with col2:
        # Add some visual element or leave space for future content
        st.markdown("### 🤖 AI-Powered")
        st.markdown("""
        - Personalized recommendations
        - Smart property matching
        - Expert guidance
        - London market insights
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Powered by Uchi AI - Making home finding simple and intelligent</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
