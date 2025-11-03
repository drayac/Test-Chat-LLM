import streamlit as st
import json
import hashlib
import datetime
import os
import requests
import random
import string
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file using absolute path
env_path = "/Users/acoudray/AlitheaGenomics/r&d/app_test_groq/.env"
load_dotenv(dotenv_path=env_path)

# Initialize Groq client with secure API key handling
def get_api_key():
    """Get API key from multiple sources in order of preference"""
    # 1. Environment variable (production)
    if os.getenv("GROQ_API_KEY"):
        return os.getenv("GROQ_API_KEY")
    
    # 2. Streamlit secrets (Streamlit Cloud)
    try:
        if hasattr(st, 'secrets') and "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    
    # 3. Demo fallback (with warning) - REPLACE WITH YOUR KEY
    return "gsk_YOUR_API_KEY_HERE_REPLACE_THIS_PLACEHOLDER"

GROQ_API_KEY = get_api_key()

# Warn if using demo key
if GROQ_API_KEY == "gsk_YOUR_API_KEY_HERE_REPLACE_THIS_PLACEHOLDER":
    print("⚠️  WARNING: Using placeholder API key. Set GROQ_API_KEY environment variable for production!")

client = Groq(api_key=GROQ_API_KEY)

# Function to fetch available models from Groq API
def get_groq_models():
    """Fetch available models from Groq API"""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
        if response.status_code == 200:
            models_data = response.json()
            # Filter for text generation models and create a clean dictionary
            groq_models = {}
            for model in models_data.get("data", []):
                model_id = model.get("id", "")
                # Filter out non-text generation models (whisper, etc.)
                if not any(skip in model_id.lower() for skip in ["whisper", "distil"]):
                    # Create a clean display name
                    display_name = model_id.replace("-", " ").title()
                    groq_models[model_id] = display_name
            return groq_models
        else:
            # Fallback to static list if API fails
            return get_fallback_models()
    except Exception as e:
        # Fallback to static list if API fails
        return get_fallback_models()

def get_fallback_models():
    """Fallback model list if API fails"""
    return {
        "llama-3.1-70b-versatile": "Llama 3.1 70B Versatile",
        "llama-3.1-8b-instant": "Llama 3.1 8B Instant", 
        "llama-3.2-11b-text-preview": "Llama 3.2 11B Text",
        "llama-3.2-3b-preview": "Llama 3.2 3B Preview",
        "llama-3.2-1b-preview": "Llama 3.2 1B Preview",
        "llama3-groq-70b-8192-tool-use-preview": "Llama 3 Groq 70B Tool Use",
        "llama3-groq-8b-8192-tool-use-preview": "Llama 3 Groq 8B Tool Use",
        "llama3-70b-8192": "Llama 3 70B",
        "llama3-8b-8192": "Llama 3 8B",
        "mixtral-8x7b-32768": "Mixtral 8x7B",
        "gemma2-9b-it": "Gemma 2 9B IT",
        "gemma-7b-it": "Gemma 7B IT"
    }

# Function to test API connection and get status
def test_groq_api():
    """Test if Groq API is working and return status info"""
    try:
        # Test with model list endpoint first
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5)
        if response.status_code == 200:
            models_count = len(response.json().get("data", []))
            return True, f"API Connected - {models_count} models available"
        else:
            return False, f"API Error: {response.status_code}"
    except Exception as e:
        return False, f"Connection Error: {str(e)[:50]}"

def format_thinking_tags(text):
    """Format text between <think> and </think> tags in italic with a note"""
    import re
    
    def replace_thinking(match):
        thinking_content = match.group(1).strip()
        return f'<em>{thinking_content}</em> <em>(Model\'s thoughts)</em>'
    
    # Replace <think>content</think> with HTML italic formatting and note
    formatted_text = re.sub(r'<think>(.*?)</think>', replace_thinking, text, flags=re.DOTALL)
    return formatted_text

# Function to generate random guest ID
def generate_guest_id():
    """Generate a random guest ID"""
    return "Guest_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Get models on app start - cache to avoid repeated API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_groq_models():
    """Cached version of get_groq_models to reduce memory usage"""
    return get_groq_models()

# Authentication functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_user_data():
    """Load user data from JSON file with caching"""
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    """Save user data to JSON file and clear cache"""
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)
    # Clear the cache when data is updated
    load_user_data.clear()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email, password):
    """Authenticate user credentials"""
    users = load_user_data()
    if email in users:
        if users[email]["password"] == hash_password(password):
            return True, "Login successful!"
        else:
            return False, "Invalid password"
    return False, "User not found"

def register_user(email, password, is_guest=False):
    """Register new user or guest"""
    users = load_user_data()
    if email in users and not is_guest:
        return False, "User already exists"
    
    users[email] = {
        "password": hash_password(password) if password else "",
        "created_at": datetime.datetime.now().isoformat(),
        "chat_history": [],
        "is_guest": is_guest,
        "guest_session_id": st.session_state.get("session_id", "") if is_guest else ""
    }
    save_user_data(users)
    return True, "Registration successful!" if not is_guest else "Guest session created!"

