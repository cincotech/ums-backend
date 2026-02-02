from django.core.management.base import BaseCommand
from services.foundational_service.auth_module.guest_app.models import RoleDocumentRequirement
from services.foundational_service.auth_module.user_app.models import Role


class Command(BaseCommand):
    help = 'Seed document requirements for all roles'

    def handle(self, *args, **kwargs):
        documents = [
            # Student
            {'role': 'student', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'student', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente (format passeport)', 'required': True},
            {'role': 'student', 'document_type': 'diploma', 'label': 'Diplôme d\'État', 'description': 'Copie certifiée du diplôme d\'État', 'required': True},
            {'role': 'student', 'document_type': 'transcript', 'label': 'Bulletin de 6ème année', 'description': 'Bulletin de la dernière année du secondaire', 'required': True},
            
            # Teacher
            {'role': 'teacher', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'teacher', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente (format passeport)', 'required': True},
            {'role': 'teacher', 'document_type': 'cv', 'label': 'CV détaillé', 'description': 'Curriculum Vitae complet et actualisé', 'required': True},
            {'role': 'teacher', 'document_type': 'diploma', 'label': 'Diplômes académiques', 'description': 'Copies certifiées de tous les diplômes universitaires', 'required': True},
            {'role': 'teacher', 'document_type': 'teaching_cert', 'label': 'Certificat d\'enseignement', 'description': 'Certificat d\'aptitude à l\'enseignement si disponible', 'required': False},
            
            # Supervisor
            {'role': 'supervisor', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'supervisor', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'supervisor', 'document_type': 'cv', 'label': 'CV académique', 'description': 'Curriculum Vitae avec publications et recherches', 'required': True},
            {'role': 'supervisor', 'document_type': 'diploma', 'label': 'Diplômes', 'description': 'Copies certifiées des diplômes (minimum Master)', 'required': True},
            {'role': 'supervisor', 'document_type': 'research_proposal', 'label': 'Domaines de recherche', 'description': 'Description des domaines de recherche et d\'expertise', 'required': True},
            
            # Alumni
            {'role': 'alumni', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'alumni', 'document_type': 'diploma', 'label': 'Diplôme universitaire', 'description': 'Copie du diplôme obtenu à l\'université', 'required': True},
            
            # delegate
            {'role': 'delegate', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité', 'required': True},
            {'role': 'delegate', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            
            # Administrative roles (super_admin, rector, directors, dean, services, offices)
            {'role': 'super_admin', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'super_admin', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'super_admin', 'document_type': 'admin_appointment', 'label': 'Lettre de nomination', 'description': 'Lettre officielle de nomination au poste', 'required': True},
            
            {'role': 'rector', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'rector', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'rector', 'document_type': 'cv', 'label': 'CV académique', 'description': 'Curriculum Vitae complet', 'required': True},
            {'role': 'rector', 'document_type': 'diploma', 'label': 'Diplômes', 'description': 'Copies certifiées des diplômes universitaires', 'required': True},
            {'role': 'rector', 'document_type': 'admin_appointment', 'label': 'Lettre de nomination', 'description': 'Lettre officielle de nomination au poste de Recteur', 'required': True},
            
            {'role': 'director_academic', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'director_academic', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'director_academic', 'document_type': 'cv', 'label': 'CV', 'description': 'Curriculum Vitae complet', 'required': True},
            {'role': 'director_academic', 'document_type': 'diploma', 'label': 'Diplômes', 'description': 'Copies certifiées des diplômes', 'required': True},
            {'role': 'director_academic', 'document_type': 'admin_appointment', 'label': 'Lettre de nomination', 'description': 'Lettre officielle de nomination', 'required': True},
            
            {'role': 'director_quality_assurance', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'director_quality_assurance', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'director_quality_assurance', 'document_type': 'cv', 'label': 'CV', 'description': 'Curriculum Vitae complet', 'required': True},
            {'role': 'director_quality_assurance', 'document_type': 'diploma', 'label': 'Diplômes', 'description': 'Copies certifiées des diplômes', 'required': True},
            {'role': 'director_quality_assurance', 'document_type': 'admin_appointment', 'label': 'Lettre de nomination', 'description': 'Lettre officielle de nomination', 'required': True},
            
            {'role': 'dean', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'dean', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'dean', 'document_type': 'cv', 'label': 'CV académique', 'description': 'Curriculum Vitae complet', 'required': True},
            {'role': 'dean', 'document_type': 'diploma', 'label': 'Diplômes', 'description': 'Copies certifiées des diplômes universitaires', 'required': True},
            {'role': 'dean', 'document_type': 'admin_appointment', 'label': 'Lettre de nomination', 'description': 'Lettre officielle de nomination au poste de Doyen', 'required': True},
            
            {'role': 'student_service', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'student_service', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'student_service', 'document_type': 'cv', 'label': 'CV', 'description': 'Curriculum Vitae complet', 'required': True},
            {'role': 'student_service', 'document_type': 'diploma', 'label': 'Diplômes', 'description': 'Copies certifiées des diplômes', 'required': True},
            
            {'role': 'finance_service', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'finance_service', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'finance_service', 'document_type': 'cv', 'label': 'CV', 'description': 'Curriculum Vitae complet', 'required': True},
            {'role': 'finance_service', 'document_type': 'diploma', 'label': 'Diplômes', 'description': 'Copies certifiées des diplômes en comptabilité/finance', 'required': True},
            
            {'role': 'general_service', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'general_service', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'general_service', 'document_type': 'cv', 'label': 'CV', 'description': 'Curriculum Vitae complet', 'required': True},
            {'role': 'general_service', 'document_type': 'diploma', 'label': 'Diplômes', 'description': 'Copies certifiées des diplômes', 'required': True},
            
            {'role': 'rector_office', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'rector_office', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'rector_office', 'document_type': 'cv', 'label': 'CV', 'description': 'Curriculum Vitae complet', 'required': True},
            {'role': 'rector_office', 'document_type': 'diploma', 'label': 'Diplômes', 'description': 'Copies certifiées des diplômes', 'required': True},
            
            {'role': 'academic_affairs', 'document_type': 'identity', 'label': 'Carte d\'identité', 'description': 'Copie de la carte d\'identité nationale ou passeport', 'required': True},
            {'role': 'academic_affairs', 'document_type': 'photo', 'label': 'Photo d\'identité', 'description': 'Photo d\'identité récente', 'required': True},
            {'role': 'academic_affairs', 'document_type': 'cv', 'label': 'CV', 'description': 'Curriculum Vitae complet', 'required': True},
            {'role': 'academic_affairs', 'document_type': 'diploma', 'label': 'Diplômes', 'description': 'Copies certifiées des diplômes universitaires', 'required': True},
        ]

        created_count = 0
        updated_count = 0

        for doc_data in documents:
            try:
                role = Role.objects.get(name=doc_data['role'])
                obj, created = RoleDocumentRequirement.objects.update_or_create(
                    role=role,
                    document_type=doc_data['document_type'],
                    defaults={
                        'label': doc_data['label'],
                        'description': doc_data['description'],
                        'required': doc_data['required']
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Role {doc_data["role"]} not found, skipping'))

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded document requirements: {created_count} created, {updated_count} updated'
            )
        )
