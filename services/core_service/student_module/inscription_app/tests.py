import logging
from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from services.core_service.academic_module.class_app.models import Class, ClassGroup
from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import Faculty, TypeFormation
from services.core_service.academic_module.university_app.models import AcademicYear, University
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.student_profile_app.models import (
    Student,
    StudentGraduateInfo,
    StudentMatricule,
)
from services.foundational_service.auth_module.user_app.models import User
from services.foundational_service.geo_module.colline_app.models import Colline
from services.foundational_service.geo_module.commune_app.models import Commune
from services.foundational_service.geo_module.country_app.models import Country
from services.foundational_service.geo_module.province_app.models import Province
from services.foundational_service.geo_module.zone_app.models import Zone

logger = logging.getLogger("inscription_tests")


# ─────────────────────────────────────────────
# BASE TEST CASE — shared fixtures
# ─────────────────────────────────────────────
class BaseInscriptionTestCase(TestCase):

    def setUp(self):
        logger.info(f"\n{'='*60}")
        logger.info(f"SETUP: {self.__class__.__name__}.{self._testMethodName}")
        logger.info(f"{'='*60}")

        # Geo
        self.country = Country.objects.create(country_name="Burundi")
        self.province = Province.objects.create(province_name="Gitega", country=self.country)
        self.commune = Commune.objects.create(commune_name="Gitega", province=self.province)
        self.zone = Zone.objects.create(zone_name="Zone1", commune=self.commune)
        self.colline = Colline.objects.create(colline_name="Colline1", zone=self.zone)

        # University & Academic Year
        self.university = University.objects.create(university_name="UPG")
        self.academic_year = AcademicYear.objects.create(
            academic_year="2024-2025",
            civil_year="2025",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 7, 31),
            university=self.university,
        )
        logger.info(f"AcademicYear created: {self.academic_year}")

        # TypeFormations
        self.type_faculte = TypeFormation.objects.create(name="Faculté", code="F")
        self.type_master = TypeFormation.objects.create(name="Master", code="M")
        self.type_institut = TypeFormation.objects.create(name="Institut", code="I")
        logger.info(f"TypeFormations: F, M, I")

        # Faculties
        self.faculty_f = Faculty.objects.create(faculty_name="Sciences", types=self.type_faculte, university=self.university)
        self.faculty_m = Faculty.objects.create(faculty_name="Master Sciences", types=self.type_master, university=self.university)
        self.faculty_i = Faculty.objects.create(faculty_name="Institut Tech", types=self.type_institut, university=self.university)

        # Departments
        self.dept_info = Department.objects.create(department_name="Informatique", abreviation="INFO", faculty=self.faculty_f)
        self.dept_maths = Department.objects.create(department_name="Mathématiques", abreviation="MATH", faculty=self.faculty_f)
        self.dept_master = Department.objects.create(department_name="Dev Master", abreviation="DEV", faculty=self.faculty_m)
        self.dept_institut = Department.objects.create(department_name="Génie Civil", abreviation="GC", faculty=self.faculty_i)

        # Classes with levels
        self.class_f_l1 = Class.objects.create(class_name="L1 Info", level=1, department=self.dept_info)
        self.class_f_l2 = Class.objects.create(class_name="L2 Info", level=2, department=self.dept_info)
        self.class_f_l3 = Class.objects.create(class_name="L3 Info", level=3, department=self.dept_info)
        self.class_f_l1_maths = Class.objects.create(class_name="L1 Maths", level=1, department=self.dept_maths)
        self.class_f_l2_maths = Class.objects.create(class_name="L2 Maths", level=2, department=self.dept_maths)
        self.class_m_l1 = Class.objects.create(class_name="M1 Dev", level=1, department=self.dept_master)
        self.class_i_l1 = Class.objects.create(class_name="G1 GC", level=1, department=self.dept_institut)
        self.class_i_l2 = Class.objects.create(class_name="G2 GC", level=2, department=self.dept_institut)
        logger.info(f"Classes created: L1/L2/L3 Info, L1/L2 Maths, M1 Dev, G1/G2 GC")

        # User & Student
        self.user = User.objects.create_user(email="jean@test.com", password="pass123", first_name="Jean", last_name="Dupont")
        self.student = Student.objects.create(user=self.user, colline=self.colline)
        logger.info(f"Student created: {self.student}")

    def _save_bypass_clean(self, insc):
        """Save inscription bypassing clean() but still triggering StudentMatricule generation."""
       
        logger.debug(f"  _save_bypass_clean: student={insc.student}, class={insc.class_fk}, status={insc.regist_status}")
        self._save_bypass_clean(insc)

        if insc.class_fk:
            try:
                type_formation = insc.class_fk.department.faculty.types
                type_code = type_formation.code
                year = insc.academic_year.civil_year
                if not StudentMatricule.objects.filter(student=insc.student, type_formation=type_formation).exists():
                    count = StudentMatricule.objects.filter(matricule__startswith=f"{type_code}{year}").count()
                    StudentMatricule.objects.create(
                        student=insc.student,
                        type_formation=type_formation,
                        matricule=f"{type_code}{year}/{str(count + 1).zfill(5)}",
                        academic_year=insc.academic_year,
                    )
            except AttributeError:
                pass
        return insc

    def _run_test(self, test_fn):
        """Wrapper to log test start/pass/fail."""
        test_name = self._testMethodName
        logger.info(f"\n--- TEST: {test_name} ---")
        try:
            test_fn()
            logger.info(f"✅ PASS: {test_name}")
        except AssertionError as e:
            logger.error(f"❌ FAIL: {test_name} → {e}")
            raise
        except Exception as e:
            logger.error(f"💥 ERROR: {test_name} → {type(e).__name__}: {e}")
            raise


