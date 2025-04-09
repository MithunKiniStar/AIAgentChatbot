import os
import logging
import numpy as np
from typing import List, Optional

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.embeddings.base import Embeddings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleEmbeddings(Embeddings):
    """Simple deterministic embeddings as fallback when API-based embeddings are unavailable."""
    
    def __init__(self, embedding_dim: int = 384):
        """Initialize with deterministic embedding parameters."""
        self.embedding_dim = embedding_dim
        logger.info(f"Initializing SimpleEmbeddings with dimension {embedding_dim}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate a deterministic embedding based on text content."""
        # Create a seed based on the text
        seed = sum(ord(c) for c in text)
        rng = np.random.RandomState(seed)
        
        # Generate a random vector with consistent output for the same input
        embedding = rng.randn(self.embedding_dim)
        
        # Normalize to unit length (cosine similarity requires this)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.tolist()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        logger.info(f"Embedding {len(texts)} documents")
        return [self._get_embedding(text) for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query."""
        logger.info(f"Embedding query: {text[:50]}...")
        return self._get_embedding(text)

class DocumentProcessor:
    """Class for processing documents and creating searchable indexes."""
    
    def __init__(self, documents_dir: str, chunk_size: int = 1000, chunk_overlap: int = 200, 
                 use_openai: bool = False, use_google: bool = True,
                 google_api_key: Optional[str] = None, 
                 openai_api_key: Optional[str] = None):
        """
        Initialize the document processor.
        
        Args:
            documents_dir: Directory containing documents
            chunk_size: Size of text chunks for indexing
            chunk_overlap: Overlap between text chunks
            use_openai: Whether to use OpenAI embeddings
            use_google: Whether to use Google AI embeddings
            google_api_key: Google API key for embeddings
            openai_api_key: OpenAI API key for embeddings
        """
        self.documents_dir = documents_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        
        # Get API keys from environment if not provided
        if google_api_key is None:
            google_api_key = os.environ.get("GOOGLE_API_KEY")
        if openai_api_key is None:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            
        # Initialize embeddings based on availability
        if use_google and google_api_key:
            try:
                logger.info("Initializing Google Generative AI Embeddings")
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=google_api_key,
                    task_type="retrieval_query"
                )
                logger.info("Successfully initialized Google Embeddings")
            except Exception as e:
                logger.error(f"Error initializing Google embeddings: {e}")
                logger.info("Falling back to SimpleEmbeddings")
                self.embeddings = SimpleEmbeddings()
        elif use_openai and openai_api_key:
            try:
                logger.info("Initializing OpenAI Embeddings")
                self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)
                logger.info("Successfully initialized OpenAI Embeddings")
            except Exception as e:
                logger.error(f"Error initializing OpenAI embeddings: {e}")
                logger.info("Falling back to SimpleEmbeddings")
                self.embeddings = SimpleEmbeddings()
        else:
            # Use simple embeddings as fallback
            try:
                self.embeddings = SimpleEmbeddings()
                logger.info("Successfully initialized SimpleEmbeddings")
            except Exception as e:
                logger.error(f"Error initializing embeddings: {e}")
                raise
            
        self.document_store = None
    
    def _load_pdf(self, pdf_path: str) -> List[Document]:
        """Load a PDF file and return documents."""
        try:
            logger.info(f"Loading PDF: {os.path.basename(pdf_path)}")
            loader = PyPDFLoader(pdf_path)
            return loader.load()
        except Exception as e:
            logger.warning(f"Error loading PDF {pdf_path}: {str(e)}")
            # If PDF loading fails, check if there's a corresponding .txt file
            txt_path = pdf_path.replace('.pdf', '.txt')
            if os.path.exists(txt_path):
                return self._load_text(txt_path)
            return []
    
    def _load_text(self, text_path: str) -> List[Document]:
        """Load a text file and return documents."""
        try:
            logger.info(f"Loading text file: {os.path.basename(text_path)}")
            loader = TextLoader(text_path)
            return loader.load()
        except Exception as e:
            logger.error(f"Error loading text file {text_path}: {str(e)}")
            return []
            
    def process_uploaded_file(self, file_path: str) -> List[Document]:
        """Process an uploaded file and return its documents."""
        if file_path.lower().endswith('.pdf'):
            return self._load_pdf(file_path)
        elif file_path.lower().endswith('.txt'):
            return self._load_text(file_path)
        else:
            logger.warning(f"Unsupported file format: {file_path}")
            return []
    
    def load_and_index_documents(self, additional_files: List[str] = None) -> None:
        """
        Load all documents in the documents directory and any additional files, then index them.
        
        Args:
            additional_files: List of additional file paths to process
        """
        all_docs = []
        
        # Process files in the directory
        if os.path.exists(self.documents_dir):
            for filename in os.listdir(self.documents_dir):
                filepath = os.path.join(self.documents_dir, filename)
                if not os.path.isfile(filepath):
                    continue
                    
                docs = []
                if filename.lower().endswith('.pdf'):
                    docs = self._load_pdf(filepath)
                elif filename.lower().endswith('.txt'):
                    docs = self._load_text(filepath)
                    
                all_docs.extend(docs)
        
        # Process additional files if provided
        if additional_files:
            for filepath in additional_files:
                if os.path.isfile(filepath):
                    docs = self.process_uploaded_file(filepath)
                    all_docs.extend(docs)
                
        if all_docs:
            # Split documents into chunks
            split_docs = self.text_splitter.split_documents(all_docs)
            
            try:
                # Create vector store
                self.document_store = FAISS.from_documents(split_docs, self.embeddings)
                logger.info(f"Indexed {len(split_docs)} document chunks from {len(all_docs)} documents")
            except Exception as e:
                logger.error(f"Error creating vector store: {e}")
                raise
        else:
            logger.warning("No documents found to index")
    
    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        """
        Search for documents relevant to the query.
        
        Args:
            query: The search query
            k: Number of documents to return
            
        Returns:
            List of relevant document chunks
        """
        if not self.document_store:
            logger.warning("Document store not initialized. Call load_and_index_documents first.")
            return []
        
        try:
            docs_with_scores = self.document_store.similarity_search_with_score(query, k=k)
            logger.info(f"Found {len(docs_with_scores)} document chunks for query: {query}")
            for i, (doc, score) in enumerate(docs_with_scores):
                logger.info(f"Doc {i+1} score: {score:.4f} - Content: {doc.page_content[:100]}...")
            return [doc for doc, score in docs_with_scores]
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
            
    def get_document_count(self) -> int:
        """Get the number of documents in the index."""
        if not self.document_store:
            return 0
            
        try:
            # This is a rough estimate as FAISS doesn't directly expose document count
            return len(self.document_store.index_to_docstore_id)
        except:
            return 0 