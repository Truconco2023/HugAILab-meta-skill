.PHONY: test validate trigger ir output lint type release-local check

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

validate:
	python3 scripts/validate_skill.py .

trigger:
	python3 scripts/trigger_eval.py . --cases evals/trigger_cases.json

ir:
	python3 scripts/export_skill_ir.py . --output reports/skill-ir.json

output:
	python3 scripts/output_eval.py . --cases evals/output_cases.json --output reports/output-eval.json

lint:
	ruff check scripts tests

type:
	mypy scripts

release-local:
	python3 scripts/release_check.py . --phase local --run-tests

check: test validate trigger ir output lint type
