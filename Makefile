all: test

test:
	pytest --cov-report term-missing:skip-covered \
	--cov=automates --cov-report=xml \
	--ignore=tests/data -v tests


develop:
	bundle exec jekyll serve --incremental
