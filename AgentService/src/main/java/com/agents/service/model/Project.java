package com.agents.service.model;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Represents a project in the system.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Project information")
public class Project {
    @Schema(description = "Unique identifier for the project", example = "project-001")
    private String id;
    
    @Schema(description = "Name of the project", example = "API Modernization")
    private String name;
    
    @Schema(description = "Detailed description of the project", example = "Update and modernize the legacy API infrastructure")
    private String description;
    
    @Schema(description = "Current status of the project", example = "Active", allowableValues = {"Planning", "Active", "Completed", "On Hold"})
    private String status;
    
    @Schema(description = "Start date of the project", example = "2023-05-01", format = "date")
    private String startDate;
    
    @Schema(description = "End date of the project", example = "2023-08-31", format = "date")
    private String endDate;
    
    @Schema(description = "List of user IDs who are members of this project team", example = "[\"user-001\", \"user-002\"]")
    private List<String> teamMembers;
    
    @Schema(description = "List of task IDs associated with this project", example = "[\"task-001\", \"task-003\"]")
    private List<String> tasks;
} 