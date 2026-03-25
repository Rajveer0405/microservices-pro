# Kubernetes Setup

## Build Docker Images

```powershell
cd c:\Users\91810\Desktop\microservice
docker build -t auth-service:latest .\auth_service
docker build -t user-service:latest .\user_service
```

## Apply Kubernetes Manifests

```powershell
kubectl apply -f .\k8s\auth-deployment.yaml
kubectl apply -f .\k8s\auth-service.yaml
kubectl apply -f .\k8s\user-deployment.yaml
kubectl apply -f .\k8s\user-service.yaml
```

## Check Resources

```powershell
kubectl get pods
kubectl get services
```

## Port Forward For Local Testing

```powershell
kubectl port-forward service/auth-service 8000:8000
```

```powershell
kubectl port-forward service/user-service 8001:8001
```

## Notes

- Inside Kubernetes, the user service calls the auth service using `http://auth-service:8000/verify`.
- SQLite is stored inside each container, so data is not durable if a pod is recreated.
