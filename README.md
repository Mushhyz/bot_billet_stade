# Bot d'achat de billets Stade de France

Bot automatisé pour l'achat de billets sur le site du Stade de France.

## Installation

1. Installer Python 3.8+
2. Cloner le dépôt:
```bash
git clone https://github.com/votre-utilisateur/bot-achat-billets.git
cd bot-achat-billets
```
3. Installer les dépendances:
```bash
pip install -r requirements.txt
```
4. Configurer les variables d'environnement dans un fichier `.env`:
```
EMAIL=votre_email@exemple.com
PASSWORD=votre_mot_de_passe
EVENT_NAME=Match Équipe de France
TICKET_QUANTITY=2
TICKET_CATEGORY=Catégorie 1
REFRESH_INTERVAL=5
CARD_NUMBER=4111111111111111
EXPIRY_DATE=12/25
CVV=123
CAPTCHA_API_KEY=votre_captcha_api_key
CAPTCHA_SITE_KEY=votre_captcha_site_key
```

## Utilisation

Exécuter le script:
```bash
python ticket_bot.py
```

Le bot se connectera automatiquement, recherchera l'événement, sélectionnera les billets, et procédera au paiement.

## Avertissement

Ce bot est fourni à des fins éducatives uniquement. Utilisez-le à vos propres risques.

---

Créé par Mushh
