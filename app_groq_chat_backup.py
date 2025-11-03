import streamlit as st
import os
import json
import hashlib
from datetime import datetime

try:
    import groq
except ImportError:
    st.error("groq package not found. Please install with 'pip install groq'.")
    st.stop()

# User data storage file
USER_DATA_FILE = "user_data.json"
CHAT_HISTORY_FILE = "chat_histories.json"

def load_user_data():
    """Load user data from JSON file"""
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(user_data):
    """Save user data to JSON file"""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f, indent=2)

def load_chat_histories():
    """Load chat histories from JSON file"""
    try:
        with open(CHAT_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_chat_histories(chat_histories):
    """Save chat histories to JSON file"""
    with open(CHAT_HISTORY_FILE, 'w') as f:
        json.dump(chat_histories, f, indent=2)

def hash_password(password):
    """Hash password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email, password):
    """Authenticate user credentials"""
    user_data = load_user_data()
    if email in user_data:
        return user_data[email]["password"] == hash_password(password)
    return False

def register_user(email, password):
    """Register a new user"""
    user_data = load_user_data()
    if email in user_data:
        return False, "Email already exists"
    
    user_data[email] = {
        "password": hash_password(password),
        "created_at": datetime.now().isoformat()
    }
    save_user_data(user_data)
    return True, "User registered successfully"

def save_user_prompt(email, prompt, response, model):
    """Save user prompt to history"""
    chat_histories = load_chat_histories()
    if email not in chat_histories:
        chat_histories[email] = []
    
    chat_histories[email].append({
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "model": model
    })
    save_chat_histories(chat_histories)

def get_user_history(email):
    """Get user chat history"""
    chat_histories = load_chat_histories()
    return chat_histories.get(email, [])

st.set_page_config(
    page_title="LLM-library Chat Test",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "guest_mode" not in st.session_state:
    st.session_state.guest_mode = True  # Start in guest mode by default
if "show_login" not in st.session_state:
    st.session_state.show_login = False

# Main header with dark theme styling
st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background-color: #000000 !important;
        color: white !important;
    }
    
    /* Remove white top bar */
    .css-18e3th9, .css-1d391kg .css-1d391kg, header, .stApp > header {
        background-color: #000000 !important;
        visibility: hidden !important;
        height: 0px !important;
        position: fixed !important;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling - force dark */
    .css-1d391kg, .css-1r6slb0, .css-17eq0hr, .css-1544g2n, section[data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        color: white !important;
    }
    
    .css-1544g2n .css-1d391kg {
        background-color: #1a1a1a !important;
    }
    
    /* Sidebar content */
    .css-1d391kg * {
        color: white !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #000000 !important;
        color: white !important;
        padding-top: 1rem;
    }
    
    /* Simple white title - no background */
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 3rem;
        font-weight: 300;
        letter-spacing: 3px;
        background: none !important;
        border: none !important;
    }
    .main-header p {
        color: #ccc !important;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Force all text to be white */
    .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    /* Remove ugly rectangles - make containers transparent */
    .stContainer, .css-1r6slb0, .css-12oz5g7 {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Status cards */
    .status-card {
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #555;
        background-color: #1a1a1a;
        color: white !important;
        margin: 1rem 0;
    }
    
    /* Chat container - remove rectangle */
    .chat-container {
        background: transparent !important;
        border: none !important;
        padding: 1rem 0;
        box-shadow: none !important;
        margin: 1rem 0;
    }
    
    /* Chat messages area with scrollable height - remove rectangle */
    .chat-messages {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: transparent !important;
        border: none !important;
        margin-bottom: 1rem;
    }
    
    /* User messages */
    .user-message {
        margin: 15px 0;
        padding: 0;
        display: flex;
        justify-content: flex-end;
    }
    
    .user-message .message-content {
        background: #333;
        color: white !important;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        max-width: 70%;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        border: 1px solid #555;
    }
    
    /* AI messages */
    .ai-message {
        margin: 15px 0;
        padding: 0;
        display: flex;
        justify-content: flex-start;
    }
    
    .ai-message .message-content {
        background: #2a2a2a;
        color: white !important;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        max-width: 70%;
        border: 1px solid #555;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    /* Chat placeholder - remove rectangle */
    .chat-placeholder {
        display: none !important;
    }
    
    /* Remove all container backgrounds */
    .stContainer, .css-1r6slb0, .css-12oz5g7, .element-container {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Input area at bottom - remove rectangle */
    .input-area {
        background: transparent !important;
        padding: 1rem 0;
        border: none !important;
        margin-top: 1rem;
    }
    
    /* Selectbox dropdown - fix white on white */
    .stSelectbox > div > div > div[role="listbox"] {
        background-color: #2a2a2a !important;
        border: 1px solid #555 !important;
    }
    
    .stSelectbox > div > div > div[role="listbox"] > div {
        background-color: #2a2a2a !important;
        color: white !important;
    }
    
    .stSelectbox > div > div > div[role="listbox"] > div:hover {
        background-color: #333 !important;
        color: white !important;
    }
    
    /* Selectbox selected option */
    .stSelectbox > div > div > div[data-baseweb="select"] > div {
        background-color: #2a2a2a !important;
        color: white !important;
        border: 1px solid #555 !important;
    }
    
    /* Sidebar sections */
    .sidebar-section {
        padding: 1rem 0;
        border-bottom: 1px solid #333;
        color: white !important;
    }
    
    /* History items - clickable */
    .history-item {
        background-color: #2a2a2a;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid #555;
        font-size: 0.9rem;
        color: white !important;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .history-item:hover {
        background-color: #333;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #333 !important;
        color: white !important;
        border: 1px solid #555 !important;
        border-radius: 5px !important;
    }
    
    .stButton > button:hover {
        background-color: #555 !important;
        color: white !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #2a2a2a !important;
        color: white !important;
        border: 1px solid #555 !important;
        border-radius: 5px !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #2a2a2a !important;
        color: white !important;
        border: 1px solid #555 !important;
        border-radius: 5px !important;
    }
    
    /* Selectbox options */
    .stSelectbox > div > div > div {
        background-color: #2a2a2a !important;
        color: white !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #2a2a2a !important;
        color: white !important;
    }
    
    /* Success/Error messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #555 !important;
    }
    
    /* Spinner */
    .stSpinner {
        color: white !important;
    }
    
    /* Force sidebar text color */
    .css-1d391kg .stMarkdown, 
    .css-1d391kg .stText,
    .css-1d391kg p,
    .css-1d391kg span,
    .css-1d391kg div,
    .css-1d391kg h1,
    .css-1d391kg h2,
    .css-1d391kg h3 {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>LLM-library Chat Test</h1>
</div>
""", unsafe_allow_html=True)

