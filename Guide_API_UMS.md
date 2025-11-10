# Guide d'utilisation de l'API UMS

## 📋 Vue d'ensemble

Cette collection Postman contient toutes les APIs du système de gestion universitaire (UMS) avec authentification JWT et support 2FA complet.

## 🚀 Configuration initiale

### 1. Variables de collection
- `base_url`: http://localhost:8000 (modifiez selon votre environnement)
- `access_token`: Token JWT (automatiquement mis à jour)
- `refresh_token`: Token de rafraîchissement (automatiquement mis à jour)
- `user_email`: Email de test (modifiez selon vos besoins)

### 2. Import dans Postman
1. Ouvrez Postman
2. Cliquez sur "Import"
3. Sélectionnez le fichier `UMS_API_Collection.json`
4. La collection sera importée avec toutes les requêtes

## 🔐 Flux d'authentification

### Inscription et vérification
1. **Inscription** → `POST /register/`
2. **Vérifier email** → `POST /verify-email/` (avec OTP reçu par email)
3. **Connexion** → `POST /login/`

### Authentification 2FA (optionnel)
1. **Configurer 2FA** → `POST /2fa/set/email/` ou `GET /2fa/set/totp/`
2. **Connexion avec 2FA** → `POST /login/email/` ou `POST /login/totp/`

## 📚 Endpoints disponibles

### 🔐 Authentication (Public)
- `POST /register/` - Inscription utilisateur
- `POST /send-email-otp/` - Envoyer OTP par email
- `POST /verify-email/` - Vérifier email avec OTP
- `POST /login/` - Connexion utilisateur
- `POST /password/reset/verify/` - Réinitialiser mot de passe
- `POST /token/refresh/` - Actualiser token JWT

### 🔒 2FA (Authentifié)
- `POST /2fa/set/email/` - Configurer 2FA email
- `GET /2fa/set/totp/` - Configurer 2FA TOTP (QR code)
- `POST /2fa/set/static/` - Configurer 2FA statique
- `POST /2fa/verify/email/` - Vérifier 2FA email
- `POST /2fa/verify/totp/` - Vérifier 2FA TOTP
- `POST /2fa/verify/static/` - Vérifier 2FA statique
- `POST /login/email/` - Connexion 2FA email
- `POST /login/totp/` - Connexion 2FA TOTP
- `POST /login/static/` - Connexion 2FA statique
- `POST /2fa/disable/email/` - Désactiver 2FA email
- `POST /2fa/disable/totp/` - Désactiver 2FA TOTP
- `POST /2fa/disable/static/` - Désactiver 2FA statique

### 👥 Gestion Utilisateurs (Authentifié)
- `GET /users/` - Liste des utilisateurs
- `GET /users/{id}/` - Détails utilisateur
- `PUT /users/{id}/` - Modifier utilisateur
- `POST /users/{id}/verify-password/` - Vérifier mot de passe

### 🎭 Gestion des Rôles
- `GET /available-roles/` - Rôles disponibles (public)
- `GET /roles/` - Liste des rôles (admin)
- `POST /roles/` - Créer rôle (admin)
- `GET /roles/{id}/` - Détails rôle (admin)
- `PUT /roles/{id}/` - Modifier rôle (admin)
- `DELETE /roles/{id}/` - Supprimer rôle (admin)
- `POST /roles/{id}/reassign/` - Réassigner utilisateurs (admin)

### 📚 Documentation
- `GET /api/schema/` - Schéma OpenAPI
- `GET /api/docs/swagger/` - Documentation Swagger
- `GET /api/docs/redoc/` - Documentation ReDoc
- `GET /admin/` - Interface admin Django

## 🔑 Types d'authentification

### 1. Public (AllowAny)
- Inscription, connexion, vérification email
- Documentation API
- Rôles disponibles

### 2. Authentifié (IsAuthenticated)
- Gestion du profil utilisateur
- Configuration et vérification 2FA
- Opérations utilisateur

### 3. Administrateur (IsAdminUser)
- Gestion complète des rôles
- Interface d'administration

## 📝 Exemples d'utilisation

### Inscription complète
```bash
# 1. Inscription
POST /register/
{
  "email": "user@example.com",
  "first_name": "Jean",
  "last_name": "Dupont"
}

# 2. Vérification email (OTP reçu par email)
POST /verify-email/
{
  "email": "user@example.com",
  "otp": "123456"
}

# 3. Connexion
POST /login/
{
  "email": "user@example.com",
}
```

### Configuration 2FA TOTP
```bash
# 1. Générer QR code
GET /2fa/set/totp/
Authorization: Bearer {access_token}

# 2. Vérifier configuration
POST /2fa/verify/totp/
Authorization: Bearer {access_token}
{
  "otp": "123456"
}
```

## 🛡️ Sécurité

### Headers requis
- `Content-Type: application/json`
- `Authorization: Bearer {access_token}` (pour endpoints authentifiés)

### Gestion des tokens
- Les tokens sont automatiquement mis à jour dans les variables
- Le refresh token permet de renouveler l'access token
- Durée de vie configurable dans Django settings

### Codes d'erreur courants
- `400` - Données invalides
- `401` - Non authentifié
- `403` - Accès refusé / 2FA requis
- `404` - Ressource non trouvée
- `500` - Erreur serveur

## 🧪 Tests automatiques

La collection inclut des tests automatiques :
- Vérification des codes de statut
- Extraction automatique des tokens
- Validation des temps de réponse
- Tests de non-régression

## 📞 Support

Pour toute question ou problème :
1. Vérifiez les logs Django
2. Consultez la documentation Swagger
3. Testez avec des données valides
4. Vérifiez l'authentification et les permissions

## 🔄 Mise à jour

Cette collection sera mise à jour automatiquement avec :
- Nouveaux endpoints
- Modifications d'authentification
- Nouveaux modules du système UMS

---

**Note**: Assurez-vous que votre serveur Django est démarré avant d'utiliser la collection.
