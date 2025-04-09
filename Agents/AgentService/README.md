# AgentService

This is a Java Spring Boot backend service that implements the same endpoints as the mock server in the AI Agent Chatbot. It provides REST APIs for users, tasks, and projects that the chatbot frontend can interact with.

## Project Structure

- `src/main/java/com/agents/service`: Main application code
  - `controller`: REST controllers for handling API endpoints
  - `model`: Data models (User, Task, Project)
  - `service`: Service layer for business logic
  - `config`: Application configuration
- `src/main/resources`: Application resources and configuration

## Prerequisites

- Java 17+
- Maven 3.6+

## Building the Application

```bash
mvn clean package
```

## Running the Application

```bash
java -jar target/AgentService-1.0.0.jar
```

Or using Maven:

```bash
mvn spring-boot:run
```

The application will start on port 8080 by default.

## API Documentation

The API is documented using OpenAPI/Swagger, which provides an interactive way to explore and test the endpoints.

Once the application is running, you can access:
- Swagger UI: http://localhost:8080/swagger-ui
- OpenAPI JSON: http://localhost:8080/api-docs

### Using Swagger UI

1. Start the application
2. Navigate to http://localhost:8080/swagger-ui in your browser
3. You'll see all available endpoints grouped by controller
4. Click on an endpoint to expand it
5. Use the "Try it out" button to test the endpoint
6. Fill in the required parameters
7. Click "Execute" to make a real API call
8. The response will be displayed below

## API Endpoints

### User Endpoints
- `GET /api/users/active`: Get all active users
- `GET /api/users/{userId}`: Get user by ID
- `GET /api/users/me`: Get current user

### Task Endpoints
- `GET /api/tasks/user/{userId}`: Get tasks for a specific user
- `GET /api/tasks/me`: Get tasks for current user
- `GET /api/tasks/{taskId}`: Get task by ID

### Project Endpoints
- `GET /api/projects`: Get all projects
- `GET /api/projects/{projectId}`: Get project by ID

## Integration with AI Agent Chatbot

To use this backend with the chatbot:

1. Start this Java backend service
2. In the chatbot application, set the `API_BASE_URL` to `http://localhost:8080` and disable the mock server
3. Run the chatbot as usual

## Sample Data

The service comes pre-loaded with sample data, including:
- 5 users (4 active, 1 inactive)
- 6 tasks with various priorities and statuses
- 2 projects with associated team members and tasks

## Docker Support

The application includes a Dockerfile for containerization:

```bash
# Build Docker image
docker build -t agentservice .

# Run Docker container
docker run -p 8080:8080 agentservice
``` 