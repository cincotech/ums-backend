# Système d'Emails d'Inscription - Documentation Complète

## Vue d'ensemble

Système professionnel d'envoi d'emails automatiques pour tous les statuts d'inscription à l'Université du Burundi. Chaque changement de statut déclenche un email personnalisé en français.

## Statuts et Emails Correspondants

| Statut | Email | Déclencheur |
|--------|-------|-------------|
| **Pending** | Inscription en attente | Création initiale |
| **Active** | Inscription activée - Bienvenue | Activation de l'inscription |
| **Completed** | Félicitations - Complétée | Fin de l'inscription |
| **Suspended** | Inscription suspendue | Suspension temporaire |
| **Withdrawn** | Confirmation de retrait | Retrait volontaire |
| **Dropped** | Inscription abandonnée | Abandon en cours d'année |
| **Canceled** | Inscription annulée | Annulation |
| **Replaced** | Changement de classe | Transfert de classe/faculté |
| **Complement** | Complément requis | Documents manquants |

## Architecture

### 1. Fichiers créés

```
inscription_app/
├── email_utils.py                          # Logique d'envoi
├── templates/emails/
│   ├── inscription_pending.html            # Email attente
│   ├── inscription_active.html             # Email activation
│   ├── inscription_completed.html          # Email complété
│   ├── inscription_suspended.html          # Email suspendu
│   ├── inscription_withdrawn.html          # Email retrait
│   ├── inscription_dropped.html            # Email abandonné
│   ├── inscription_canceled.html           # Email annulé
│   ├── inscription_replaced.html           # Email remplacement
│   └── inscription_complement.html         # Email complément
├── views.py                                # Intégration automatique
└── management/commands/
    └── send_inscription_emails.py          # Commande CLI
```

### 2. Configuration (email_utils.py)

```python
STATUS_EMAIL_CONFIG = {
    'Pending': {
        'template': 'emails/inscription_pending.html',
        'subject': 'Inscription en attente - Action requise',
    },
    'Active': {
        'template': 'emails/inscription_active.html',
        'subject': 'Inscription activée - Bienvenue',
    },
    # ... autres statuts
}
```

## Utilisation

### 1. Envoi automatique (Recommandé)

Les emails sont envoyés automatiquement lors des changements de statut :

```python
# POST /api/inscriptions/{id}/activate/
# → Envoie automatiquement l'email "Active"

# POST /api/inscriptions/{id}/complete/
# → Envoie automatiquement l'email "Completed"

# POST /api/inscriptions/{id}/suspend/
# → Envoie automatiquement l'email "Suspended"

# POST /api/inscriptions/{id}/withdraw/
# → Envoie automatiquement l'email "Withdrawn"

# POST /api/inscriptions/{id}/drop/
# → Envoie automatiquement l'email "Dropped"

# POST /api/inscriptions/{id}/cancel/
# → Envoie automatiquement l'email "Canceled"

# POST /api/inscriptions/{id}/replace/
# → Envoie automatiquement l'email "Replaced"
```

### 2. Envoi manuel via API

```python
# POST /api/inscriptions/{id}/send_email/
{
    "email_type": "Active"  # Optionnel, utilise le statut actuel si absent
}
```

### 3. Envoi via commande Django

```bash
# Email pour une inscription spécifique
python manage.py send_inscription_emails --inscription-id=<UUID>

# Emails pour toutes les inscriptions actives
python manage.py send_inscription_emails --status=Active

# Emails pour une année académique
python manage.py send_inscription_emails --academic-year=<UUID>

# Emails pour toutes les inscriptions
python manage.py send_inscription_emails --all

# Spécifier le type d'email
python manage.py send_inscription_emails --status=Active --email-type=Pending
```

### 4. Utilisation programmatique

```python
from services.core_service.student_module.inscription_app.email_utils import (
    send_inscription_email,
    send_bulk_inscription_emails
)

# Envoyer un email
inscription = Inscription.objects.get(id=inscription_id)
send_inscription_email(inscription)  # Utilise le statut actuel
send_inscription_email(inscription, 'Active')  # Force un type spécifique

# Envoi en masse
inscriptions = Inscription.objects.filter(regist_status='Active')
stats = send_bulk_inscription_emails(inscriptions)
print(f"Succès: {stats['success']}, Échecs: {stats['failed']}")
```

