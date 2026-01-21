from django.db.models import Count, Q, Case, When, IntegerField, F
from datetime import date, timedelta
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.academic_module.university_app.models import AcademicYear
from services.core_service.student_module.student_profile_app.models import Student

from .models import (
    AbsenceJustification,
    CounselingSession,
    DocumentRequest,
    Scholarship,
    StudentActivity,
    StudentStatusChange,
)


class StudentServicesService:

    @staticmethod
    def get_dashboard_stats():
        return {
            "total_students": Student.objects.count(),
            "pending_documents": DocumentRequest.objects.filter(
                status="pending"
            ).count(),
            "pending_absences": AbsenceJustification.objects.filter(
                status="pending"
            ).count(),
            "active_scholarships": Scholarship.objects.filter(is_active=True).count(),
            "upcoming_sessions": CounselingSession.objects.count(),
            "active_activities": StudentActivity.objects.filter(
                is_approved=True
            ).count(),
            "pending_status_changes": StudentStatusChange.objects.filter(
                approval_status="pending"
            ).count(),
        }


class PopulationDataService:
    """Service for generating student population statistics"""
    
    @staticmethod
    def get_population_data(filters=None):
        """Get student population data with age and gender breakdown"""
        if filters is None:
            filters = {}
        
        # Base queryset for active inscriptions
        queryset = Inscription.objects.filter(
            regist_status='Active'
        ).select_related(
            'student__user',
            'class_fk__department__faculty',
            'class_fk__department',
            'class_fk',
            'academic_year'
        )
        
        # Apply filters
        if filters.get('academic_year'):
            queryset = queryset.filter(academic_year_id=filters['academic_year'])
        
        if filters.get('faculty'):
            queryset = queryset.filter(class_fk__department__faculty_id=filters['faculty'])
            
        if filters.get('department'):
            queryset = queryset.filter(class_fk__department_id=filters['department'])
            
        if filters.get('class_name'):
            queryset = queryset.filter(class_fk_id=filters['class_name'])
            
        if filters.get('sexe'):
            queryset = queryset.filter(student__user__gender=filters['sexe'])
        
        # Calculate age ranges
        today = date.today()
        
        # Group by faculty, department, class, and gender
        population_data = []
        
        # Get unique combinations
        combinations = queryset.values(
            'class_fk__department__faculty__faculty_abreviation',
            'class_fk__department__department_name', 
            'class_fk__class_name',
            'student__user__gender'
        ).distinct()
        
        for combo in combinations:
            if not combo['student__user__gender']:
                continue
                
            # Filter for this specific combination
            combo_queryset = queryset.filter(
                class_fk__department__faculty__faculty_abreviation=combo['class_fk__department__faculty__faculty_abreviation'],
                class_fk__department__department_name=combo['class_fk__department__department_name'],
                class_fk__class_name=combo['class_fk__class_name'],
                student__user__gender=combo['student__user__gender']
            )
            
            # Calculate age breakdowns
            age_counts = {}
            total_count = 0
            
            for inscription in combo_queryset:
                if inscription.student.user.birth_date:
                    age = today.year - inscription.student.user.birth_date.year
                    if today < inscription.student.user.birth_date.replace(year=today.year):
                        age -= 1
                    
                    total_count += 1
                    
                    if age < 19:
                        age_counts['less_than_nineteen'] = age_counts.get('less_than_nineteen', 0) + 1
                    elif age == 19:
                        age_counts['nineteen'] = age_counts.get('nineteen', 0) + 1
                    elif age == 20:
                        age_counts['twenty'] = age_counts.get('twenty', 0) + 1
                    elif age == 21:
                        age_counts['twenty_one'] = age_counts.get('twenty_one', 0) + 1
                    elif age == 22:
                        age_counts['twenty_two'] = age_counts.get('twenty_two', 0) + 1
                    elif age == 23:
                        age_counts['twenty_three'] = age_counts.get('twenty_three', 0) + 1
                    elif age == 24:
                        age_counts['twenty_four'] = age_counts.get('twenty_four', 0) + 1
                    elif age == 25:
                        age_counts['twenty_five'] = age_counts.get('twenty_five', 0) + 1
                    elif age == 26:
                        age_counts['twenty_six'] = age_counts.get('twenty_six', 0) + 1
                    elif age == 27:
                        age_counts['twenty_seven'] = age_counts.get('twenty_seven', 0) + 1
                    elif age == 28:
                        age_counts['twenty_eight'] = age_counts.get('twenty_eight', 0) + 1
                    elif age == 29:
                        age_counts['twenty_nine'] = age_counts.get('twenty_nine', 0) + 1
                    elif age == 30:
                        age_counts['thirty'] = age_counts.get('thirty', 0) + 1
                    elif age == 31:
                        age_counts['thirty_one'] = age_counts.get('thirty_one', 0) + 1
                    else:
                        age_counts['greater_than_thirty_one'] = age_counts.get('greater_than_thirty_one', 0) + 1
            
            if total_count > 0:
                # Get totals by gender for this class
                class_totals = queryset.filter(
                    class_fk__department__faculty__faculty_abreviation=combo['class_fk__department__faculty__faculty_abreviation'],
                    class_fk__department__department_name=combo['class_fk__department__department_name'],
                    class_fk__class_name=combo['class_fk__class_name']
                ).aggregate(
                    total_male=Count('id', filter=Q(student__user__gender='M')),
                    total_female=Count('id', filter=Q(student__user__gender='F'))
                )
                
                population_data.append({
                    'id': len(population_data) + 1,
                    'faculty_abreviation': combo['class_fk__department__faculty__faculty_abreviation'] or '',
                    'departement_name': combo['class_fk__department__department_name'] or '',
                    'class_name': combo['class_fk__class_name'] or '',
                    'sexe': combo['student__user__gender'],
                    'less_than_nineteen': age_counts.get('less_than_nineteen', 0),
                    'nineteen': age_counts.get('nineteen', 0),
                    'twenty': age_counts.get('twenty', 0),
                    'twenty_one': age_counts.get('twenty_one', 0),
                    'twenty_two': age_counts.get('twenty_two', 0),
                    'twenty_three': age_counts.get('twenty_three', 0),
                    'twenty_four': age_counts.get('twenty_four', 0),
                    'twenty_five': age_counts.get('twenty_five', 0),
                    'twenty_six': age_counts.get('twenty_six', 0),
                    'twenty_seven': age_counts.get('twenty_seven', 0),
                    'twenty_eight': age_counts.get('twenty_eight', 0),
                    'twenty_nine': age_counts.get('twenty_nine', 0),
                    'thirty': age_counts.get('thirty', 0),
                    'thirty_one': age_counts.get('thirty_one', 0),
                    'greater_than_thirty_one': age_counts.get('greater_than_thirty_one', 0),
                    'total_female': class_totals['total_female'],
                    'total_male': class_totals['total_male'],
                    'student_count': total_count
                })
        
        # Apply search filter
        if filters.get('search'):
            search_term = filters['search'].lower()
            population_data = [
                item for item in population_data
                if search_term in item['faculty_abreviation'].lower() or
                   search_term in item['departement_name'].lower() or
                   search_term in item['class_name'].lower()
            ]
        
        # Apply age range filter
        if filters.get('age_range'):
            age_range = filters['age_range']
            if age_range == 'less_than_nineteen':
                population_data = [item for item in population_data if item['less_than_nineteen'] > 0]
            elif age_range == 'nineteen_to_twenty_two':
                population_data = [item for item in population_data if 
                                 item['nineteen'] > 0 or item['twenty'] > 0 or 
                                 item['twenty_one'] > 0 or item['twenty_two'] > 0]
            elif age_range == 'twenty_three_to_twenty_six':
                population_data = [item for item in population_data if 
                                 item['twenty_three'] > 0 or item['twenty_four'] > 0 or 
                                 item['twenty_five'] > 0 or item['twenty_six'] > 0]
            elif age_range == 'twenty_seven_to_thirty':
                population_data = [item for item in population_data if 
                                 item['twenty_seven'] > 0 or item['twenty_eight'] > 0 or 
                                 item['twenty_nine'] > 0 or item['thirty'] > 0]
            elif age_range == 'greater_than_thirty':
                population_data = [item for item in population_data if 
                                 item['thirty_one'] > 0 or item['greater_than_thirty_one'] > 0]
        
        return population_data