# ─────────────────────────────────────────────
# 1. MATRICULE GENERATION
# ─────────────────────────────────────────────
class TestMatriculeGeneration(BaseInscriptionTestCase):

    def test_matricule_generated_on_save(self):
        """Saving an inscription creates a StudentMatricule for the correct TypeFormation."""
        insc = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        Inscription.objects.filter(pk=insc.pk).delete()
        self._save_bypass_clean(insc)

        sm = StudentMatricule.objects.filter(student=self.student, type_formation=self.type_faculte).first()
        self.assertIsNotNone(sm)
        self.assertTrue(sm.matricule.startswith("F2025"))

    def test_matricule_not_duplicated_same_type(self):
        """Second inscription in same TypeFormation does not create a new StudentMatricule."""
        insc1 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        self._save_bypass_clean(insc1)

        insc2 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1_maths,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        self._save_bypass_clean(insc2)

        count = StudentMatricule.objects.filter(student=self.student, type_formation=self.type_faculte).count()
        self.assertEqual(count, 1)

    def test_different_matricule_per_type_formation(self):
        """Master inscription creates a separate StudentMatricule with M prefix."""
        insc_f = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        insc_m = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_m_l1,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        self._save_bypass_clean(insc_f)
        self._save_bypass_clean(insc_m)

        sm_f = StudentMatricule.objects.filter(student=self.student, type_formation=self.type_faculte).first()
        sm_m = StudentMatricule.objects.filter(student=self.student, type_formation=self.type_master).first()

        self.assertIsNotNone(sm_f)
        self.assertIsNotNone(sm_m)
        self.assertTrue(sm_f.matricule.startswith("F"))
        self.assertTrue(sm_m.matricule.startswith("M"))
        self.assertNotEqual(sm_f.matricule, sm_m.matricule)


    def test_generate_matricule_returns_existing(self):
        """generate_matricule() returns existing matricule without creating a new one."""
        insc = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        from django.db.models import Model
        self._save_bypass_clean(insc)

        matricule_first = insc.generate_matricule()
        matricule_second = insc.generate_matricule()

        self.assertEqual(matricule_first, matricule_second)
        self.assertEqual(StudentMatricule.objects.filter(student=self.student, type_formation=self.type_faculte).count(), 1)


