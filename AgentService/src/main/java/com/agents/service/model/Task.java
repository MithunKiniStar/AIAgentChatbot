package com.agents.service.model;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents a task in the system.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Task information")
public class Task {
    @Schema(description = "Unique identifier for the task", example = "task-001")
    private String id;
    
    @Schema(description = "Title of the task", example = "Implement user authentication")
    private String title;
    
    @Schema(description = "Detailed description of the task", example = "Add OAuth2 authentication to the API endpoints")
    private String description;
    
    @Schema(description = "Current status of the task", example = "In Progress", allowableValues = {"To Do", "In Progress", "Done"})
    private String status;
    
    @Schema(description = "Priority level of the task", example = "High", allowableValues = {"Low", "Medium", "High"})
    private String priority;
    
    @Schema(description = "User ID of the person assigned to this task", example = "user-001")
    private String assignee;  // User ID
    
    @Schema(description = "Due date for the task completion", example = "2023-06-15", format = "date")
    private String dueDate;
    
    @Schema(description = "Project ID that this task belongs to", example = "project-001")
    private String projectId;
    
    @Schema(description = "Date when the task was created", example = "2023-05-20", format = "date")
    private String createdAt;
} 