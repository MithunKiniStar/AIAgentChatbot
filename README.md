# AI Agent Chatbot

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.26%2B-FF4B4B)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.0.335%2B-41BFB3)](https://python.langchain.com/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2%2B-6DB33F)](https://spring.io/projects/spring-boot)

This project implements an agentic LLM chatbot that can:
1. Retrieve information from a Java REST API backend
2. Extract information from documents (PDF and TXT files)
3. Allow users to upload their own documents through the UI

![Chatbot Demo](https://via.placeholder.com/800x400?text=Chatbot+Demo+Screenshot)

## 📋 Project Structure

```
/
├── agents_chatbot/            # Main application directory
│   ├── api_client/            # Code for communicating with Java REST API
│   ├── documents/             # Sample documents with application information
│   ├── models/                # LLM models and agent configuration
│   ├── ui/                    # Streamlit UI components
│   └── utils/                 # Utility functions for document processing and other helpers
└── AgentService/              # Java Spring Boot backend implementation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Java 17+ (for running the backend service)
- Maven (for building the backend service)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-agent-chatbot.git
   cd ai-agent-chatbot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables in a `.env` file:
   ```bash
   # LLM Options (choose one)
   # For OpenAI (default)
   OPENAI_API_KEY=your_openai_api_key_here
   
   # For Google (embeddings)
   GOOGLE_API_KEY=your_google_api_key_here
   USE_GOOGLE_EMBEDDINGS=true
   
   # For Llama3 via Groq
   USE_GROQ=true
   GROQ_API_KEY=your_groq_api_key_here
   
   # For local Llama3
   USE_LLAMA=true
   LLAMA_MODEL_PATH=/path/to/llama3-8b-8192.gguf
   
   # Backend Options
   API_BASE_URL=http://localhost:8080
   USE_MOCK_API=false
   ```

### Running the Application

#### Start the Java Backend (Recommended)

```bash
cd AgentService
./run.sh
```

Or use the mock server by setting `USE_MOCK_API=true` in your `.env` file.

#### Start the Chatbot Frontend

```bash
streamlit run agents_chatbot/ui/app.py
```

You can also run the application in the background:
```bash
streamlit run agents_chatbot/ui/app.py &
```

The app will be available at:
- Local URL: http://localhost:8501
- Network URL: http://YOUR_IP:8501

## 🤖 Model Options

This chatbot supports three LLM options:

### 1. OpenAI GPT-4o (Default)
- Requires an OpenAI API key
- Provides high-quality responses
- Connects to OpenAI's servers

### 2. Llama-3.1-8b-instant via Groq API (Recommended)
- Uses Groq's fast API service to access Llama 3.1
- Requires a Groq API key
- Set `USE_GROQ=true` in your .env file
- Provide your Groq API key in `GROQ_API_KEY`
- Sign up at [groq.com](https://groq.com) to get an API key

### 3. Llama3-8b-8192 Local
- Runs completely locally
- Requires downloading the model first (>4GB)
- Set `USE_LLAMA=true` in your .env file
- Specify the path to your downloaded model in `LLAMA_MODEL_PATH`

To download the Llama3 model (for local option only):
1. Visit [HuggingFace](https://huggingface.co/collections/meta-llama/llama-3-hf-6535b035e71ae6e3c484fadb) to access the models
2. Download the 8B model in GGUF format (optimized for CPU/GPU inference)
3. Set the path to the downloaded model in your .env file

## 🔧 Backend Options

You can use either the included Java backend or the Python mock server:

### Java Backend (AgentService)
- Full Java Spring Boot REST API implementation
- Provides the same endpoints and data as the mock server
- More extensible and closer to real-world implementations
- Can be containerized using the included Dockerfile
- Includes Swagger UI for API testing and exploration (http://localhost:8080/swagger-ui)

### Python Mock Server
- Simple in-memory server for development/testing
- Requires no additional setup
- Less realistic but easier to modify

## 📖 API Documentation and Testing

The Java backend includes Swagger UI documentation that lets you explore and test the APIs directly:

1. Start the Java backend service
2. Open http://localhost:8080/swagger-ui in your browser
3. You'll see all available endpoints organized by controller
4. Expand any endpoint to see details about parameters and responses
5. Click "Try it out" to test the endpoint with real data
6. View the response directly in the browser

## ✨ Features

### Document Handling
- Upload your own PDF and TXT files through the UI
- Automatic document processing with text chunking and embedding
- Vector similarity search for retrieving relevant information
- Fallback to keyword search when vector search doesn't yield good results

### API Integration
- Connect to backend REST APIs for real-time data
- Java backend included for demonstration
- Can be customized to work with real API endpoints

### Conversation UI
- Clean, modern Streamlit interface
- Quick-access buttons for common queries
- Mobile-friendly responsive design
- Document upload sidebar

## 🔌 API Endpoints

The backend (either Java or mock) provides these endpoints:

| Endpoint | Description |
|----------|-------------|
| `/api/users/active` | Get active users |
| `/api/users/{userId}` | Get user by ID |
| `/api/users/me` | Get current user |
| `/api/tasks/user/{userId}` | Get tasks for a specific user |
| `/api/tasks/me` | Get tasks for the current user |
| `/api/tasks/{taskId}` | Get task by ID |
| `/api/projects` | Get list of projects |
| `/api/projects/{projectId}` | Get project by ID |

## 💬 Sample Queries

The chatbot can handle queries like:
- "What are the upcoming features?"
- "How many active users are there?"
- "Show me my current tasks"
- "How do I create an action?"
- "What are the system requirements?" 

## ⚠️ Troubleshooting

- If you encounter port conflicts, Streamlit will automatically select a new port (e.g., 8502, 8503). Check the terminal output for the correct URL.
- For warnings about deprecated LangChain imports, these can be safely ignored or you can update imports according to LangChain documentation.
- If you have issues with the GROQ API, ensure the model name is correctly specified as "llama-3.1-8b-instant" as model names can change frequently.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details. 
