.PHONY: better run
PROJECT = trio_monitor

run:
	poetry run python main.py


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
