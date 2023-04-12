COLOR_NORM		:=	\033[0m
COLOR_RED		:=	\033[31m
COLOR_PURPLE	:=	\033[35m
cmd				:=	$(shell which docker-compose >/dev/null; RETVAL=$$?; if [ $$RETVAL -eq 0 ]; then echo 'docker-compose'; else echo 'docker compose'; fi)
arg				:=	$(wordlist 2,2,$(MAKECMDGOALS))

re-up: down up

logs:
	${cmd} logs --follow


log:
	${cmd} logs --follow $(arg)


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

restart_service:
	${cmd} up -d --build ${arg}

reset_php:
	rm -rf ./oauth2/vendor

# reset_db:
# 	rm -rf ./mariadb/volume

help:
	@printf "make $(COLOR_PURPLE)re-up$(COLOR_NORM) [default]\n"
	@printf "\tdown & up dockers\n"
	@printf "make $(COLOR_PURPLE)logs$(COLOR_NORM)\n"
	@printf "\tdisplay logs of dockers\n"
	@printf "make $(COLOR_PURPLE)log$(COLOR_NORM) $(COLOR_RED)<service_name>$(COLOR_NORM)\n"
	@printf "\tdisplay log of service $(COLOR_RED)service_name$(COLOR_NORM)\n"
	@printf "make $(COLOR_PURPLE)reset_php$(COLOR_NORM)\n"
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
	@printf "make $(COLOR_PURPLE)restart_service$(COLOR_NORM) $(COLOR_RED)<service_name>$(COLOR_NORM)\n"
	@printf "\tupdate the service and all his dependences\n"
	@printf "make $(COLOR_PURPLE)reset_php$(COLOR_NORM)\n"
	@printf "\tremove all the php dependences\n"
	@printf "make $(COLOR_RED)reset_db$(COLOR_NORM)\n"
	@printf "\tremove all the data from the database $(COLOR_RED)only for dev$(COLOR_NORM)\n"
	@printf "make $(COLOR_PURPLE)help$(COLOR_NORM)\n"
	@printf "\tdisplay help\n"
