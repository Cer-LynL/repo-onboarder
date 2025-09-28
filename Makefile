# Repo Onboarder Makefile

.PHONY: help install test demo clean setup

help: ## Show this help message
	@echo "Repo Onboarder - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and setup virtual environment
	@echo "Installing Repo Onboarder..."
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	chmod +x onboarder.py
	@echo "Installation complete! Run 'make setup' to activate the environment."

setup: ## Activate virtual environment (run this in each new shell)
	@echo "To activate the virtual environment, run:"
	@echo "  source venv/bin/activate"

test: ## Run tests
	. venv/bin/activate && python test_onboarder.py

demo: ## Run demo
	. venv/bin/activate && python demo.py

analyze: ## Analyze current repository
	. venv/bin/activate && python onboarder.py . --no-llm

clean: ## Clean up generated files
	rm -rf onboarding/
	rm -rf venv/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

install-github: ## Install GitHub Actions workflow
	@echo "Installing GitHub Actions workflow..."
	@if [ ! -d ".github/workflows" ]; then mkdir -p .github/workflows; fi
	@cp .github/workflows/onboarder.yml .github/workflows/onboarder.yml
	@echo "GitHub Actions workflow installed!"
	@echo "Don't forget to add ANTHROPIC_API_KEY to your repository secrets."

all: install test ## Install, test, and run demo
	. venv/bin/activate && python demo.py
