import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

from langchain.schema import Document
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.llms import LlamaCpp
from langchain_groq import ChatGroq

from ..utils.pdf_processor import DocumentProcessor
from ..api_client.client import APIClient

class ChatbotAgent:
    """
    Main agent class for handling user conversations and routing to appropriate handlers.
    """
    
    def __init__(
        self, 
        documents_dir: str,
        api_base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        use_mock_api: bool = False,
        openai_api_key: Optional[str] = None,
        use_llama: bool = False,
        llama_model_path: Optional[str] = None,
        use_groq: bool = False,
        groq_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
        use_google_embeddings: bool = True,
        uploaded_files: List[str] = None
    ):
        """
        Initialize the chatbot agent.
        
        Args:
            documents_dir: Directory containing PDF documents
            api_base_url: Base URL for the Java REST API
            api_key: Optional API key for the Java REST API
            use_mock_api: Whether to use the mock API (for development)
            openai_api_key: OpenAI API key for the language model
            use_llama: Whether to use Llama3 model instead of OpenAI
            llama_model_path: Path to the Llama3 model
            use_groq: Whether to use Groq's API for Llama3
            groq_api_key: Groq API key for accessing their models
            google_api_key: Google API key for embeddings
            use_google_embeddings: Whether to use Google's AI embeddings
            uploaded_files: List of paths to uploaded document files
        """
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('ChatbotAgent')
        
        # Get API keys from environment if not provided
        if google_api_key is None:
            google_api_key = os.environ.get("GOOGLE_API_KEY")
        
        if openai_api_key is None:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            
        # Setup document processor with best available embedding model
        use_openai_embeddings = not (use_llama or use_groq) and openai_api_key is not None 
        
        self.doc_processor = DocumentProcessor(
            documents_dir=documents_dir, 
            use_openai=use_openai_embeddings,
            use_google=use_google_embeddings,
            google_api_key=google_api_key,
            openai_api_key=openai_api_key
        )
        self.doc_processor.load_and_index_documents(additional_files=uploaded_files)
        
        # Setup API client
        if use_mock_api:
            # Import mock server only if needed to avoid circular imports
            from ..api_client.mock_server import MockAPIServer
            self.mock_server = MockAPIServer()
            self.api_client = None
        else:
            if not api_base_url:
                # Default to environment variable or localhost if not provided
                api_base_url = os.environ.get("API_BASE_URL", "http://localhost:8080")
            
            if not api_key:
                api_key = os.environ.get("API_KEY")
                
            self.api_client = APIClient(api_base_url, api_key)
            self.mock_server = None
        
        # Setup language model and conversation memory
        if use_groq:
            # Get Groq API key from environment if not provided
            if not groq_api_key:
                groq_api_key = os.environ.get("GROQ_API_KEY")
                if not groq_api_key:
                    raise ValueError(
                        "Groq API key must be provided either as an argument or "
                        "through the GROQ_API_KEY environment variable"
                    )
            
            self.llm = ChatGroq(
                groq_api_key=groq_api_key,
                model_name="llama-3.1-8b-instant",
                temperature=0.7
            )
        elif use_llama:
            if not llama_model_path:
                raise ValueError("Llama model path must be provided when using Llama locally")
                
            self.llm = LlamaCpp(
                model_path=llama_model_path,
                temperature=0.7,
                max_tokens=4096,
                n_ctx=8192,
                verbose=True
            )
        else:
            # Get OpenAI API key from environment if not provided
            if not openai_api_key:
                openai_api_key = os.environ.get("OPENAI_API_KEY")
                if not openai_api_key:
                    raise ValueError(
                        "OpenAI API key must be provided either as an argument or "
                        "through the OPENAI_API_KEY environment variable"
                    )
            
            self.llm = ChatOpenAI(
                temperature=0.7,
                openai_api_key=openai_api_key,
                model_name="gpt-4o"
            )
        
        self.memory = ConversationBufferMemory(
            return_messages=True,
            ai_prefix="Assistant",
            human_prefix="User"
        )
        
        # Create conversation chain
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )
    
    def add_documents(self, file_paths: List[str]) -> int:
        """
        Add new documents to the index.
        
        Args:
            file_paths: List of paths to document files to add
            
        Returns:
            Number of documents in the index after addition
        """
        self.doc_processor.load_and_index_documents(additional_files=file_paths)
        return self.doc_processor.get_document_count()
    
    def _query_api(self, query_type: str, **kwargs) -> Dict:
        """
        Query the API (either mock or real).
        
        Args:
            query_type: Type of query to make
            **kwargs: Additional arguments for the query
            
        Returns:
            API response
        """
        if self.mock_server:
            # Use mock server
            if query_type == "active_users":
                return self.mock_server.get_active_users()
            elif query_type == "user_by_id":
                return self.mock_server.get_user_by_id(kwargs.get("user_id"))
            elif query_type == "current_user":
                return self.mock_server.get_current_user()
            elif query_type == "tasks_for_user":
                return self.mock_server.get_tasks_for_user(kwargs.get("user_id"))
            elif query_type == "my_tasks":
                return self.mock_server.get_my_tasks()
            elif query_type == "task_by_id":
                return self.mock_server.get_task_by_id(kwargs.get("task_id"))
            elif query_type == "projects":
                return self.mock_server.get_projects()
            elif query_type == "project_by_id":
                return self.mock_server.get_project_by_id(kwargs.get("project_id"))
            else:
                return {"error": f"Unknown query type: {query_type}"}
        else:
            # Use real API client
            try:
                if query_type == "active_users":
                    return self.api_client.get_active_users()
                elif query_type == "user_by_id":
                    return self.api_client.get_user_by_id(kwargs.get("user_id"))
                elif query_type == "current_user":
                    return self.api_client.get_current_user()
                elif query_type == "tasks_for_user":
                    return self.api_client.get_tasks_for_user(kwargs.get("user_id"))
                elif query_type == "my_tasks":
                    return self.api_client.get_my_tasks()
                elif query_type == "task_by_id":
                    return self.api_client.get_task_by_id(kwargs.get("task_id"))
                elif query_type == "projects":
                    return self.api_client.get_projects()
                elif query_type == "project_by_id":
                    return self.api_client.get_project_by_id(kwargs.get("project_id"))
                else:
                    return {"error": f"Unknown query type: {query_type}"}
            except Exception as e:
                self.logger.error(f"API request error: {str(e)}")
                return {"error": f"API error: {str(e)}"}
    
    def _classify_query_intent(self, query: str) -> Tuple[str, Dict]:
        """
        Classify the intent of the user's query.
        
        Args:
            query: User's query
            
        Returns:
            Tuple of (intent_type, parameters)
        """
        self.logger.info(f"Classifying query intent: {query}")
        
        # First check for common patterns that we can classify without LLM
        query_lower = query.lower()
        
        # API queries
        if "active user" in query_lower or "how many user" in query_lower:
            classification = ("API", {"specific_intent": "active_users", "parameters": {}})
            self.logger.info(f"Pattern-based classification: {classification}")
            return classification
            
        elif ("my task" in query_lower or "tasks assigned to me" in query_lower or 
                "current task" in query_lower or ("what are my" in query_lower and "task" in query_lower) or
                "show me my" in query_lower and "task" in query_lower):
            classification = ("API", {"specific_intent": "my_tasks", "parameters": {}})
            self.logger.info(f"Pattern-based classification: {classification}")
            return classification
            
        elif "task id" in query_lower or "details for task" in query_lower:
            # Extract the task ID using regex
            import re
            task_id_match = re.search(r'task (?:id\s*)?(\w+)', query_lower)
            task_id = task_id_match.group(1) if task_id_match else None
            classification = ("API", {"specific_intent": "task_by_id", "parameters": {"task_id": task_id}})
            self.logger.info(f"Pattern-based classification: {classification}")
            return classification
            
        elif "list of project" in query_lower or "show me project" in query_lower or "what project" in query_lower:
            classification = ("API", {"specific_intent": "projects", "parameters": {}})
            self.logger.info(f"Pattern-based classification: {classification}")
            return classification
            
        elif "current user" in query_lower or "who am i" in query_lower:
            classification = ("API", {"specific_intent": "current_user", "parameters": {}})
            self.logger.info(f"Pattern-based classification: {classification}")
            return classification
            
        # DOCS queries  
        elif "upcoming feature" in query_lower or "new feature" in query_lower or "future feature" in query_lower or "what are the upcoming" in query_lower:
            classification = ("DOCS", {"specific_intent": "upcoming_features", "parameters": {}})
            self.logger.info(f"Pattern-based classification: {classification}")
            return classification
            
        elif "create" in query_lower and "action" in query_lower:
            classification = ("DOCS", {"specific_intent": "how_to_create_action", "parameters": {}})
            self.logger.info(f"Pattern-based classification: {classification}")
            return classification
            
        elif "system requirement" in query_lower or "what are the system" in query_lower:
            classification = ("DOCS", {"specific_intent": "system_requirements", "parameters": {}})
            self.logger.info(f"Pattern-based classification: {classification}")
            return classification
        
        # If no pattern match, use LLM classification
        prompt = PromptTemplate(
            input_variables=["query"],
            template="""
            Determine whether the following query is asking for:
            1. Real-time data about users, tasks, or projects (API)
            2. Information about features, how-to guides, or FAQs (DOCS)
            
            Query: {query}
            
            If it's an API query, also identify what specific data is being requested and any parameters needed.
            If it's a DOCS query, identify what specific information is being requested.
            
            Output your answer in the following JSON format:
            {{
                "type": "API" or "DOCS",
                "specific_intent": "<specific intent like 'active_users', 'tasks_for_user', 'upcoming_features', 'how_to_create_action', etc.>",
                "parameters": {{<any parameters needed for the API call, such as user_id, task_id, etc.>}}
            }}
            """
        )
        
        response = self.llm.invoke(prompt.format(query=query))
        self.logger.info(f"LLM classification response: {response.content}")
        
        try:
            classification = json.loads(response.content)
            self.logger.info(f"Using LLM classification: {classification}")
            return classification["type"], {
                "specific_intent": classification.get("specific_intent", ""),
                "parameters": classification.get("parameters", {})
            }
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"LLM classification failed: {str(e)}. Falling back to simple classification.")
            # Fall back to a simple classification if the LLM doesn't return valid JSON
            if "active user" in query.lower() or "how many user" in query.lower():
                classification = ("API", {"specific_intent": "active_users", "parameters": {}})
                self.logger.info(f"Fallback classification: {classification}")
                return classification
            elif "my task" in query.lower() or "tasks assigned to me" in query.lower() or "current task" in query.lower() or "what are my" in query.lower() and "task" in query.lower():
                classification = ("API", {"specific_intent": "my_tasks", "parameters": {}})
                self.logger.info(f"Fallback classification: {classification}")
                return classification
            elif "task id" in query.lower() or "details for task" in query.lower():
                # Extract the task ID using regex
                import re
                task_id_match = re.search(r'task (?:id\s*)?(\w+)', query.lower())
                task_id = task_id_match.group(1) if task_id_match else None
                classification = ("API", {"specific_intent": "task_by_id", "parameters": {"task_id": task_id}})
                self.logger.info(f"Fallback classification: {classification}")
                return classification
            elif "upcoming feature" in query.lower() or "new feature" in query.lower() or "future feature" in query.lower() or "what are the upcoming" in query.lower():
                classification = ("DOCS", {"specific_intent": "upcoming_features", "parameters": {}})
                self.logger.info(f"Fallback classification: {classification}")
                return classification
            elif "create" in query.lower() and "action" in query.lower():
                classification = ("DOCS", {"specific_intent": "how_to_create_action", "parameters": {}})
                self.logger.info(f"Fallback classification: {classification}")
                return classification
            elif "list of project" in query.lower() or "show me project" in query.lower() or "what project" in query.lower():
                classification = ("API", {"specific_intent": "projects", "parameters": {}})
                self.logger.info(f"Fallback classification: {classification}")
                return classification
            elif "current user" in query.lower() or "who am i" in query.lower():
                classification = ("API", {"specific_intent": "current_user", "parameters": {}})
                self.logger.info(f"Fallback classification: {classification}")
                return classification
            elif "system requirement" in query.lower() or "what are the system" in query.lower():
                classification = ("DOCS", {"specific_intent": "system_requirements", "parameters": {}})
                self.logger.info(f"Fallback classification: {classification}")
                return classification
            else:
                classification = ("DOCS", {"specific_intent": "general", "parameters": {}})
                self.logger.info(f"Fallback classification: {classification}")
                return classification
    
    def _handle_api_query(self, specific_intent: str, parameters: Dict) -> str:
        """
        Handle API queries by fetching data from the API.
        
        Args:
            specific_intent: Specific intent of the query
            parameters: Parameters for the query
            
        Returns:
            Generated response for the user
        """
        self.logger.info(f"Handling as API query: {specific_intent}")
        
        # Query the API
        api_response = self._query_api(specific_intent, **parameters)
        
        # Check for errors in API response
        if isinstance(api_response, dict) and "error" in api_response:
            error_message = api_response.get("error", "Unknown error")
            status_code = api_response.get("status_code", 500)
            details = api_response.get("details", {})
            
            # Log the error
            self.logger.error(f"API error ({status_code}): {error_message}")
            
            # For connection issues - inform the user
            if status_code in [503, 504]:
                prompt = f"""
                The API server is currently not reachable or timed out. Please help the user by:
                1. Suggesting they check if the backend server is running
                2. Verify the API URL is correct ({self.api_client.base_url if self.api_client else 'unknown'})
                3. Check network connectivity
                4. Suggest using the mock server for testing by selecting the "Use Mock Server" option
                
                Error details: {error_message}
                
                Provide a friendly response:
                """
                return self.llm.invoke(prompt).content
            
            # For authentication issues
            if status_code in [401, 403]:
                prompt = f"""
                There was an authentication issue with the API server. Please help the user by:
                1. Suggesting they check their API key is correct
                2. Verify they have proper permissions
                3. Check if token has expired
                4. Suggest using the mock server for testing
                
                Error details: {error_message}
                
                Provide a friendly response:
                """
                return self.llm.invoke(prompt).content
                
            # For not found issues
            if status_code == 404:
                prompt = f"""
                The requested resource was not found on the API server. Please help the user by:
                1. Checking if the API endpoint is correct
                2. Verify the resource ID if one was used
                3. Suggest using the mock server which has predefined data
                
                Error details: {error_message}
                
                Provide a friendly response:
                """
                return self.llm.invoke(prompt).content
            
            # Generic error
            prompt = f"""
            There was an error accessing the API. Please help the user by:
            1. Explaining the error in simple terms
            2. Suggesting possible solutions
            3. Mention they can use the mock server for testing
            
            Error details: {error_message}
            Status code: {status_code}
            Additional details: {json.dumps(details) if details else "None"}
            
            Provide a friendly response:
            """
            return self.llm.invoke(prompt).content
        
        # Build prompt for LLM
        if specific_intent == "active_users":
            prompt = f"""
            Based on the data provided, analyze the active users and provide a helpful response.
            
            Active users data: {json.dumps(api_response, indent=2)}
            
            In your response:
            1. How many active users are there?
            2. Mention any key information about these users (roles, departments)
            3. Present the information in a conversational way
            4. Don't include any JSON formatting or code blocks in your response
            """
        elif specific_intent == "my_tasks":
            prompt = f"""
            Based on the data provided, analyze the tasks assigned to the current user and provide a helpful response.
            
            Tasks data: {json.dumps(api_response, indent=2)}
            
            In your response:
            1. How many tasks are assigned to the user?
            2. Mention high priority tasks first
            3. Include brief details like due dates and status
            4. Present the information in a conversational way
            5. Don't include any JSON formatting or code blocks in your response
            """
        elif specific_intent == "tasks_for_user":
            user_id = parameters.get("user_id", "unknown")
            prompt = f"""
            Based on the data provided, analyze the tasks assigned to user ID {user_id} and provide a helpful response.
            
            Tasks data: {json.dumps(api_response, indent=2)}
            
            In your response:
            1. How many tasks are assigned to the user?
            2. Mention high priority tasks first
            3. Include brief details like due dates and status
            4. Present the information in a conversational way
            5. Don't include any JSON formatting or code blocks in your response
            """
        elif specific_intent == "projects":
            prompt = f"""
            Based on the data provided, analyze the projects and provide a helpful response.
            
            Projects data: {json.dumps(api_response, indent=2)}
            
            In your response:
            1. How many projects are there?
            2. Mention key information like status, timelines, and team size
            3. Present the information in a conversational way
            4. Don't include any JSON formatting or code blocks in your response
            """
        elif specific_intent == "project_by_id":
            project_id = parameters.get("project_id", "unknown")
            prompt = f"""
            Based on the data provided, analyze the project with ID {project_id} and provide a helpful response.
            
            Project data: {json.dumps(api_response, indent=2)}
            
            In your response:
            1. Provide an overview of the project
            2. Mention key information like status, timeline, team members, and associated tasks
            3. Present the information in a conversational way
            4. Don't include any JSON formatting or code blocks in your response
            """
        elif specific_intent == "task_by_id":
            task_id = parameters.get("task_id", "unknown")
            prompt = f"""
            Based on the data provided, analyze the task with ID {task_id} and provide a helpful response.
            
            Task data: {json.dumps(api_response, indent=2)}
            
            In your response:
            1. Provide an overview of the task
            2. Mention key information like status, priority, assignee, due date
            3. Present the information in a conversational way
            4. Don't include any JSON formatting or code blocks in your response
            """
        else:
            prompt = f"""
            Based on the data provided, analyze the information and provide a helpful response.
            
            Data: {json.dumps(api_response, indent=2)}
            
            In your response:
            1. Summarize the key information
            2. Present the information in a conversational way
            3. Don't include any JSON formatting or code blocks in your response
            """
        
        # Generate response using LLM
        self.logger.info(f"Generating response from API data using LLM")
        response = self.llm.invoke(prompt).content
        self.logger.info(f"Response generated: {response[:100]}...")
        
        return response
    
    def _handle_doc_query(self, query: str, specific_intent: str) -> str:
        """
        Handle document-related queries.
        
        Args:
            query: Original user query
            specific_intent: Specific document query intent
            
        Returns:
            Response to the user
        """
        # For specific intents, modify the search query to improve results
        search_query = query
        
        # Use more specific queries for known intents to improve retrieval
        if specific_intent == "upcoming_features":
            search_terms = ["upcoming features", "future features", "planned features", "new features", "real-time collaboration", "ai-powered"]
            self.logger.info(f"Using enhanced search terms for upcoming_features: {search_terms}")
            
            # Try multiple search terms to find the best matching documents
            all_docs = []
            for term in search_terms:
                docs = self.doc_processor.search_documents(term, k=2)
                # Add documents that aren't already in the list
                for doc in docs:
                    if not any(existing_doc.page_content == doc.page_content for existing_doc in all_docs):
                        all_docs.append(doc)
                
                # If we found good results, no need to try more terms
                if len(all_docs) >= 3:
                    break
            
            # Use the first three docs or whatever we found
            docs = all_docs[:3] if all_docs else []
            
            # If vector search didn't find enough results, try falling back to simple keyword search in the txt files
            if len(docs) < 2:
                self.logger.info("Vector search didn't yield enough results, trying direct keyword search")
                txt_docs = self._direct_keyword_search(specific_intent)
                if txt_docs:
                    # Add these documents if they're not already in the list
                    for doc in txt_docs:
                        if not any(existing_doc.page_content == doc.page_content for existing_doc in all_docs):
                            all_docs.append(doc)
                    
                    # Use up to three docs
                    docs = all_docs[:3] if all_docs else []
            
        elif specific_intent == "how_to_create_action":
            search_terms = ["create an action", "creating actions", "action steps", "new action"]
            self.logger.info(f"Using enhanced search terms for how_to_create_action: {search_terms}")
            
            # Try multiple search terms to find the best matching documents
            all_docs = []
            for term in search_terms:
                docs = self.doc_processor.search_documents(term, k=2)
                # Add documents that aren't already in the list
                for doc in docs:
                    if not any(existing_doc.page_content == doc.page_content for existing_doc in all_docs):
                        all_docs.append(doc)
                
                # If we found good results, no need to try more terms
                if len(all_docs) >= 3:
                    break
            
            # Use the first three docs or whatever we found
            docs = all_docs[:3] if all_docs else []
            
            # If vector search didn't find enough results, try falling back to simple keyword search in the txt files
            if len(docs) < 2:
                self.logger.info("Vector search didn't yield enough results, trying direct keyword search")
                txt_docs = self._direct_keyword_search(specific_intent)
                if txt_docs:
                    # Add these documents if they're not already in the list
                    for doc in txt_docs:
                        if not any(existing_doc.page_content == doc.page_content for existing_doc in all_docs):
                            all_docs.append(doc)
                    
                    # Use up to three docs
                    docs = all_docs[:3] if all_docs else []
            
        elif specific_intent == "system_requirements":
            search_terms = ["system requirements", "operating system", "browser", "requirements"]
            self.logger.info(f"Using enhanced search terms for system_requirements: {search_terms}")
            
            # Try multiple search terms to find the best matching documents
            all_docs = []
            for term in search_terms:
                docs = self.doc_processor.search_documents(term, k=2)
                # Add documents that aren't already in the list
                for doc in docs:
                    if not any(existing_doc.page_content == doc.page_content for existing_doc in all_docs):
                        all_docs.append(doc)
                
                # If we found good results, no need to try more terms
                if len(all_docs) >= 3:
                    break
            
            # Use the first three docs or whatever we found
            docs = all_docs[:3] if all_docs else []
            
            # If vector search didn't find enough results, try falling back to simple keyword search in the txt files
            if len(docs) < 2:
                self.logger.info("Vector search didn't yield enough results, trying direct keyword search")
                txt_docs = self._direct_keyword_search(specific_intent)
                if txt_docs:
                    # Add these documents if they're not already in the list
                    for doc in txt_docs:
                        if not any(existing_doc.page_content == doc.page_content for existing_doc in all_docs):
                            all_docs.append(doc)
                    
                    # Use up to three docs
                    docs = all_docs[:3] if all_docs else []
            
        else:
            # For general queries, perform a standard search
            docs = self.doc_processor.search_documents(search_query, k=3)
            
            # If vector search didn't find enough results, try falling back to simple keyword search in the txt files
            if len(docs) < 2:
                self.logger.info("Vector search didn't yield enough results, trying direct keyword search")
                txt_docs = self._direct_keyword_search(query)
                if txt_docs:
                    # Add these documents if they're not already in the list
                    for doc in txt_docs:
                        if not any(existing_doc.page_content == doc.page_content for existing_doc in docs):
                            docs.append(doc)
                    
                    # Use up to three docs
                    docs = docs[:3]
        
        if not docs:
            return "I couldn't find any documentation on that topic. Can you try rephrasing your question?"
        
        # Log the documents found
        self.logger.info(f"Found {len(docs)} documents for query")
        for i, doc in enumerate(docs):
            self.logger.info(f"Document {i+1}: {doc.page_content[:100]}...")
        
        # Format document content for the LLM
        doc_contents = "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])
        
        # Generate response with clear instructions to focus on the document content
        prompt = PromptTemplate(
            input_variables=["query", "doc_contents", "specific_intent"],
            template="""
            I need you to answer the following query based ONLY on the information provided in these documentation excerpts:
            
            {doc_contents}
            
            Query: {query}
            
            Your task is specifically about: {specific_intent}
            
            Provide a clear, conversational response using ONLY the information in the provided documents.
            If the exact answer isn't in the documents, acknowledge that limitation and provide the most relevant information that IS available.
            If the documents fully address the query, provide a complete and accurate answer based on them.
            """
        )
        
        response = self.llm.invoke(prompt.format(
            query=query, 
            doc_contents=doc_contents,
            specific_intent=specific_intent
        ))
        return response.content
        
    def _direct_keyword_search(self, query_or_intent: str) -> List[Document]:
        """
        Perform a direct keyword-based search on the text files.
        This is a fallback when vector search doesn't yield good results.
        
        Args:
            query_or_intent: The search query or intent
            
        Returns:
            List of documents that match the keywords
        """
        self.logger.info(f"Performing direct keyword search for: {query_or_intent}")
        
        # Map intents to relevant keywords
        intent_keywords = {
            "upcoming_features": ["upcoming features", "real-time collaboration", "ai-powered", "mobile experience", "analytics dashboard"],
            "how_to_create_action": ["create an action", "create new action", "action steps"],
            "system_requirements": ["system requirements", "operating system", "browser"]
        }
        
        # Get keywords based on intent or use the query directly
        keywords = intent_keywords.get(query_or_intent, [query_or_intent.lower()])
        
        results = []
        documents_dir = self.doc_processor.documents_dir
        
        # Search through text files
        for filename in os.listdir(documents_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(documents_dir, filename)
                try:
                    with open(filepath, 'r') as file:
                        content = file.read()
                        
                        # Check if any keyword is in the content
                        for keyword in keywords:
                            if keyword.lower() in content.lower():
                                # Find the section containing the keyword
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if keyword.lower() in line.lower():
                                        # Get context around the keyword - a window of lines
                                        start = max(0, i - 10)
                                        end = min(len(lines), i + 20)
                                        section = '\n'.join(lines[start:end])
                                        
                                        # Create a document with the relevant section
                                        doc = Document(page_content=section, metadata={"source": filename})
                                        results.append(doc)
                                        break  # Found a match in this file, move to next file
                                break  # Found a match with this keyword, move to next file
                                
                except Exception as e:
                    self.logger.error(f"Error reading file {filepath}: {e}")
        
        self.logger.info(f"Direct keyword search found {len(results)} matching documents")
        return results
    
    def process_query(self, query: str) -> str:
        """
        Process a user query and return a response.
        
        Args:
            query: User's query
            
        Returns:
            Agent's response
        """
        self.logger.info(f"Processing query: {query}")
        
        # Classify the query intent
        intent_type, intent_details = self._classify_query_intent(query)
        self.logger.info(f"Query classified as: {intent_type} with details: {intent_details}")
        
        # Handle based on intent type
        if intent_type == "API":
            self.logger.info(f"Handling as API query: {intent_details['specific_intent']}")
            response = self._handle_api_query(
                specific_intent=intent_details["specific_intent"],
                parameters=intent_details["parameters"]
            )
        else:  # intent_type == "DOCS"
            self.logger.info(f"Handling as DOCS query: {intent_details['specific_intent']}")
            response = self._handle_doc_query(
                query=query,
                specific_intent=intent_details["specific_intent"]
            )
        
        # Update conversation memory
        self.memory.save_context({"input": query}, {"output": response})
        self.logger.info(f"Response generated: {response[:100]}..." if len(response) > 100 else f"Response generated: {response}")
        
        return response 