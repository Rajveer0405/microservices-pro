# Minikube Guide For This Microservices Project

This guide explains how to run this FastAPI microservices project with Minikube.

The project has two services:

- `auth_service`
- `user_service`

In Kubernetes, these do not run as normal Docker containers like `auth_container` and `user_container`.
They run as:

- Deployments
- Pods
- Services

## What Minikube Is

Minikube is a local Kubernetes cluster.

It lets you run Kubernetes on your own machine for learning and testing.

With Minikube:

- Docker builds the images
- Kubernetes runs the pods
- Services allow pods to communicate

## Important Difference

These are different things:

- Docker container: `auth_container`, `user_container`
- Kubernetes pod: created by `Deployment`
- Kubernetes service: internal network name for pod communication

Your old Docker containers are not automatically used by Kubernetes.

Kubernetes needs its own images and resources.

## Files Used In This Project

Kubernetes manifest files:

- [k8s/auth-deployment.yaml](c:/Users/91810/Desktop/microservice/k8s/auth-deployment.yaml)
- [k8s/auth-service.yaml](c:/Users/91810/Desktop/microservice/k8s/auth-service.yaml)
- [k8s/user-deployment.yaml](c:/Users/91810/Desktop/microservice/k8s/user-deployment.yaml)
- [k8s/user-service.yaml](c:/Users/91810/Desktop/microservice/k8s/user-service.yaml)

Docker files:

- [auth_service/Dockerfile](c:/Users/91810/Desktop/microservice/auth_service/Dockerfile)
- [user_service/Dockerfile](c:/Users/91810/Desktop/microservice/user_service/Dockerfile)

Application file using Kubernetes service-to-service URL:

- [user_service/main.py](c:/Users/91810/Desktop/microservice/user_service/main.py)

## How Communication Works In Kubernetes

Inside Kubernetes, `user_service` does not call `localhost`.

It calls:

```text
http://auth-service:8000/verify
```

Why this works:

- `auth-service` is the Kubernetes Service name
- Kubernetes provides internal DNS
- `user_service` can find `auth_service` through that name

So in Kubernetes:

- `localhost` is wrong for cross-service communication
- service name is correct

## Full Flow

### 1. Start Minikube

```powershell
minikube start --driver=docker
```

This creates a local Kubernetes cluster.

### 2. Use Minikube's Docker Environment

```powershell
minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

Why this is needed:

- without this, Docker builds images in your normal Docker Desktop environment
- Kubernetes inside Minikube may not see those images
- with this command, images are built inside Minikube's Docker environment

### 3. Build Images

Run from project root:

```powershell
cd c:\Users\91810\Desktop\microservice
docker build -t auth-service:latest .\auth_service
docker build -t user-service:latest .\user_service
```

### 4. Apply Kubernetes Manifests

```powershell
kubectl apply -f .\k8s\auth-deployment.yaml
kubectl apply -f .\k8s\auth-service.yaml
kubectl apply -f .\k8s\user-deployment.yaml
kubectl apply -f .\k8s\user-service.yaml
```

This creates:

- one Deployment for auth
- one Service for auth
- one Deployment for user
- one Service for user

## What Each Kubernetes Resource Does

### Deployment

A Deployment manages pods.

Example:

- `auth-deployment.yaml` starts auth pods
- `user-deployment.yaml` starts user pods

If a pod crashes, Kubernetes recreates it.

### Pod

A pod is the running unit in Kubernetes.

Your FastAPI app actually runs inside a pod.

### Service

A Service gives stable networking to pods.

Example:

- `auth-service.yaml` creates the hostname `auth-service`
- `user-service.yaml` creates the hostname `user-service`

Even if pods restart, the Service name stays stable.

## Check Running Resources

Check pods:

```powershell
kubectl get pods
```

Check services:

```powershell
kubectl get services
```

Expected idea:

- auth pod should be `Running`
- user pod should be `Running`
- auth and user services should exist

## View Logs

Auth logs:

```powershell
kubectl logs deployment/auth-service
```

User logs:

```powershell
kubectl logs deployment/user-service
```

## Access The Services Locally

Kubernetes services are internal by default in this setup, so use port-forwarding.

In one terminal:

```powershell
kubectl port-forward service/auth-service 8000:8000
```

In another terminal:

```powershell
kubectl port-forward service/user-service 8001:8001
```

Then open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8001/docs`

## Test Flow

1. Open auth docs
2. Call `POST /signup`
3. Call `POST /login`
4. Copy the token
5. Open user docs
6. Click `Authorize`
7. Paste token
8. Call `POST /add_user`

## If Ports Are Busy

If you already have Docker containers running on `8000` or `8001`, stop them first:

```powershell
docker stop auth_container user_container
```

Why:

- Docker container port mappings can conflict with `kubectl port-forward`

## Useful Debug Commands

Describe pod:

```powershell
kubectl describe pod <pod-name>
```

See all resources:

```powershell
kubectl get all
```

Open Minikube dashboard:

```powershell
minikube dashboard
```

Check cluster status:

```powershell
minikube status
```

## Delete Kubernetes Resources

```powershell
kubectl delete -f .\k8s\auth-deployment.yaml
kubectl delete -f .\k8s\auth-service.yaml
kubectl delete -f .\k8s\user-deployment.yaml
kubectl delete -f .\k8s\user-service.yaml
```

## Stop Minikube

```powershell
minikube stop
```

## Common Confusion

### "I already built Docker images. Why build again?"

Because Minikube may use a different Docker environment.

That is why this command matters:

```powershell
minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

### "Are my old Docker containers used by Minikube?"

No.

Kubernetes creates its own pods from images.

### "How do services talk to each other?"

By Kubernetes Service name, not `localhost`.

For this project:

```text
http://auth-service:8000/verify
```

## Summary

Minikube workflow for this project:

1. Start Minikube
2. Point Docker to Minikube
3. Build images
4. Apply manifests
5. Check pods and services
6. Port-forward services
7. Test auth and user APIs

That is the basic Kubernetes lifecycle for your project on local machine.
