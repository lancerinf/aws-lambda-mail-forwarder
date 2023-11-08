SHELL = /bin/bash -e
.RECIPEPREFIX := $(.RECIPEPREFIX)

test:
	sam validate --lint
	./scripts/run_tests.sh

build:
	 sam build MailForwarder

deploy:
	sam sync --no-dependency-layer

local-invoke:
	sam local invoke MailForwarder -e resources/event.json
