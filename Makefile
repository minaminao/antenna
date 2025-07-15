all: fmt lint type-check-strict

test-sample:
	rm -rf ./archive
	python antenna.py --task-file task_sample.json
	python antenna.py --task-file task_sample.json

test:
	rm -rf ./archive
	python antenna.py
	python antenna.py

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
