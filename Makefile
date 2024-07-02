PYTHON = python
PIP = pip

.DEFAULT_GOAL = help
.PHONY        : help

help: ## Outputs this help screen
	@grep -E '(^[a-zA-Z0-9\./_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

venv: venv/touchfile

venv/touchfile: scripts/requirements.txt
	cd ./scripts; test -d venv || virtualenv venv
	cd ./scripts; . venv/bin/activate; $(PIP) install -Ur requirements.txt
	cd ./scripts; touch venv/touchfile

init: venv ## Initializes the sub-repositories for build system
	cd ./scripts; . venv/bin/activate; $(PYTHON) ./init.py

release-prepare: ## Prepares releases
	cd ./scripts; . venv/bin/activate; $(PYTHON) ./release.py "$(RELEASE_NAME)"

release-merge: ## Merges releases in GitHub
	cd ./scripts; . venv/bin/activate; $(PYTHON) ./release.py "$(RELEASE_NAME)" --merge

clean: ## Clean the build system
	cd ./scripts; rm -rf venv
	cd ./scripts; find -iname "*.pyc" -delete