# Main chat interface

# Embedded API key - no user input required
api_key = "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"

# Model selection
model_options = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "moonshotai/kimi-k2-instruct",
    "moonshotai/kimi-k2-instruct-0905",
    "groq/compound-mini",
    "groq/compound",
    "allam-2-7b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b"
]

st.markdown("**Select Model:**")
model_choice = st.selectbox(
    "Choose your AI model",
    model_options,
    help="Each model has different capabilities and response styles",
    label_visibility="collapsed"
)

# API client initialization
os.environ["GROQ_API_KEY"] = api_key
client = groq.Client(api_key=api_key)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Authentication UI - Only show if user clicks login or already authenticated
if st.session_state.show_login and not st.session_state.authenticated:
    st.markdown("### Authentication Portal")
    
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    with tab1:
        st.subheader("Sign In")
        login_email = st.text_input("Email Address", key="login_email", placeholder="Enter your email")
        login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign In", key="main_signin", type="primary", use_container_width=True):
                if authenticate_user(login_email, login_password):
                    st.session_state.authenticated = True
                    st.session_state.user_email = login_email
                    st.session_state.guest_mode = False
                    st.session_state.show_login = False
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
        
        with col2:
            if st.button("Cancel", key="cancel_signin", use_container_width=True):
                st.session_state.show_login = False
                st.rerun()
    
    with tab2:
        st.subheader("Create Account")
        reg_email = st.text_input("Email Address", key="reg_email", placeholder="Enter your email")
        reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Choose a secure password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm", placeholder="Confirm your password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create Account", key="main_register", type="primary", use_container_width=True):
                if reg_password != reg_password_confirm:
                    st.error("Passwords don't match")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif "@" not in reg_email:
                    st.error("Please enter a valid email address")
                else:
                    success, message = register_user(reg_email, reg_password)
                    if success:
                        st.success("Account created successfully! You can now sign in.")
                    else:
                        st.error(message)
        
        with col2:
            if st.button("Cancel", key="cancel_reg", use_container_width=True):
                st.session_state.show_login = False
                st.rerun()
    
    st.stop()

# User status display
if st.session_state.authenticated:
    st.markdown(f"""
    <div class="status-card">
        <strong>Signed in as:</strong> {st.session_state.user_email}<br>
        <small>Your conversations are automatically saved</small>
    </div>
    """, unsafe_allow_html=True)

