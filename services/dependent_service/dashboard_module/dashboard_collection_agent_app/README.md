# Collection Agent Dashboard

Dashboard specifically designed for the Agent Recouvrement du Minerval role - focused strictly on financial debt collection and payment management for student debtors. This role ensures tuition fees and other institutional debts are collected.

## Use Cases

### 1. Extraction des Données d'Impayés
**Description**: Générer des listes et rapports précis des étudiants en retard de paiement ou ayant des soldes impayés, avec filtrage par programme, montant ou ancienneté.

**Endpoints**:
- `GET /dashboard/finance/debtors/` - Extract debtor student data with filtering

### 2. Enregistrement des Paiements
**Description**: Enregistrer les paiements de minerval reçus et émettre des reçus.

**Endpoints**:
- `POST /dashboard/finance/payments/` - Record payments and issue receipts

### 3. Génération de notifications
**Description**: Envoyer des rappels et mises en demeure automatiques basés sur des scénarios prédéfinis (J+7, J+30, J+60).

**Endpoints**:
- `POST /dashboard/finance/payment-reminders/` - Send payment reminders

pourquoi alors ca ??

### 5. Gestion des dérogations
**Description**: Modifier la date d'échéance pour les étudiants justifiés ou bénéficiant d'une bourse.

**Endpoints**:
- Integrated with installment management for derogation cases

### 6. Gestion de la Correspondance
**Description**: Rédiger et envoyer des courriers officiels exigeant le paiement.

**Endpoints**:
- `POST /dashboard/finance/collection-correspondence/` - Send official correspondence
- `GET /dashboard/finance/collection-correspondence/{student_id}/` - View correspondence history

### 7. Communication Ciblée
**Description**: Utiliser la messagerie interne pour dialoguer avec l'étudiant ou ses garants.

**Endpoints**:
- Integrated messaging system for targeted communication

### 8. Proposition d'Échéanciers
**Description**: Saisir et valider le plan de paiement échelonné dans le système.

**Endpoints**:
- `POST /dashboard/finance/payment-plans/` - Create payment plans
- `GET /dashboard/finance/payment-plans/` - List payment plans

### 9. Suivi des Promesses de Paiement
**Description**: Enregistrer les dates et montants promis par les débiteurs.

**Endpoints**:
- `POST /dashboard/finance/payment-promises/` - Record payment promises
- `GET /dashboard/finance/payment-promises/` - Track payment promises

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
- `POST /dashboard/finance/legal-cases/{student_id}/prepare/` - Prepare legal cases
- `GET /dashboard/finance/legal-cases/` - List legal cases

## API Endpoints

### Dashboard Overview
```
GET /dashboard/finance/overview/
```
Returns collection dashboard statistics including total debtors, debt amounts, overdue cases.

### Debtor Management
```
GET /dashboard/finance/debtors/?program=&min_amount=&min_days_overdue=
```
Extract debtor student data with filtering options by program, amount, or overdue days.

### Payment Processing
```
POST /dashboard/finance/payments/
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
POST /dashboard/finance/payment-reminders/
```
Send payment reminders. Request body:
```json
{
    "reminder_type": "reminder_7|reminder_30|formal_notice_60|final_notice"
}
```

### Installment Management
```
GET /dashboard/finance/payment-installements/
POST /dashboard/finance/payment-installements/
```
Manage payment installments and tranches.

```
PUT /dashboard/finance/payment-installements/{installment_id}/update-date/
```
Update installment due dates for justified cases.

### Payment Plans
```
POST /dashboard/finance/payment-plans/
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
POST /dashboard/finance/payment-promises/
```
Record payment promises from students.

### Correspondence
```
POST /dashboard/finance/collection-correspondence/
```
Send official correspondence to students.

### Legal Cases
```
POST /dashboard/finance/legal-cases/{student_id}/prepare/
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
response = requests.post('/dashboard/finance/payments/',
                        json={'student_id': 'uuid', 'amount': '500.00', 'payment_method': 'cash'},
                        headers={'Authorization': 'Bearer <token>'})

# Send reminder
response = requests.post('/dashboard/finance/payment-reminders/',
                        json={'reminder_type': 'reminder_30'},
                        headers={'Authorization': 'Bearer <token>'})
```

## Collection Philosophy

The Collection Agent dashboard is designed for:
- **Debt Recovery**: Systematic approach to payment collection
- **Student Communication**: Professional correspondence and negotiation
- **Legal Preparation**: Complete documentation for irrecoverable cases
- **Financial Compliance**: Ensuring institutional revenue collection
