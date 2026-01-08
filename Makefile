.PHONY: help run test clean

help:
	@echo "Available commands:"
	@echo "  make run   - Run end-to-end data pipeline"
	@echo "  make test  - Run data quality tests (pytest)"
	@echo "  make clean - Clean output folders"

run:
	python run_pipeline.py

test:
	pytest -q

clean:
	rm -rf out/*.csv out/*.parquet
