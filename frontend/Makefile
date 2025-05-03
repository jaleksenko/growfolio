dev:
	npm run dev
build:
	npm run build

### Docker-Compose
up:
	docker-compose -f docker-compose.dev.yaml up --build
# upp:
# 	docker-compose -f docker-compose.prod.yaml up --build
down:
	docker-compose -f docker-compose.dev.yaml down
# downp:
# 	docker-compose -f docker-compose.prod.yaml down
ps:
	docker ps
psa:
	docker ps
rm:
	docker rm $(docker ps -a -q) --force
rmi:
	docker-compose down --rmi all

