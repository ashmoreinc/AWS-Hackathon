#!/bin/bash

set -e

export AWS_PROFILE=AdministratorAccess-851311377237

echo "🚀 Déploiement du Système de Gestion d'Offres"
echo "=============================================="
echo ""
echo "📋 Profil AWS: $AWS_PROFILE"
echo ""

# Vérifier les credentials
echo "🔐 Vérification des credentials AWS..."
aws sts get-caller-identity || {
    echo "❌ Erreur: Credentials non valides"
    echo "Exécutez d'abord: aws sso login --profile AdministratorAccess-851311377237"
    exit 1
}

echo "✓ Credentials valides"
echo ""

# Package Lambda
echo "📦 Packaging des fonctions Lambda..."
cd lambda
rm -f deployment.zip
zip -q deployment.zip get_offers.py track_event.py inventory_monitor.py
echo "✓ Lambda packagées ($(ls -lh deployment.zip | awk '{print $5}'))"
cd ..

# Terraform
echo ""
echo "🔧 Déploiement Terraform..."
cd terraform

terraform init

echo ""
echo "📋 Planification..."
terraform plan -out=tfplan

echo ""
read -p "Déployer sur AWS? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    echo ""
    echo "🚀 Déploiement en cours..."
    terraform apply tfplan
    
    echo ""
    echo "✅ Déploiement terminé!"
    echo ""
    echo "📡 Endpoint API:"
    terraform output -raw api_endpoint
    echo ""
    echo ""
    echo "📝 Prochaines étapes:"
    echo "1. Insérer les données: python ../seed_database.py"
    echo "2. Tester l'API: python ../test_api.py \$(terraform output -raw api_endpoint)"
    echo ""
else
    echo "❌ Déploiement annulé"
    rm -f tfplan
fi
