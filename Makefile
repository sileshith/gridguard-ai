PYTHON := .venv/bin/python
.PHONY: test validate train pipeline

test:
	$(PYTHON) -m pytest
validate:
	$(PYTHON) scripts/validate_data.py --config configs/development.yaml
train:
	$(PYTHON) scripts/train.py --config configs/development.yaml
pipeline:
	$(PYTHON) scripts/run_pipeline.py --config configs/development.yaml

.PHONY: dashboard
dashboard:
	$(PYTHON) scripts/build_dashboard.py
	$(PYTHON) scripts/serve_dashboard.py
