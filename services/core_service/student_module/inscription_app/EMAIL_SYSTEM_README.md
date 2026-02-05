# Système d'Email de Confirmation d'Inscription

## Vue d'ensemble

Ce système envoie automatiquement des emails de confirmation professionnels en français aux étudiants lors de leur inscription à l'Université du Burundi. L'email contient toutes les informations de l'étudiant et les instructions pour soumettre les documents physiques.

## Fichiers créés

### 1. Templates d'email

- **`templates/emails/inscription_confirmation.html`** - Template HTML professionnel avec design responsive
- **`templates/emails/inscription_confirmation.txt`** - Version texte brut pour les clients email sans HTML

### 2. Utilitaires

- **`email_utils.py`** - Fonctions pour envoyer les emails
  - `send_inscription_confirmation_email(inscription)` - Envoie un email pour une inscription
  - `send_bulk_inscription_emails(inscriptions)` - Envoie des emails en masse

### 3. Commande de gestion

- **`management/commands/send_inscription_emails.py`** - Commande Django pour envoyer des emails

### 4. Intégration dans les vues

- **`views.py`** - Modifié pour envoyer automatiquement l'email lors de l'activation

## Données incluses dans l'email

### Informations personnelles
- Nom complet
- Matricule
- Email
- Téléphone
- Date de naissance
- Lieu de naissance (Colline, Commune, Province)
- Adresse

### Informations académiques
- Faculté
- Département
- Classe
- Groupe
- Année académique
- Date d'inscription
- Statut de l'inscription

### Informations de paiement (optionnel)
- Montant
- Statut du paiement
- Référence de paiement

### Documents soumis
- Liste des documents uploadés
- Statut de vérification
- Date d'upload

### Instructions pour documents physiques
- Liste des documents requis
- **Option 1**: Envoi par poste à **B.P. 490 GITEGA**
- **Option 2**: Dépôt en personne à l'université
- Délai de 30 jours

## Utilisation

### 1. Envoi automatique lors de l'activation

L'email est envoyé automatiquement quand une inscription est activée :

```python
# POST /api/inscriptions/{id}/activate/
```

### 2. Envoi manuel via l'API

```python
# POST /api/inscriptions/{id}/send_confirmation_email/
```

### 3. Envoi via commande Django

```bash
# Envoyer pour une inscription spécifique
python manage.py send_inscription_emails --inscription-id=<UUID>

# Envoyer pour toutes les inscriptions actives
python manage.py send_inscription_emails --status=Active

# Envoyer pour une année académique spécifique
python manage.py send_inscription_emails --academic-year=<UUID>

# Envoyer pour toutes les inscriptions
python manage.py send_inscription_emails --all
```

### 4. Utilisation programmatique

```python
from services.core_service.student_module.inscription_app.email_utils import (
    send_inscription_confirmation_email
)

# Envoyer l'email
inscription = Inscription.objects.get(id=inscription_id)
success = send_inscription_confirmation_email(inscription)

if success:
    print("Email envoyé avec succès")
else:
    print("Erreur lors de l'envoi")
```

## Configuration requise

### 1. Settings Django

Assurez-vous que les paramètres email sont configurés dans `settings.py` :

```python
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # ou votre serveur SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@example.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe'
DEFAULT_FROM_EMAIL = 'inscriptions@ub.edu.bi'
```

### 2. Templates

Les templates doivent être dans le dossier :
```
inscription_app/templates/emails/
```

Django les trouvera automatiquement si `APP_DIRS = True` dans `TEMPLATES` settings.

## Personnalisation

### Modifier le contenu de l'email

Éditez les fichiers template :
- `templates/emails/inscription_confirmation.html` - Version HTML
- `templates/emails/inscription_confirmation.txt` - Version texte

### Ajouter des données supplémentaires

Modifiez `email_utils.py` dans la fonction `send_inscription_confirmation_email()` :

```python
context = {
    # Ajoutez vos données ici
    'nouvelle_donnee': valeur,
}
```

### Modifier l'adresse postale

Dans le template HTML, cherchez :
```html
<strong style="font-size: 20px; color: #059669;">B.P. 490 GITEGA</strong>
```

## Fonctionnalités

✅ Design professionnel et responsive
✅ Toutes les données de l'étudiant incluses
✅ Informations sur la faculté, département, classe
✅ Instructions claires pour l'envoi des documents
✅ Deux options : poste (B.P. 490 GITEGA) ou dépôt en personne
✅ Version HTML et texte brut
✅ Envoi automatique lors de l'activation
✅ Envoi manuel via API
✅ Commande Django pour envoi en masse
✅ Gestion des erreurs
✅ Statistiques d'envoi

## Test

Pour tester l'envoi d'email :

```bash
# En développement, utilisez la console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Puis testez
python manage.py send_inscription_emails --inscription-id=<UUID>
```

## Dépannage

### L'email n'est pas envoyé

1. Vérifiez la configuration SMTP dans settings.py
2. Vérifiez que l'étudiant a une adresse email valide
3. Consultez les logs Django pour les erreurs
4. Testez avec le backend console en développement

### Les templates ne sont pas trouvés

1. Vérifiez que `APP_DIRS = True` dans TEMPLATES
2. Vérifiez le chemin : `inscription_app/templates/emails/`
3. Vérifiez que l'app est dans INSTALLED_APPS

### Les données manquent dans l'email

1. Vérifiez que les relations (student, user, colline, etc.) existent
2. Ajoutez des valeurs par défaut dans email_utils.py
3. Utilisez `.select_related()` pour optimiser les requêtes

## Support

Pour toute question ou problème, contactez l'équipe de développement.
