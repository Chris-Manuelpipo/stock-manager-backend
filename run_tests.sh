#!/bin/bash
echo "=== Installation des dépendances ==="
pip install pytest pytest-asyncio httpx pytest-cov -q

echo -e "\n=== Exécution des tests ==="
pytest -v --cov=app --cov-report=term-missing

echo -e "\n=== Génération rapport HTML ==="
pytest --cov=app --cov-report=html

echo -e "\n=== Tests terminés ==="
echo "Rapport HTML: file://$(pwd)/htmlcov/index.html"
