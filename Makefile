COLOR_NORM		:=	\033[0m
COLOR_RED		:=	\033[31m
COLOR_PURPLE	:=	\033[35m
cmd				:=	$(shell which docker-compose >/dev/null; RETVAL=$$?; if [ $$RETVAL -eq 0 ]; then echo 'docker-compose'; else echo 'docker compose'; fi)


re-up: down up

logs:
	${cmd} logs --follow

up:
	${cmd} up --build -d

down:
	${cmd} down -v

clean: #down
	docker builder prune --all

fclean: clean
	docker system prune -a -f --volumes

info:
	docker system df

# reset_db:
# 	rm -rf ./mariadb/volume

# reset_php:
# 	rm -rf ./oauth2/vendor

help:
	@printf "make $(COLOR_PURPLE)re-up$(COLOR_NORM) [default]\n"
	@printf "\tdown & up dockers\n"
	@printf "make $(COLOR_PURPLE)logs$(COLOR_NORM)\n"
	@printf "\tdisplay logs of dockers\n"
	@printf "make $(COLOR_PURPLE)up$(COLOR_NORM)\n"
	@printf "\tup dockers\n"
	@printf "make $(COLOR_PURPLE)down$(COLOR_NORM)\n"
	@printf "\tdown dockers\n"
	@printf "make $(COLOR_PURPLE)clean$(COLOR_NORM)\n"
	@printf "\tclean build\n"
	@printf "make $(COLOR_PURPLE)fclean$(COLOR_NORM)\n"
	@printf "\tdelete all images, volumes\n"
	@printf "make $(COLOR_PURPLE)info$(COLOR_NORM)\n"
	@printf "\tdisplay docker infos\n"
	@printf "make $(COLOR_PURPLE)help$(COLOR_NORM)\n"
	@printf "\tdisplay help\n"
