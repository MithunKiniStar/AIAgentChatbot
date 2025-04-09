import os
import streamlit as st
import time
from pathlib import Path
from dotenv import load_dotenv
import sys
from datetime import datetime
import tempfile

# Load environment variables
load_dotenv()

# Add current directory to path (to make package imports work)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the agent
from agents_chatbot.models.agent import ChatbotAgent

# Set up page configuration
st.set_page_config(
    page_title="AI Agent Chatbot",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for better styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #f0f2f6;
        color: #262730;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #e0e2e6;
        border-color: #aaa;
    }
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: #1E88E5;
    }
    .sub-header {
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        color: #0D47A1;
    }
    .category-header {
        font-size: 1.2rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #333;
        font-weight: 600;
    }
    .model-info {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .stChatMessage {
        background-color: rgba(240, 242, 246, 0.3);
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .status-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_initialized" not in st.session_state:
    st.session_state.agent_initialized = False
    
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
    
if "temp_files" not in st.session_state:
    st.session_state.temp_files = []

# Sidebar configuration
with st.sidebar:
    st.markdown('<div class="sub-header">Document Upload</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Upload documents for the chatbot to use", 
        type=["pdf", "txt"], 
        accept_multiple_files=True
    )
    
    # Process uploaded files
    if uploaded_files:
        temp_file_paths = []
        for uploaded_file in uploaded_files:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_paths.append(temp_file.name)
                # Add to cleanup list
                st.session_state.temp_files.append(temp_file.name)
                
        # Only update if we have new files
        if temp_file_paths:
            st.session_state.uploaded_files.extend(temp_file_paths)
            if st.session_state.agent_initialized:
                doc_count = st.session_state.chatbot_agent.add_documents(temp_file_paths)
                st.markdown(f'<div class="status-message success-message">✅ Documents uploaded successfully. Total documents: {doc_count}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-message success-message">✅ Documents uploaded. They will be processed when the chatbot initializes.</div>', unsafe_allow_html=True)

# Initialize the agent
if "chatbot_agent" not in st.session_state:
    # Initialize the agent
    documents_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "documents")
    
    # Determine which model to use
    use_llama = os.environ.get("USE_LLAMA", "false").lower() == "true"
    use_groq = os.environ.get("USE_GROQ", "false").lower() == "true"
    use_google_embeddings = os.environ.get("USE_GOOGLE_EMBEDDINGS", "true").lower() == "true"
    use_mock_api = os.environ.get("USE_MOCK_API", "false").lower() == "true"
    
    # Get API configuration from environment variables
    api_base_url = os.environ.get("API_BASE_URL", "http://localhost:8080")
    api_key = os.environ.get("API_KEY", "")
    
    llama_model_path = None
    groq_api_key = None
    openai_api_key = None
    google_api_key = None
    
    # Get API keys and model paths
    if use_groq:
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            groq_api_key = st.secrets.get("GROQ_API_KEY", None)
            
        if not groq_api_key:
            st.error("Groq API key not found. Please set GROQ_API_KEY in .env file or Streamlit secrets.")
            st.stop()
    elif use_llama:
        llama_model_path = os.environ.get("LLAMA_MODEL_PATH")
        if not llama_model_path:
            st.error("Llama model path not found. Please set LLAMA_MODEL_PATH in .env file.")
            st.stop()
    else:
        # Using OpenAI
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            openai_api_key = st.secrets.get("OPENAI_API_KEY", None)
            
        if not openai_api_key:
            st.error("OpenAI API key not found. Please set it in .env file or Streamlit secrets.")
            st.stop()
    
    # Get Google API key for embeddings
    if use_google_embeddings:
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        if not google_api_key:
            google_api_key = st.secrets.get("GOOGLE_API_KEY", None)
            
        if not google_api_key:
            st.warning("Google API key not found. Will fall back to simple embeddings.")
            use_google_embeddings = False
    
    try:
        st.session_state.chatbot_agent = ChatbotAgent(
            documents_dir=documents_dir,
            api_base_url=api_base_url,
            api_key=api_key,
            use_mock_api=use_mock_api,
            openai_api_key=openai_api_key,
            use_llama=use_llama,
            llama_model_path=llama_model_path,
            use_groq=use_groq,
            groq_api_key=groq_api_key,
            google_api_key=google_api_key,
            use_google_embeddings=use_google_embeddings,
            uploaded_files=st.session_state.uploaded_files
        )
        st.session_state.agent_initialized = True
    except Exception as e:
        st.error(f"Error initializing the chatbot agent: {str(e)}")
        st.session_state.agent_initialized = False
        st.stop()

# Main page content
col1, col2 = st.columns([3, 1])

with col1:
    # Header
    st.markdown('<div class="main-header">📱 AI Agent Chatbot</div>', unsafe_allow_html=True)

    # Display model information
    if os.environ.get("USE_GROQ", "false").lower() == "true":
        model_info = "Using Llama-3.1-8b-instant via Groq API"
    elif os.environ.get("USE_LLAMA", "false").lower() == "true":
        model_info = "Using Llama3-8b-8192 locally"
    else:
        model_info = "Using OpenAI GPT-4o"
        
    # Add embedding model information
    if os.environ.get("USE_GOOGLE_EMBEDDINGS", "true").lower() == "true" and os.environ.get("GOOGLE_API_KEY"):
        embedding_info = "Google AI Embeddings"
    elif os.environ.get("OPENAI_API_KEY") and not (os.environ.get("USE_LLAMA", "false").lower() == "true" or os.environ.get("USE_GROQ", "false").lower() == "true"):
        embedding_info = "OpenAI Embeddings"
    else:
        embedding_info = "Simple Embeddings"
    
    # Display API info
    if os.environ.get("USE_MOCK_API", "false").lower() == "true":
        api_info = "Using Mock API Server"
    else:
        api_info = "Connected to REST API"
        
    st.markdown(f'<div class="model-info">{model_info} | Embeddings: {embedding_info} | {api_info}</div>', unsafe_allow_html=True)

with col2:
    # Document count information
    if st.session_state.agent_initialized:
        doc_count = st.session_state.chatbot_agent.doc_processor.get_document_count()
        st.markdown(f'<div class="model-info">Documents indexed: {doc_count}</div>', unsafe_allow_html=True)

# Add predefined prompts in two columns
st.markdown('<div class="sub-header">Try a predefined prompt:</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="category-header">📊 API Queries</div>', unsafe_allow_html=True)
    api_buttons = [
        "Show me my current tasks",
        "How many active users are there?",
        "Show me the list of projects"
    ]
    
    for prompt in api_buttons:
        if st.button(prompt, key=f"api_{prompt}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot_agent.process_query(prompt)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Force a rerun to update the chat history
            st.rerun()

with col2:
    st.markdown('<div class="category-header">📚 Documentation</div>', unsafe_allow_html=True)
    doc_buttons = [
        "What are the upcoming features?",
        "How do I create an action?",
        "What are the system requirements?"
    ]
    
    for prompt in doc_buttons:
        if st.button(prompt, key=f"doc_{prompt}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot_agent.process_query(prompt)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Force a rerun to update the chat history
            st.rerun()

# Divider
st.markdown("---")

# Display chat messages section header
if st.session_state.messages:
    st.markdown('<div class="sub-header">Chat History</div>', unsafe_allow_html=True)

# Display chat messages
for idx, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask me something..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chatbot_agent.process_query(prompt)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Clean up temporary files on app exit
def cleanup_temp_files():
    for file_path in st.session_state.temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting temporary file {file_path}: {e}")

# Register the cleanup function
import atexit
atexit.register(cleanup_temp_files) 