def create_guest_user():
    """Create a temporary guest user"""
    guest_id = generate_guest_id()
    # Generate a session ID to track the guest
    if "session_id" not in st.session_state:
        st.session_state.session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    success, message = register_user(guest_id, "", is_guest=True)
    if success:
        st.session_state.authenticated = True
        st.session_state.user_email = guest_id
        st.session_state.guest_mode = True
        st.session_state.chat_history = []
    return guest_id

def cleanup_guest_users():
    """Remove guest users from storage - optimized to run less frequently"""
    # Only cleanup every 10th session to reduce overhead
    if "cleanup_counter" not in st.session_state:
        st.session_state.cleanup_counter = 0
    
    st.session_state.cleanup_counter += 1
    if st.session_state.cleanup_counter % 10 != 0:
        return  # Skip cleanup most of the time
    
    users = load_user_data()
    current_session_id = st.session_state.get("session_id", "")
    
    # Keep only non-guest users and current session guest
    cleaned_users = {}
    for email, user_data in users.items():
        if not user_data.get("is_guest", False):
            # Keep regular users
            cleaned_users[email] = user_data
        elif user_data.get("guest_session_id") == current_session_id:
            # Keep current session guest
            cleaned_users[email] = user_data
    
    # Only save if there's actually a difference to reduce I/O
    if len(cleaned_users) != len(users):
        save_user_data(cleaned_users)

def save_user_prompt(email, prompt, response, model):
    """Save user prompt and response to history"""
    users = load_user_data()
    if email in users:
        users[email]["chat_history"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "prompt": prompt,
            "response": response,
            "model": model
        })
        save_user_data(users)

def get_user_history(email, limit=10):
    """Get user chat history with memory optimization"""
    users = load_user_data()
    if email in users:
        # Only return the last 'limit' entries to save memory
        history = users[email]["chat_history"]
        return history[-limit:] if len(history) > limit else history
    return []

