POETRY_EXPORT_OPTS := --without-hashes --without-urls --without dev

up:
	docker-compose -f docker-compose.yaml up --build

down:
	docker-compose -f docker-compose.yaml down

logs:
	docker-compose -f docker-compose.yaml logs -f
	
reb:
	docker-compose down --remove-orphans
	docker compose up --build

rmc:
	docker rm --force $$(docker ps -a -q)

rmvol:
	docker volume rm $$(docker volume ls -q)

rmall: rmc rmvol

ps:
	docker ps

psa:
	docker ps -a

net:
	docker network ls

cr-net:
	@read -p "Enter docker network name to create: " NETWORK_NAME; \
	docker network create $$NETWORK_NAME

rm-net:
	@read -p "Enter docker network name to remove: " NETWORK_NAME; \
	docker network rm $$NETWORK_NAME

exec:
	@read -p "Enter container name or ID: " CONTAINER_NAME; \
	docker exec -it $$CONTAINER_NAME /bin/bash

### Poetry
pa:
	poetry add
pe:
	poetry export -f requirements.txt --output requirements.txt $(POETRY_EXPORT_OPTS)

pi:
	poetry install

pu:
	poetry update

pt:
	poetry run pytest

pl:
	poetry run flake8 .

pr:
	@read -p "Enter the name of the Python script to run: " SCRIPT_NAME; \
	poetry run python $$SCRIPT_NAME
	
run:
	poetry run uvicorn main:app --reload

### Git, Gitlab

# Check git status
st:
	git status

# Add all files to git
add:
	git add .

# Add commit and push it to Gitlab / dev branch
commit:
	@current_branch=$$(git rev-parse --abbrev-ref HEAD); \
	if [ "$$current_branch" != "dev" ]; then \
		echo "You are on branch '$$current_branch'. Please switch to 'dev' to continue."; \
		exit 1; \
	fi; \
	read -p "Enter commit message: " COMMIT_MSG; \
	git add .; \
	git commit -m "$$COMMIT_MSG"; \
	git push origin dev

# Switch to dev branch
dev:
	git checkout dev

# Switch to main branch
main:
	git checkout main

# Create a new branch
branch:
	@read -p "Enter the name of the new branch: " BRANCH_NAME; \
	git checkout -b $$BRANCH_NAME


### Alembic
alrev:
	@read -p "Enter the name of the revision: " REVISION_NAME; \
	alembic revision --autogenerate -m "$$REVISION_NAME"

alh:
	alembic upgrade head

### Postgres
# Connect to the database
po:
	psql -U postgres

postgres:
	docker exec -it postgres_db psql -U postgres -d postgres

### Sqlite3
# Connect to the database from the database's folder
sq:
	sqlite3 database.db

