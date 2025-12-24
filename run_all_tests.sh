#!/bin/bash
echo "🧪 EXÉCUTION DE TOUS LES TESTS"
echo "================================"

echo -e "\n1. Tests d'authentification:"
pytest tests/test_auth.py -v -q

echo -e "\n2. Tests produits:"
pytest tests/test_products.py -v -q

echo -e "\n3. Tests mouvements:"
pytest tests/test_movements.py -v -q

echo -e "\n4. Tests dashboard:"
pytest tests/test_dashboard.py -v -q

echo -e "\n5. Tests utilisateurs:"
pytest tests/test_users.py -v -q

echo -e "\n6. Rapport de couverture:"
pytest --cov=app --cov-report=term-missing --cov-report=html

echo -e "\n✅ Tous les tests sont terminés!"
echo "📊 Rapport HTML: file://$(pwd)/htmlcov/index.html"
