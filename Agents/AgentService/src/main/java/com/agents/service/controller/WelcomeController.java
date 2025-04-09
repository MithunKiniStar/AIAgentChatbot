package com.agents.service.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * Controller for the root endpoint.
 */
@RestController
public class WelcomeController {

    @Value("${spring.application.name}")
    private String appName;
    
    @Value("${server.port:8080}")
    private String serverPort;

    /**
     * Welcome message at the root endpoint.
     */
    @GetMapping("/")
    public Map<String, Object> welcome() {
        Map<String, Object> response = new HashMap<>();
        response.put("service", appName);
        response.put("status", "running");
        response.put("description", "REST API backend for AI Agent Chatbot");
        
        // Add documentation links
        Map<String, String> documentation = new HashMap<>();
        documentation.put("swagger_ui", "/swagger-ui");
        documentation.put("openapi_docs", "/api-docs");
        documentation.put("api_url", "http://localhost:" + serverPort);
        response.put("documentation", documentation);
        
        response.put("endpoints", new String[] {
                "/api/users/active",
                "/api/users/{userId}",
                "/api/users/me",
                "/api/tasks/user/{userId}",
                "/api/tasks/me",
                "/api/tasks/{taskId}",
                "/api/projects",
                "/api/projects/{projectId}"
        });
        
        return response;
    }
} 