import json
from typing import Dict, List, Any, Optional

class MockAPIServer:
    """
    Mock server to simulate responses from the Java REST API.
    This is used for development and testing purposes.
    """
    
    def __init__(self):
        """Initialize the mock server with sample data."""
        self._load_mock_data()
    
    def _load_mock_data(self):
        """Load mock data for all API endpoints."""
        # Users data
        self.users = [
            {
                "id": "user-001",
                "username": "john.doe",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "isActive": True,
                "role": "Project Manager",
                "department": "Engineering"
            },
            {
                "id": "user-002",
                "username": "jane.smith",
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "isActive": True,
                "role": "Developer",
                "department": "Engineering"
            },
            {
                "id": "user-003",
                "username": "bob.johnson",
                "name": "Bob Johnson",
                "email": "bob.johnson@example.com",
                "isActive": False,
                "role": "Designer",
                "department": "Product"
            },
            {
                "id": "user-004",
                "username": "alice.williams",
                "name": "Alice Williams",
                "email": "alice.williams@example.com",
                "isActive": True,
                "role": "QA Engineer",
                "department": "Quality Assurance"
            },
            {
                "id": "user-005",
                "username": "current.user",
                "name": "Current User",
                "email": "current.user@example.com",
                "isActive": True,
                "role": "Team Lead",
                "department": "Engineering"
            }
        ]
        
        # Tasks data
        self.tasks = [
            {
                "id": "task-001",
                "title": "Implement user authentication",
                "description": "Add OAuth2 authentication to the API endpoints",
                "status": "In Progress",
                "priority": "High",
                "assignee": "user-002",
                "dueDate": "2023-06-15",
                "projectId": "project-001",
                "createdAt": "2023-05-20"
            },
            {
                "id": "task-002",
                "title": "Design landing page",
                "description": "Create a responsive design for the application landing page",
                "status": "To Do",
                "priority": "Medium",
                "assignee": "user-003",
                "dueDate": "2023-06-20",
                "projectId": "project-002",
                "createdAt": "2023-05-22"
            },
            {
                "id": "task-003",
                "title": "Fix navigation bug",
                "description": "Address issue with dropdown menu not working in Safari",
                "status": "In Progress",
                "priority": "High",
                "assignee": "user-002",
                "dueDate": "2023-06-10",
                "projectId": "project-001",
                "createdAt": "2023-05-25"
            },
            {
                "id": "task-004",
                "title": "Write API documentation",
                "description": "Document all API endpoints using Swagger",
                "status": "To Do",
                "priority": "Medium",
                "assignee": "user-001",
                "dueDate": "2023-06-25",
                "projectId": "project-001",
                "createdAt": "2023-05-28"
            },
            {
                "id": "task-005",
                "title": "Implement dashboard widgets",
                "description": "Add customizable widgets to the user dashboard",
                "status": "To Do",
                "priority": "Medium",
                "assignee": "user-005",
                "dueDate": "2023-06-30",
                "projectId": "project-002",
                "createdAt": "2023-05-29"
            },
            {
                "id": "task-006",
                "title": "Performance optimization",
                "description": "Optimize database queries for faster page loads",
                "status": "In Progress",
                "priority": "High",
                "assignee": "user-005",
                "dueDate": "2023-06-18",
                "projectId": "project-001",
                "createdAt": "2023-05-30"
            }
        ]
        
        # Projects data
        self.projects = [
            {
                "id": "project-001",
                "name": "API Modernization",
                "description": "Update and modernize the legacy API infrastructure",
                "status": "Active",
                "startDate": "2023-05-01",
                "endDate": "2023-08-31",
                "teamMembers": ["user-001", "user-002", "user-005"],
                "tasks": ["task-001", "task-003", "task-004", "task-006"]
            },
            {
                "id": "project-002",
                "name": "Website Redesign",
                "description": "Complete overhaul of the company website",
                "status": "Active",
                "startDate": "2023-04-15",
                "endDate": "2023-07-31",
                "teamMembers": ["user-001", "user-003", "user-005"],
                "tasks": ["task-002", "task-005"]
            }
        ]
        
        # Set the current user ID
        self.current_user_id = "user-005"
    
    # API endpoint implementations
    
    def get_active_users(self) -> List[Dict]:
        """Get all active users."""
        return [user for user in self.users if user.get("isActive", False)]
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None
    
    def get_current_user(self) -> Dict:
        """Get the current user."""
        return self.get_user_by_id(self.current_user_id)
    
    def get_tasks_for_user(self, user_id: str) -> List[Dict]:
        """Get tasks assigned to a specific user."""
        return [task for task in self.tasks if task["assignee"] == user_id]
    
    def get_my_tasks(self) -> List[Dict]:
        """Get tasks assigned to the current user."""
        return self.get_tasks_for_user(self.current_user_id)
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get task by ID."""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def get_projects(self) -> List[Dict]:
        """Get all projects."""
        return self.projects
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict]:
        """Get project by ID."""
        for project in self.projects:
            if project["id"] == project_id:
                return project
        return None 