# ─────────────────────────────────────────────
# 2. RULE 3 — DUPLICATE INSCRIPTION
# ─────────────────────────────────────────────
class TestDuplicateInscription(BaseInscriptionTestCase):

    def test_duplicate_inscription_same_class_blocked(self):
        """Cannot create two Active/Pending inscriptions for the same class and academic year."""
        insc1 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        self._save_bypass_clean(insc1)

        insc2 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        with self.assertRaises(ValidationError):
            insc2.clean()


# ─────────────────────────────────────────────
# 3. RULE 4 — NO HIGHER LEVEL SAME YEAR
# ─────────────────────────────────────────────
class TestNoHigherLevelSameYear(BaseInscriptionTestCase):

    def test_higher_level_same_year_blocked(self):
        """Cannot enroll in L2 if already enrolled in L1 same year same TypeFormation."""
        insc_l1 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Active",
        )
        self._save_bypass_clean(insc_l1)

        insc_l2 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l2,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        with self.assertRaises(ValidationError):
            insc_l2.clean()

    def test_same_level_different_department_same_faculty_allowed(self):
        """Can enroll in L1 Maths if already enrolled in L1 Info (same faculty, different dept)."""
        insc_info = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Active",
        )
        self._save_bypass_clean(insc_info)

        insc_maths = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1_maths,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        # Should not raise
        try:
            insc_maths.clean()
        except ValidationError as e:
            self.fail(f"clean() raised ValidationError unexpectedly: {e}")

    def test_different_type_formation_same_year_allowed(self):
        """Can enroll in Master L1 while enrolled in Faculté L1 same year."""
        insc_f = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Active",
        )
        self._save_bypass_clean(insc_f)

        insc_m = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_m_l1,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        try:
            insc_m.clean()
        except ValidationError as e:
            self.fail(f"clean() raised ValidationError unexpectedly: {e}")


# ─────────────────────────────────────────────
# 4. RULE 5 — NO LEVEL SKIP
# ─────────────────────────────────────────────
class TestNoLevelSkip(BaseInscriptionTestCase):

    def test_level_skip_blocked_without_background(self):
        """Cannot enroll in L2 without having L1 and no graduate_infos."""
        insc_l2 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l2,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        with self.assertRaises(ValidationError) as ctx:
            insc_l2.clean()
        self.assertIn("level 1", str(ctx.exception).lower())

    def test_level_skip_allowed_with_graduate_infos_same_type(self):
        """Can enroll in L2 if StudentGraduateInfo exists for same TypeFormation."""
        from services.core_service.academic_module.university_app.models import UniversityDegree

        degree = UniversityDegree.objects.create(degree_name="Licence", description="L")
        StudentGraduateInfo.objects.create(
            student=self.student,
            department=self.dept_info,
            mention="Bien",
            degree=degree,
        )

        insc_l2 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l2,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        try:
            insc_l2.clean()
        except ValidationError as e:
            self.fail(f"clean() raised ValidationError unexpectedly: {e}")


    def test_level_skip_blocked_with_graduate_infos_different_type(self):
        """Graduate infos for Institut does NOT allow skipping levels in Faculté."""
        from services.core_service.academic_module.university_app.models import UniversityDegree
        degree = UniversityDegree.objects.create(degree_name="Graduat", description="G")
        StudentGraduateInfo.objects.create(
            student=self.student,
            department=self.dept_institut,  # dept_institut → faculty_i → type_institut
            mention="Bien",
            degree=degree,
        )

        insc_l2 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l2,  # Faculté L2
            date_inscription=date.today(),
            regist_status="Pending",
        )
        with self.assertRaises(ValidationError):
            insc_l2.clean()

    def test_level_1_always_allowed(self):
        """Level 1 is always accessible without any prior inscription."""
        insc_l1 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        try:
            insc_l1.clean()
        except ValidationError as e:
            self.fail(f"clean() raised ValidationError unexpectedly: {e}")

    def test_level_2_allowed_after_level_1_completed(self):
        """Can enroll in L2 if L1 inscription exists with Completed status."""
        insc_l1 = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Completed",
        )
        self._save_bypass_clean(insc_l1)

        # Close current year first
        self.academic_year.is_closed = True
        self.academic_year.save()

        year2 = AcademicYear.objects.create(
            academic_year="2025-2026",
            civil_year="2026",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 7, 31),
            university=self.university,
        )
        insc_l2 = Inscription(
            student=self.student,
            academic_year=year2,
            class_fk=self.class_f_l2,
            date_inscription=date.today(),
            regist_status="Pending",
        )
        try:
            insc_l2.clean()
        except ValidationError as e:
            self.fail(f"clean() raised ValidationError unexpectedly: {e}")


