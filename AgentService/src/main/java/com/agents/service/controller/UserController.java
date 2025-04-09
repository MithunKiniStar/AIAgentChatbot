package com.agents.service.controller;

import com.agents.service.model.User;
import com.agents.service.service.DataService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for user-related endpoints.
 */
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Tag(name = "User Controller", description = "API endpoints for user operations")
public class UserController {

    private final DataService dataService;

    /**
     * Get all active users.
     * @return List of active users
     */
    @Operation(summary = "Get all active users", description = "Returns a list of currently active users in the system")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved the list of active users", 
                         content = @Content(mediaType = "application/json", schema = @Schema(implementation = User.class)))
    })
    @GetMapping("/active")
    public List<User> getActiveUsers() {
        return dataService.getActiveUsers();
    }

    /**
     * Get a user by their ID.
     * @param userId The ID of the user to retrieve
     * @return The user with the specified ID or 404 if not found
     */
    @Operation(summary = "Get user by ID", description = "Returns a user based on their unique ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved the user", 
                         content = @Content(mediaType = "application/json", schema = @Schema(implementation = User.class))),
            @ApiResponse(responseCode = "404", description = "User not found")
    })
    @GetMapping("/{userId}")
    public ResponseEntity<User> getUserById(
            @Parameter(description = "ID of the user to retrieve", required = true) 
            @PathVariable String userId) {
        return dataService.getUserById(userId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get the current user (simulating an authenticated user).
     * @return The current user or 404 if not found
     */
    @Operation(summary = "Get current user", description = "Returns the currently authenticated user's information")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved the current user", 
                         content = @Content(mediaType = "application/json", schema = @Schema(implementation = User.class))),
            @ApiResponse(responseCode = "401", description = "Unauthorized, no current user found")
    })
    @GetMapping("/me")
    public ResponseEntity<User> getCurrentUser() {
        return dataService.getCurrentUser()
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.status(HttpStatus.UNAUTHORIZED).build());
    }
} 