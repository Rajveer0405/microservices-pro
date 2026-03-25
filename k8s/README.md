# Kubernetes Setup

## Push Images To Docker Hub

```powershell
cd c:\Users\91810\Desktop\microservice
docker build -t rajveersinghrajput/auth-service:v1 .\auth_service
docker build -t rajveersinghrajput/user-service:v1 .\user_service
docker push rajveersinghrajput/auth-service:v1
docker push rajveersinghrajput/user-service:v1
```

After that, anyone who pulls this repo can deploy the same images without rebuilding them locally.

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
- The Kubernetes deployment files are now set to pull images from Docker Hub.
