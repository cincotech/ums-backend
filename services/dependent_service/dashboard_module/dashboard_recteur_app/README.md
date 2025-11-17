# Recteur Dashboard

Dashboard specifically designed for the Recteur role - the supreme authority of the institution responsible for strategy, key appointment validations, performance monitoring, and granting exceptional authorizations.

## Use Cases

### 1. Octroi de Dérogations de Paiement
**Description**: Recevoir, examiner et accorder/rejeter les demandes exceptionnelles de dérogation (exemption, report ou aménagement) du paiement du minerval.

**Endpoints**:
- `GET /dashboard/recteur/derogations/` - List payment derogation requests
- `POST /dashboard/recteur/derogations/{derogation_id}/process/` - Approve/reject derogation

### 2. Validation des Attributions de Cours (Visiteurs)
**Description**: Valider l'attribution des cours proposés aux professeurs visiteurs après la recommandation du Doyen/Chef de Département.

**Endpoints**:
- `GET /dashboard/recteur/attributions/` - List pending course attributions
- `POST /dashboard/recteur/attributions/{attribution_id}/validate/` - Validate attribution

### 3. Suivi Global des Paiements
**Description**: Consulter les indicateurs clés de suivi des paiements des frais académiques par les étudiants pour évaluer le taux de recouvrement et les arriérés.

**Endpoints**:
- `GET /dashboard/recteur/payments/overview/` - Global payment tracking overview

### 4. Supervision de la Performance Académique
**Description**: Consulter les rapports agrégés sur les taux de réussite, de rétention et l'avancement global des programmes.

**Endpoints**:
- `GET /dashboard/recteur/performance/` - Academic performance supervision data

### 5. Consultation des Rapports de Qualité
**Description**: Recevoir et analyser les rapports d'Assurance Qualité pour orienter la politique générale de l'établissement.

**Endpoints**:
- `GET /dashboard/recteur/quality-reports/` - Quality assurance reports consultation

## API Endpoints

### Dashboard Overview
```
GET /dashboard/recteur/overview/
```
Returns recteur dashboard statistics including pending derogations, attributions, payment rates, and academic performance.

### Payment Derogations
```
GET /dashboard/recteur/derogations/?status=pending
```
Get payment derogation requests by status.

```
POST /dashboard/recteur/derogations/{derogation_id}/process/
```
Process derogation decision. Request body:
```json
{
    "decision": "approved|rejected",
    "notes": "Decision notes"
}
```

### Course Attributions
```
GET /dashboard/recteur/attributions/
```
Get pending course attributions for visiting professors.

```
POST /dashboard/recteur/attributions/{attribution_id}/validate/
```
Validate course attribution. Request body:
```json
{
    "decision": "approved|rejected",
    "notes": "Validation notes"
}
```

### Payment Tracking
```
GET /dashboard/recteur/payments/overview/
```
Get global payment collection rates, outstanding amounts, and arrears statistics.

### Academic Performance
```
GET /dashboard/recteur/performance/
```
Get academic performance metrics including success rates, retention rates, and program advancement.

### Quality Reports
```
GET /dashboard/recteur/quality-reports/
```
Get quality assurance reports for strategic decision making.

## Models

### PaymentDerogation
Manages exceptional payment derogation requests (exemptions, postponements, arrangements).

### RecteurDecision
Records all decisions made by the Recteur for audit and tracking purposes.

## Key Features

✅ **Payment Derogation Management**: Complete workflow for exceptional payment requests
✅ **Course Attribution Validation**: Approve/reject visiting professor assignments
✅ **Global Payment Monitoring**: Real-time payment collection and arrears tracking
✅ **Academic Performance Oversight**: Comprehensive performance metrics and trends
✅ **Quality Assurance**: Strategic reports for institutional policy guidance
✅ **Decision Audit Trail**: Complete record of all recteur decisions
✅ **Exception Handling**: Robust error handling for all operations

## Installation

1. Add `services.dependent_service.dashboard_module.dashboard_recteur_app` to `INSTALLED_APPS`
2. Run migrations: `python manage.py makemigrations dashboard_recteur_app && python manage.py migrate`

## Usage

All endpoints require Recteur-level authentication.

Example usage:
```python
# Process payment derogation
response = requests.post('/dashboard/recteur/derogations/{id}/process/',
                        json={'decision': 'approved', 'notes': 'Exceptional circumstances approved'},
                        headers={'Authorization': 'Bearer <token>'})

# Validate course attribution
response = requests.post('/dashboard/recteur/attributions/{id}/validate/',
                        json={'decision': 'approved', 'notes': 'Qualified visiting professor'},
                        headers={'Authorization': 'Bearer <token>'})
```
