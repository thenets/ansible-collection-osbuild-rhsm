# =============
# Utils
# =============
venv:
	python3 -m venv venv
	venv/bin/pip install -U pip isort black bandit ruff

.PHONY: clean
clean:
	rm -rf venv/

.PHONY: fmt
## Run code formatters and linters
fmt: venv
	./venv/bin/isort ./roles/ --skip-glob '*/cache/*'
	./venv/bin/black -q ./roles/ --force-exclude 'cache/'
	./venv/bin/ruff --fix ./roles/ --exclude '*/cache/*'

.PHONY: lint
lint: venv
	@./venv/bin/ruff check ./roles/
	@./venv/bin/bandit \
		-r ./roles/ \
		--severity high

.PHONY: pre-commit
pre-commit: fmt lint
