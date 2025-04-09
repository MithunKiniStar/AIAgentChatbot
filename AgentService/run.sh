#!/bin/sh

# Build and run the AgentService

echo "Building AgentService..."
mvn clean package -DskipTests

if [ $? -eq 0 ]; then
    echo "Build successful. Starting the application..."
    java -jar target/AgentService-1.0.0.jar
else
    echo "Build failed. Please check the errors above."
    exit 1
fi 