all: fmt lint type-check-strict

test:
	rm -rf ./archive
	antenna --task-file task_sample.json
	antenna --task-file task_sample.json

clean:
	rm -rf ./archive

fmt:
	isort antenna/*.py
	ruff format .

lint:
	ruff check .

lint-fix:
	ruff check . --fix

type-check:
	mypy antenna --ignore-missing-imports

type-check-strict:
	mypy antenna --strict --ignore-missing-imports