# Streamlit configuration
st.set_page_config(
    page_title="LLM-library Chat Test",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS styling - optimized for memory
st.markdown("""
    <style>
    .stApp { background-color: #000 !important; color: #fff !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .main-title { 
        color: #fff !important; font-size: 3.2rem !important; font-weight: 700 !important;
        text-align: center !important; margin: 0 !important; padding: 1.5rem 0 !important;
        background: linear-gradient(135deg, #fff 0%, #e0e0e0 100%) !important;
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    }
    .css-1d391kg, .css-1cypcdb, [data-testid="stSidebar"] { background-color: #1a1a1a !important; }
    .stSelectbox label, .stTextInput label, .stTextArea label { color: #fff !important; }
    .stSelectbox div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
        background-color: #2a2a2a !important; border: 1px solid #4a4a4a !important; color: #fff !important;
    }
    [data-baseweb="select"] ul, [data-baseweb="menu"] { background-color: #2a2a2a !important; }
    [data-baseweb="select"] li, [data-baseweb="menu"] li { background-color: #2a2a2a !important; color: #fff !important; }
    [data-baseweb="select"] li:hover, [data-baseweb="menu"] li:hover { background-color: #444 !important; }
    .stButton button { background-color: #333 !important; color: #fff !important; border: 1px solid #4a4a4a !important; }
    .stButton button:hover { background-color: #444 !important; }
    .stSuccess, .stError, .stInfo, .stWarning { background-color: #2a2a2a !important; color: #fff !important; }
    .stMarkdown, .stText, p, span, div, [data-testid="stSidebar"] * { color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state with memory optimization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "guest_mode" not in st.session_state:
    st.session_state.guest_mode = True
    # Only create guest user if not already authenticated
    if not st.session_state.authenticated:
        guest_id = create_guest_user()

# Clean up guest users less frequently to reduce overhead
cleanup_guest_users()

# Main page title
st.markdown("""
    <div class="main-title">
        LLM-library Chat Test
    </div>
    """, unsafe_allow_html=True)

# Model selection - available to all users
# Get sorted list of model IDs (original names), filtered to exclude certain models
groq_models = get_cached_groq_models()
all_models = list(groq_models.keys())
filtered_models = [model for model in all_models 
                  if not model.startswith('allam') and not model.startswith('playai')]
available_models = sorted(filtered_models)

# Initialize default selection if not in session state
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = available_models[0]

# Find current index
current_index = 0
if st.session_state.selected_model in available_models:
    current_index = available_models.index(st.session_state.selected_model)

selected_model = st.selectbox(
    "Choose a model",
    options=available_models,
    index=current_index,
    help="Choose from our available Groq models for text generation",
    key="model_selector"
)

# Update session state
st.session_state.selected_model = selected_model
model = selected_model

# Chat interface
st.markdown("### Chat")

# User input
user_input = st.text_area(
    "Enter your message:",
    height=100,
    placeholder="Type your message here..."
)

# Send and Clear buttons
col1, col2 = st.columns([3, 1])
with col1:
    send_button = st.button("Send", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ Clear", use_container_width=True)

if clear_button:
    st.session_state.chat_history = []
    st.rerun()

if send_button:
    if user_input.strip():
        try:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Prepare messages with system prompt for response length control
            system_prompt = {
                "role": "system", 
                "content": "You MUST keep your responses very short and concise. Maximum 200 words total. Maximum 3 paragraphs. Be direct and to the point. Do not elaborate unnecessarily. Stop writing when you reach the limit."
            }
            
            # Combine system prompt with chat history
            messages_for_api = [system_prompt] + st.session_state.chat_history
            
            # Get response from Groq
            response = client.chat.completions.create(
                model=model,
                messages=messages_for_api,
                max_tokens=300,  # Enforce shorter responses (~200 words)
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
            
            # Save to user history for all authenticated users (including guests)
            if st.session_state.authenticated and st.session_state.user_email:
                save_user_prompt(st.session_state.user_email, user_input, assistant_response, model)
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display only the latest conversation
if st.session_state.chat_history:
    # Find the last user message and assistant response
    messages = st.session_state.chat_history
    if len(messages) >= 2:
        last_user = messages[-2] if messages[-2]["role"] == "user" else None
        last_assistant = messages[-1] if messages[-1]["role"] == "assistant" else None
        
        if last_user and last_assistant:
            with st.chat_message("user"):
                st.write(last_user["content"])
            with st.chat_message("assistant"):
                # Format the assistant response to handle <think> tags
                formatted_response = format_thinking_tags(last_assistant["content"])
                st.markdown(formatted_response, unsafe_allow_html=True)

# Sidebar for authentication and chat history
with st.sidebar:
    # API Status indicator with detailed info
    api_working, api_status = test_groq_api()
    if api_working:
        st.success(f"🟢 {api_status}")
    else:
        st.error(f"🔴 {api_status}")
    
    # Authentication section
    st.markdown("### 🔐 Authentication")
    
    if st.session_state.guest_mode and not st.session_state.show_login:
        # Show guest info and sign-in option
        st.info(f"👤 Logged in as: {st.session_state.user_email}")
        if st.button("Sign In with Email", key="sidebar_signin", use_container_width=True):
            st.session_state.show_login = True
            st.rerun()
    elif st.session_state.show_login:
        # Login form
        st.markdown("#### Login")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="login_btn"):
                if login_email and login_password:
                    success, message = authenticate_user(login_email, login_password)
                    if success:
                        # Clean up guest user before switching
                        cleanup_guest_users()
                        st.session_state.authenticated = True
                        st.session_state.user_email = login_email
                        st.session_state.guest_mode = False
                        st.session_state.show_login = False
                        # Load user's chat history (limit to last 5 to save memory)
                        user_history = get_user_history(login_email, limit=5)
                        if user_history:
                            # Convert user history to chat format
                            st.session_state.chat_history = []
                            for entry in user_history:  # Already limited to 5
                                st.session_state.chat_history.append({"role": "user", "content": entry["prompt"]})
                                st.session_state.chat_history.append({"role": "assistant", "content": entry["response"]})
                        st.rerun()
                    else:
                        st.error(message)
        
        with col2:
            if st.button("Cancel", key="cancel_login"):
                st.session_state.show_login = False
                st.rerun()
        
        # Register form
        st.markdown("#### Register")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create Account", key="register_btn"):
                if reg_password != reg_password_confirm:
                    st.error("Passwords don't match")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif "@" not in reg_email:
                    st.error("Please enter a valid email")
                else:
                    success, message = register_user(reg_email, reg_password, is_guest=False)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        with col2:
            if st.button("Cancel", key="cancel_register"):
                st.session_state.show_login = False
                st.rerun()
    
    elif not st.session_state.guest_mode:
        # User is authenticated with email/password
        st.markdown(f"### 👤 {st.session_state.user_email}")
        
        if st.button("Sign Out", key="signout_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = ""
            st.session_state.chat_history = []
            st.session_state.guest_mode = True
            st.session_state.show_login = False
            # Create new guest user
            guest_id = create_guest_user()
            st.rerun()
    
    # Chat history display for all users (including guests) - limit to save memory
    st.markdown("### 📜 Chat History")
    
    user_history = get_user_history(st.session_state.user_email, limit=5)  # Reduce from 10 to 5
    if user_history:
        for i, entry in enumerate(reversed(user_history)):  # Already limited to 5
            with st.expander(f"Chat {len(user_history)-i}", expanded=False):
                st.write(f"**Prompt:** {entry['prompt'][:50]}...")  # Reduce from 100 to 50 chars
                st.write(f"**Model:** {entry['model']}")
                st.write(f"**Date:** {entry['timestamp'][:19]}")
    else:
        st.write("No chat history yet")
    
    # Show additional info for guest users
    if st.session_state.guest_mode:
        st.markdown("### 🔒 Guest Info")
        st.write("💡 Sign in with email to permanently save your chat history across sessions!")