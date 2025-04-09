import json
import logging
import requests
from typing import Dict, List, Any, Optional

class APIClient:
    """Client for interacting with the Java REST API."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
            
        # Setup logging
        self.logger = logging.getLogger('APIClient')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """
        Make an API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data
            
        Returns:
            API response as a dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.logger.info(f"Making {method} request to {url}")
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, params=params, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, params=params, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params, json=data, timeout=10)
            else:
                error_msg = f"Unsupported HTTP method: {method}"
                self.logger.error(error_msg)
                return {"error": error_msg, "status_code": 400}
            
            # Log the response status
            self.logger.info(f"Response status: {response.status_code}")
            
            # Raise for 4xx/5xx status codes
            response.raise_for_status()
            
            # Return JSON response or empty dict if no content
            if response.status_code == 204 or not response.content:
                return {}
                
            return response.json()
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "status_code": 503, "details": "API server is not reachable"}
            
        except requests.exceptions.Timeout as e:
            error_msg = f"Request timeout: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "status_code": 504, "details": "API request timed out"}
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error: {str(e)}"
            self.logger.error(error_msg)
            status_code = e.response.status_code if hasattr(e, 'response') and hasattr(e.response, 'status_code') else 500
            
            # Try to get more error details from response
            error_details = {}
            try:
                error_details = e.response.json()
            except:
                error_details = {"message": e.response.text} if hasattr(e, 'response') and hasattr(e.response, 'text') else {}
                
            return {"error": error_msg, "status_code": status_code, "details": error_details}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "status_code": 500}
            
        except ValueError as e:
            error_msg = f"Invalid JSON in response: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "status_code": 500, "details": "API returned invalid JSON"}
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "status_code": 500}
    
    # User-related endpoints
    
    def get_active_users(self) -> List[Dict]:
        """Get a list of active users."""
        return self._make_request('GET', '/api/users/active')
    
    def get_user_by_id(self, user_id: str) -> Dict:
        """Get user details by ID."""
        if not user_id:
            return {"error": "User ID is required", "status_code": 400}
        return self._make_request('GET', f'/api/users/{user_id}')
    
    def get_current_user(self) -> Dict:
        """Get current user information."""
        return self._make_request('GET', '/api/users/me')
    
    # Task-related endpoints
    
    def get_tasks_for_user(self, user_id: str) -> List[Dict]:
        """Get tasks assigned to a specific user."""
        if not user_id:
            return {"error": "User ID is required", "status_code": 400}
        return self._make_request('GET', f'/api/tasks/user/{user_id}')
    
    def get_my_tasks(self) -> List[Dict]:
        """Get tasks assigned to the current user."""
        return self._make_request('GET', '/api/tasks/me')
    
    def get_task_by_id(self, task_id: str) -> Dict:
        """Get task details by ID."""
        if not task_id:
            return {"error": "Task ID is required", "status_code": 400}
        return self._make_request('GET', f'/api/tasks/{task_id}')
    
    # Project-related endpoints
    
    def get_projects(self) -> List[Dict]:
        """Get a list of all projects."""
        return self._make_request('GET', '/api/projects')
    
    def get_project_by_id(self, project_id: str) -> Dict:
        """Get project details by ID."""
        if not project_id:
            return {"error": "Project ID is required", "status_code": 400}
        return self._make_request('GET', f'/api/projects/{project_id}')
    
    # Additional methods for custom API endpoints
    
    def custom_api_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """
        Make a custom API request for any endpoint.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data
            
        Returns:
            API response as a dictionary
        """
        return self._make_request(method, endpoint, params, data) 