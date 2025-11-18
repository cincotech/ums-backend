# Collection Agent Dashboard

Dashboard specifically designed for the Agent Recouvrement du Minerval role - focused strictly on financial debt collection and payment management for student debtors. This role ensures tuition fees and other institutional debts are collected.

## Use Cases

### 1. Extraction des Données d'Impayés
**Description**: Générer des listes et rapports précis des étudiants en retard de paiement ou ayant des soldes impayés, avec filtrage par programme, montant ou ancienneté.

**Endpoints**:
- `GET /dashboard/collection-agent/debtors/` - Extract debtor student data with filtering

### 2. Enregistrement des Paiements
**Description**: Enregistrer les paiements de minerval reçus et émettre des reçus.

**Endpoints**:
- `POST /dashboard/collection-agent/payments/record/` - Record payments and issue receipts

### 3. Génération de notifications
**Description**: Envoyer des rappels et mises en demeure automatiques basés sur des scénarios prédéfinis (J+7, J+30, J+60).

**Endpoints**:
- `POST /dashboard/collection-agent/reminders/{student_id}/send/` - Send payment reminders

### 4. Gestion des tranches de paiements
**Description**: Fixer les tranches de paiement des frais académiques et modifier les dates d'échéance.

**Endpoints**:
- `GET/POST /dashboard/collection-agent/installments/` - Manage payment installments
- `PUT /dashboard/collection-agent/installments/{installment_id}/update-date/` - Update due dates

### 5. Gestion des dérogations
**Description**: Modifier la date d'échéance pour les étudiants justifiés ou bénéficiant d'une bourse.

**Endpoints**:
- Integrated with installment management for derogation cases

### 6. Gestion de la Correspondance
**Description**: Rédiger et envoyer des courriers officiels exigeant le paiement.

**Endpoints**:
- `POST /dashboard/collection-agent/correspondence/send/` - Send official correspondence
- `GET /dashboard/collection-agent/correspondence/{student_id}/` - View correspondence history

### 7. Communication Ciblée
**Description**: Utiliser la messagerie interne pour dialoguer avec l'étudiant ou ses garants.

**Endpoints**:
- Integrated messaging system for targeted communication

### 8. Proposition d'Échéanciers
**Description**: Saisir et valider le plan de paiement échelonné dans le système.

**Endpoints**:
- `POST /dashboard/collection-agent/payment-plans/create/` - Create payment plans
- `GET /dashboard/collection-agent/payment-plans/` - List payment plans

### 9. Suivi des Promesses de Paiement
**Description**: Enregistrer les dates et montants promis par les débiteurs.

**Endpoints**:
- `POST /dashboard/collection-agent/promises/record/` - Record payment promises
- `GET /dashboard/collection-agent/promises/` - Track payment promises

### 10. Mise à Jour du Statut
**Description**: Mettre à jour le statut du compte à "soldé" ou "en cours de règlement".

**Endpoints**:
- Automatic status updates through payment recording

### 11. Alerte Administrative
**Description**: Signaler les cas persistants de non-paiement aux services académiques.

**Endpoints**:
- Administrative alert system integration

### 12. Préparation du Contentieux
**Description**: Extraire tous les documents financiers pour constituer le dossier juridique.

**Endpoints**:
- `POST /dashboard/collection-agent/legal-cases/{student_id}/prepare/` - Prepare legal cases
- `GET /dashboard/collection-agent/legal-cases/` - List legal cases

## API Endpoints

### Dashboard Overview
```
GET /dashboard/collection-agent/overview/
```
Returns collection dashboard statistics including total debtors, debt amounts, overdue cases.

### Debtor Management
```
GET /dashboard/collection-agent/debtors/?program=&min_amount=&min_days_overdue=
```
Extract debtor student data with filtering options by program, amount, or overdue days.

### Payment Processing
```
POST /dashboard/collection-agent/payments/record/
```
Record payment and issue receipt. Request body:
```json
{
    "student_id": "uuid",
    "amount": "decimal",
    "payment_method": "cash|bank_transfer|card",
    "reference": "string"
}
```

### Reminder System
```
POST /dashboard/collection-agent/reminders/{student_id}/send/
```
Send payment reminders. Request body:
```json
{
    "reminder_type": "reminder_7|reminder_30|formal_notice_60|final_notice"
}
```

### Installment Management
```
GET /dashboard/collection-agent/installments/
POST /dashboard/collection-agent/installments/
```
Manage payment installments and tranches.

```
PUT /dashboard/collection-agent/installments/{installment_id}/update-date/
```
Update installment due dates for justified cases.

### Payment Plans
```
POST /dashboard/collection-agent/payment-plans/create/
```
Create payment plans. Request body:
```json
{
    "student_id": "uuid",
    "total_amount": "decimal",
    "monthly_amount": "decimal",
    "start_date": "date"
}
```

### Promise Tracking
```
POST /dashboard/collection-agent/promises/record/
```
Record payment promises from students.

### Correspondence
```
POST /dashboard/collection-agent/correspondence/send/
```
Send official correspondence to students.

### Legal Cases
```
POST /dashboard/collection-agent/legal-cases/{student_id}/prepare/
```
Prepare legal case documentation for irrecoverable debts.

## Models

### PaymentInstallment
Manages payment tranches and installment schedules.

### PaymentReminder
Tracks automated reminders and formal notices.

### PaymentPlan
Manages negotiated payment plans and schedules.

### PaymentPromise
Records student payment promises and commitments.

### CollectionCorrespondence
Tracks all correspondence with debtor students.

### LegalCase
Prepares documentation for legal proceedings.

## Key Features

✅ **Debt Tracking**: Comprehensive debtor identification and filtering
✅ **Payment Processing**: Complete payment recording and receipt generation
✅ **Automated Reminders**: Scheduled reminder system (J+7, J+30, J+60)
✅ **Installment Management**: Flexible payment tranche configuration
✅ **Payment Plans**: Negotiated repayment schedule management
✅ **Promise Tracking**: Student commitment monitoring
✅ **Correspondence**: Official communication management
✅ **Legal Preparation**: Complete case documentation for litigation
✅ **Status Updates**: Real-time account status management

## Installation

1. Add `services.dependent_service.dashboard_module.dashboard_collection_agent_app` to `INSTALLED_APPS`
2. Run migrations: `python manage.py makemigrations dashboard_collection_agent_app && python manage.py migrate`

## Usage

All endpoints require Collection Agent authentication.

Example usage:
```python
# Record payment
response = requests.post('/dashboard/collection-agent/payments/record/',
                        json={'student_id': 'uuid', 'amount': '500.00', 'payment_method': 'cash'},
                        headers={'Authorization': 'Bearer <token>'})

# Send reminder
response = requests.post('/dashboard/collection-agent/reminders/{student_id}/send/',
                        json={'reminder_type': 'reminder_30'},
                        headers={'Authorization': 'Bearer <token>'})
```

## Collection Philosophy

The Collection Agent dashboard is designed for:
- **Debt Recovery**: Systematic approach to payment collection
- **Student Communication**: Professional correspondence and negotiation
- **Legal Preparation**: Complete documentation for irrecoverable cases
- **Financial Compliance**: Ensuring institutional revenue collection
