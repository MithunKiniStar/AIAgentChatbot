package com.agents.service.service;

import com.agents.service.model.Project;
import com.agents.service.model.Task;
import com.agents.service.model.User;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

/**
 * Service for providing mock data similar to what was used in the Python mock server.
 * In a real application, this would interact with a database or other services.
 */
@Service
public class DataService {

    private List<User> users = new ArrayList<>();
    private List<Task> tasks = new ArrayList<>();
    private List<Project> projects = new ArrayList<>();
    
    // The current user ID (simulating an authenticated user)
    private final String currentUserId = "user-005";

    /**
     * Initialize the mock data when the service starts.
     */
    @PostConstruct
    public void initMockData() {
        // Initialize users
        users.add(User.builder()
                .id("user-001")
                .username("john.doe")
                .name("John Doe")
                .email("john.doe@example.com")
                .isActive(true)
                .role("Project Manager")
                .department("Engineering")
                .build());
        
        users.add(User.builder()
                .id("user-002")
                .username("jane.smith")
                .name("Jane Smith")
                .email("jane.smith@example.com")
                .isActive(true)
                .role("Developer")
                .department("Engineering")
                .build());
        
        users.add(User.builder()
                .id("user-003")
                .username("bob.johnson")
                .name("Bob Johnson")
                .email("bob.johnson@example.com")
                .isActive(false)
                .role("Designer")
                .department("Product")
                .build());
        
        users.add(User.builder()
                .id("user-004")
                .username("alice.williams")
                .name("Alice Williams")
                .email("alice.williams@example.com")
                .isActive(true)
                .role("QA Engineer")
                .department("Quality Assurance")
                .build());
        
        users.add(User.builder()
                .id("user-005")
                .username("current.user")
                .name("Current User")
                .email("current.user@example.com")
                .isActive(true)
                .role("Team Lead")
                .department("Engineering")
                .build());

        // Initialize tasks
        tasks.add(Task.builder()
                .id("task-001")
                .title("Implement user authentication")
                .description("Add OAuth2 authentication to the API endpoints")
                .status("In Progress")
                .priority("High")
                .assignee("user-002")
                .dueDate("2023-06-15")
                .projectId("project-001")
                .createdAt("2023-05-20")
                .build());
        
        tasks.add(Task.builder()
                .id("task-002")
                .title("Design landing page")
                .description("Create a responsive design for the application landing page")
                .status("To Do")
                .priority("Medium")
                .assignee("user-003")
                .dueDate("2023-06-20")
                .projectId("project-002")
                .createdAt("2023-05-22")
                .build());
        
        tasks.add(Task.builder()
                .id("task-003")
                .title("Fix navigation bug")
                .description("Address issue with dropdown menu not working in Safari")
                .status("In Progress")
                .priority("High")
                .assignee("user-002")
                .dueDate("2023-06-10")
                .projectId("project-001")
                .createdAt("2023-05-25")
                .build());
        
        tasks.add(Task.builder()
                .id("task-004")
                .title("Write API documentation")
                .description("Document all API endpoints using Swagger")
                .status("To Do")
                .priority("Medium")
                .assignee("user-001")
                .dueDate("2023-06-25")
                .projectId("project-001")
                .createdAt("2023-05-28")
                .build());
        
        tasks.add(Task.builder()
                .id("task-005")
                .title("Implement dashboard widgets")
                .description("Add customizable widgets to the user dashboard")
                .status("To Do")
                .priority("Medium")
                .assignee("user-005")
                .dueDate("2023-06-30")
                .projectId("project-002")
                .createdAt("2023-05-29")
                .build());
        
        tasks.add(Task.builder()
                .id("task-006")
                .title("Performance optimization")
                .description("Optimize database queries for faster page loads")
                .status("In Progress")
                .priority("High")
                .assignee("user-005")
                .dueDate("2023-06-18")
                .projectId("project-001")
                .createdAt("2023-05-30")
                .build());

        // Initialize projects
        projects.add(Project.builder()
                .id("project-001")
                .name("API Modernization")
                .description("Update and modernize the legacy API infrastructure")
                .status("Active")
                .startDate("2023-05-01")
                .endDate("2023-08-31")
                .teamMembers(Arrays.asList("user-001", "user-002", "user-005"))
                .tasks(Arrays.asList("task-001", "task-003", "task-004", "task-006"))
                .build());
        
        projects.add(Project.builder()
                .id("project-002")
                .name("Website Redesign")
                .description("Complete overhaul of the company website")
                .status("Active")
                .startDate("2023-04-15")
                .endDate("2023-07-31")
                .teamMembers(Arrays.asList("user-001", "user-003", "user-005"))
                .tasks(Arrays.asList("task-002", "task-005"))
                .build());
    }

    /**
     * Get all active users.
     */
    public List<User> getActiveUsers() {
        return users.stream()
                .filter(User::isActive)
                .toList();
    }

    /**
     * Get a user by their ID.
     */
    public Optional<User> getUserById(String userId) {
        return users.stream()
                .filter(user -> user.getId().equals(userId))
                .findFirst();
    }

    /**
     * Get the current user (simulating an authenticated user).
     */
    public Optional<User> getCurrentUser() {
        return getUserById(currentUserId);
    }

    /**
     * Get tasks assigned to a specific user.
     */
    public List<Task> getTasksForUser(String userId) {
        return tasks.stream()
                .filter(task -> task.getAssignee().equals(userId))
                .toList();
    }

    /**
     * Get tasks assigned to the current user.
     */
    public List<Task> getMyTasks() {
        return getTasksForUser(currentUserId);
    }

    /**
     * Get a task by its ID.
     */
    public Optional<Task> getTaskById(String taskId) {
        return tasks.stream()
                .filter(task -> task.getId().equals(taskId))
                .findFirst();
    }

    /**
     * Get all projects.
     */
    public List<Project> getProjects() {
        return projects;
    }

    /**
     * Get a project by its ID.
     */
    public Optional<Project> getProjectById(String projectId) {
        return projects.stream()
                .filter(project -> project.getId().equals(projectId))
                .findFirst();
    }
} 