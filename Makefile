build:
	@docker compose build --no-cache


up:
	@docker compose up --build -d

down:
	@docker compose down