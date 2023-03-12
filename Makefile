all: down up

logs:
	docker-compose logs --follow

up:
	docker-compose up --build -d

down:
	docker-compose down -v

clean: #down
	docker builder prune --all

fclean: clean
	docker system prune -a -f --volumes

info:
	docker system df