# ─────────────────────────────────────────────
# 5. REPLACE — MATRICULE PRESERVATION
# ─────────────────────────────────────────────
class TestReplace(BaseInscriptionTestCase):

    def _create_inscription_with_matricule(self, class_fk, status="Active"):
        """Creates inscription and its StudentMatricule directly."""
        insc = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=class_fk,
            date_inscription=date.today(),
            regist_status=status,
        )
        self._save_bypass_clean(insc)

        type_formation = class_fk.department.faculty.types
        if not StudentMatricule.objects.filter(student=self.student, type_formation=type_formation).exists():
            StudentMatricule.objects.create(
                student=self.student,
                type_formation=type_formation,
                matricule=f"{type_formation.code}2025/00001",
                academic_year=self.academic_year,
            )
        return insc

    def test_replace_preserves_original_matricule(self):
        """After replace(), original TypeFormation matricule is preserved."""
        insc = self._create_inscription_with_matricule(self.class_f_l1)
        original_matricule = StudentMatricule.objects.get(student=self.student, type_formation=self.type_faculte).matricule

        insc.replace(self.class_i_l1)

        sm_f = StudentMatricule.objects.filter(student=self.student, type_formation=self.type_faculte).first()
        self.assertIsNotNone(sm_f)
        self.assertEqual(sm_f.matricule, original_matricule)

    def test_replace_creates_new_matricule_for_new_type(self):
        """After replace() to Institut, a new StudentMatricule for Institut is created."""
        insc = self._create_inscription_with_matricule(self.class_f_l1)

        insc.replace(self.class_i_l1)

        sm_i = StudentMatricule.objects.filter(student=self.student, type_formation=self.type_institut).first()
        self.assertIsNotNone(sm_i)
        self.assertTrue(sm_i.matricule.startswith("I"))

    def test_replace_marks_old_inscription_as_replaced(self):
        """After replace(), original inscription status is 'Replaced'."""
        insc = self._create_inscription_with_matricule(self.class_f_l1)
        insc.replace(self.class_i_l1)

        insc.refresh_from_db()
        self.assertEqual(insc.regist_status, "Replaced")

    def test_replace_creates_new_active_inscription(self):
        """After replace(), a new Active inscription is created for the new class."""
        insc = self._create_inscription_with_matricule(self.class_f_l1)
        new_insc = insc.replace(self.class_i_l1)

        self.assertEqual(new_insc.regist_status, "Active")
        self.assertEqual(new_insc.class_fk, self.class_i_l1)

    def test_replace_does_not_duplicate_matricule_on_return(self):
        """Replacing to same TypeFormation (different class) reuses existing matricule."""
        insc = self._create_inscription_with_matricule(self.class_f_l1)
        new_insc = insc.replace(self.class_i_l1)

        # Replace back to Faculté but different class (L1 Maths) — same TypeFormation
        new_insc.replace(self.class_f_l1_maths)

        count = StudentMatricule.objects.filter(student=self.student, type_formation=self.type_faculte).count()
        self.assertEqual(count, 1)



