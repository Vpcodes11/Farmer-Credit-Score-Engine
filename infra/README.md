# Deployment Guide

## Docker Compose (Single Server)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

### Quick Start

```bash
# Clone repository
git clone https://github.com/youruser/farmer-credit-score-engine.git
cd farmer-credit-score-engine

# Run deployment script
chmod +x scripts/deploy_local.sh
./scripts/deploy_local.sh
```

### Manual Deployment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Scaling

```bash
# Scale API service
docker-compose up -d --scale api=3

# Scale worker service
docker-compose up -d --scale worker=2
```

---

## Kubernetes (Production)

### Prerequisites
- Kubernetes cluster (1.24+)
- kubectl configured
- 3 nodes minimum (2 CPU, 4GB RAM each)
- Ingress controller (nginx)
- Cert-manager (optional, for TLS)

### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name fcs-engine \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3

# Configure kubectl
aws eks update-kubeconfig --name fcs-engine --region us-east-1

# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/aws/deploy.yaml

# Deploy application
kubectl apply -f k8s/
```

### Azure AKS

```bash
# Create resource group
az group create --name fcs-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group fcs-rg \
  --name fcs-engine \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --enable-addons monitoring

# Get credentials
az aks get-credentials --resource-group fcs-rg --name fcs-engine

# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Deploy application
kubectl apply -f k8s/
```

### Google GKE

```bash
# Create GKE cluster
gcloud container clusters create fcs-engine \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2

# Get credentials
gcloud container clusters get-credentials fcs-engine --zone us-central1-a

# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Deploy application
kubectl apply -f k8s/
```

### Configuration

1. **Edit Secrets**:
```bash
# Edit k8s/configmap.yaml with your values
nano k8s/configmap.yaml

# IMPORTANT: Change JWT_SECRET and database passwords
```

2. **Update Image Names**:
```bash
# Replace 'youruser' with your Docker Hub username in:
# - k8s/api.yaml
# - k8s/frontend.yaml
# - k8s/dashboard.yaml
# - k8s/worker.yaml
```

3. **Configure Ingress**:
```bash
# Edit k8s/ingress.yaml
# Replace 'fcs.example.com' with your domain
```

### Deployment

```bash
# Apply all manifests
kubectl apply -f k8s/

# Watch deployment
kubectl get pods -n fcs-engine -w

# Check services
kubectl get svc -n fcs-engine

# Get ingress IP
kubectl get ingress -n fcs-engine
```

### Verification

```bash
# Check pod status
kubectl get pods -n fcs-engine

# Check logs
kubectl logs -f deployment/api -n fcs-engine

# Test API health
kubectl port-forward svc/api 8000:8000 -n fcs-engine
curl http://localhost:8000/healthz
```

### Monitoring

```bash
# Install Prometheus + Grafana (optional)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
# Default credentials: admin / prom-operator
```

---

## CI/CD Setup

### GitHub Secrets

Configure the following secrets in your GitHub repository:

```
DOCKERHUB_USER=your-dockerhub-username
DOCKERHUB_TOKEN=your-dockerhub-token
KUBECONFIG=base64-encoded-kubeconfig
API_URL=https://api.fcs.example.com
```

### Get KUBECONFIG

```bash
# Encode kubeconfig
cat ~/.kube/config | base64 -w 0

# Add to GitHub Secrets as KUBECONFIG
```

### Trigger Deployment

```bash
# Push to main branch
git push origin main

# GitHub Actions will:
# 1. Build Docker images
# 2. Push to Docker Hub
# 3. Deploy to Kubernetes
```

---

## Troubleshooting

### Pods not starting

```bash
# Describe pod
kubectl describe pod POD_NAME -n fcs-engine

# Check events
kubectl get events -n fcs-engine --sort-by='.lastTimestamp'
```

### Database connection errors

```bash
# Check PostgreSQL pod
kubectl logs statefulset/postgres -n fcs-engine

# Test connection
kubectl exec -it postgres-0 -n fcs-engine -- psql -U postgres -d fcs
```

### Ingress not working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress
kubectl describe ingress fcs-ingress -n fcs-engine

# Test backend
kubectl port-forward svc/api 8000:8000 -n fcs-engine
```

---

## Backup & Restore

### Backup Database

```bash
# Create backup
kubectl exec postgres-0 -n fcs-engine -- pg_dump -U postgres fcs > backup.sql

# Copy to local
kubectl cp fcs-engine/postgres-0:/backup.sql ./backup.sql
```

### Restore Database

```bash
# Copy backup to pod
kubectl cp ./backup.sql fcs-engine/postgres-0:/backup.sql

# Restore
kubectl exec postgres-0 -n fcs-engine -- psql -U postgres fcs < /backup.sql
```

---

## Scaling

### Horizontal Pod Autoscaling

```bash
# Create HPA for API
kubectl autoscale deployment api -n fcs-engine \
  --cpu-percent=70 \
  --min=2 \
  --max=10

# Check HPA
kubectl get hpa -n fcs-engine
```

### Vertical Scaling

```bash
# Edit deployment
kubectl edit deployment api -n fcs-engine

# Update resources:
#   requests:
#     memory: "512Mi"
#     cpu: "500m"
#   limits:
#     memory: "1Gi"
#     cpu: "1000m"
```

---

## Security

### Network Policies

```bash
# Apply network policies
kubectl apply -f k8s/network-policies.yaml
```

### Secrets Management

```bash
# Use external secrets (recommended)
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace

# Configure with AWS Secrets Manager / Azure Key Vault / GCP Secret Manager
```

---

## Cost Optimization

### AWS EKS
- Use Spot Instances for worker nodes
- Enable Cluster Autoscaler
- Use Fargate for worker pods

### Azure AKS
- Use Azure Spot VMs
- Enable cluster autoscaler
- Use Azure Container Instances for burst workloads

### Google GKE
- Use Preemptible VMs
- Enable node auto-provisioning
- Use GKE Autopilot mode

---

**Last Updated**: 2024-11-25  
**Version**: 1.0  
**Contact**: devops@example.com
