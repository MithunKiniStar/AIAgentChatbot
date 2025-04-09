package com.agents.service;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Main entry point for the Agent Service application.
 * This Spring Boot application provides REST endpoints that mimic
 * the mock server used in the AI Agent Chatbot.
 */
@SpringBootApplication
public class AgentServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(AgentServiceApplication.class, args);
    }
} 