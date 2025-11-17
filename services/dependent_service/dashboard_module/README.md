# Dashboard Module

This module provides dashboard functionality for the University Management System, specifically designed to handle three key use cases:

## Use Cases

### 1. Validation des Attributions de Cours (Visiteurs)
**Description**: Sur ordre du Recteur, valider l'attribution des cours proposés aux professeurs visiteurs après la recommandation du Doyen/Chef de Département.

**Endpoints**:
- `GET /dashboard/attributions/visiting-professors/` - Get pending course attributions for visiting professors
- `POST /dashboard/attributions/{attribution_id}/validate/` - Validate course attribution

### 2. Supervision de la Performance Académique
**Description**: Consulter les rapports agrégés sur les taux de réussite, de rétention et l'avancement global des programmes.

**Endpoints**:
- `GET /dashboard/performance/academic/` - Get academic performance statistics
- `GET /dashboard/overview/` - Get dashboard overview with key metrics

### 3. Consultation des Rapports de Qualité
**Description**: Recevoir et analyser les rapports d'Assurance Qualité.

**Endpoints**:
- `POST /dashboard/reports/generate/` - Generate quality assurance reports
- `GET /dashboard/reports/` - Get list of generated quality reports

## API Endpoints

### Dashboard Overview
```
GET /dashboard/overview/
```
Returns key statistics including:
- Pending/approved attributions count
- Total students count
- Success rate percentage
- Retention rate percentage

### Visiting Professors Attributions
```
GET /dashboard/attributions/visiting-professors/
```
Returns list of course attributions pending validation for visiting professors.

```
POST /dashboard/attributions/{attribution_id}/validate/
```
Validate a course attribution. Request body:
```json
{
    "status": "approved|rejected",
    "comments": "Optional validation comments"
}
```

### Academic Performance
```
GET /dashboard/performance/academic/
```
Returns academic performance metrics including success rates, retention rates, and student statistics.

### Quality Reports
```
POST /dashboard/reports/generate/
```
Generate quality assurance reports. Request body:
```json
{
    "report_type": "academic_performance|retention_rate|success_rate|program_advancement"
}
```

```
GET /dashboard/reports/
```
Get list of all generated quality reports.

## Models

### QualityReport
Stores generated quality assurance reports with aggregated data.

### AttributionValidation
Tracks validation status of course attributions for visiting professors.

## Services

### DashboardService
Contains business logic for:
- Calculating attribution statistics
- Computing academic performance metrics
- Validating course attributions
- Generating quality reports

## Installation

1. Add `services.dependent_service.dashboard_module.dashboard_app` to `INSTALLED_APPS`
2. Include dashboard URLs in main `urls.py`
3. Run migrations: `python manage.py makemigrations dashboard_app && python manage.py migrate`

## Usage

All endpoints require authentication. Use JWT tokens for API access.

Example usage:
```python
# Get dashboard overview
response = requests.get('/dashboard/overview/', headers={'Authorization': 'Bearer <token>'})

# Validate attribution
response = requests.post('/dashboard/attributions/{id}/validate/',
                        json={'status': 'approved', 'comments': 'Approved by Rector'},
                        headers={'Authorization': 'Bearer <token>'})
```
