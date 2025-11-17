# Dashboard Alumni App

## Description
Tableau de bord pour les Alumni (anciens étudiants) permettant la gestion du réseau professionnel, mentorat, événements, donations et demandes de documents.

## Cas d'Utilisation

### Annuaire Professionnel
- Mise à jour du profil professionnel
- Recherche et contact d'anciens camarades
- Gestion des informations de carrière

### Offres d'Emploi et Stage
- Publication d'opportunités professionnelles
- Gestion des offres actives
- Ciblage vers étudiants actuels

### Programmes de Mentorat
- Inscription comme mentor
- Suivi des relations mentor-étudiant
- Communication intégrée

### Témoignages et Contenu
- Partage d'expériences professionnelles
- Contribution au contenu académique
- Publication d'articles d'expertise

### Participation aux Événements
- Inscription aux événements institutionnels
- Gestion de la billetterie
- Suivi des participations

### Donations et Levée de Fonds
- Système de dons en ligne
- Suivi des contributions
- Support aux projets institutionnels

### Accès Dossier Académique
- Consultation de l'historique académique
- Accès aux relevés de notes
- Téléchargement des diplômes numériques

### Demandes de Documents
- Commande de duplicatas
- Suivi des demandes
- Paiement intégré

## Modèles

### AlumniProfile
- Profil professionnel complet
- Informations de carrière
- Statut de mentor

### JobOffer
- Offres d'emploi et stages
- Gestion des opportunités
- Ciblage étudiant

### MentorshipProgram
- Relations mentor-étudiant
- Suivi des programmes
- Domaines d'expertise

### AlumniTestimonial
- Témoignages d'expérience
- Contenu éditorial
- Publication contrôlée

### AlumniEvent
- Événements institutionnels
- Gestion des inscriptions
- Types d'événements variés

### AlumniDonation
- Système de donations
- Traçabilité des contributions
- Catégorisation des dons

### AlumniDocumentRequest
- Demandes de documents officiels
- Processus de commande
- Suivi de livraison

## API Endpoints

### Profils Alumni
- `GET /profiles/` - Liste des profils
- `POST /profiles/` - Création de profil
- `GET /profiles/search/` - Recherche d'alumni
- `PUT /profiles/{id}/` - Mise à jour profil

### Offres d'Emploi
- `GET /job-offers/` - Liste des offres
- `POST /job-offers/` - Création d'offre
- `PUT /job-offers/{id}/` - Modification d'offre

### Mentorat
- `GET /mentorship/` - Programmes de mentorat
- `POST /mentorship/` - Création de relation
- `PUT /mentorship/{id}/` - Mise à jour statut

### Témoignages
- `GET /testimonials/` - Liste des témoignages
- `POST /testimonials/` - Création de témoignage

### Événements
- `GET /events/` - Liste des événements
- `POST /events/{id}/register/` - Inscription événement

### Donations
- `GET /donations/` - Historique des dons
- `POST /donations/` - Nouveau don

### Demandes de Documents
- `GET /document-requests/` - Liste des demandes
- `POST /document-requests/` - Nouvelle demande
- `GET /document-requests/{id}/` - Suivi de demande
