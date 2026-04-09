import streamlit as st
import requests
import io
from PIL import Image
import json
import time
from datetime import datetime

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
    
    /* Global font improvements */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-rendering: optimizeLegibility;
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
        font-weight: 900;
        letter-spacing: 1px;
    }
    
    h2, h3, h4, h5, h6 {
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    
    /* Disease name styling */
    .disease-name {
        font-size: 32px;
        font-weight: 900;
        color: #764ba2;
        margin: 10px 0;
        letter-spacing: 1px;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .confidence-score {
        font-size: 22px;
        color: #667eea;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    
    /* Chat message styling */
    .chat-question {
        font-size: 16px;
        font-weight: 700;
        color: #1f1f1f;
        line-height: 1.6;
        letter-spacing: 0.3px;
        background: #e3f2fd;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #667eea;
    }
    
    .chat-answer {
        font-size: 15px;
        font-weight: 600;
        color: #1f1f1f;
        line-height: 1.7;
        letter-spacing: 0.2px;
        background: #f1f8e9;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #4caf50;
    }
    
    /* Sidebar history items */
    .history-item {
        background: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        cursor: pointer;
        font-weight: 600;
        border-left: 4px solid #667eea;
        transition: all 0.3s;
    }
    
    .history-item:hover {
        background: #e0e0e0;
        transform: translateX(5px);
    }
    
    .history-item-active {
        background: #667eea;
        color: white;
        border-left: 4px solid #764ba2;
    }
    
    /* Text inputs and buttons */
    input, button, textarea {
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    
    p, span, div {
        letter-spacing: 0.3px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.authenticated = False
    st.session_state.diagnosed = False
    st.session_state.current_session_id = None
    st.session_state.disease = None
    st.session_state.confidence = 0
    st.session_state.system_context = None
    st.session_state.chat_history = []
    st.session_state.past_sessions = []

# Backend configuration
backend_url = "http://localhost:8000"


def load_user_sessions():
    """Load user's past sessions from backend"""
    try:
        if not st.session_state.user_id:
            return False

        response = requests.get(
            f"{backend_url}/auth/sessions/{st.session_state.user_id}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if "sessions" in data:
                st.session_state.past_sessions = data["sessions"]
                return True
            else:
                # API returned 200 but no 'sessions' key
                return False
        else:
            return False
    except requests.exceptions.ConnectionError:
        return False
    except Exception as e:
        return False


def load_session_by_id(session_id: str):
    """Load a specific session"""
    try:
        response = requests.get(
            f"{backend_url}/auth/session/{session_id}"
        )
        if response.status_code == 200:
            session = response.json()
            st.session_state.current_session_id = session['session_id']
            st.session_state.disease = session['disease']
            st.session_state.confidence = session['confidence']
            st.session_state.system_context = session.get('system_context')
            st.session_state.chat_history = session['messages']
            st.session_state.diagnosed = True
            return True
    except Exception as e:
        pass
    return False


# Check if user is still logged in via URL params (persist across reloads)
if "uid" in st.query_params and not st.session_state.authenticated:
    st.session_state.user_id = int(st.query_params["uid"])
    st.session_state.username = st.query_params.get("username", "User")
    st.session_state.authenticated = True
    # Load past sessions after auto-login
    load_user_sessions()


# AUTHENTICATION PAGE
if not st.session_state.authenticated:
    st.markdown("<h1>🏥 Skin Disease Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: white; font-size: 16px;'>AI-Powered Skin Analysis with Real-Time Results</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.markdown("### 🔑 Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input(
            "Password", type="password", key="login_password")

        if st.button("Login", type="primary", use_container_width=True):
            try:
                response = requests.post(
                    f"{backend_url}/auth/login",
                    json={
                        "username": login_username,
                        "password": login_password
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.authenticated = True
                    st.session_state.user_id = data["user_id"]
                    st.session_state.username = data["username"]

                    # Store in URL params to persist across reloads
                    st.query_params["uid"] = data["user_id"]
                    st.query_params["username"] = data["username"]

                    # Load past sessions immediately
                    load_user_sessions()

                    st.success("✅ Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    with tab2:
        st.markdown("### 📝 Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input(
            "Password", type="password", key="reg_password")
        reg_confirm = st.text_input(
            "Confirm Password", type="password", key="reg_confirm")

        if st.button("Register", type="primary", use_container_width=True):
            if reg_password != reg_confirm:
                st.error("❌ Passwords don't match")
            elif len(reg_password) < 6:
                st.error("❌ Password must be at least 6 characters")
            else:
                try:
                    response = requests.post(
                        f"{backend_url}/auth/register",
                        json={
                            "username": reg_username,
                            "email": reg_email,
                            "password": reg_password
                        }
                    )

                    if response.status_code == 200:
                        st.success("✅ Registration successful! Please login.")
                    else:
                        st.error(f"❌ {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# MAIN APPLICATION (After login)
else:
    # Sidebar with user info and history
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")

        if st.button("🚪 Logout", use_container_width=True):
            # Clear URL params to logout
            st.query_params.clear()

            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.diagnosed = False
            st.session_state.current_session_id = None
            st.session_state.chat_history = []
            st.session_state.past_sessions = []
            st.rerun()

        st.divider()

        # Display past sessions (auto-loaded after login)
        # Force reload if empty (in case initial load failed)
        if not st.session_state.past_sessions and st.session_state.authenticated:
            load_user_sessions()

        if st.session_state.past_sessions:
            st.markdown("### 📋 Chat History")
            for session in st.session_state.past_sessions:
                # Highlight current session
                is_current = (st.session_state.current_session_id ==
                              session['session_id'])
                session_class = "history-item-active" if is_current else ""

                if st.button(
                    f"🦠 {session['disease']}\n_{session['created_at'][:10]}_",
                    key=f"session_{session['session_id']}",
                    use_container_width=True
                ):
                    # Load this session
                    load_session_by_id(session['session_id'])
                    st.rerun()
        else:
            st.info("No chat history yet. Upload an image to start!")

        st.markdown("---")
        st.sidebar.markdown("""
        ### 📋 How to use:
        1. Upload a skin image
        2. Wait for the API to analyze it
        3. Get instant recommendations
        4. Ask follow-up questions
        5. History is saved automatically
        """)

    # Main content
    st.markdown("<h1>🏥 Skin Disease Analyzer</h1>", unsafe_allow_html=True)

    if not st.session_state.diagnosed:
        # Upload section
        st.markdown("<p style='text-align: center; color: white; font-size: 16px;'>AI-Powered Skin Analysis with Real-Time Results</p>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 📸 Upload Image")
            uploaded_file = st.file_uploader(
                "Choose a skin image...",
                type=["jpg", "jpeg", "png", "bmp"],
                help="Upload a clear image of the affected skin area"
            )

            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, use_column_width=True,
                         caption="Uploaded Image")
                st.info(
                    f"📁 File: {uploaded_file.name} | Size: {uploaded_file.size / 1024:.1f} KB")

        with col2:
            st.markdown("### 🔄 Analysis Results")

            if uploaded_file is not None:
                if st.button("🔍 Analyze Image", use_container_width=True, type="primary"):
                    with st.spinner("🔄 Analyzing image..."):
                        time.sleep(0.3)
                        try:
                            files = {
                                'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

                            response = requests.post(
                                f"{backend_url}/analyze_skin",
                                files=files,
                                params={"user_id": st.session_state.user_id},
                                timeout=30
                            )

                            if response.status_code == 200:
                                data = response.json()

                                st.session_state.diagnosed = True
                                st.session_state.current_session_id = data.get(
                                    'session_id')
                                st.session_state.disease = data.get('disease')
                                st.session_state.confidence = data.get(
                                    'confidence')
                                st.session_state.system_context = data.get(
                                    'system_context')
                                st.session_state.chat_history = []

                                # Immediately add new session to sidebar
                                new_session = {
                                    'session_id': data.get('session_id'),
                                    'disease': data.get('disease'),
                                    'confidence': data.get('confidence'),
                                    'recommendations': data.get('recommendations'),
                                    'next_steps': data.get('next_steps'),
                                    'tips': data.get('tips'),
                                    'system_context': data.get('system_context'),
                                    'created_at': datetime.now().isoformat(),
                                    'messages': []
                                }

                                # Add to front of the list
                                st.session_state.past_sessions.insert(
                                    0, new_session)

                                st.success("✅ Analysis Complete!")
                                time.sleep(0.5)
                                st.rerun()

                            else:
                                st.error(f"❌ Error: {response.status_code}")
                                st.error(response.json().get(
                                    'detail', 'Unknown error occurred'))

                        except requests.exceptions.ConnectionError:
                            st.error(
                                f"❌ Cannot connect to backend at {backend_url}")
                            st.info("Make sure your FastAPI backend is running!")
                        except requests.exceptions.Timeout:
                            st.error(
                                "⏱️ Request timeout. The analysis took too long.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            else:
                st.info("👆 Upload an image to get started!")

    # Chat section - displayed if diagnosed (Side-by-side layout)
    else:
        # Two column layout: Diagnosis on left, Chat on right
        diag_col, chat_col = st.columns([1, 1.2])

        with diag_col:
            st.markdown("### 📋 Diagnosis")

            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='disease-name'>{st.session_state.disease}</div>", unsafe_allow_html=True)

            confidence = st.session_state.confidence * 100
            st.markdown(
                f"<div class='confidence-score'>Confidence: {confidence:.1f}%</div>", unsafe_allow_html=True)

            st.progress(min(st.session_state.confidence, 1.0))
            st.markdown("</div>", unsafe_allow_html=True)

            # Get full session data for recommendations
            current_session = next(
                (s for s in st.session_state.past_sessions if s['session_id']
                 == st.session_state.current_session_id),
                None
            )

            if current_session:
                st.markdown("#### 💊 Recommendations")
                st.info(current_session.get('recommendations', 'N/A'))

                st.markdown("#### 📋 Next Steps")
                st.warning(current_session.get('next_steps', 'N/A'))

                st.markdown("#### 💡 Tips")
                st.success(current_session.get('tips', 'N/A'))

            # New analysis button
            if st.button("🔄 New Analysis", use_container_width=True):
                st.session_state.diagnosed = False
                st.session_state.current_session_id = None
                st.session_state.chat_history = []
                st.rerun()

        with chat_col:
            st.markdown("### 💬 Chat About Diagnosis")

            # Chat input
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
                                "session_id": st.session_state.current_session_id,
                                "disease": st.session_state.disease,
                                "confidence": st.session_state.confidence,
                                "message": user_question,
                                "history": st.session_state.chat_history,
                                "system_context": st.session_state.system_context
                            },
                            timeout=30
                        )

                        if response.status_code == 200:
                            chat_response = response.json()
                            st.session_state.chat_history = chat_response.get(
                                "history", [])

                            # Update the current session in past_sessions
                            for session in st.session_state.past_sessions:
                                if session['session_id'] == st.session_state.current_session_id:
                                    session['messages'] = st.session_state.chat_history
                                    break

                            st.rerun()
                        else:
                            st.error("❌ Failed to get response")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            # Display chat history (latest at top, question above answer)
            if st.session_state.chat_history:
                st.markdown("<br>**📖 Conversation History**",
                            unsafe_allow_html=True)

                # Convert to list of dicts if needed
                messages_list = []
                for msg in st.session_state.chat_history:
                    if isinstance(msg, dict):
                        messages_list.append(msg)
                    else:
                        messages_list.append(
                            {"role": msg.role, "content": msg.content})

                # Group messages into Q&A pairs and reverse
                qa_pairs = []
                i = 0
                while i < len(messages_list):
                    if i < len(messages_list) and messages_list[i].get("role") == "user":
                        user_msg = messages_list[i].get('content', '')
                        asst_msg = messages_list[i+1].get(
                            'content', '') if i+1 < len(messages_list) else ''
                        qa_pairs.append((user_msg, asst_msg))
                        i += 2
                    else:
                        i += 1

                # Display in reverse (latest first)
                for user_msg, asst_msg in reversed(qa_pairs):
                    st.markdown(
                        f"<div class='chat-question'>❓ **Q:** {user_msg}</div>", unsafe_allow_html=True)
                    st.markdown(
                        f"<div class='chat-answer'>💡 **A:** {asst_msg}</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("<hr><p style='text-align: center; color: white; font-size: 12px;'>© 2026 Skin Disease Analyzer. All rights reserved.</p>", unsafe_allow_html=True)
