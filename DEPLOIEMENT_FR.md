# 🚀 Guide de Déploiement - Système de Gestion d'Offres

## ⚠️ Prérequis - Configuration AWS

**Votre AWS CLI n'est pas encore configuré.** Suivez ces étapes :

### Étape 1 : Configurer AWS CLI

```bash
aws configure
```

Vous aurez besoin de :
- **AWS Access Key ID** : Votre clé d'accès AWS
- **AWS Secret Access Key** : Votre clé secrète AWS
- **Default region** : `us-east-1` (recommandé)
- **Default output format** : `json`

### Étape 2 : Obtenir vos Credentials AWS

1. Connectez-vous à [AWS Console](https://console.aws.amazon.com)
2. Allez dans **IAM** → **Users** → Sélectionnez votre utilisateur
3. Onglet **Security credentials**
4. Cliquez sur **Create access key**
5. Téléchargez et sauvegardez vos credentials

### Étape 3 : Vérifier la Configuration

```bash
aws sts get-caller-identity
```

Si configuré correctement, vous verrez votre Account ID et User ARN.

---

## 📦 Déploiement Automatique

Une fois AWS configuré, lancez :

```bash
./deploy.sh
```

Le script va :
1. ✅ Packager les fonctions Lambda
2. ✅ Initialiser Terraform
3. ✅ Créer les tables DynamoDB
4. ✅ Créer le stream Kinesis
5. ✅ Déployer 3 fonctions Lambda
6. ✅ Configurer API Gateway
7. ✅ Configurer les triggers DynamoDB Streams

---

## 📋 Déploiement Manuel (Étape par Étape)

### 1. Packager les Lambdas

```bash
cd lambda
zip deployment.zip get_offers.py track_event.py inventory_monitor.py
cd ..
```

### 2. Déployer l'Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Tapez `yes` quand demandé.

### 3. Récupérer l'Endpoint API

```bash
terraform output api_endpoint
```

Exemple : `https://abc123.execute-api.us-east-1.amazonaws.com/prod`

### 4. Insérer les Données de Test

```bash
cd ..
python seed_database.py
```

Cela crée :
- 5 offres (électronique, mode, alimentation, sport)
- 3 utilisateurs avec préférences

### 5. Tester l'API

```bash
python test_api.py https://VOTRE_API_ENDPOINT
```

---

## 🎯 Utilisation de l'API

### Obtenir des Offres Personnalisées

```bash
curl -X POST https://VOTRE_API_ENDPOINT/offers/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER001"}'
```

**Réponse :**
```json
{
  "user_id": "USER001",
  "recommended_offers": [
    {
      "offer_id": "OFF001",
      "offer_name": "Premium Laptop Deal",
      "category": "electronics",
      "discount_value": 25,
      "score": 87.5
    }
  ]
}
```

### Tracker un Événement

```bash
curl -X POST https://VOTRE_API_ENDPOINT/events/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER001",
    "offer_id": "OFF001",
    "category": "electronics",
    "event_type": "CLICK"
  }'
```

---

## 🏗️ Infrastructure Déployée

| Ressource | Nom | Description |
|-----------|-----|-------------|
| DynamoDB | Offers | Catalogue d'offres avec Streams |
| DynamoDB | UserActivity | Profils et historique utilisateurs |
| Kinesis | offer-engagement-stream | Stream d'événements temps réel |
| Lambda | offer-get-offers | Recommandations personnalisées |
| Lambda | offer-track-event | Tracking d'événements |
| Lambda | offer-inventory-monitor | Détection de rupture de stock |
| API Gateway | offer-management-api | API HTTP publique |

---

## 💰 Coûts Estimés

Pour **100 000 requêtes/mois** :

- API Gateway : $0.35
- Lambda : $0.20
- DynamoDB : $1.25
- Kinesis : $10.80
- **Total : ~$13/mois**

---

## 🧪 Scénarios de Test

### Test 1 : Recommandations Personnalisées

```bash
# Utilisateur qui aime l'électronique
curl -X POST https://VOTRE_API/offers/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER001"}'

# Utilisateur qui aime la mode
curl -X POST https://VOTRE_API/offers/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER002"}'
```

### Test 2 : Simulation de Rupture de Stock

```python
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Offers')

# Mettre l'inventaire à 0
table.update_item(
    Key={'PK': 'OFFER#OFF001', 'SK': 'METADATA'},
    UpdateExpression='SET inventory_count = :zero',
    ExpressionAttributeValues={':zero': Decimal('0')}
)
```

Vérifiez les logs CloudWatch :
```bash
aws logs tail /aws/lambda/offer-inventory-monitor --follow
```

Vous verrez :
- `STOCKOUT DETECTED: OFF001 (electronics)`
- `PIVOT TO: OFF004 (Priority: 82)`

### Test 3 : Tracking d'Événements

```bash
# Clic
curl -X POST https://VOTRE_API/events/track \
  -d '{"user_id":"USER001","offer_id":"OFF001","category":"electronics","event_type":"CLICK"}'

# Rédemption
curl -X POST https://VOTRE_API/events/track \
  -d '{"user_id":"USER001","offer_id":"OFF001","category":"electronics","event_type":"REDEMPTION"}'
```

---

## 🔍 Monitoring

### Logs CloudWatch

```bash
# Lambda get-offers
aws logs tail /aws/lambda/offer-get-offers --follow

# Lambda track-event
aws logs tail /aws/lambda/offer-track-event --follow

# Lambda inventory-monitor
aws logs tail /aws/lambda/offer-inventory-monitor --follow
```

### Métriques à Surveiller

- **API Gateway** : Nombre de requêtes, latence, erreurs 4xx/5xx
- **Lambda** : Invocations, durée, erreurs
- **DynamoDB** : Capacité lecture/écriture, throttling
- **Kinesis** : Records entrants, latence GetRecords

---

## 🧹 Nettoyage

Pour supprimer toutes les ressources AWS :

```bash
cd terraform
terraform destroy
```

Tapez `yes` pour confirmer.

**⚠️ Attention** : Cela supprimera toutes les données !

---

## 🆘 Dépannage

### Erreur : "No valid credential sources found"
**Solution** : Configurez AWS CLI avec `aws configure`

### Erreur : "Access Denied"
**Solution** : Vérifiez que votre utilisateur IAM a les permissions nécessaires

### Erreur : "Resource already exists"
**Solution** : Supprimez les ressources existantes ou changez les noms dans `main.tf`

### API retourne 500
**Solution** : Vérifiez les logs Lambda pour les détails de l'erreur

### Aucune offre retournée
**Solution** : Vérifiez que `seed_database.py` a été exécuté avec succès

---

## 📞 Support

Pour toute question :
1. Vérifiez les logs CloudWatch
2. Consultez la console DynamoDB pour les données
3. Testez les endpoints dans la console API Gateway

---

## ✨ Fonctionnalités Clés

- ✅ **Ranking Multi-Armed Bandit** - Équilibre exploration/exploitation
- ✅ **Auto-pivot sur rupture** - Redirection automatique du trafic
- ✅ **Filtre de diversité** - Max 2 offres par catégorie
- ✅ **Tracking temps réel** - Via Kinesis Data Streams
- ✅ **Latence < 100ms** - Requêtes DynamoDB optimisées

---

**Prêt à déployer !** 🚀

Commencez par configurer AWS CLI, puis lancez `./deploy.sh`
