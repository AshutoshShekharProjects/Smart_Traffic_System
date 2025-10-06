#!/bin/bash

# Smart Traffic Control System - Deployment Script
# This script handles deployment to various cloud platforms

set -e

echo "🚦 Smart Traffic Control System - Deployment Script"
echo "=================================================="

# Configuration
PROJECT_NAME="smart-traffic-control"
VERSION="1.0.0"
REGISTRY="your-registry.com"  # Replace with your container registry

# Functions
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  local       Deploy locally with Docker Compose"
    echo "  aws         Deploy to AWS ECS"
    echo "  gcp         Deploy to Google Cloud Run"
    echo "  azure       Deploy to Azure Container Instances"
    echo "  build       Build Docker image only"
    echo "  help        Show this help message"
    echo ""
}

deploy_local() {
    echo "🏠 Deploying locally with Docker Compose..."
    
    # Create necessary directories
    mkdir -p data logs models
    
    # Build and start services
    docker-compose build
    docker-compose up -d
    
    echo "✅ Local deployment completed!"
    echo "🌐 Dashboard: http://localhost:5000"
    echo "📊 API: http://localhost:5000/api/current-traffic"
    echo ""
    echo "📋 Useful commands:"
    echo "  docker-compose logs -f    # View logs"
    echo "  docker-compose down       # Stop services"
    echo "  docker-compose restart    # Restart services"
}

build_image() {
    echo "🔨 Building Docker image..."
    
    # Build the image
    docker build -t $PROJECT_NAME:$VERSION .
    docker tag $PROJECT_NAME:$VERSION $PROJECT_NAME:latest
    
    echo "✅ Docker image built successfully!"
    echo "📦 Image: $PROJECT_NAME:$VERSION"
}

deploy_aws() {
    echo "☁️ Deploying to AWS ECS..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not found. Please install it first."
        exit 1
    fi
    
    # Build and push image
    build_image
    
    # Tag for ECR
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region)
    ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME"
    
    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI
    
    # Create ECR repository if it doesn't exist
    aws ecr describe-repositories --repository-names $PROJECT_NAME --region $AWS_REGION || \
    aws ecr create-repository --repository-name $PROJECT_NAME --region $AWS_REGION
    
    # Push image
    docker tag $PROJECT_NAME:latest $ECR_URI:latest
    docker push $ECR_URI:latest
    
    echo "✅ Image pushed to ECR: $ECR_URI:latest"
    echo "📝 Next steps:"
    echo "  1. Create ECS cluster"
    echo "  2. Create task definition using the pushed image"
    echo "  3. Create ECS service"
    echo "  4. Configure load balancer"
}

deploy_gcp() {
    echo "☁️ Deploying to Google Cloud Run..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        echo "❌ Google Cloud SDK not found. Please install it first."
        exit 1
    fi
    
    # Build and push to Google Container Registry
    PROJECT_ID=$(gcloud config get-value project)
    IMAGE_URI="gcr.io/$PROJECT_ID/$PROJECT_NAME:$VERSION"
    
    # Build and push
    docker build -t $IMAGE_URI .
    docker push $IMAGE_URI
    
    # Deploy to Cloud Run
    gcloud run deploy $PROJECT_NAME \
        --image $IMAGE_URI \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --port 5000 \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 10
    
    echo "✅ Deployed to Google Cloud Run!"
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $PROJECT_NAME --platform managed --region us-central1 --format 'value(status.url)')
    echo "🌐 Service URL: $SERVICE_URL"
}

deploy_azure() {
    echo "☁️ Deploying to Azure Container Instances..."
    
    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        echo "❌ Azure CLI not found. Please install it first."
        exit 1
    fi
    
    # Build image
    build_image
    
    # Create resource group
    RESOURCE_GROUP="smart-traffic-rg"
    LOCATION="eastus"
    
    az group create --name $RESOURCE_GROUP --location $LOCATION
    
    # Create container registry
    ACR_NAME="smarttrafficacr$(date +%s)"
    az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
    
    # Get ACR credentials
    ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv)
    ACR_USERNAME=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query username --output tsv)
    ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query passwords[0].value --output tsv)
    
    # Login and push image
    docker login $ACR_SERVER --username $ACR_USERNAME --password $ACR_PASSWORD
    docker tag $PROJECT_NAME:latest $ACR_SERVER/$PROJECT_NAME:latest
    docker push $ACR_SERVER/$PROJECT_NAME:latest
    
    # Deploy container instance
    az container create \
        --resource-group $RESOURCE_GROUP \
        --name $PROJECT_NAME \
        --image $ACR_SERVER/$PROJECT_NAME:latest \
        --registry-login-server $ACR_SERVER \
        --registry-username $ACR_USERNAME \
        --registry-password $ACR_PASSWORD \
        --dns-name-label $PROJECT_NAME-$(date +%s) \
        --ports 5000 \
        --cpu 1 \
        --memory 2
    
    echo "✅ Deployed to Azure Container Instances!"
    
    # Get container URL
    CONTAINER_FQDN=$(az container show --resource-group $RESOURCE_GROUP --name $PROJECT_NAME --query ipAddress.fqdn --output tsv)
    echo "🌐 Service URL: http://$CONTAINER_FQDN:5000"
}

# Main script logic
case "${1:-help}" in
    local)
        deploy_local
        ;;
    aws)
        deploy_aws
        ;;
    gcp)
        deploy_gcp
        ;;
    azure)
        deploy_azure
        ;;
    build)
        build_image
        ;;
    help|*)
        show_help
        ;;
esac