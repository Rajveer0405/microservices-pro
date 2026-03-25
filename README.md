# FastAPI Microservices Example

This project contains two simple FastAPI microservices:

- `auth_service`: handles login and token verification
- `user_service`: manages users and validates tokens through the auth service

Both services use SQLite for persistence:

- `auth_service/auth.db`: stores demo users and issued tokens
- `user_service/users.db`: stores user records

## Docker Files

- `auth_service/Dockerfile`
- `user_service/Dockerfile`

## Kubernetes Files

- `k8s/auth-deployment.yaml`
- `k8s/auth-service.yaml`
- `k8s/user-deployment.yaml`
- `k8s/user-service.yaml`

## Folder Structure

```text
microservice/
|-- auth_service/
|   |-- main.py
|   `-- requirements.txt
|-- user_service/
|   |-- main.py
|   `-- requirements.txt
`-- README.md
```

## Install Dependencies

Open two terminals and install dependencies for each service:

```powershell
cd auth_service
pip install -r requirements.txt
```

```powershell
cd user_service
pip install -r requirements.txt
```

## Run Services

Start the auth service on port `8000`:

```powershell
cd auth_service
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Start the user service on port `8001`:

```powershell
cd user_service
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

## Sample Requests

### 1. Create auth account

```powershell
curl -X POST "http://127.0.0.1:8000/signup" `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"newuser\",\"password\":\"newpass123\"}"
```

### 2. Login and get token

```powershell
curl -X POST "http://127.0.0.1:8000/login" `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"newuser\",\"password\":\"newpass123\"}"
```

### 3. Verify token

```powershell
curl "http://127.0.0.1:8000/verify" `
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Add user

```powershell
curl -X POST "http://127.0.0.1:8001/add_user" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -d "{\"name\":\"John Doe\",\"email\":\"john@example.com\",\"age\":30}"
```

### 5. Get users

```powershell
curl "http://127.0.0.1:8001/get_users"
```

Optional authenticated request:

```powershell
curl "http://127.0.0.1:8001/get_users" `
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Update user

```powershell
curl -X PUT "http://127.0.0.1:8001/update_user/1" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -d "{\"name\":\"John Updated\",\"age\":31}"
```

### 7. Delete user

```powershell
curl -X DELETE "http://127.0.0.1:8001/delete_user/1" `
  -H "Authorization: Bearer YOUR_TOKEN"
```
