APP_NAME=gpt-teacher-backend
CONTAINER_NAME=gpt-teacher-backend-container
PORT=8000

build:
	docker build -t $(APP_NAME) .

up: build
	docker run --rm -it -p $(PORT):$(PORT) --name $(CONTAINER_NAME) $(APP_NAME)

down:
	docker rm -f $(CONTAINER_NAME) || true
	docker rmi -f $(APP_NAME) || true

rebuild: clean build

logs:
	docker logs -f $(CONTAINER_NAME)
