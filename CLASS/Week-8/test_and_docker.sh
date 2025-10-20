#!/bin/bash
# Complete Testing and Dockerization Script for FastAPI + W&B

set -e

echo "=================================================="
echo "FastAPI + W&B - Testing & Docker Deployment"
echo "=================================================="

# Set working directory
cd /home/chakri/Documents/S-7/MLoPs/Mlops2025w-112201022/CLASS/Week-8

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Set environment variables
echo -e "\n${YELLOW}Step 1: Setting environment variables${NC}"
export WANDB_API_KEY='fbd5089fe8ff8a2f6dfc053ad7ac625ab10a7a2f'

# Get username from W&B
WANDB_USERNAME=$(python3 -c "import wandb; api = wandb.Api(); user = api.viewer; print(user.username if hasattr(user, 'username') else user.entity)" 2>/dev/null || echo "unknown")
export WANDB_MODEL_ARTIFACT="${WANDB_USERNAME}/classroom-deploy/iris-rf:latest"

echo -e "${GREEN}✓ WANDB_API_KEY set${NC}"
echo -e "${GREEN}✓ WANDB_MODEL_ARTIFACT: ${WANDB_MODEL_ARTIFACT}${NC}"

# Step 2: Test with Python requests (no server needed, direct artifact test)
echo -e "\n${YELLOW}Step 2: Testing artifact download and inference${NC}"
python3 << 'EOF'
import wandb
import joblib
import numpy as np
import os

api = wandb.Api()
user = api.viewer
username = user.username if hasattr(user, 'username') else user.entity
artifact_ref = f'{username}/classroom-deploy/iris-rf:latest'

print(f"Downloading artifact: {artifact_ref}")
artifact = api.artifact(artifact_ref)
path = artifact.download()
print(f"✓ Downloaded to: {path}")

model = joblib.load(os.path.join(path, 'model.pkl'))
sample = np.array([5.1, 3.5, 1.4, 0.2]).reshape(1, -1)
prediction = model.predict(sample)[0]
print(f"✓ Test prediction: {prediction} (Iris class)")
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Artifact test successful${NC}"
else
    echo -e "${RED}✗ Artifact test failed${NC}"
    exit 1
fi

# Step 3: Start FastAPI server in background
echo -e "\n${YELLOW}Step 3: Starting FastAPI server${NC}"
echo "Starting server on http://localhost:8080"

# Kill any existing process on port 8080
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# Start server in background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8080 > /tmp/fastapi.log 2>&1 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✓ Server started successfully${NC}"
else
    echo -e "${RED}✗ Server failed to start. Check /tmp/fastapi.log${NC}"
    cat /tmp/fastapi.log
    exit 1
fi

# Step 4: Test with curl
echo -e "\n${YELLOW}Step 4: Testing API with curl${NC}"

echo "Testing root endpoint..."
curl -s http://localhost:8080/ | python3 -m json.tool

echo -e "\nTesting predict endpoint..."
RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" --data '[5.1,3.5,1.4,0.2]' http://localhost:8080/predict)
echo $RESPONSE | python3 -m json.tool

if [[ $RESPONSE == *"prediction"* ]]; then
    echo -e "${GREEN}✓ API test successful${NC}"
else
    echo -e "${RED}✗ API test failed${NC}"
    kill $SERVER_PID
    exit 1
fi

# Step 5: Test with Python requests
echo -e "\n${YELLOW}Step 5: Testing with Python requests${NC}"
python3 << 'EOF'
import requests
import json

# Test root
response = requests.get('http://localhost:8080/')
print(f"Status endpoint: {response.json()}")

# Test prediction
data = [5.1, 3.5, 1.4, 0.2]
response = requests.post('http://localhost:8080/predict', json=data)
result = response.json()
print(f"Prediction endpoint: {result}")
print(f"✓ Predicted Iris class: {result['prediction']}")
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python requests test successful${NC}"
else
    echo -e "${RED}✗ Python requests test failed${NC}"
fi

# Kill the server
echo -e "\n${YELLOW}Stopping FastAPI server${NC}"
kill $SERVER_PID 2>/dev/null || true
echo -e "${GREEN}✓ Server stopped${NC}"

# Step 6: Docker Build
echo -e "\n${YELLOW}Step 6: Building Docker image${NC}"
cd app
docker build -t iris-wandb:local . 2>&1 | tail -20

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi

cd ..

# Step 7: Run Docker container
echo -e "\n${YELLOW}Step 7: Running Docker container${NC}"

# Stop any existing container
docker stop iris-wandb-test 2>/dev/null || true
docker rm iris-wandb-test 2>/dev/null || true

# Run container
docker run -d \
  --name iris-wandb-test \
  -e WANDB_API_KEY="$WANDB_API_KEY" \
  -e WANDB_MODEL_ARTIFACT="$WANDB_MODEL_ARTIFACT" \
  -p 8080:8080 \
  iris-wandb:local

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker container started${NC}"
else
    echo -e "${RED}✗ Failed to start container${NC}"
    exit 1
fi

# Wait for container to be ready
echo "Waiting for container to initialize..."
sleep 10

# Step 8: Test Docker container
echo -e "\n${YELLOW}Step 8: Testing Dockerized API${NC}"

echo "Testing root endpoint..."
curl -s http://localhost:8080/ | python3 -m json.tool

echo -e "\nTesting predict endpoint..."
DOCKER_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" --data '[5.1,3.5,1.4,0.2]' http://localhost:8080/predict)
echo $DOCKER_RESPONSE | python3 -m json.tool

if [[ $DOCKER_RESPONSE == *"prediction"* ]]; then
    echo -e "${GREEN}✓ Docker container test successful${NC}"
else
    echo -e "${RED}✗ Docker container test failed${NC}"
    echo "Container logs:"
    docker logs iris-wandb-test
    docker stop iris-wandb-test
    exit 1
fi

# Show container info
echo -e "\n${YELLOW}Container Information:${NC}"
docker ps | grep iris-wandb-test

echo -e "\n${GREEN}=================================================="
echo "✓ ALL TESTS PASSED!"
echo "==================================================${NC}"

echo -e "\n${YELLOW}Quick Commands:${NC}"
echo "View logs:     docker logs iris-wandb-test"
echo "Stop:          docker stop iris-wandb-test"
echo "Remove:        docker rm iris-wandb-test"
echo "Test API:      curl -X POST -H 'Content-Type: application/json' --data '[5.1,3.5,1.4,0.2]' http://localhost:8080/predict"

echo -e "\n${YELLOW}Keep container running? (y/n)${NC}"
read -t 10 -p "Press 'n' to stop and remove container, or wait 10s to keep running: " response || response="y"

if [[ $response == "n" ]]; then
    docker stop iris-wandb-test
    docker rm iris-wandb-test
    echo -e "${GREEN}✓ Container stopped and removed${NC}"
else
    echo -e "${GREEN}✓ Container still running on http://localhost:8080${NC}"
fi
