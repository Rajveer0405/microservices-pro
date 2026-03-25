# Docker Guide For This Microservices Project

This project has two services:

- `auth_service`
- `user_service`

Both services run in separate Docker containers.

## Why The Error Happened

Inside Docker, `localhost` means "this same container".

So if `user_service` tries to call:

```text
http://127.0.0.1:8000/verify
```

it will look inside the `user_service` container itself, not the `auth_service` container.

That is why `user_service` returned:

```text
503 Service Unavailable
```

## Correct Docker Idea

Two containers should communicate using:

- the same Docker network
- the other container's name as the hostname

For this project:

- auth container name: `auth_container`
- user container name: `user_container`
- shared network: `micro-net`

So the correct auth URL for `user_service` is:

```text
http://auth_container:8000/verify
```

## What Was Done

The containers were connected like this:

1. `auth_container` was attached to Docker network `micro-net`
2. `user_container` was recreated on `micro-net`
3. `user_container` was started with:

```text
AUTH_SERVICE_VERIFY_URL=http://auth_container:8000/verify
```

## Build Images

Run these commands from:

```text
c:\Users\91810\Desktop\microservice
```

Build auth image:

```powershell
docker build -t auth_service .\auth_service
```

Build user image:

```powershell
docker build -t user_service .\user_service
```

## Create Docker Network

```powershell
docker network create micro-net
```

## Run Auth Container

```powershell
docker run -d --name auth_container --network micro-net -p 8000:8000 auth_service
```

## Run User Container

```powershell
docker run -d --name user_container --network micro-net -p 8001:8001 `
  -e AUTH_SERVICE_VERIFY_URL=http://auth_container:8000/verify `
  user_service
```

## Check Running Containers

```powershell
docker ps
```

## Check Network Connection

To inspect auth container networks:

```powershell
docker inspect -f "{{json .NetworkSettings.Networks}}" auth_container
```

To inspect user container networks:

```powershell
docker inspect -f "{{json .NetworkSettings.Networks}}" user_container
```

## Check Environment Variable In User Container

```powershell
docker inspect -f "{{range .Config.Env}}{{println .}}{{end}}" user_container
```

You should see:

```text
AUTH_SERVICE_VERIFY_URL=http://auth_container:8000/verify
```

## Test Container-To-Container Connection

Run this command:

```powershell
docker exec user_container python -c "import requests; print(requests.get('http://auth_container:8000/docs', timeout=5).status_code)"
```

Expected result:

```text
200
```

That means `user_container` can reach `auth_container`.

## Open Swagger Docs

Auth service:

```text
http://127.0.0.1:8000/docs
```

User service:

```text
http://127.0.0.1:8001/docs
```

## Test Flow

1. Open auth Swagger docs
2. Call `POST /signup`
3. Call `POST /login`
4. Copy the returned token
5. Open user Swagger docs
6. Click `Authorize`
7. Paste the token
8. Call `POST /add_user`

## If User Service Still Shows 503

Check these:

1. Is `auth_container` running?
2. Is `user_container` running?
3. Are both attached to `micro-net`?
4. Does `user_container` have `AUTH_SERVICE_VERIFY_URL=http://auth_container:8000/verify`?
5. Can `user_container` reach `auth_container` using `docker exec` test?

## Remove Containers

```powershell
docker rm -f user_container
docker rm -f auth_container
```

## Remove Network

```powershell
docker network rm micro-net
```

## Important Note

This setup works because Docker provides internal DNS for container names on the same network.

That is why:

```text
http://auth_container:8000/verify
```

works between containers, while:

```text
http://localhost:8000/verify
```

does not work from inside `user_container`.
