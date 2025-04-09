package com.agents.service.controller;

import com.agents.service.model.Task;
import com.agents.service.service.DataService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for task-related endpoints.
 */
@RestController
@RequestMapping("/api/tasks")
@RequiredArgsConstructor
@Tag(name = "Task Controller", description = "API endpoints for task operations")
public class TaskController {

    private final DataService dataService;

    /**
     * Get tasks assigned to a specific user.
     * @param userId The ID of the user
     * @return List of tasks assigned to the user
     */
    @Operation(summary = "Get tasks for a user", description = "Returns all tasks assigned to a specific user")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved tasks for the user", 
                         content = @Content(mediaType = "application/json", schema = @Schema(implementation = Task.class)))
    })
    @GetMapping("/user/{userId}")
    public List<Task> getTasksForUser(
            @Parameter(description = "ID of the user to get tasks for", required = true)
            @PathVariable String userId) {
        return dataService.getTasksForUser(userId);
    }

    /**
     * Get tasks assigned to the current user.
     * @return List of tasks assigned to the current user
     */
    @Operation(summary = "Get my tasks", description = "Returns all tasks assigned to the currently authenticated user")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved tasks for the current user", 
                         content = @Content(mediaType = "application/json", schema = @Schema(implementation = Task.class)))
    })
    @GetMapping("/me")
    public List<Task> getMyTasks() {
        return dataService.getMyTasks();
    }

    /**
     * Get a task by its ID.
     * @param taskId The ID of the task to retrieve
     * @return The task with the specified ID or 404 if not found
     */
    @Operation(summary = "Get task by ID", description = "Returns a specific task based on its unique ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved the task", 
                         content = @Content(mediaType = "application/json", schema = @Schema(implementation = Task.class))),
            @ApiResponse(responseCode = "404", description = "Task not found")
    })
    @GetMapping("/{taskId}")
    public ResponseEntity<Task> getTaskById(
            @Parameter(description = "ID of the task to retrieve", required = true)
            @PathVariable String taskId) {
        return dataService.getTaskById(taskId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
} 