# Remove authentication UI from main area - now handled in sidebar only
    
    with tab1:
        st.subheader("Login")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="old_login"):
                if authenticate_user(login_email, login_password):
                    st.session_state.authenticated = True
                    st.session_state.user_email = login_email
                    st.session_state.guest_mode = False
                    st.session_state.show_login = False
                    st.rerun()
                else:
                    st.error("Invalid email or password")
        
        with col2:
            if st.button("Back to Guest Mode", key="back_guest_login"):
                st.session_state.guest_mode = True
                st.session_state.show_login = False
                st.rerun()
    
    with tab2:
        st.subheader("Register")
        # Main chat interface starts here
    
    st.stop()

# User status display
if st.session_state.authenticated:
    st.success(f"🔐 Logged in as: {st.session_state.user_email}")
elif st.session_state.guest_mode:
    st.info("� Guest Mode - Chat history will be lost when you close the app")

# Main chat interface

# Navigation bar
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

with col1:
    st.markdown("#### Start your conversation")

with col2:
    if not st.session_state.authenticated and st.button("Sign In", key="sidebar_signin", use_container_width=True):
        st.session_state.show_login = True
        st.rerun()

with col3:
    if st.button("Clear Chat", key="sidebar_clear", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

with col4:
    if st.session_state.authenticated and st.button("Sign Out", key="sidebar_signout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.chat_history = []
        st.session_state.guest_mode = True
        st.session_state.show_login = False
        st.rerun()

# Sidebar for chat history
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    
    # Authentication in sidebar
    if not st.session_state.authenticated:
        if st.button("🔐 Sign In", key="sidebar_signin", use_container_width=True):
            st.session_state.show_login = True
            st.rerun()
        
        # Show login form if requested
        if st.session_state.show_login:
            st.markdown("### Login")
            login_email = st.text_input("Email", key="sidebar_login_email")
            login_password = st.text_input("Password", type="password", key="sidebar_login_password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login", key="sidebar_login_btn", use_container_width=True):
                    if authenticate_user(login_email, login_password):
                        st.session_state.authenticated = True
                        st.session_state.user_email = login_email
                        st.session_state.guest_mode = False
                        st.session_state.show_login = False
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            with col2:
                if st.button("Cancel", key="sidebar_cancel", use_container_width=True):
                    st.session_state.show_login = False
                    st.rerun()
            
            st.markdown("### Register")
            register_email = st.text_input("Email", key="sidebar_register_email")
            register_password = st.text_input("Password", type="password", key="sidebar_register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="sidebar_confirm_password")
            
            if st.button("Create Account", key="sidebar_register_btn", use_container_width=True):
                if register_password == confirm_password:
                    if register_user(register_email, register_password):
                        st.success("Account created! Please login.")
                        st.session_state.show_login = False
                        st.rerun()
                    else:
                        st.error("Email already exists")
                else:
                    st.error("Passwords don't match")
    else:
        st.success(f"Logged in as: {st.session_state.user_email}")
        if st.button("Sign Out", key="sidebar_signout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.guest_mode = True
            st.session_state.show_login = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("## Chat History")
    
    if st.session_state.authenticated:
        # Show persistent history for logged-in users
        user_history = get_user_history(st.session_state.user_email)
        
        if user_history:
            st.markdown(f"**{len(user_history)} saved conversations**")
            
            # Show recent prompts with better styling
            for i, chat in enumerate(reversed(user_history[-10:])):  # Show last 10
                prompt_preview = chat['prompt'][:50] + "..." if len(chat['prompt']) > 50 else chat['prompt']
                
                st.markdown(f'''
                <div class="history-item">
                    <strong>#{len(user_history) - i}</strong><br>
                    <small>{chat['timestamp'][:16].replace('T', ' ')}</small><br>
                    <small>Model: {chat['model']}</small><br>
                    {prompt_preview}
                </div>
                ''', unsafe_allow_html=True)
                
                if st.button(f"Load #{len(user_history) - i}", key=f"load_{i}", use_container_width=True):
                    st.session_state.chat_history = [
                        ("user", chat['prompt']),
                        ("groq", chat['response'])
                    ]
                    st.rerun()
        else:
            st.markdown("*No saved conversations yet*")
    
    elif st.session_state.guest_mode:
        # Show clickable history for current session
        if st.session_state.chat_history:
            # Count user messages
            user_messages = [(i, msg) for i, (role, msg) in enumerate(st.session_state.chat_history) if role == "user"]
            
            if user_messages:
                st.markdown(f"**Current session: {len(user_messages)} messages**")
                st.markdown("*Click to view previous conversations*")
                
                # Show each user message as clickable
                for i, (original_index, message) in enumerate(reversed(user_messages)):
                    prompt_preview = message[:40] + "..." if len(message) > 40 else message
                    
                    st.markdown(f'''
                    <div class="history-item">
                        <strong>Message #{len(user_messages) - i}</strong><br>
                        {prompt_preview}
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    if st.button(f"View Message #{len(user_messages) - i}", key=f"view_msg_{original_index}", use_container_width=True):
                        # Temporarily show this specific exchange
                        if original_index + 1 < len(st.session_state.chat_history):
                            # Store the full history and show selected conversation
                            if "full_chat_history" not in st.session_state:
                                st.session_state.full_chat_history = st.session_state.chat_history.copy()
                            
                            # Show selected conversation
                            st.session_state.chat_history = [
                                st.session_state.full_chat_history[original_index],  # user message
                                st.session_state.full_chat_history[original_index + 1]  # ai response
                            ]
                            st.rerun()
                
                # Add button to return to latest conversation
                if "full_chat_history" in st.session_state and len(st.session_state.full_chat_history) != len(st.session_state.chat_history):
                    if st.button("🔄 Back to Latest", key="back_to_latest", use_container_width=True):
                        st.session_state.chat_history = st.session_state.full_chat_history.copy()
                        del st.session_state.full_chat_history
                        st.rerun()
        else:
            st.markdown("*No messages in current session*")
    
    else:
        st.markdown("*Sign in to save chat history*")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main chat interface

# Main chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Embedded API key - no user input required
api_key = "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"

# Model selection
model_options = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "moonshotai/kimi-k2-instruct",
    "moonshotai/kimi-k2-instruct-0905",
    "groq/compound-mini",
    "groq/compound",
    "allam-2-7b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b"
]

st.markdown("**Select Model:**")
model_choice = st.selectbox(
    "Choose your AI model",
    model_options,
    help="Each model has different capabilities and response styles",
    label_visibility="collapsed"
)

# API client initialization
os.environ["GROQ_API_KEY"] = api_key
client = groq.Client(api_key=api_key)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat display area with constrained height - show only last exchange
st.markdown("### Conversation")
st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

if st.session_state.chat_history:
    # Show only the last user message and AI response
    if len(st.session_state.chat_history) >= 2:
        # Get the last two messages (user + AI response)
        last_messages = st.session_state.chat_history[-2:]
        for i, (role, message) in enumerate(last_messages):
            if role == "user":
                st.markdown(f'<div class="user-message">'
                           f'<div class="message-content">'
                           f'<strong>You:</strong><br>{message}'
                           f'</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-message">'
                           f'<div class="message-content">'
                           f'<strong>AI ({model_choice}):</strong><br>{message}'
                           f'</div></div>', unsafe_allow_html=True)
    elif len(st.session_state.chat_history) == 1:
        # Show just the user message if AI hasn't responded yet
        role, message = st.session_state.chat_history[0]
        if role == "user":
            st.markdown(f'<div class="user-message">'
                       f'<div class="message-content">'
                       f'<strong>You:</strong><br>{message}'
                       f'</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input area at the bottom
st.markdown('<div class="input-area">', unsafe_allow_html=True)
st.markdown("**Your Message:**")

# Use session state to manage input clearing
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

user_input = st.text_area(
    "Type your message here...", 
    height=100,
    placeholder="Ask me anything! I'm powered by Groq's advanced language models.",
    label_visibility="collapsed",
    value=st.session_state.input_text,
    key="message_input"
)

col1, col2 = st.columns([1, 4])
with col1:
    send_button = st.button("Send Message", key="send_msg", type="primary", use_container_width=True)

if send_button and user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("Processing your request..."):
        try:
            # Add length limitation instruction to the prompt
            modified_prompt = f"{user_input}\n\nPlease keep your response concise: maximum 100 words, 2-3 paragraphs."
            
            response = client.chat.completions.create(
                model=model_choice,
                messages=[{"role": "user", "content": modified_prompt}]
            )
            reply = response.choices[0].message.content
            st.session_state.chat_history.append(("groq", reply))
            
            # Save to user history only if logged in
            if st.session_state.authenticated:
                save_user_prompt(st.session_state.user_email, user_input, reply, model_choice)
            
            # Clear the input after sending
            st.session_state.input_text = ""
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
