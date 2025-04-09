package com.agents.service.controller;

import com.agents.service.model.Project;
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
 * REST controller for project-related endpoints.
 */
@RestController
@RequestMapping("/api/projects")
@RequiredArgsConstructor
@Tag(name = "Project Controller", description = "API endpoints for project operations")
public class ProjectController {

    private final DataService dataService;

    /**
     * Get all projects.
     * @return List of all projects
     */
    @Operation(summary = "Get all projects", description = "Returns a list of all projects in the system")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved the list of projects", 
                         content = @Content(mediaType = "application/json", schema = @Schema(implementation = Project.class)))
    })
    @GetMapping
    public List<Project> getAllProjects() {
        return dataService.getProjects();
    }

    /**
     * Get a project by its ID.
     * @param projectId The ID of the project to retrieve
     * @return The project with the specified ID or 404 if not found
     */
    @Operation(summary = "Get project by ID", description = "Returns a project based on its unique ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Successfully retrieved the project", 
                         content = @Content(mediaType = "application/json", schema = @Schema(implementation = Project.class))),
            @ApiResponse(responseCode = "404", description = "Project not found")
    })
    @GetMapping("/{projectId}")
    public ResponseEntity<Project> getProjectById(
            @Parameter(description = "ID of the project to retrieve", required = true)
            @PathVariable String projectId) {
        return dataService.getProjectById(projectId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
} 