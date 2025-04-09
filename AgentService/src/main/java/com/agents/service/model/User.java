package com.agents.service.model;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents a user in the system.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "User information")
public class User {
    @Schema(description = "Unique identifier for the user", example = "user-001")
    private String id;
    
    @Schema(description = "Username for authentication", example = "john.doe")
    private String username;
    
    @Schema(description = "Full name of the user", example = "John Doe")
    private String name;
    
    @Schema(description = "Email address of the user", example = "john.doe@example.com")
    private String email;
    
    @Schema(description = "Whether the user is active in the system", example = "true")
    private boolean isActive;
    
    @Schema(description = "Role of the user in the organization", example = "Project Manager")
    private String role;
    
    @Schema(description = "Department the user belongs to", example = "Engineering")
    private String department;
} 