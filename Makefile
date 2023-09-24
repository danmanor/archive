.PHONY: format test install-test install

install-test:
	pip install .[test-runner]
	pip install .[test]
	pip install .[format]
	pip install .[types]
	pip install .[lint]

install:
	pip install .

format:
	isort --profile black src/
	black src/

test:
	tox

