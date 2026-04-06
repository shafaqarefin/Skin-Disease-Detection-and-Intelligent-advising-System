import streamlit as st
import requests
import io
from PIL import Image
import json
import time

# Page configuration
st.set_page_config(
    page_title="Skin Disease Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Result card styling */
    .result-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    
    /* Title styling */
    h1 {
        color: white;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Disease name styling */
    .disease-name {
        font-size: 28px;
        font-weight: bold;
        color: #764ba2;
        margin: 10px 0;
    }
    
    .confidence-score {
        font-size: 20px;
        color: #667eea;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "diagnosed" not in st.session_state:
    st.session_state.diagnosed = False
    st.session_state.disease = None
    st.session_state.confidence = 0
    st.session_state.analysis_data = None
    st.session_state.chat_history = []

# Sidebar configuration
st.sidebar.title("⚙️ Settings")
backend_url = st.sidebar.text_input(
    "Backend API URL",
    value="http://localhost:8000",
    help="Enter the URL of your FastAPI backend"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📋 How to use:
1. Upload a skin image
2. Wait for the API to analyze it
3. Get instant recommendations
4. Ask follow-up questions
""")

# Main title
st.markdown("<h1>🏥 Skin Disease Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; font-size: 16px;'>AI-Powered Skin Analysis with Real-Time Results</p>", unsafe_allow_html=True)

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📸 Upload Image")
    uploaded_file = st.file_uploader(
        "Choose a skin image...",
        type=["jpg", "jpeg", "png", "bmp"],
        help="Upload a clear image of the affected skin area"
    )

    if uploaded_file is not None:
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True, caption="Uploaded Image")

        # Show image info
        st.info(
            f"📁 File: {uploaded_file.name} | Size: {uploaded_file.size / 1024:.1f} KB")

with col2:
    st.markdown("### 🔄 Analysis Results")

    if uploaded_file is not None:
        # Analyze button
        if st.button("🔍 Analyze Image", use_container_width=True, type="primary"):
            with st.spinner("🔄 Analyzing image..."):
                time.sleep(0.3)
                try:
                    # Prepare the file for API
                    files = {
                        'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

                    # Call backend API
                    response = requests.post(
                        f"{backend_url}/analyze_skin",
                        files=files,
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()

                        # Store in session state
                        st.session_state.diagnosed = True
                        st.session_state.disease = data.get('disease')
                        st.session_state.confidence = data.get('confidence')
                        st.session_state.analysis_data = data
                        st.session_state.chat_history = []

                        # Display results with nice formatting
                        st.success("✅ Analysis Complete!")

                        # Disease section
                        st.markdown("<div class='result-card'>",
                                    unsafe_allow_html=True)
                        col_res1, col_res2 = st.columns(2)

                        with col_res1:
                            st.markdown(
                                f"<div class='disease-name'>{data.get('disease', 'Unknown')}</div>", unsafe_allow_html=True)

                        with col_res2:
                            confidence = data.get('confidence', 0) * 100
                            st.markdown(
                                f"<div class='confidence-score'>Confidence: {confidence:.1f}%</div>", unsafe_allow_html=True)

                        # Confidence bar
                        st.progress(min(data.get('confidence', 0), 1.0))

                        st.markdown("</div>", unsafe_allow_html=True)

                        # Recommendations
                        st.markdown("#### 💊 Recommendations")
                        st.info(data.get('recommendations',
                                'No recommendations available'))

                        # Next Steps
                        st.markdown("#### 📋 Next Steps")
                        st.warning(
                            data.get('next_steps', 'No next steps available'))

                        # Tips
                        st.markdown("#### 💡 Tips")
                        st.success(data.get('tips', 'No tips available'))

                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        st.error(response.json().get(
                            'detail', 'Unknown error occurred'))

                except requests.exceptions.ConnectionError:
                    st.error(f"❌ Cannot connect to backend at {backend_url}")
                    st.info("Make sure your FastAPI backend is running!")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timeout. The analysis took too long.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.info("👆 Upload an image to get started!")

# Chat section - displayed below if diagnosed
if st.session_state.diagnosed:
    st.divider()
    st.markdown("<h3 style='color: white; text-align: center;'>💬 Ask Questions About Your Diagnosis</h3>",
                unsafe_allow_html=True)

    col_chat1, col_chat2 = st.columns([3, 1])

    with col_chat1:
        user_question = st.text_input(
            "Ask anything about your condition",
            placeholder="E.g., How long does this take to heal?",
            label_visibility="collapsed"
        )

    with col_chat2:
        send_clicked = st.button(
            "Send", use_container_width=True, type="primary")

    if user_question and send_clicked:
        with st.spinner("🤔 Thinking..."):
            time.sleep(0.3)
            try:
                response = requests.post(
                    f"{backend_url}/chat",
                    json={
                        "disease": st.session_state.disease,
                        "confidence": st.session_state.confidence,
                        "message": user_question
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    chat_response = response.json().get("response")
                    st.session_state.chat_history.append({
                        "q": user_question,
                        "a": chat_response
                    })
                    st.rerun()
                else:
                    st.error("❌ Failed to get response")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Display chat history
    if st.session_state.chat_history:
        st.markdown("<h4 style='color: white;'>📖 Conversation</h4>",
                    unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            st.info(f"**Q:** {msg['q']}")
            st.success(f"**A:** {msg['a']}")

    # New analysis button
    if st.button("🔄 New Analysis", use_container_width=True):
        st.session_state.diagnosed = False
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.markdown("<hr><p style='text-align: center; color: white; font-size: 12px;'>© 2024 Skin Disease Analyzer. All rights reserved.</p>", unsafe_allow_html=True)
