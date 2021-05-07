.PHONY: better run
PROJECT = .

run:
	poetry run python main.py

test:
	poetry run pytest


# TODO: add pycodestyle
better:
	@poetry run black $(PROJECT)
	@poetry run autoflake \
			--remove-all-unused-imports --recursive \
			--remove-unused-variables --in-plac \
			--exclude=__init__.py \
			 $(PROJECT)
	@poetry run isort $(PROJECT)
	@poetry run mypy $(PROJECT)
