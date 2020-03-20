all: test docs

docs:
	cd docs; make html

test:
	pytest --cov-report term-missing:skip-covered --cov=src \
	--ignore=tests/data tests


develop:
	bundle exec jekyll serve --incremental