# ─────────────────────────────────────────────
# 6. STUDENT MATRICULE API
# ─────────────────────────────────────────────
class TestStudentMatriculeEndpoint(BaseInscriptionTestCase):
    from django.urls import reverse

    def setUp(self):
        super().setUp()
        from rest_framework.test import APIClient
        self.client = APIClient()
        admin_user = User.objects.create_superuser(email="admin@test.com", password="admin123")
        self.client.force_authenticate(user=admin_user)

    def _url(self, suffix=""):
        return f"/student/students/{self.student.id}/matricules/{suffix}"

    def _setup_matricules(self):
        StudentMatricule.objects.create(
            student=self.student,
            type_formation=self.type_faculte,
            matricule="F2025/00001",
            academic_year=self.academic_year,
        )
        StudentMatricule.objects.create(
            student=self.student,
            type_formation=self.type_master,
            matricule="M2025/00001",
            academic_year=self.academic_year,
        )

    def test_get_all_matricules(self):
        """GET /students/{id}/matricules/ returns all matricules."""
        from django.urls import reverse
        url = reverse("student-detail", kwargs={"pk": str(self.student.id)})
        response = self.client.get(f"/student/students/{self.student.id}/matricules/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]), 2)

    def test_filter_matricules_by_status(self):
        """GET /students/{id}/matricules/?status=Active returns only Active ones."""
        self._setup_matricules()
        # Create Active inscription for Faculté only
        insc = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_f_l1,
            date_inscription=date.today(),
            regist_status="Active",
        )
        self._save_bypass_clean(insc)

        response = self.client.get(f"/student/students/{self.student.id}/matricules/?status=Active")
        self.assertEqual(response.status_code, 200)
        codes = [m["type_formation_code"] for m in response.data["data"]]
        self.assertIn("F", codes)
        self.assertNotIn("M", codes)


# ─────────────────────────────────────────────
# 7. EMAIL UTILS — correct matricule per type
# ─────────────────────────────────────────────
class TestEmailMatricule(BaseInscriptionTestCase):

    def setUp(self):
        super().setUp()
        StudentMatricule.objects.create(
            student=self.student,
            type_formation=self.type_faculte,
            matricule="F2025/00001",
            academic_year=self.academic_year,
        )
        StudentMatricule.objects.create(
            student=self.student,
            type_formation=self.type_master,
            matricule="M2025/00001",
            academic_year=self.academic_year,
        )

    def _make_insc(self, class_fk):
        insc = Inscription(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=class_fk,
            date_inscription=date.today(),
            regist_status="Active",
        )
        self._save_bypass_clean(insc)
        return insc

    def test_email_context_uses_correct_matricule_for_faculte(self):
        """Email context for Faculté inscription uses F matricule."""
        from services.core_service.student_module.inscription_app.email_utils import (
            _get_matricule_for_inscription,
        )
        insc = self._make_insc(self.class_f_l1)
        matricule = _get_matricule_for_inscription(insc)
        self.assertEqual(matricule, "F2025/00001")

    def test_email_context_uses_correct_matricule_for_master(self):
        """Email context for Master inscription uses M matricule."""
        from services.core_service.student_module.inscription_app.email_utils import (
            _get_matricule_for_inscription,
        )
        insc = self._make_insc(self.class_m_l1)
        matricule = _get_matricule_for_inscription(insc)
        self.assertEqual(matricule, "M2025/00001")

    def test_email_context_fallback_when_no_student_matricule(self):
        """Email context returns 'En attente' when no StudentMatricule exists."""
        from services.core_service.student_module.inscription_app.email_utils import (
            _get_matricule_for_inscription,
        )
        # No StudentMatricule exists for this student/type combination
        # The legacy student.matricule field no longer exists
        insc = self._make_insc(self.class_i_l1)  # Institut — no StudentMatricule created
        matricule = _get_matricule_for_inscription(insc)
        self.assertEqual(matricule, "En attente")
