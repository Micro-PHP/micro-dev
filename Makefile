PYTHON = python
PIP = pip

.DEFAULT_GOAL = help
.PHONY        : help

help: ## Outputs this help screen
	@grep -E '(^[a-zA-Z0-9\./_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

venv: venv/touchfile

venv/touchfile: ./requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate; $(PIP) install -Ur requirements.txt
	touch venv/touchfile

init: ## Initializes the sub-repositories for build system
init: venv
	. venv/bin/activate; $(PYTHON) ./scripts/init.py --config=./repository.json $(INIT_ARGS)

release-prepare: ## Prepares releases
	. venv/bin/activate; $(PYTHON) ./scripts/release.py --config=./repository.json --base-branch "$(BASE_BRANCH)" --release-branch "$(RELEASE_BRANCH)" "$(RELEASE_NAME)"

release-merge: ## Merges releases in GitHub
	. venv/bin/activate; $(PYTHON) ./scripts/release.py --config=./repository.json --merge --base-branch "$(BASE_BRANCH)" --release-branch "$(RELEASE_BRANCH)" "$(RELEASE_NAME)"

release-dry-run: ## Shows planned release actions without mutating anything
	. venv/bin/activate; $(PYTHON) ./scripts/release.py --config=./repository.json --dry-run --base-branch "$(BASE_BRANCH)" --release-branch "$(RELEASE_BRANCH)" "$(RELEASE_NAME)"

release-status: ## Shows per-package release status without mutating anything
	. venv/bin/activate; $(PYTHON) ./scripts/release.py --config=./repository.json --status --base-branch "$(BASE_BRANCH)" --release-branch "$(RELEASE_BRANCH)" "$(RELEASE_NAME)"

clean: ## Clean the build system
	$(PYTHON) ./scripts/clean.py --config=./repository.json
	rm -rf venv __pycache__
	find -iname "*.pyc" -delete
