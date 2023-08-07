.PHONY: all
all: format lint type test

.PHONY: static
static: format lint type

.PHONY: lint
lint: 
	isort . -q
	autoflake .

.PHONY: format
format:
	black .

.PHONY: type
type:
	mypy --strict pyrsercomb tests


.PHONY: test
test:
	pytest -n auto


.PHONY: coverage
coverage:
	pytest --cov=pyrsercomb


.PHONY: dead-code
dead-code:
	vulture pyrsercomb


.PHONY: env
env:
	! [ -d .venv ] && python3 -m venv .venv || true

.PHONY: install
install:
	yes | pip uninstall pyrsercomb
	pip install -e .[test]

.PHONY: clean
clean:
	rm -r .venv
