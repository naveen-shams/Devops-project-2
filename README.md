# DevOps Todo App — Full Pipeline Project

A production-grade DevOps project covering all 5 pillars:
**Docker → CI/CD (GitHub Actions) → Terraform (AWS) → Kubernetes → Prometheus + Grafana**

---

## Project Structure

```
devops-project/
├── app/
│   ├── main.py              # Flask REST API + /metrics endpoint
│   └── requirements.txt
├── tests/
│   └── test_app.py          # pytest test suite
├── Dockerfile               # Multi-stage production image
├── docker-compose.yml       # Local dev: app + prometheus + grafana
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # GitHub Actions: test → build → deploy
├── terraform/
│   ├── main.tf              # VPC, EC2, S3, Security Groups
│   ├── variables.tf
│   ├── outputs.tf
│   └── userdata.sh          # Bootstrap: Docker + Minikube on EC2
├── k8s/
│   ├── namespace.yml
│   ├── deployment.yml       # 2 replicas + HPA (auto-scaling)
│   ├── service.yml
│   └── ingress.yml
└── monitoring/
    ├── prometheus/
    │   ├── prometheus.yml   # Scrape config + k8s pod discovery
    │   └── alert_rules.yml  # Error rate, latency, uptime alerts
    └── grafana/
        └── provisioning/    # Auto-loaded datasource + dashboard
```

---

## Getting Started

### Prerequisites
- Docker & docker-compose
- Terraform >= 1.7
- AWS CLI (configured with `aws configure`)
- kubectl
- A Docker Hub account

---

## Phase 1 — Run the app locally

```bash
# Run Flask app only
cd app
pip install -r requirements.txt
python main.py

# Or with the full monitoring stack
docker-compose up --build
```

- App: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / admin)

---

## Phase 2 — Run tests

```bash
pip install -r app/requirements.txt
pytest tests/ -v
```

---

## Phase 3 — Set up GitHub Actions

Add these secrets to your GitHub repo (Settings → Secrets):

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `AWS_ACCESS_KEY_ID` | AWS IAM key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret |

Push to `main` — the pipeline will test, build, and deploy automatically.

---

## Phase 4 — Provision AWS infrastructure

```bash
cd terraform

# First time only: create the S3 bucket for state
aws s3 mb s3://devops-todo-tfstate --region ap-south-1

# Deploy infrastructure
terraform init
terraform plan
terraform apply
```

SSH into the server:
```bash
ssh ubuntu@$(terraform output -raw server_public_ip)
```

---

## Phase 5 — Deploy to Kubernetes

```bash
# Update image name in k8s/deployment.yml first
# Then apply:
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml

# Check status
kubectl get pods -n todo-app
kubectl get svc -n todo-app
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Health check |
| GET | /metrics | Prometheus metrics |
| GET | /api/todos | List all todos |
| POST | /api/todos | Create a todo `{"title": "..."}` |
| GET | /api/todos/:id | Get one todo |
| PUT | /api/todos/:id | Update a todo |
| DELETE | /api/todos/:id | Delete a todo |

---

## What you learn from this project

- Containerising a Python app with Docker
- Writing a real CI/CD pipeline that runs on every push
- Provisioning cloud infrastructure as code with Terraform
- Deploying and auto-scaling with Kubernetes
- Observing a live app with Prometheus metrics and Grafana dashboards
- Setting up alert rules for production issues
