.PHONY: test test-all test-cov test-html clean

test:
	pytest -v

test-all:
	pytest tests/ -v

test-cov:
	pytest --cov=app --cov-report=term-missing

test-html:
	pytest --cov=app --cov-report=html
	@echo "Ouvrez: file://$(PWD)/htmlcov/index.html"

clean:
	rm -rf .pytest_cache htmlcov report.html test.db

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev: clean test run