## Contenu des Emails

### Données communes à tous les emails

- **Informations personnelles** : Nom, matricule, email, téléphone, date/lieu de naissance, adresse
- **Informations académiques** : Faculté, département, classe, groupe, année académique
- **Statut** : Statut actuel de l'inscription
- **Documents** : Liste des documents soumis avec leur statut
- **Paiement** : Informations de paiement (si disponibles)

### Spécificités par statut

#### Pending (En attente)
- Actions requises : Compléter profil, télécharger documents, payer
- Couleur : Orange/Jaune

#### Active (Activé)
- Instructions pour envoi documents physiques
- Adresse postale : **B.P. 490 GITEGA**
- Option dépôt en personne
- Prochaines étapes
- Couleur : Bleu

#### Completed (Complété)
- Félicitations
- Accès aux services universitaires
- Couleur : Vert

#### Suspended (Suspendu)
- Alerte importante
- Contact service inscriptions
- Couleur : Rouge

#### Withdrawn (Retiré)
- Confirmation de retrait
- Date de retrait
- Message d'au revoir
- Couleur : Gris

#### Dropped/Canceled/Replaced/Complement
- Information sur le changement
- Contact pour plus d'infos
- Couleur : Bleu

## Configuration Email Django

Dans `settings.py` :

```python
# Production (SMTP réel)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@example.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe'
DEFAULT_FROM_EMAIL = 'inscriptions@ub.edu.bi'

# Développement (Console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Test (Fichier)
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-emails'
```

## Personnalisation

### Modifier un template

Éditez le fichier HTML correspondant dans `templates/emails/` :

```html
<!-- Exemple : inscription_active.html -->
<div class="highlight-box">
    <strong>Cher(e) {{ student_name }},</strong>
    <p>Votre message personnalisé ici...</p>
</div>
```

### Ajouter des données au contexte

Dans `email_utils.py`, fonction `get_inscription_context()` :

```python
context = {
    # ... données existantes
    'nouvelle_donnee': valeur,
}
```

### Changer les couleurs

Chaque template a son propre style inline. Modifiez les couleurs dans la section `<style>` :

```css
.header{background:linear-gradient(135deg,#1e3a8a 0%,#3b82f6 100%)}
```

## Tests

### Test en développement

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Puis testez
python manage.py send_inscription_emails --inscription-id=<UUID>
# L'email s'affichera dans la console
```

### Test unitaire

```python
from django.test import TestCase
from django.core import mail

class EmailTest(TestCase):
    def test_inscription_email(self):
        inscription = Inscription.objects.create(...)
        send_inscription_email(inscription, 'Active')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Inscription activée', mail.outbox[0].subject)
```

## Monitoring et Logs

Les erreurs sont loggées automatiquement :

```python
try:
    send_inscription_email(inscription)
except Exception as e:
    print(f"Erreur lors de l'envoi de l'email: {str(e)}")
```

Pour un logging avancé, ajoutez dans `settings.py` :

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'emails.log',
        },
    },
    'loggers': {
        'inscription_emails': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

## Fonctionnalités

✅ 9 templates professionnels pour tous les statuts
✅ Envoi automatique lors des changements de statut
✅ Envoi manuel via API
✅ Commande Django pour envoi en masse
✅ Design responsive et professionnel
✅ Toutes les données de l'étudiant incluses
✅ Instructions pour documents physiques (B.P. 490 GITEGA)
✅ Gestion des erreurs
✅ Statistiques d'envoi
✅ Support HTML et texte brut
✅ Personnalisable facilement

## Dépannage

### Email non envoyé
1. Vérifiez la configuration SMTP
2. Vérifiez que l'étudiant a un email valide
3. Consultez les logs Django
4. Testez avec le backend console

### Template non trouvé
1. Vérifiez `APP_DIRS = True` dans TEMPLATES
2. Vérifiez le chemin : `inscription_app/templates/emails/`
3. Vérifiez que l'app est dans INSTALLED_APPS

### Données manquantes
1. Vérifiez les relations (student, user, colline, etc.)
2. Ajoutez des valeurs par défaut dans `get_inscription_context()`
3. Utilisez `.select_related()` pour optimiser

## Support

Pour toute question : inscriptions@ub.edu.bi
