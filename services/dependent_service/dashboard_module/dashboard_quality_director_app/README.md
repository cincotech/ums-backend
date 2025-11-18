# Quality Director Dashboard

Dashboard specifically designed for the Directeur Assurance Qualité (DAQ) role - focused on accessing raw and aggregated data to evaluate university process quality and effectiveness. This role analyzes and reports, not manages operations.

## Use Cases

### 1. Analyse de la Performance Académique
**Description**: Consulter les résultats des étudiants de manière agrégée (par cours, par promotion, par programme) pour suivre les taux de réussite et d'échec, identifier les cours sous-performants, et mesurer la moyenne académique globale.

**Endpoints**:
- `GET /dashboard/quality-director/academic-performance/` - Academic performance analysis

### 2. Suivi de l'Exécution des Programmes
**Description**: Consulter l'avancement des programmes et des enseignements, vérifier la progression des matières par rapport au calendrier académique planifié.

**Endpoints**:
- `GET /dashboard/quality-director/program-execution/` - Program execution tracking

### 3. Audit des Effectifs et de la Rétention
**Description**: Consulter les statistiques détaillées des étudiants inscrits, analyser les taux de rétention, d'abandon et la répartition par filière.

**Endpoints**:
- `GET /dashboard/quality-director/demographics/` - Student demographics audit

### 4. Évaluation des Cours et Enseignants
**Description**: Gérer les enquêtes de satisfaction des étudiants sur les cours, professeurs et environnement d'étude.

**Endpoints**:
- `GET /dashboard/quality-director/evaluations/` - Course and teacher evaluations

### 5. Suivi des Normes et Accréditations
**Description**: Auditer la conformité des processus académiques et administratifs avec les normes de qualité internes et externes.

**Endpoints**:
- `GET /dashboard/quality-director/compliance/` - Compliance standards audit

### 6. Génération de Rapports de Qualité
**Description**: Générer des rapports périodiques d'assurance qualité basés sur toutes les données consultées.

**Endpoints**:
- `POST /dashboard/quality-director/reports/generate/` - Generate quality reports
- `GET /dashboard/quality-director/metrics/` - Quality metrics summary

## API Endpoints

### Dashboard Overview
```
GET /dashboard/quality-director/overview/
```
Returns quality director dashboard statistics including course analysis, ratings, compliance rates.

### Academic Performance Analysis
```
GET /dashboard/quality-director/academic-performance/
```
Get aggregated student results by course, program, promotion with success/failure rates and averages.

### Program Execution Tracking
```
GET /dashboard/quality-director/program-execution/
```
Track program advancement and curriculum coverage against planned academic calendar.

### Student Demographics Audit
```
GET /dashboard/quality-director/demographics/
```
Get detailed enrollment statistics, retention rates, dropout analysis, and distribution by program/level.

### Course & Teacher Evaluations
```
GET /dashboard/quality-director/evaluations/
```
Access student satisfaction surveys and evaluation data for courses, teachers, and study environment.

### Compliance Standards Audit
```
GET /dashboard/quality-director/compliance/
```
Review compliance audit results for academic and administrative processes against quality standards.

### Quality Report Generation
```
POST /dashboard/quality-director/reports/generate/
```
Generate comprehensive quality reports. Request body:
```json
{
    "report_type": "academic_performance|program_execution|student_demographics|compliance_audit"
}
```

### Quality Metrics Summary
```
GET /dashboard/quality-director/metrics/
```
Get comprehensive quality metrics summary for strategic reporting.

## Models

### StudentSurvey
Manages student satisfaction surveys for courses, teachers, and environment.

### QualityStandard
Defines quality standards and compliance criteria for auditing.

### ComplianceAudit
Records compliance audit results and findings.

## Key Features

✅ **Academic Performance Analytics**: Comprehensive success/failure rate analysis
✅ **Program Execution Monitoring**: Curriculum coverage and schedule adherence tracking
✅ **Student Demographics Analysis**: Enrollment, retention, and dropout statistics
✅ **Satisfaction Surveys**: Student feedback on courses, teachers, and environment
✅ **Compliance Auditing**: Standards adherence and accreditation requirements
✅ **Quality Reporting**: Automated generation of comprehensive quality reports
✅ **Data Aggregation**: Multi-dimensional analysis (course, program, promotion level)
✅ **Trend Analysis**: Historical data comparison and performance trends

## Installation

1. Add `services.dependent_service.dashboard_module.dashboard_quality_director_app` to `INSTALLED_APPS`
2. Run migrations: `python manage.py makemigrations dashboard_quality_director_app && python manage.py migrate`

## Usage

All endpoints require Quality Director authentication. This role focuses on analysis and reporting, not operational management.

Example usage:
```python
# Get academic performance analysis
response = requests.get('/dashboard/quality-director/academic-performance/',
                       headers={'Authorization': 'Bearer <token>'})

# Generate quality report
response = requests.post('/dashboard/quality-director/reports/generate/',
                        json={'report_type': 'academic_performance'},
                        headers={'Authorization': 'Bearer <token>'})
```

## Data Access Philosophy

The DAQ role is designed for:
- **Analysis, not Management**: Read-only access to operational data
- **Quality Assessment**: Evaluation of processes and outcomes
- **Strategic Reporting**: Data-driven insights for institutional improvement
- **Compliance Monitoring**: Adherence to quality standards and accreditation requirements
