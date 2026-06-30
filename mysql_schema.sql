-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: ums
-- ------------------------------------------------------
-- Server version	8.0.46-0ubuntu0.24.04.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `absence_justifications`
--

DROP TABLE IF EXISTS `absence_justifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `absence_justifications` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `absence_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `reason` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `supporting_documents` json NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `submitted_at` datetime(6) NOT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `reviewed_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `absence_justificatio_reviewed_by_id_c45dcf39_fk_user_app_` (`reviewed_by_id`),
  KEY `absence_justifications_student_id_42427370_fk_students_id` (`student_id`),
  CONSTRAINT `absence_justificatio_reviewed_by_id_c45dcf39_fk_user_app_` FOREIGN KEY (`reviewed_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `absence_justifications_student_id_42427370_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `academic_performance_reports`
--

DROP TABLE IF EXISTS `academic_performance_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `academic_performance_reports` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `semester` int NOT NULL,
  `success_rate` double NOT NULL,
  `failure_rate` double NOT NULL,
  `average_grade` double NOT NULL,
  `underperforming_courses` json NOT NULL,
  `generated_at` datetime(6) NOT NULL,
  `generated_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `academic_performance_rep_academic_year_semester_6868a2e5_uniq` (`academic_year`,`semester`),
  KEY `academic_performance_generated_by_id_993ca3a4_fk_user_app_` (`generated_by_id`),
  CONSTRAINT `academic_performance_generated_by_id_993ca3a4_fk_user_app_` FOREIGN KEY (`generated_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `academic_years`
--

DROP TABLE IF EXISTS `academic_years`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `academic_years` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `civil_year` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `is_closed` tinyint(1) NOT NULL,
  `closed_date` date DEFAULT NULL,
  `closed_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `academic_years_closed_by_id_8f2436b1_fk_user_app_user_id` (`closed_by_id`),
  KEY `academic_years_university_id_067dee47_fk_universities_id` (`university_id`),
  CONSTRAINT `academic_years_closed_by_id_8f2436b1_fk_user_app_user_id` FOREIGN KEY (`closed_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `academic_years_university_id_067dee47_fk_universities_id` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `activity_reports`
--

DROP TABLE IF EXISTS `activity_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_reports` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `planned_hours` int unsigned DEFAULT NULL,
  `delivered_hours` int unsigned DEFAULT NULL,
  `completion_rate` decimal(5,2) DEFAULT NULL,
  `observations` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `timetable_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `activity_reports_timetable_id_d0febfa0_fk_timetables_id` (`timetable_id`),
  CONSTRAINT `activity_reports_timetable_id_d0febfa0_fk_timetables_id` FOREIGN KEY (`timetable_id`) REFERENCES `timetables` (`id`),
  CONSTRAINT `activity_reports_chk_1` CHECK ((`planned_hours` >= 0)),
  CONSTRAINT `activity_reports_chk_2` CHECK ((`delivered_hours` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alumni_donations`
--

DROP TABLE IF EXISTS `alumni_donations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alumni_donations` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `donation_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `purpose` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `transaction_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `donated_at` datetime(6) NOT NULL,
  `alumni_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transaction_id` (`transaction_id`),
  KEY `alumni_donations_alumni_id_f09c3d6b_fk_alumni_profiles_id` (`alumni_id`),
  CONSTRAINT `alumni_donations_alumni_id_f09c3d6b_fk_alumni_profiles_id` FOREIGN KEY (`alumni_id`) REFERENCES `alumni_profiles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alumni_event_registrations`
--

DROP TABLE IF EXISTS `alumni_event_registrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alumni_event_registrations` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `registered_at` datetime(6) NOT NULL,
  `event_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `alumni_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `alumni_event_registrations_event_id_alumni_id_9d8620cf_uniq` (`event_id`,`alumni_id`),
  KEY `alumni_event_registr_alumni_id_b49c442b_fk_alumni_pr` (`alumni_id`),
  CONSTRAINT `alumni_event_registr_alumni_id_b49c442b_fk_alumni_pr` FOREIGN KEY (`alumni_id`) REFERENCES `alumni_profiles` (`id`),
  CONSTRAINT `alumni_event_registrations_event_id_28bb9446_fk_alumni_events_id` FOREIGN KEY (`event_id`) REFERENCES `alumni_events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alumni_events`
--

DROP TABLE IF EXISTS `alumni_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alumni_events` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `event_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` datetime(6) NOT NULL,
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `max_attendees` int DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alumni_job_offers`
--

DROP TABLE IF EXISTS `alumni_job_offers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alumni_job_offers` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `company` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `job_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `requirements` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `alumni_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `alumni_job_offers_alumni_id_b31ce397_fk_alumni_profiles_id` (`alumni_id`),
  CONSTRAINT `alumni_job_offers_alumni_id_b31ce397_fk_alumni_profiles_id` FOREIGN KEY (`alumni_id`) REFERENCES `alumni_profiles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alumni_profiles`
--

DROP TABLE IF EXISTS `alumni_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alumni_profiles` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `current_position` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `company` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sector` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `linkedin_profile` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_mentor` tinyint(1) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  CONSTRAINT `alumni_profiles_student_id_608ab068_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alumni_testimonials`
--

DROP TABLE IF EXISTS `alumni_testimonials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alumni_testimonials` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_published` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `alumni_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `alumni_testimonials_alumni_id_15379de1_fk_alumni_profiles_id` (`alumni_id`),
  CONSTRAINT `alumni_testimonials_alumni_id_15379de1_fk_alumni_profiles_id` FOREIGN KEY (`alumni_id`) REFERENCES `alumni_profiles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `attendances`
--

DROP TABLE IF EXISTS `attendances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendances` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `remarks` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `timetable_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attendances_timetable_id_student_id_b0397902_uniq` (`timetable_id`,`student_id`),
  KEY `attendances_student_id_c2734dbd_fk_students_id` (`student_id`),
  CONSTRAINT `attendances_student_id_c2734dbd_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `attendances_timetable_id_39f94884_fk_timetables_id` FOREIGN KEY (`timetable_id`) REFERENCES `timetables` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `attributions`
--

DROP TABLE IF EXISTS `attributions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attributions` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_attribution` date DEFAULT NULL,
  `status_principal_teacher` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status_substitute_teacher` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `commentaire` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `validation_date` datetime(6) DEFAULT NULL,
  `validation_comments` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `academic_year_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `authorized_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `course_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `submitted_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `validated_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `principal_teacher_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `substitute_teacher_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `attributions_academic_year_id_628bb019_fk_academic_years_id` (`academic_year_id`),
  KEY `attributions_authorized_by_id_49f9fc05_fk_user_app_user_id` (`authorized_by_id`),
  KEY `attributions_course_id_e1a6eba3_fk_courses_id` (`course_id`),
  KEY `attributions_submitted_by_id_378ff290_fk_user_app_user_id` (`submitted_by_id`),
  KEY `attributions_validated_by_id_fff95a68_fk_user_app_user_id` (`validated_by_id`),
  KEY `attributions_principal_teacher_id_f5868bd7_fk_teachers_id` (`principal_teacher_id`),
  KEY `attributions_substitute_teacher_id_8381e2b9_fk_teachers_id` (`substitute_teacher_id`),
  CONSTRAINT `attributions_academic_year_id_628bb019_fk_academic_years_id` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `attributions_authorized_by_id_49f9fc05_fk_user_app_user_id` FOREIGN KEY (`authorized_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `attributions_course_id_e1a6eba3_fk_courses_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `attributions_principal_teacher_id_f5868bd7_fk_teachers_id` FOREIGN KEY (`principal_teacher_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `attributions_submitted_by_id_378ff290_fk_user_app_user_id` FOREIGN KEY (`submitted_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `attributions_substitute_teacher_id_8381e2b9_fk_teachers_id` FOREIGN KEY (`substitute_teacher_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `attributions_validated_by_id_fff95a68_fk_user_app_user_id` FOREIGN KEY (`validated_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `severity` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `entity_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `entity_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `changes` json NOT NULL,
  `ip_address` char(39) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `success` tinyint(1) NOT NULL,
  `error_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `timestamp` datetime(6) NOT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `audit_logs_user_id_88267f_idx` (`user_id`,`timestamp`),
  KEY `audit_logs_univers_5f69fc_idx` (`university_id`,`timestamp`),
  KEY `audit_logs_action_474804_idx` (`action`,`timestamp`),
  KEY `audit_logs_severit_fc52cc_idx` (`severity`),
  CONSTRAINT `audit_logs_university_id_1dbf2592_fk_universities_id` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`),
  CONSTRAINT `audit_logs_user_id_752b0e2b_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=561 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `authorization_app_supervisor`
--

DROP TABLE IF EXISTS `authorization_app_supervisor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authorization_app_supervisor` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_supervisor_active` tinyint(1) NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `authorization_app_su_user_id_1cf902dc_fk_user_app_` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `backup_records`
--

DROP TABLE IF EXISTS `backup_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `backup_records` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `backup_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_size` bigint DEFAULT NULL,
  `backup_location` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `started_at` datetime(6) NOT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `error_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `metadata` json NOT NULL,
  `initiated_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `backup_records_initiated_by_id_35a3166d_fk_user_app_user_id` (`initiated_by_id`),
  CONSTRAINT `backup_records_initiated_by_id_35a3166d_fk_user_app_user_id` FOREIGN KEY (`initiated_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `banks`
--

DROP TABLE IF EXISTS `banks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `banks` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `bank_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `bank_abreviation` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `account_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bordereau_lines`
--

DROP TABLE IF EXISTS `bordereau_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bordereau_lines` (
  `id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `bordereau_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `feessheet_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `payment_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `payment_plan_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `payment_id` (`payment_id`),
  KEY `bordereau_lines_bordereau_id_3bfad116_fk_bordereaux_id` (`bordereau_id`),
  KEY `bordereau_lines_feessheet_id_7c3fb12f_fk_fees_sheets_id` (`feessheet_id`),
  KEY `bordereau_lines_payment_plan_id_052d5bfb_fk_payment_plans_id` (`payment_plan_id`),
  CONSTRAINT `bordereau_lines_bordereau_id_3bfad116_fk_bordereaux_id` FOREIGN KEY (`bordereau_id`) REFERENCES `bordereaux` (`id`),
  CONSTRAINT `bordereau_lines_feessheet_id_7c3fb12f_fk_fees_sheets_id` FOREIGN KEY (`feessheet_id`) REFERENCES `fees_sheets` (`id`),
  CONSTRAINT `bordereau_lines_payment_id_392e6d99_fk_payments_id` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`),
  CONSTRAINT `bordereau_lines_payment_plan_id_052d5bfb_fk_payment_plans_id` FOREIGN KEY (`payment_plan_id`) REFERENCES `payment_plans` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bordereaux`
--

DROP TABLE IF EXISTS `bordereaux`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bordereaux` (
  `id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `numero` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `payment_date` date NOT NULL,
  `payment_method` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slip_uri` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `verified_at` datetime(6) DEFAULT NULL,
  `bank_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `verified_by_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bordereaux_bank_id_5d861a70_fk_banks_id` (`bank_id`),
  KEY `bordereaux_created_by_id_07f88114_fk_user_app_user_id` (`created_by_id`),
  KEY `bordereaux_parent_id_133c5ce9_fk_bordereaux_id` (`parent_id`),
  KEY `bordereaux_student_id_e33d26bd_fk_students_id` (`student_id`),
  KEY `bordereaux_verified_by_id_b9afaf04_fk_user_app_user_id` (`verified_by_id`),
  CONSTRAINT `bordereaux_bank_id_5d861a70_fk_banks_id` FOREIGN KEY (`bank_id`) REFERENCES `banks` (`id`),
  CONSTRAINT `bordereaux_created_by_id_07f88114_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `bordereaux_parent_id_133c5ce9_fk_bordereaux_id` FOREIGN KEY (`parent_id`) REFERENCES `bordereaux` (`id`),
  CONSTRAINT `bordereaux_student_id_e33d26bd_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `bordereaux_verified_by_id_b9afaf04_fk_user_app_user_id` FOREIGN KEY (`verified_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `buildings`
--

DROP TABLE IF EXISTS `buildings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `buildings` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `building_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `building_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `buildings_university_id_338089c0_fk_universities_id` (`university_id`),
  CONSTRAINT `buildings_university_id_338089c0_fk_universities_id` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `certificates`
--

DROP TABLE IF EXISTS `certificates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certificates` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `certificate_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `section_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `certificates_section_id_6f56cb66_fk_sections_id` (`section_id`),
  CONSTRAINT `certificates_section_id_6f56cb66_fk_sections_id` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `class_groups`
--

DROP TABLE IF EXISTS `class_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_groups` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `group_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `academic_year_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_fk_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `class_groups_class_fk_id_academic_yea_768f8c13_uniq` (`class_fk_id`,`academic_year_id`,`group_name`),
  KEY `class_groups_academic_year_id_817ecf92_fk_academic_years_id` (`academic_year_id`),
  CONSTRAINT `class_groups_academic_year_id_817ecf92_fk_academic_years_id` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `class_groups_class_fk_id_2f805826_fk_classes_id` FOREIGN KEY (`class_fk_id`) REFERENCES `classes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `classes`
--

DROP TABLE IF EXISTS `classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classes` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `department_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `level` smallint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `classes_class_name_department_id_ae317850_uniq` (`class_name`,`department_id`),
  KEY `classes_department_id_f0eaa53a_fk_departments_id` (`department_id`),
  CONSTRAINT `classes_department_id_f0eaa53a_fk_departments_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
  CONSTRAINT `classes_chk_1` CHECK ((`level` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collection_correspondence`
--

DROP TABLE IF EXISTS `collection_correspondence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collection_correspondence` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `correspondence_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `response` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `sent_at` datetime(6) NOT NULL,
  `sent_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `collection_correspon_sent_by_id_e90b1b80_fk_user_app_` (`sent_by_id`),
  KEY `collection_correspondence_student_id_af0558b1_fk_students_id` (`student_id`),
  CONSTRAINT `collection_correspon_sent_by_id_e90b1b80_fk_user_app_` FOREIGN KEY (`sent_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `collection_correspondence_student_id_af0558b1_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collines`
--

DROP TABLE IF EXISTS `collines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collines` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `colline_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `zone_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `collines_zone_id_16db0704_fk_zones_id` (`zone_id`),
  CONSTRAINT `collines_zone_id_16db0704_fk_zones_id` FOREIGN KEY (`zone_id`) REFERENCES `zones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `communes`
--

DROP TABLE IF EXISTS `communes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `communes` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `commune_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `province_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `communes_province_id_27a16e48_fk_provinces_id` (`province_id`),
  CONSTRAINT `communes_province_id_27a16e48_fk_provinces_id` FOREIGN KEY (`province_id`) REFERENCES `provinces` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `compiled_results`
--

DROP TABLE IF EXISTS `compiled_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compiled_results` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `results` json NOT NULL,
  `average_mark` decimal(5,2) NOT NULL,
  `status` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_promoted` tinyint(1) NOT NULL,
  `inscription_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `compiled_results_inscription_id_6de1b2fc_fk_inscriptions_id` (`inscription_id`),
  CONSTRAINT `compiled_results_inscription_id_6de1b2fc_fk_inscriptions_id` FOREIGN KEY (`inscription_id`) REFERENCES `inscriptions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `complement_requirements`
--

DROP TABLE IF EXISTS `complement_requirements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complement_requirements` (
  `id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `requirements` longtext COLLATE utf8mb4_unicode_ci,
  `amount_due` decimal(10,2) NOT NULL,
  `annual_renewal` tinyint(1) NOT NULL,
  `due_date` date DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inscription_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `course_count` int unsigned NOT NULL,
  `feesheet_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `jury_decision_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `course_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `complement_requireme_created_by_id_591924f6_fk_user_app_` (`created_by_id`),
  KEY `complement_requireme_inscription_id_5458c2cb_fk_inscripti` (`inscription_id`),
  KEY `complement_requirements_student_id_43632847_fk_students_id` (`student_id`),
  KEY `complement_requirements_feesheet_id_ef920b5d_fk_fees_sheets_id` (`feesheet_id`),
  KEY `complement_requireme_jury_decision_id_a4f8146f_fk_jury_deci` (`jury_decision_id`),
  KEY `complement_requirements_course_id_f8f6e9eb_fk_courses_id` (`course_id`),
  CONSTRAINT `complement_requireme_created_by_id_591924f6_fk_user_app_` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `complement_requireme_inscription_id_5458c2cb_fk_inscripti` FOREIGN KEY (`inscription_id`) REFERENCES `inscriptions` (`id`),
  CONSTRAINT `complement_requireme_jury_decision_id_a4f8146f_fk_jury_deci` FOREIGN KEY (`jury_decision_id`) REFERENCES `jury_decisions` (`id`),
  CONSTRAINT `complement_requirements_course_id_f8f6e9eb_fk_courses_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `complement_requirements_feesheet_id_ef920b5d_fk_fees_sheets_id` FOREIGN KEY (`feesheet_id`) REFERENCES `fees_sheets` (`id`),
  CONSTRAINT `complement_requirements_student_id_43632847_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `complement_requirements_chk_1` CHECK ((`course_count` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `compliance_audits`
--

DROP TABLE IF EXISTS `compliance_audits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compliance_audits` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `audit_period` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `compliance_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `findings` json NOT NULL,
  `recommendations` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `audit_date` datetime(6) NOT NULL,
  `audited_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `standard_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `compliance_audits_audited_by_id_95ad792d_fk_user_app_user_id` (`audited_by_id`),
  KEY `compliance_audits_standard_id_321b4575_fk_quality_standards_id` (`standard_id`),
  CONSTRAINT `compliance_audits_audited_by_id_95ad792d_fk_user_app_user_id` FOREIGN KEY (`audited_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `compliance_audits_standard_id_321b4575_fk_quality_standards_id` FOREIGN KEY (`standard_id`) REFERENCES `quality_standards` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `counseling_sessions`
--

DROP TABLE IF EXISTS `counseling_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `counseling_sessions` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `scheduled_date` datetime(6) NOT NULL,
  `duration_minutes` int NOT NULL,
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_group_session` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `counselor_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `counseling_sessions_counselor_id_ab4dbd81_fk_user_app_user_id` (`counselor_id`),
  CONSTRAINT `counseling_sessions_counselor_id_ab4dbd81_fk_user_app_user_id` FOREIGN KEY (`counselor_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `counseling_sessions_participants`
--

DROP TABLE IF EXISTS `counseling_sessions_participants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `counseling_sessions_participants` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `counselingsession_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `counseling_sessions_part_counselingsession_id_stu_497398d2_uniq` (`counselingsession_id`,`student_id`),
  KEY `counseling_sessions__student_id_40ce167f_fk_students_` (`student_id`),
  CONSTRAINT `counseling_sessions__counselingsession_id_2c9911f7_fk_counselin` FOREIGN KEY (`counselingsession_id`) REFERENCES `counseling_sessions` (`id`),
  CONSTRAINT `counseling_sessions__student_id_40ce167f_fk_students_` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `countries`
--

DROP TABLE IF EXISTS `countries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `countries` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `country_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `country_name` (`country_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `course_satisfaction_surveys`
--

DROP TABLE IF EXISTS `course_satisfaction_surveys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_satisfaction_surveys` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `course_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `teacher_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `course_quality_rating` int NOT NULL,
  `teacher_rating` int NOT NULL,
  `environment_rating` int NOT NULL,
  `comments` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `survey_date` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `course_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `course_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `cm` smallint unsigned NOT NULL,
  `td` smallint unsigned NOT NULL,
  `tp` smallint unsigned NOT NULL,
  `credits` smallint unsigned NOT NULL,
  `module_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `courses_module_id_course_name_05d32560_uniq` (`module_id`,`course_name`),
  CONSTRAINT `courses_module_id_ebd104de_fk_modules_id` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`),
  CONSTRAINT `courses_chk_1` CHECK ((`cm` >= 0)),
  CONSTRAINT `courses_chk_2` CHECK ((`td` >= 0)),
  CONSTRAINT `courses_chk_3` CHECK ((`tp` >= 0)),
  CONSTRAINT `courses_chk_4` CHECK ((`credits` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_recteur_app_paymentderogation`
--

DROP TABLE IF EXISTS `dashboard_recteur_app_paymentderogation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dashboard_recteur_app_paymentderogation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reason` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `decision_comment` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `decision_date` datetime(6) DEFAULT NULL,
  `rector_decision_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `requested_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_recteur_ap_rector_decision_by_i_29728327_fk_user_app_` (`rector_decision_by_id`),
  KEY `dashboard_recteur_ap_requested_by_id_35e53204_fk_user_app_` (`requested_by_id`),
  KEY `dashboard_recteur_ap_student_id_57224420_fk_user_app_` (`student_id`),
  CONSTRAINT `dashboard_recteur_ap_rector_decision_by_i_29728327_fk_user_app_` FOREIGN KEY (`rector_decision_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `dashboard_recteur_ap_requested_by_id_35e53204_fk_user_app_` FOREIGN KEY (`requested_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `dashboard_recteur_ap_student_id_57224420_fk_user_app_` FOREIGN KEY (`student_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dashboard_recteur_app_visitorcourseattribution`
--

DROP TABLE IF EXISTS `dashboard_recteur_app_visitorcourseattribution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dashboard_recteur_app_visitorcourseattribution` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `course_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `recommended_by` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `rector_validation` tinyint(1) NOT NULL,
  `validation_date` datetime(6) DEFAULT NULL,
  `professor_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_recteur_ap_professor_id_5685b692_fk_user_app_` (`professor_id`),
  CONSTRAINT `dashboard_recteur_ap_professor_id_5685b692_fk_user_app_` FOREIGN KEY (`professor_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `departments`
--

DROP TABLE IF EXISTS `departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departments` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `department_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `abreviation` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `faculty_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `departments_faculty_id_9081f888_fk_faculties_id` (`faculty_id`),
  CONSTRAINT `departments_faculty_id_9081f888_fk_faculties_id` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_user_app_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=1273 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=141 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=153 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `document_requests`
--

DROP TABLE IF EXISTS `document_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_requests` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `document_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `purpose` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `requested_at` datetime(6) NOT NULL,
  `processed_at` datetime(6) DEFAULT NULL,
  `notes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `processed_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `document_requests_processed_by_id_d5fb6bdc_fk_user_app_user_id` (`processed_by_id`),
  KEY `document_requests_student_id_930ac324_fk_students_id` (`student_id`),
  CONSTRAINT `document_requests_processed_by_id_d5fb6bdc_fk_user_app_user_id` FOREIGN KEY (`processed_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `document_requests_student_id_930ac324_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `documents`
--

DROP TABLE IF EXISTS `documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documents` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `document_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `document_description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `document_price` int unsigned NOT NULL,
  `processing_time` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `documents_chk_1` CHECK ((`document_price` >= 0)),
  CONSTRAINT `documents_chk_2` CHECK ((`processing_time` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `emergency_recoveries`
--

DROP TABLE IF EXISTS `emergency_recoveries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emergency_recoveries` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `recovery_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `reason` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `details` json NOT NULL,
  `result` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `initiated_at` datetime(6) NOT NULL,
  `completed_at` datetime(6) DEFAULT NULL,
  `performed_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `target_user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `emergency_recoveries_performed_by_id_fbbb854f_fk_user_app_` (`performed_by_id`),
  KEY `emergency_recoveries_target_user_id_ec1f7af1_fk_user_app_user_id` (`target_user_id`),
  CONSTRAINT `emergency_recoveries_performed_by_id_fbbb854f_fk_user_app_` FOREIGN KEY (`performed_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `emergency_recoveries_target_user_id_ec1f7af1_fk_user_app_user_id` FOREIGN KEY (`target_user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `equipment_allocations`
--

DROP TABLE IF EXISTS `equipment_allocations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment_allocations` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `allocation_date` date NOT NULL,
  `return_date` date DEFAULT NULL,
  `status` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `allocated_to_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `equipment_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `room_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `equipment_allocation_allocated_to_id_8b35faf9_fk_user_app_` (`allocated_to_id`),
  KEY `equipment_allocations_equipment_id_58fd0256_fk_equipments_id` (`equipment_id`),
  KEY `equipment_allocations_room_id_d97a3891_fk_rooms_id` (`room_id`),
  CONSTRAINT `equipment_allocation_allocated_to_id_8b35faf9_fk_user_app_` FOREIGN KEY (`allocated_to_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `equipment_allocations_equipment_id_58fd0256_fk_equipments_id` FOREIGN KEY (`equipment_id`) REFERENCES `equipments` (`id`),
  CONSTRAINT `equipment_allocations_room_id_d97a3891_fk_rooms_id` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `equipment_app_equipmenttype`
--

DROP TABLE IF EXISTS `equipment_app_equipmenttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment_app_equipmenttype` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `equipment_maintenance`
--

DROP TABLE IF EXISTS `equipment_maintenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment_maintenance` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `maintenance_date` date NOT NULL,
  `return_date` date DEFAULT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `performed_by` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cost` decimal(10,2) NOT NULL,
  `equipment_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `equipment_maintenance_equipment_id_6e96e858_fk_equipments_id` (`equipment_id`),
  CONSTRAINT `equipment_maintenance_equipment_id_6e96e858_fk_equipments_id` FOREIGN KEY (`equipment_id`) REFERENCES `equipments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `equipments`
--

DROP TABLE IF EXISTS `equipments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipments` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipment_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `serial_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `equipment_number` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `purchase_date` date DEFAULT NULL,
  `status` varchar(86) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `equipment_type_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `serial_number` (`serial_number`),
  KEY `equipments_equipment_type_id_8ec922c7_fk_equipment` (`equipment_type_id`),
  CONSTRAINT `equipments_equipment_type_id_8ec922c7_fk_equipment` FOREIGN KEY (`equipment_type_id`) REFERENCES `equipment_app_equipmenttype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exam_attendances`
--

DROP TABLE IF EXISTS `exam_attendances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_attendances` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `attendance_time` datetime(6) NOT NULL,
  `status` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `incident_notes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `recorded_at` datetime(6) DEFAULT NULL,
  `card_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `examroom_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `inscription_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `recorded_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_attendances_card_id_c050c904_fk_student_cards_id` (`card_id`),
  KEY `exam_attendances_examroom_id_61adb778_fk_exam_rooms_id` (`examroom_id`),
  KEY `exam_attendances_inscription_id_1f5a8b01_fk_inscriptions_id` (`inscription_id`),
  KEY `exam_attendances_recorded_by_id_a39209db_fk_user_app_user_id` (`recorded_by_id`),
  CONSTRAINT `exam_attendances_card_id_c050c904_fk_student_cards_id` FOREIGN KEY (`card_id`) REFERENCES `student_cards` (`id`),
  CONSTRAINT `exam_attendances_examroom_id_61adb778_fk_exam_rooms_id` FOREIGN KEY (`examroom_id`) REFERENCES `exam_rooms` (`id`),
  CONSTRAINT `exam_attendances_inscription_id_1f5a8b01_fk_inscriptions_id` FOREIGN KEY (`inscription_id`) REFERENCES `inscriptions` (`id`),
  CONSTRAINT `exam_attendances_recorded_by_id_a39209db_fk_user_app_user_id` FOREIGN KEY (`recorded_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exam_rooms`
--

DROP TABLE IF EXISTS `exam_rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_rooms` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `range_student` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `exam_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `room_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_rooms_exam_id_a172562f_fk_exams_id` (`exam_id`),
  KEY `exam_rooms_room_id_c158249e_fk_rooms_id` (`room_id`),
  CONSTRAINT `exam_rooms_exam_id_a172562f_fk_exams_id` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`),
  CONSTRAINT `exam_rooms_room_id_c158249e_fk_rooms_id` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exam_supervisors`
--

DROP TABLE IF EXISTS `exam_supervisors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_supervisors` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `exam_room_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `supervisor_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `exam_supervisors_exam_room_id_supervisor_id_8b5d1ea5_uniq` (`exam_room_id`,`supervisor_id`),
  KEY `exam_supervisors_supervisor_id_8fc19041_fk_authoriza` (`supervisor_id`),
  CONSTRAINT `exam_supervisors_exam_room_id_fa526ae1_fk_exam_rooms_id` FOREIGN KEY (`exam_room_id`) REFERENCES `exam_rooms` (`id`),
  CONSTRAINT `exam_supervisors_supervisor_id_8fc19041_fk_authoriza` FOREIGN KEY (`supervisor_id`) REFERENCES `authorization_app_supervisor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exam_types`
--

DROP TABLE IF EXISTS `exam_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_types` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `exam_type_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exams`
--

DROP TABLE IF EXISTS `exams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exams` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `exam_date` date NOT NULL,
  `start_time` datetime(6) NOT NULL,
  `end_time` datetime(6) NOT NULL,
  `status` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `academic_year_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `course_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `exam_type_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `exams_academic_year_id_e95594d4_fk_academic_years_id` (`academic_year_id`),
  KEY `exams_course_id_c9046395_fk_courses_id` (`course_id`),
  KEY `exams_created_by_id_6cd46f54_fk_user_app_user_id` (`created_by_id`),
  KEY `exams_exam_type_id_f0b43774_fk_exam_types_id` (`exam_type_id`),
  CONSTRAINT `exams_academic_year_id_e95594d4_fk_academic_years_id` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `exams_course_id_c9046395_fk_courses_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `exams_created_by_id_6cd46f54_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `exams_exam_type_id_f0b43774_fk_exam_types_id` FOREIGN KEY (`exam_type_id`) REFERENCES `exam_types` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `external_notifications`
--

DROP TABLE IF EXISTS `external_notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `external_notifications` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(125) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telephone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sent_at` datetime(6) NOT NULL,
  `delivery_status` varchar(6) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `faculties`
--

DROP TABLE IF EXISTS `faculties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculties` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `faculty_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `faculty_abreviation` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `types_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `faculties_university_id_51b484a5_fk_universities_id` (`university_id`),
  KEY `faculties_types_id_ff81031c_fk_type_formations_id` (`types_id`),
  CONSTRAINT `faculties_types_id_ff81031c_fk_type_formations_id` FOREIGN KEY (`types_id`) REFERENCES `type_formations` (`id`),
  CONSTRAINT `faculties_university_id_51b484a5_fk_universities_id` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fees_sheets`
--

DROP TABLE IF EXISTS `fees_sheets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fees_sheets` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `base_amount` int unsigned NOT NULL,
  `academic_year_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_fk_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `department_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `faculty_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `wording_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fees_sheets_academic_year_id_e3a9f39e_fk_academic_years_id` (`academic_year_id`),
  KEY `fees_sheets_class_fk_id_5aded7fc_fk_classes_id` (`class_fk_id`),
  KEY `fees_sheets_department_id_c5138411_fk_departments_id` (`department_id`),
  KEY `fees_sheets_faculty_id_7c339026_fk_faculties_id` (`faculty_id`),
  KEY `fees_sheets_wording_id_bc2bec89_fk_wordings_id` (`wording_id`),
  CONSTRAINT `fees_sheets_academic_year_id_e3a9f39e_fk_academic_years_id` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `fees_sheets_class_fk_id_5aded7fc_fk_classes_id` FOREIGN KEY (`class_fk_id`) REFERENCES `classes` (`id`),
  CONSTRAINT `fees_sheets_department_id_c5138411_fk_departments_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
  CONSTRAINT `fees_sheets_faculty_id_7c339026_fk_faculties_id` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`),
  CONSTRAINT `fees_sheets_wording_id_bc2bec89_fk_wordings_id` FOREIGN KEY (`wording_id`) REFERENCES `wordings` (`id`),
  CONSTRAINT `fees_sheets_chk_1` CHECK ((`base_amount` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `grade_complaints`
--

DROP TABLE IF EXISTS `grade_complaints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grade_complaints` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `original_grade` double NOT NULL,
  `complaint_reason` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `new_grade` double DEFAULT NULL,
  `resolution_notes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `submitted_at` datetime(6) NOT NULL,
  `resolved_at` datetime(6) DEFAULT NULL,
  `assigned_to_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `course_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `grade_complaints_assigned_to_id_193202b8_fk_user_app_user_id` (`assigned_to_id`),
  KEY `grade_complaints_course_id_a3a25676_fk_courses_id` (`course_id`),
  KEY `grade_complaints_student_id_0cc62396_fk_students_id` (`student_id`),
  CONSTRAINT `grade_complaints_assigned_to_id_193202b8_fk_user_app_user_id` FOREIGN KEY (`assigned_to_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `grade_complaints_course_id_a3a25676_fk_courses_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `grade_complaints_student_id_0cc62396_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guest_documents`
--

DROP TABLE IF EXISTS `guest_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `guest_documents` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `file` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` int NOT NULL,
  `mime_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `verified_at` datetime(6) DEFAULT NULL,
  `rejection_reason` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `verified_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `guest_request_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `guest_documents_verified_by_id_0625ff6e_fk_user_app_user_id` (`verified_by_id`),
  KEY `guest_documents_guest_request_id_ddbee49d_fk_guest_requests_id` (`guest_request_id`),
  CONSTRAINT `guest_documents_guest_request_id_ddbee49d_fk_guest_requests_id` FOREIGN KEY (`guest_request_id`) REFERENCES `guest_requests` (`id`),
  CONSTRAINT `guest_documents_verified_by_id_0625ff6e_fk_user_app_user_id` FOREIGN KEY (`verified_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guest_notifications`
--

DROP TABLE IF EXISTS `guest_notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `guest_notifications` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `document_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `guest_request_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `guest_notifications_document_id_0c070ea4_fk_guest_documents_id` (`document_id`),
  KEY `guest_notifications_guest_request_id_b0a9f1ad_fk_guest_req` (`guest_request_id`),
  CONSTRAINT `guest_notifications_document_id_0c070ea4_fk_guest_documents_id` FOREIGN KEY (`document_id`) REFERENCES `guest_documents` (`id`),
  CONSTRAINT `guest_notifications_guest_request_id_b0a9f1ad_fk_guest_req` FOREIGN KEY (`guest_request_id`) REFERENCES `guest_requests` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `guest_requests`
--

DROP TABLE IF EXISTS `guest_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `guest_requests` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `address` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `profile_submitted` tinyint(1) NOT NULL,
  `profile_submitted_at` datetime(6) DEFAULT NULL,
  `reviewed_at` datetime(6) DEFAULT NULL,
  `rejection_reason` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `requested_role_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reviewed_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `guest_requests_requested_role_id_1dfaefb5_fk_user_app_role_id` (`requested_role_id`),
  KEY `guest_requests_reviewed_by_id_c33aa4d0_fk_user_app_user_id` (`reviewed_by_id`),
  CONSTRAINT `guest_requests_requested_role_id_1dfaefb5_fk_user_app_role_id` FOREIGN KEY (`requested_role_id`) REFERENCES `user_app_role` (`id`),
  CONSTRAINT `guest_requests_reviewed_by_id_c33aa4d0_fk_user_app_user_id` FOREIGN KEY (`reviewed_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `guest_requests_user_id_e257c772_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `highschools`
--

DROP TABLE IF EXISTS `highschools`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `highschools` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `hs_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `zone_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `highschools_zone_id_e37abe0e_fk_zones_id` (`zone_id`),
  CONSTRAINT `highschools_zone_id_e37abe0e_fk_zones_id` FOREIGN KEY (`zone_id`) REFERENCES `zones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inscription_draft_inscriptiondraft`
--

DROP TABLE IF EXISTS `inscription_draft_inscriptiondraft`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inscription_draft_inscriptiondraft` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `session_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `current_step` int unsigned NOT NULL,
  `form_data` json NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_completed` tinyint(1) NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `modified_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `inscription_draft_inscriptiondraft_modified_by_id_7579a9dd` (`modified_by_id`),
  KEY `inscription_draft_inscriptiondraft_status_93179c44` (`status`),
  CONSTRAINT `inscription_draft_inscriptiondraft_chk_1` CHECK ((`current_step` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inscriptions`
--

DROP TABLE IF EXISTS `inscriptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inscriptions` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_inscription` date NOT NULL,
  `regist_status` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `withdrawal_date` date DEFAULT NULL,
  `is_year_close` tinyint(1) NOT NULL,
  `academic_year_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `class_fk_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `class_group_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `modified_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `modified_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inscriptions_student_id_academic_year_7535aa7d_uniq` (`student_id`,`academic_year_id`,`class_fk_id`),
  KEY `inscriptions_academic_year_id_2bb0a09f_fk_academic_years_id` (`academic_year_id`),
  KEY `inscriptions_class_fk_id_0720f33a_fk_classes_id` (`class_fk_id`),
  KEY `inscriptions_class_group_id_a1b9d95b_fk_class_groups_id` (`class_group_id`),
  KEY `inscription_student_5e8f34_idx` (`student_id`,`academic_year_id`,`class_fk_id`),
  KEY `inscriptions_created_by_id_698df77a_fk_user_app_user_id` (`created_by_id`),
  KEY `inscriptions_modified_by_id_106b1b6f_fk_user_app_user_id` (`modified_by_id`),
  CONSTRAINT `inscriptions_academic_year_id_2bb0a09f_fk_academic_years_id` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `inscriptions_class_fk_id_0720f33a_fk_classes_id` FOREIGN KEY (`class_fk_id`) REFERENCES `classes` (`id`),
  CONSTRAINT `inscriptions_class_group_id_a1b9d95b_fk_class_groups_id` FOREIGN KEY (`class_group_id`) REFERENCES `class_groups` (`id`),
  CONSTRAINT `inscriptions_created_by_id_698df77a_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `inscriptions_modified_by_id_106b1b6f_fk_user_app_user_id` FOREIGN KEY (`modified_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `inscriptions_student_id_52455416_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jury_decisions`
--

DROP TABLE IF EXISTS `jury_decisions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jury_decisions` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `decision` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `validated_at` datetime(6) DEFAULT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `validated_by_id` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `jury_session_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jury_decisions_student_id_ef279b7e_fk_students_id` (`student_id`),
  KEY `jury_decisions_validated_by_id_feb913b4_fk_user_app_user_id` (`validated_by_id`),
  KEY `jury_decisions_jury_session_id_dfb22a97_fk_jury_sessions_id` (`jury_session_id`),
  CONSTRAINT `jury_decisions_jury_session_id_dfb22a97_fk_jury_sessions_id` FOREIGN KEY (`jury_session_id`) REFERENCES `jury_sessions` (`id`),
  CONSTRAINT `jury_decisions_student_id_ef279b7e_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `jury_decisions_validated_by_id_feb913b4_fk_user_app_user_id` FOREIGN KEY (`validated_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jury_members`
--

DROP TABLE IF EXISTS `jury_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jury_members` (
  `id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `jury_session_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `jury_members_jury_session_id_user_id_64579ffd_uniq` (`jury_session_id`,`user_id`),
  KEY `jury_members_user_id_c3d20cef_fk_user_app_user_id` (`user_id`),
  CONSTRAINT `jury_members_jury_session_id_571c9fe1_fk_jury_sessions_id` FOREIGN KEY (`jury_session_id`) REFERENCES `jury_sessions` (`id`),
  CONSTRAINT `jury_members_user_id_c3d20cef_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jury_sessions`
--

DROP TABLE IF EXISTS `jury_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jury_sessions` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_date` datetime(6) NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `minutes_document` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `class_group_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jury_sessions_class_group_id_921ea388_fk_class_groups_id` (`class_group_id`),
  KEY `jury_sessions_created_by_id_e987eda5_fk_user_app_user_id` (`created_by_id`),
  CONSTRAINT `jury_sessions_class_group_id_921ea388_fk_class_groups_id` FOREIGN KEY (`class_group_id`) REFERENCES `class_groups` (`id`),
  CONSTRAINT `jury_sessions_created_by_id_e987eda5_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `jury_sessions_jury_members`
--

DROP TABLE IF EXISTS `jury_sessions_jury_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jury_sessions_jury_members` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `jurysession_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `jury_sessions_jury_members_jurysession_id_user_id_16197789_uniq` (`jurysession_id`,`user_id`),
  KEY `jury_sessions_jury_members_user_id_32c00588_fk_user_app_user_id` (`user_id`),
  CONSTRAINT `jury_sessions_jury_m_jurysession_id_7384c62c_fk_jury_sess` FOREIGN KEY (`jurysession_id`) REFERENCES `jury_sessions` (`id`),
  CONSTRAINT `jury_sessions_jury_members_user_id_32c00588_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mentorship_programs`
--

DROP TABLE IF EXISTS `mentorship_programs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mentorship_programs` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `expertise_area` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `started_at` datetime(6) NOT NULL,
  `mentee_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `mentor_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mentorship_programs_mentee_id_a2f31c83_fk_students_id` (`mentee_id`),
  KEY `mentorship_programs_mentor_id_d47998ad_fk_alumni_profiles_id` (`mentor_id`),
  CONSTRAINT `mentorship_programs_mentee_id_a2f31c83_fk_students_id` FOREIGN KEY (`mentee_id`) REFERENCES `students` (`id`),
  CONSTRAINT `mentorship_programs_mentor_id_d47998ad_fk_alumni_profiles_id` FOREIGN KEY (`mentor_id`) REFERENCES `alumni_profiles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `sent_at` datetime(6) NOT NULL,
  `recipient_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sender_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `messages_recipient_id_6dcabc5c_fk_user_app_user_id` (`recipient_id`),
  KEY `messages_sender_id_dc5a0bbd_fk_user_app_user_id` (`sender_id`),
  CONSTRAINT `messages_recipient_id_6dcabc5c_fk_user_app_user_id` FOREIGN KEY (`recipient_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `messages_sender_id_dc5a0bbd_fk_user_app_user_id` FOREIGN KEY (`sender_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `modules`
--

DROP TABLE IF EXISTS `modules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modules` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `module_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `class_fk_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `semester_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `modules_class_fk_id_9c472a6e_fk_classes_id` (`class_fk_id`),
  KEY `modules_semester_id_e6d4ec52_fk_semesters_id` (`semester_id`),
  CONSTRAINT `modules_class_fk_id_9c472a6e_fk_classes_id` FOREIGN KEY (`class_fk_id`) REFERENCES `classes` (`id`),
  CONSTRAINT `modules_semester_id_e6d4ec52_fk_semesters_id` FOREIGN KEY (`semester_id`) REFERENCES `semesters` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `modules_subscription`
--

DROP TABLE IF EXISTS `modules_subscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modules_subscription` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `recipient_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `notification_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `recipient_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_recipient_id_e1133bac_fk_user_app_user_id` (`recipient_id`),
  CONSTRAINT `notifications_recipient_id_e1133bac_fk_user_app_user_id` FOREIGN KEY (`recipient_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `official_documents`
--

DROP TABLE IF EXISTS `official_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `official_documents` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `document_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `signed_at` datetime(6) DEFAULT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `signed_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `official_documents_created_by_id_b0b8199d_fk_user_app_user_id` (`created_by_id`),
  KEY `official_documents_signed_by_id_79cc50ef_fk_user_app_user_id` (`signed_by_id`),
  CONSTRAINT `official_documents_created_by_id_b0b8199d_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `official_documents_signed_by_id_79cc50ef_fk_user_app_user_id` FOREIGN KEY (`signed_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `options`
--

DROP TABLE IF EXISTS `options`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `options` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `option_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `section_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `options_section_id_70cb11bc_fk_sections_id` (`section_id`),
  CONSTRAINT `options_section_id_70cb11bc_fk_sections_id` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `otp_email_emaildevice`
--

DROP TABLE IF EXISTS `otp_email_emaildevice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `otp_email_emaildevice` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `confirmed` tinyint(1) NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `token` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `valid_until` datetime(6) NOT NULL,
  `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `throttling_failure_count` int unsigned NOT NULL,
  `throttling_failure_timestamp` datetime(6) DEFAULT NULL,
  `last_generated_timestamp` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `last_used_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `otp_email_emaildevice_user_id_0215c274_fk_user_app_user_id` (`user_id`),
  CONSTRAINT `otp_email_emaildevice_user_id_0215c274_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `otp_email_emaildevice_chk_1` CHECK ((`throttling_failure_count` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `otp_static_staticdevice`
--

DROP TABLE IF EXISTS `otp_static_staticdevice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `otp_static_staticdevice` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `confirmed` tinyint(1) NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `throttling_failure_count` int unsigned NOT NULL,
  `throttling_failure_timestamp` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `last_used_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `otp_static_staticdevice_user_id_7f9cff2b_fk_user_app_user_id` (`user_id`),
  CONSTRAINT `otp_static_staticdevice_user_id_7f9cff2b_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `otp_static_staticdevice_chk_1` CHECK ((`throttling_failure_count` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `otp_static_statictoken`
--

DROP TABLE IF EXISTS `otp_static_statictoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `otp_static_statictoken` (
  `id` int NOT NULL AUTO_INCREMENT,
  `token` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `device_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `otp_static_statictok_device_id_74b7c7d1_fk_otp_stati` (`device_id`),
  KEY `otp_static_statictoken_token_d0a51866` (`token`),
  CONSTRAINT `otp_static_statictok_device_id_74b7c7d1_fk_otp_stati` FOREIGN KEY (`device_id`) REFERENCES `otp_static_staticdevice` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `otp_totp_totpdevice`
--

DROP TABLE IF EXISTS `otp_totp_totpdevice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `otp_totp_totpdevice` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `confirmed` tinyint(1) NOT NULL,
  `key` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `step` smallint unsigned NOT NULL,
  `t0` bigint NOT NULL,
  `digits` smallint unsigned NOT NULL,
  `tolerance` smallint unsigned NOT NULL,
  `drift` smallint NOT NULL,
  `last_t` bigint NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `throttling_failure_count` int unsigned NOT NULL,
  `throttling_failure_timestamp` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `last_used_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `otp_totp_totpdevice_user_id_0fb18292_fk_user_app_user_id` (`user_id`),
  CONSTRAINT `otp_totp_totpdevice_user_id_0fb18292_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `otp_totp_totpdevice_chk_1` CHECK ((`step` >= 0)),
  CONSTRAINT `otp_totp_totpdevice_chk_2` CHECK ((`digits` >= 0)),
  CONSTRAINT `otp_totp_totpdevice_chk_3` CHECK ((`tolerance` >= 0)),
  CONSTRAINT `otp_totp_totpdevice_chk_4` CHECK ((`throttling_failure_count` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `parents`
--

DROP TABLE IF EXISTS `parents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parents` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_phone` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `parent_email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `parent_type` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_alive` tinyint(1) NOT NULL,
  `is_contact_person` tinyint(1) NOT NULL,
  `profession_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `parents_profession_id_2748acef_fk_professions_id` (`profession_id`),
  CONSTRAINT `parents_profession_id_2748acef_fk_professions_id` FOREIGN KEY (`profession_id`) REFERENCES `professions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payment_allocation_logs`
--

DROP TABLE IF EXISTS `payment_allocation_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_allocation_logs` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `allocated_to_plan_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `payment_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payment_installments`
--

DROP TABLE IF EXISTS `payment_installments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_installments` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `due_date` date NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `paid_amount` decimal(10,2) NOT NULL,
  `paid_date` date DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `payment_plan_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_installments_created_by_id_5c4a7aa6_fk_user_app_user_id` (`created_by_id`),
  KEY `payment_installments_student_id_fdcf9d35_fk_students_id` (`student_id`),
  KEY `payment_installments_payment_plan_id_f884835d_fk_payment_p` (`payment_plan_id`),
  CONSTRAINT `payment_installments_created_by_id_5c4a7aa6_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `payment_installments_payment_plan_id_f884835d_fk_payment_p` FOREIGN KEY (`payment_plan_id`) REFERENCES `payment_plans` (`id`),
  CONSTRAINT `payment_installments_student_id_fdcf9d35_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payment_plans`
--

DROP TABLE IF EXISTS `payment_plans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_plans` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `monthly_amount` decimal(10,2) DEFAULT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `feessheet_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_plans_created_by_id_074e1733_fk_user_app_user_id` (`created_by_id`),
  KEY `payment_plans_feessheet_id_20921c93_fk_fees_sheets_id` (`feessheet_id`),
  CONSTRAINT `payment_plans_created_by_id_074e1733_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `payment_plans_feessheet_id_20921c93_fk_fees_sheets_id` FOREIGN KEY (`feessheet_id`) REFERENCES `fees_sheets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payment_promises`
--

DROP TABLE IF EXISTS `payment_promises`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_promises` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `promised_amount` decimal(10,2) NOT NULL,
  `promised_date` date NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `recorded_at` datetime(6) NOT NULL,
  `recorded_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_promises_recorded_by_id_72552d49_fk_user_app_user_id` (`recorded_by_id`),
  KEY `payment_promises_student_id_5345154f_fk_students_id` (`student_id`),
  CONSTRAINT `payment_promises_recorded_by_id_72552d49_fk_user_app_user_id` FOREIGN KEY (`recorded_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `payment_promises_student_id_5345154f_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payment_reminders`
--

DROP TABLE IF EXISTS `payment_reminders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_reminders` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `reminder_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount_due` decimal(10,2) NOT NULL,
  `message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sent_at` datetime(6) NOT NULL,
  `sent_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_reminders_sent_by_id_96781ad6_fk_user_app_user_id` (`sent_by_id`),
  KEY `payment_reminders_student_id_17a0f4a8_fk_students_id` (`student_id`),
  CONSTRAINT `payment_reminders_sent_by_id_96781ad6_fk_user_app_user_id` FOREIGN KEY (`sent_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `payment_reminders_student_id_17a0f4a8_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount_paid` decimal(10,2) NOT NULL,
  `payment_date` date DEFAULT NULL,
  `reception_date` date DEFAULT NULL,
  `payment_method` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `transaction_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remittance_slip_uri` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `payment_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `verified_at` datetime(6) DEFAULT NULL,
  `bank_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inscription_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `verified_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `paymentplan_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `declared_amount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payments_bank_id_dca57b51_fk_banks_id` (`bank_id`),
  KEY `payments_inscription_id_735ddaee_fk_inscriptions_id` (`inscription_id`),
  KEY `payments_user_id_189b9948_fk_user_app_user_id` (`user_id`),
  KEY `payments_verified_by_id_ce33a354_fk_user_app_user_id` (`verified_by_id`),
  KEY `payments_paymentplan_id_470c7de6_fk_payment_plans_id` (`paymentplan_id`),
  CONSTRAINT `payments_bank_id_dca57b51_fk_banks_id` FOREIGN KEY (`bank_id`) REFERENCES `banks` (`id`),
  CONSTRAINT `payments_inscription_id_735ddaee_fk_inscriptions_id` FOREIGN KEY (`inscription_id`) REFERENCES `inscriptions` (`id`),
  CONSTRAINT `payments_paymentplan_id_470c7de6_fk_payment_plans_id` FOREIGN KEY (`paymentplan_id`) REFERENCES `payment_plans` (`id`),
  CONSTRAINT `payments_user_id_189b9948_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `payments_verified_by_id_ce33a354_fk_user_app_user_id` FOREIGN KEY (`verified_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `professions`
--

DROP TABLE IF EXISTS `professions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `professions` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `profession_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `profiles`
--

DROP TABLE IF EXISTS `profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profiles` (
  `position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `faculty_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `room_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `profiles_faculty_id_1df3562c_fk_faculties_id` (`faculty_id`),
  KEY `profiles_room_id_62d75dcf_fk_rooms_id` (`room_id`),
  KEY `profiles_university_id_457d1348_fk_universities_id` (`university_id`),
  KEY `profiles_user_id_36580373_fk_user_app_user_id` (`user_id`),
  CONSTRAINT `profiles_faculty_id_1df3562c_fk_faculties_id` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`),
  CONSTRAINT `profiles_room_id_62d75dcf_fk_rooms_id` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`),
  CONSTRAINT `profiles_university_id_457d1348_fk_universities_id` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`),
  CONSTRAINT `profiles_user_id_36580373_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `program_execution_tracking`
--

DROP TABLE IF EXISTS `program_execution_tracking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `program_execution_tracking` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `program_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `planned_coverage` int NOT NULL,
  `actual_coverage` int NOT NULL,
  `progress_percentage` double NOT NULL,
  `objectives_met` tinyint(1) NOT NULL,
  `last_updated` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `program_execution_tracki_program_name_academic_ye_b34d61b2_uniq` (`program_name`,`academic_year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `program_images`
--

DROP TABLE IF EXISTS `program_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `program_images` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `image` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `is_cover` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `program_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `program_images_program_id_6f5eddbb_fk_programs_id` (`program_id`),
  CONSTRAINT `program_images_program_id_6f5eddbb_fk_programs_id` FOREIGN KEY (`program_id`) REFERENCES `programs` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `programs`
--

DROP TABLE IF EXISTS `programs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `programs` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `presentation` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` json NOT NULL,
  `admission_conditions` json NOT NULL,
  `prerequisites` json NOT NULL,
  `internship` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `duration` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `career_opportunities` json NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `faculty_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `programs_faculty_id_df9a5089_fk_faculties_id` (`faculty_id`),
  CONSTRAINT `programs_faculty_id_df9a5089_fk_faculties_id` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `provinces`
--

DROP TABLE IF EXISTS `provinces`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `provinces` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `province_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `country_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `provinces_country_id_province_name_d69db5b7_uniq` (`country_id`,`province_name`),
  CONSTRAINT `provinces_country_id_8ee0b7b3_fk_countries_id` FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quality_reports`
--

DROP TABLE IF EXISTS `quality_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quality_reports` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `report_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `data` json NOT NULL,
  `summary` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `generated_date` datetime(6) NOT NULL,
  `generated_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `quality_reports_generated_by_id_a13317c3_fk_user_app_user_id` (`generated_by_id`),
  CONSTRAINT `quality_reports_generated_by_id_a13317c3_fk_user_app_user_id` FOREIGN KEY (`generated_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `quality_standards`
--

DROP TABLE IF EXISTS `quality_standards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quality_standards` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `compliance_criteria` json NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `quality_standards_created_by_id_5f4c4522_fk_user_app_user_id` (`created_by_id`),
  CONSTRAINT `quality_standards_created_by_id_5f4c4522_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `requests`
--

DROP TABLE IF EXISTS `requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `requests` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `request_date` datetime(6) NOT NULL,
  `request_status` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `payment_verified` tinyint(1) NOT NULL,
  `admin_comment` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `updated_at` datetime(6) DEFAULT NULL,
  `document_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `payment_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `requests_document_id_7039b1de_fk_documents_id` (`document_id`),
  KEY `requests_payment_id_1b024d69_fk_payments_id` (`payment_id`),
  KEY `requests_student_id_16d00324_fk_students_id` (`student_id`),
  CONSTRAINT `requests_document_id_7039b1de_fk_documents_id` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`),
  CONSTRAINT `requests_payment_id_1b024d69_fk_payments_id` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`),
  CONSTRAINT `requests_student_id_16d00324_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `results`
--

DROP TABLE IF EXISTS `results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `results` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `mark` double NOT NULL,
  `course_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `inscription_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `results_course_id_inscription_id_session_id_018493d1_uniq` (`course_id`,`inscription_id`,`session_id`),
  KEY `results_inscription_id_318b9718_fk_inscriptions_id` (`inscription_id`),
  KEY `results_session_id_85d484ad_fk_sessions_id` (`session_id`),
  CONSTRAINT `results_course_id_11fd3636_fk_courses_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `results_inscription_id_318b9718_fk_inscriptions_id` FOREIGN KEY (`inscription_id`) REFERENCES `inscriptions` (`id`),
  CONSTRAINT `results_session_id_85d484ad_fk_sessions_id` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `role_document_requirements`
--

DROP TABLE IF EXISTS `role_document_requirements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_document_requirements` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `document_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `label` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `required` tinyint(1) NOT NULL,
  `max_size_mb` int NOT NULL,
  `accepted_formats` json NOT NULL,
  `role_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_document_requirements_role_id_document_type_340b9f3c_uniq` (`role_id`,`document_type`),
  CONSTRAINT `role_document_requirements_role_id_852d8380_fk_user_app_role_id` FOREIGN KEY (`role_id`) REFERENCES `user_app_role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rooms` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `room_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `capacity` int unsigned NOT NULL,
  `room_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `room_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_available` tinyint(1) NOT NULL,
  `building_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rooms_building_id_19cd4c2e_fk_buildings_id` (`building_id`),
  CONSTRAINT `rooms_building_id_19cd4c2e_fk_buildings_id` FOREIGN KEY (`building_id`) REFERENCES `buildings` (`id`),
  CONSTRAINT `rooms_chk_1` CHECK ((`capacity` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `schedule_slots`
--

DROP TABLE IF EXISTS `schedule_slots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule_slots` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `day_of_week` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_time` time(6) NOT NULL,
  `end_time` time(6) NOT NULL,
  `schedule_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduling_app_timetablemerge`
--

DROP TABLE IF EXISTS `scheduling_app_timetablemerge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scheduling_app_timetablemerge` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `scheduling_app_timet_created_by_id_01545f43_fk_user_app_` (`created_by_id`),
  CONSTRAINT `scheduling_app_timet_created_by_id_01545f43_fk_user_app_` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduling_app_timetablemerge_timetables`
--

DROP TABLE IF EXISTS `scheduling_app_timetablemerge_timetables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scheduling_app_timetablemerge_timetables` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `timetablemerge_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `timetable_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `scheduling_app_timetable_timetablemerge_id_timeta_b04ca552_uniq` (`timetablemerge_id`,`timetable_id`),
  KEY `scheduling_app_timet_timetable_id_7990593c_fk_timetable` (`timetable_id`),
  CONSTRAINT `scheduling_app_timet_timetable_id_7990593c_fk_timetable` FOREIGN KEY (`timetable_id`) REFERENCES `timetables` (`id`),
  CONSTRAINT `scheduling_app_timet_timetablemerge_id_84ceffd5_fk_schedulin` FOREIGN KEY (`timetablemerge_id`) REFERENCES `scheduling_app_timetablemerge` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scholarships`
--

DROP TABLE IF EXISTS `scholarships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scholarships` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `scholarship_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `provider` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `academic_year` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `managed_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `scholarships_managed_by_id_35df6a70_fk_user_app_user_id` (`managed_by_id`),
  KEY `scholarships_student_id_5b97aeb6_fk_students_id` (`student_id`),
  CONSTRAINT `scholarships_managed_by_id_35df6a70_fk_user_app_user_id` FOREIGN KEY (`managed_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `scholarships_student_id_5b97aeb6_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `secretary_notes`
--

DROP TABLE IF EXISTS `secretary_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `secretary_notes` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `is_resolved` tinyint(1) NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `faculty_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `secretary_notes_created_by_id_630b2588_fk_user_app_user_id` (`created_by_id`),
  KEY `secretary_notes_faculty_id_4f1d1755_fk_faculties_id` (`faculty_id`),
  CONSTRAINT `secretary_notes_created_by_id_630b2588_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `secretary_notes_faculty_id_4f1d1755_fk_faculties_id` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sections`
--

DROP TABLE IF EXISTS `sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sections` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `section_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `semesters`
--

DROP TABLE IF EXISTS `semesters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `semesters` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `number` smallint unsigned NOT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `number` (`number`),
  CONSTRAINT `semesters_chk_1` CHECK ((`number` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sessions` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_activities`
--

DROP TABLE IF EXISTS `student_activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_activities` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `activity_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_date` datetime(6) NOT NULL,
  `end_date` datetime(6) DEFAULT NULL,
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_approved` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `approved_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `organizer_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `student_activities_approved_by_id_b8767154_fk_user_app_user_id` (`approved_by_id`),
  KEY `student_activities_organizer_id_ac6eb343_fk_students_id` (`organizer_id`),
  CONSTRAINT `student_activities_approved_by_id_b8767154_fk_user_app_user_id` FOREIGN KEY (`approved_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `student_activities_organizer_id_ac6eb343_fk_students_id` FOREIGN KEY (`organizer_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_activities_participants`
--

DROP TABLE IF EXISTS `student_activities_participants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_activities_participants` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `studentactivity_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_activities_parti_studentactivity_id_stude_fc9807a2_uniq` (`studentactivity_id`,`student_id`),
  KEY `student_activities_p_student_id_fbe9773e_fk_students_` (`student_id`),
  CONSTRAINT `student_activities_p_student_id_fbe9773e_fk_students_` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `student_activities_p_studentactivity_id_becb392a_fk_student_a` FOREIGN KEY (`studentactivity_id`) REFERENCES `student_activities` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_card_logs`
--

DROP TABLE IF EXISTS `student_card_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_card_logs` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_date` datetime(6) NOT NULL,
  `performed_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `remarks` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `card_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `student_card_logs_card_id_bf512645_fk_student_cards_id` (`card_id`),
  CONSTRAINT `student_card_logs_card_id_bf512645_fk_student_cards_id` FOREIGN KEY (`card_id`) REFERENCES `student_cards` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_cards`
--

DROP TABLE IF EXISTS `student_cards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_cards` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `card_number` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `issue_date` date NOT NULL,
  `expiry_date` date NOT NULL,
  `status` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `photo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `qrcode_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `printed_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `card_number` (`card_number`),
  KEY `student_cards_printed_by_id_6cdbdb7c_fk_user_app_user_id` (`printed_by_id`),
  KEY `student_cards_student_id_6c34a424_fk_students_id` (`student_id`),
  CONSTRAINT `student_cards_printed_by_id_6cdbdb7c_fk_user_app_user_id` FOREIGN KEY (`printed_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `student_cards_student_id_6c34a424_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_files`
--

DROP TABLE IF EXISTS `student_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_files` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `file` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `verified_at` datetime(6) DEFAULT NULL,
  `notes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `verified_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_files_student_id_file_type_f224d625_uniq` (`student_id`,`file_type`),
  KEY `student_files_verified_by_id_ad1f69e1_fk_user_app_user_id` (`verified_by_id`),
  CONSTRAINT `student_files_student_id_63c1d4d4_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `student_files_verified_by_id_ad1f69e1_fk_user_app_user_id` FOREIGN KEY (`verified_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_graduate_info`
--

DROP TABLE IF EXISTS `student_graduate_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_graduate_info` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `option` varchar(127) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mention` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `degree_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `department_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `student_graduate_inf_degree_id_445f856d_fk_universit` (`degree_id`),
  KEY `student_graduate_info_department_id_7490d563_fk_departments_id` (`department_id`),
  KEY `student_graduate_info_student_id_b3c7325f_fk_students_id` (`student_id`),
  CONSTRAINT `student_graduate_inf_degree_id_445f856d_fk_universit` FOREIGN KEY (`degree_id`) REFERENCES `university_degrees` (`id`),
  CONSTRAINT `student_graduate_info_department_id_7490d563_fk_departments_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
  CONSTRAINT `student_graduate_info_student_id_b3c7325f_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_hs_info`
--

DROP TABLE IF EXISTS `student_hs_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_hs_info` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `se_mark` varchar(6) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_of_obtention` smallint unsigned NOT NULL,
  `certificate_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `highschool_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `student_hs_info_certificate_id_5faa4dfe_fk_certificates_id` (`certificate_id`),
  KEY `student_hs_info_highschool_id_99b5eedc_fk_highschools_id` (`highschool_id`),
  KEY `student_hs_info_student_id_ff0947aa_fk_students_id` (`student_id`),
  CONSTRAINT `student_hs_info_certificate_id_5faa4dfe_fk_certificates_id` FOREIGN KEY (`certificate_id`) REFERENCES `certificates` (`id`),
  CONSTRAINT `student_hs_info_highschool_id_99b5eedc_fk_highschools_id` FOREIGN KEY (`highschool_id`) REFERENCES `highschools` (`id`),
  CONSTRAINT `student_hs_info_student_id_ff0947aa_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `student_hs_info_chk_1` CHECK ((`date_of_obtention` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_hs_info_formation`
--

DROP TABLE IF EXISTS `student_hs_info_formation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_hs_info_formation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `studenthsinfo_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `training_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_hs_info_formatio_studenthsinfo_id_trainin_deca2ffa_uniq` (`studenthsinfo_id`,`training_id`),
  KEY `student_hs_info_formation_training_id_013140ba_fk_trainings_id` (`training_id`),
  CONSTRAINT `student_hs_info_form_studenthsinfo_id_2057cc15_fk_student_h` FOREIGN KEY (`studenthsinfo_id`) REFERENCES `student_hs_info` (`id`),
  CONSTRAINT `student_hs_info_formation_training_id_013140ba_fk_trainings_id` FOREIGN KEY (`training_id`) REFERENCES `trainings` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_matricules`
--

DROP TABLE IF EXISTS `student_matricules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_matricules` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `matricule` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `type_formation_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `matricule` (`matricule`),
  UNIQUE KEY `student_matricules_student_id_type_formation_id_33b3f382_uniq` (`student_id`,`type_formation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_retention_audits`
--

DROP TABLE IF EXISTS `student_retention_audits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_retention_audits` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_year` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_enrolled` int NOT NULL,
  `retained_students` int NOT NULL,
  `retention_rate` double NOT NULL,
  `dropout_rate` double NOT NULL,
  `dropout_reasons` json NOT NULL,
  `audited_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_retention_audits_academic_year_6692ee1a_uniq` (`academic_year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_status_changes`
--

DROP TABLE IF EXISTS `student_status_changes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_status_changes` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `reason` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `supporting_documents` json NOT NULL,
  `approval_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `effective_date` date NOT NULL,
  `requested_at` datetime(6) NOT NULL,
  `processed_at` datetime(6) DEFAULT NULL,
  `notes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `approved_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inscription_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `requested_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `student_status_chang_approved_by_id_a294f94c_fk_user_app_` (`approved_by_id`),
  KEY `student_status_chang_inscription_id_201cc3a2_fk_inscripti` (`inscription_id`),
  KEY `student_status_chang_requested_by_id_ffbf8eab_fk_user_app_` (`requested_by_id`),
  KEY `student_status_changes_student_id_f8b894a0_fk_students_id` (`student_id`),
  CONSTRAINT `student_status_chang_approved_by_id_a294f94c_fk_user_app_` FOREIGN KEY (`approved_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `student_status_chang_inscription_id_201cc3a2_fk_inscripti` FOREIGN KEY (`inscription_id`) REFERENCES `inscriptions` (`id`),
  CONSTRAINT `student_status_chang_requested_by_id_ffbf8eab_fk_user_app_` FOREIGN KEY (`requested_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `student_status_changes_student_id_f8b894a0_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `cam` smallint unsigned DEFAULT NULL,
  `colline_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `students_colline_id_f5d70d00_fk_collines_id` (`colline_id`),
  CONSTRAINT `students_colline_id_f5d70d00_fk_collines_id` FOREIGN KEY (`colline_id`) REFERENCES `collines` (`id`),
  CONSTRAINT `students_user_id_42864fc9_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `students_chk_1` CHECK ((`cam` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `students_parent`
--

DROP TABLE IF EXISTS `students_parent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students_parent` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `student_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `parent_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `students_parent_student_id_parent_id_b01afa56_uniq` (`student_id`,`parent_id`),
  KEY `students_parent_parent_id_4b248623_fk_parents_id` (`parent_id`),
  CONSTRAINT `students_parent_parent_id_4b248623_fk_parents_id` FOREIGN KEY (`parent_id`) REFERENCES `parents` (`id`),
  CONSTRAINT `students_parent_student_id_42cf9546_fk_students_id` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `suggestions`
--

DROP TABLE IF EXISTS `suggestions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suggestions` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `suggestion_date` date NOT NULL,
  `suggestion` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `attribution_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `teacher_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `suggestions_attribution_id_daae5921_fk_attributions_id` (`attribution_id`),
  KEY `suggestions_user_id_be2b2735_fk_user_app_user_id` (`user_id`),
  KEY `suggestions_teacher_id_5407ef31_fk_teachers_id` (`teacher_id`),
  CONSTRAINT `suggestions_attribution_id_daae5921_fk_attributions_id` FOREIGN KEY (`attribution_id`) REFERENCES `attributions` (`id`),
  CONSTRAINT `suggestions_teacher_id_5407ef31_fk_teachers_id` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `suggestions_user_id_be2b2735_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `supplements`
--

DROP TABLE IF EXISTS `supplements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `supplements` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `validation` tinyint(1) NOT NULL,
  `validation_date` date DEFAULT NULL,
  `mark` decimal(4,2) DEFAULT NULL,
  `course_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `inscription_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `supplements_course_id_b203cf53_fk_courses_id` (`course_id`),
  KEY `supplements_inscription_id_53d21c71_fk_inscriptions_id` (`inscription_id`),
  CONSTRAINT `supplements_course_id_b203cf53_fk_courses_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `supplements_inscription_id_53d21c71_fk_inscriptions_id` FOREIGN KEY (`inscription_id`) REFERENCES `inscriptions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `survey_questions`
--

DROP TABLE IF EXISTS `survey_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `survey_questions` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `label` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `required` tinyint(1) NOT NULL,
  `section` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `placeholder` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `options` json NOT NULL,
  `max` int DEFAULT NULL,
  `order` int NOT NULL,
  `survey_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `survey_questions_survey_id_f46efb7d_fk_surveys_id` (`survey_id`),
  CONSTRAINT `survey_questions_survey_id_f46efb7d_fk_surveys_id` FOREIGN KEY (`survey_id`) REFERENCES `surveys` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `survey_responses`
--

DROP TABLE IF EXISTS `survey_responses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `survey_responses` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `respondent_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `respondent_email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `responses` json NOT NULL,
  `submitted_at` datetime(6) NOT NULL,
  `respondent_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `survey_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `survey_responses_respondent_id_afb11183_fk_user_app_user_id` (`respondent_id`),
  KEY `survey_responses_survey_id_f5da88e4_fk_surveys_id` (`survey_id`),
  CONSTRAINT `survey_responses_respondent_id_afb11183_fk_user_app_user_id` FOREIGN KEY (`respondent_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `survey_responses_survey_id_f5da88e4_fk_surveys_id` FOREIGN KEY (`survey_id`) REFERENCES `surveys` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `surveys`
--

DROP TABLE IF EXISTS `surveys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `surveys` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `multi_step` tinyint(1) NOT NULL,
  `start_date` datetime(6) DEFAULT NULL,
  `end_date` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `surveys_created_by_id_0d7e6676_fk_user_app_user_id` (`created_by_id`),
  CONSTRAINT `surveys_created_by_id_0d7e6676_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_configurations`
--

DROP TABLE IF EXISTS `system_configurations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_configurations` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` json NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `modified_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `system_configurations_category_key_be616a54_uniq` (`category`,`key`),
  KEY `system_configurations_created_by_id_9a54e20b_fk_user_app_user_id` (`created_by_id`),
  KEY `system_configuration_modified_by_id_21071904_fk_user_app_` (`modified_by_id`),
  KEY `system_conf_categor_eb7070_idx` (`category`,`is_active`),
  CONSTRAINT `system_configuration_modified_by_id_21071904_fk_user_app_` FOREIGN KEY (`modified_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `system_configurations_created_by_id_9a54e20b_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `teacher_payment_claims`
--

DROP TABLE IF EXISTS `teacher_payment_claims`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_payment_claims` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `hours_taught` int NOT NULL,
  `hourly_rate` decimal(10,2) NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `submitted_at` datetime(6) NOT NULL,
  `processed_at` datetime(6) DEFAULT NULL,
  `approved_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `course_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `teacher_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `verified_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_payment_clai_approved_by_id_48ffb4b8_fk_user_app_` (`approved_by_id`),
  KEY `teacher_payment_claims_course_id_5af35b39_fk_courses_id` (`course_id`),
  KEY `teacher_payment_claims_teacher_id_1e56c20d_fk_teachers_id` (`teacher_id`),
  KEY `teacher_payment_clai_verified_by_id_7ac44aaf_fk_user_app_` (`verified_by_id`),
  CONSTRAINT `teacher_payment_clai_approved_by_id_48ffb4b8_fk_user_app_` FOREIGN KEY (`approved_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `teacher_payment_clai_verified_by_id_7ac44aaf_fk_user_app_` FOREIGN KEY (`verified_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `teacher_payment_claims_course_id_5af35b39_fk_courses_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  CONSTRAINT `teacher_payment_claims_teacher_id_1e56c20d_fk_teachers_id` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `teacher_workload`
--

DROP TABLE IF EXISTS `teacher_workload`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_workload` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_hours` int NOT NULL,
  `assigned_hours` decimal(6,2) NOT NULL,
  `is_permanent` tinyint(1) NOT NULL,
  `academic_year_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `faculty_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `teacher_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `teacher_workload_faculty_id_teacher_id_ac_91b0480a_uniq` (`faculty_id`,`teacher_id`,`academic_year_id`),
  KEY `teacher_workload_academic_year_id_0edbcfda_fk_academic_years_id` (`academic_year_id`),
  KEY `teacher_workload_teacher_id_1b247e41_fk_user_app_user_id` (`teacher_id`),
  CONSTRAINT `teacher_workload_academic_year_id_0edbcfda_fk_academic_years_id` FOREIGN KEY (`academic_year_id`) REFERENCES `academic_years` (`id`),
  CONSTRAINT `teacher_workload_faculty_id_16d658a9_fk_faculties_id` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`),
  CONSTRAINT `teacher_workload_teacher_id_1b247e41_fk_user_app_user_id` FOREIGN KEY (`teacher_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `teacher_grade` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `speciality` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `url_cv` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `url_other` json DEFAULT NULL,
  `url_diploma` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `degree_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `teachers_degree_id_4bd8bcd7_fk_university_degrees_id` (`degree_id`),
  KEY `teachers_university_id_3a6241f4_fk_universities_id` (`university_id`),
  CONSTRAINT `teachers_degree_id_4bd8bcd7_fk_university_degrees_id` FOREIGN KEY (`degree_id`) REFERENCES `university_degrees` (`id`),
  CONSTRAINT `teachers_university_id_3a6241f4_fk_universities_id` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`),
  CONSTRAINT `teachers_user_id_6fdcda53_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `teaching_progress`
--

DROP TABLE IF EXISTS `teaching_progress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teaching_progress` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `progress_percentage` decimal(5,2) NOT NULL,
  `last_updated` datetime(6) NOT NULL,
  `attribution_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `faculty_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `submitted_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attribution_id` (`attribution_id`),
  KEY `teaching_progress_faculty_id_7e56bdf0_fk_faculties_id` (`faculty_id`),
  KEY `teaching_progress_submitted_by_id_c8ef5e1e_fk_user_app_user_id` (`submitted_by_id`),
  CONSTRAINT `teaching_progress_attribution_id_b6f139b0_fk_attributions_id` FOREIGN KEY (`attribution_id`) REFERENCES `attributions` (`id`),
  CONSTRAINT `teaching_progress_faculty_id_7e56bdf0_fk_faculties_id` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`id`),
  CONSTRAINT `teaching_progress_submitted_by_id_c8ef5e1e_fk_user_app_user_id` FOREIGN KEY (`submitted_by_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `timetables`
--

DROP TABLE IF EXISTS `timetables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `timetables` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `status` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_date` datetime(6) NOT NULL,
  `published_date` datetime(6) DEFAULT NULL,
  `attribution_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `class_group_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `room_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `timetables_class_group_id_room_id_s_f3fcebfc_uniq` (`class_group_id`,`room_id`,`start_date`,`end_date`),
  KEY `timetables_attribution_id_f8a66420_fk_attributions_id` (`attribution_id`),
  KEY `timetables_created_by_id_c235403c_fk_user_app_user_id` (`created_by_id`),
  KEY `timetables_room_id_fa75cc82_fk_rooms_id` (`room_id`),
  CONSTRAINT `timetables_attribution_id_f8a66420_fk_attributions_id` FOREIGN KEY (`attribution_id`) REFERENCES `attributions` (`id`),
  CONSTRAINT `timetables_class_group_id_8e2aff42_fk_class_groups_id` FOREIGN KEY (`class_group_id`) REFERENCES `class_groups` (`id`),
  CONSTRAINT `timetables_created_by_id_c235403c_fk_user_app_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `timetables_room_id_fa75cc82_fk_rooms_id` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `timetables_shared_with`
--

DROP TABLE IF EXISTS `timetables_shared_with`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `timetables_shared_with` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `timetable_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `classgroup_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `timetables_shared_with_timetable_id_classgroup_id_39956a54_uniq` (`timetable_id`,`classgroup_id`),
  KEY `timetables_shared_with_classgroup_id_3dc4a7fc_fk_class_groups_id` (`classgroup_id`),
  CONSTRAINT `timetables_shared_with_classgroup_id_3dc4a7fc_fk_class_groups_id` FOREIGN KEY (`classgroup_id`) REFERENCES `class_groups` (`id`),
  CONSTRAINT `timetables_shared_with_timetable_id_3e439d2d_fk_timetables_id` FOREIGN KEY (`timetable_id`) REFERENCES `timetables` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `timetables_slots`
--

DROP TABLE IF EXISTS `timetables_slots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `timetables_slots` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `timetable_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `scheduleslot_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `timetables_slots_timetable_id_scheduleslot_id_05a65987_uniq` (`timetable_id`,`scheduleslot_id`),
  KEY `timetables_slots_scheduleslot_id_14a61ca4_fk_schedule_slots_id` (`scheduleslot_id`),
  CONSTRAINT `timetables_slots_scheduleslot_id_14a61ca4_fk_schedule_slots_id` FOREIGN KEY (`scheduleslot_id`) REFERENCES `schedule_slots` (`id`),
  CONSTRAINT `timetables_slots_timetable_id_fac564ef_fk_timetables_id` FOREIGN KEY (`timetable_id`) REFERENCES `timetables` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `token_blacklist_blacklistedtoken`
--

DROP TABLE IF EXISTS `token_blacklist_blacklistedtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_id` (`token_id`),
  CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=183 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `token_blacklist_outstandingtoken`
--

DROP TABLE IF EXISTS `token_blacklist_outstandingtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `jti` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  KEY `token_blacklist_outs_user_id_83bc629a_fk_user_app_` (`user_id`),
  CONSTRAINT `token_blacklist_outs_user_id_83bc629a_fk_user_app_` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=193 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `training_centers`
--

DROP TABLE IF EXISTS `training_centers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `training_centers` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `commune_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `training_centers_commune_id_fc7328be_fk_communes_id` (`commune_id`),
  CONSTRAINT `training_centers_commune_id_fc7328be_fk_communes_id` FOREIGN KEY (`commune_id`) REFERENCES `communes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trainings`
--

DROP TABLE IF EXISTS `trainings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trainings` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `domaine` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `certificate` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `training_center_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `trainings_training_center_id_f7405a9a_fk_training_centers_id` (`training_center_id`),
  CONSTRAINT `trainings_training_center_id_f7405a9a_fk_training_centers_id` FOREIGN KEY (`training_center_id`) REFERENCES `training_centers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `type_formations`
--

DROP TABLE IF EXISTS `type_formations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `type_formations` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `universities`
--

DROP TABLE IF EXISTS `universities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `universities` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `university_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `university_abrev` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `country_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `universities_country_id_8a5c3fe2_fk_countries_id` (`country_id`),
  CONSTRAINT `universities_country_id_8a5c3fe2_fk_countries_id` FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `university_app_universityadmin`
--

DROP TABLE IF EXISTS `university_app_universityadmin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_app_universityadmin` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_super_admin` tinyint(1) NOT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `university_app_unive_university_id_8f33cd9f_fk_universit` (`university_id`),
  CONSTRAINT `university_app_unive_university_id_8f33cd9f_fk_universit` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`),
  CONSTRAINT `university_app_unive_user_id_3d40de21_fk_user_app_` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `university_configurations`
--

DROP TABLE IF EXISTS `university_configurations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_configurations` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` json NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `modified_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `university_configuration_university_id_category_k_e20b9a79_uniq` (`university_id`,`category`,`key`),
  KEY `university_configura_created_by_id_c9122914_fk_user_app_` (`created_by_id`),
  KEY `university_configura_modified_by_id_c5572f36_fk_user_app_` (`modified_by_id`),
  KEY `university__univers_95fc82_idx` (`university_id`,`category`),
  KEY `university__is_acti_d6fc9b_idx` (`is_active`),
  CONSTRAINT `university_configura_created_by_id_c9122914_fk_user_app_` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `university_configura_modified_by_id_c5572f36_fk_user_app_` FOREIGN KEY (`modified_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `university_configura_university_id_7c3cdb8a_fk_universit` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `university_degrees`
--

DROP TABLE IF EXISTS `university_degrees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_degrees` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `degree_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `university_notifications`
--

DROP TABLE IF EXISTS `university_notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_notifications` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `notification_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `priority` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_read` tinyint(1) NOT NULL,
  `read_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `recipient_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `university_notificat_university_id_863b0c83_fk_universit` (`university_id`),
  KEY `university__recipie_731fb1_idx` (`recipient_id`,`is_read`),
  KEY `university__priorit_f8f14c_idx` (`priority`),
  CONSTRAINT `university_notificat_recipient_id_a37aa1f6_fk_user_app_` FOREIGN KEY (`recipient_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `university_notificat_university_id_863b0c83_fk_universit` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `university_profiles`
--

DROP TABLE IF EXISTS `university_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_profiles` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `website` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `logo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `max_users` int NOT NULL,
  `max_storage_gb` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `university_id` (`university_id`),
  CONSTRAINT `university_profiles_university_id_3c143a2f_fk_universities_id` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `university_statistics`
--

DROP TABLE IF EXISTS `university_statistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_statistics` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_students` int NOT NULL,
  `total_teachers` int NOT NULL,
  `total_faculties` int NOT NULL,
  `total_departments` int NOT NULL,
  `total_courses` int NOT NULL,
  `active_enrollments` int NOT NULL,
  `pending_payments` decimal(15,2) NOT NULL,
  `completed_exams` int NOT NULL,
  `pending_document_requests` int NOT NULL,
  `statistics_data` json NOT NULL,
  `calculated_at` datetime(6) NOT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `university_statistics_university_id_a75aebfe_fk_universities_id` (`university_id`),
  CONSTRAINT `university_statistics_university_id_a75aebfe_fk_universities_id` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `university_subscriptions`
--

DROP TABLE IF EXISTS `university_subscriptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `university_subscriptions` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `is_trial` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `module_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `university_subscriptions_university_id_module_id_5ecdb728_uniq` (`university_id`,`module_id`),
  KEY `university_subscript_created_by_id_d1d1c149_fk_user_app_` (`created_by_id`),
  KEY `university__univers_db8ed1_idx` (`university_id`,`status`),
  KEY `university__module__c6a148_idx` (`module_id`,`status`),
  KEY `university__end_dat_298b9a_idx` (`end_date`),
  CONSTRAINT `university_subscript_created_by_id_d1d1c149_fk_user_app_` FOREIGN KEY (`created_by_id`) REFERENCES `user_app_user` (`id`),
  CONSTRAINT `university_subscript_module_id_51bfee88_fk_modules_s` FOREIGN KEY (`module_id`) REFERENCES `modules_subscription` (`id`),
  CONSTRAINT `university_subscript_university_id_582d6221_fk_universit` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_app_role`
--

DROP TABLE IF EXISTS `user_app_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_app_role` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `user_app_ro_name_da5864_idx` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_app_user`
--

DROP TABLE IF EXISTS `user_app_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_app_user` (
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `first_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `marital_status` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email_verified` tinyint(1) NOT NULL,
  `requires_2fa` tinyint(1) NOT NULL,
  `requires_2fa_qr` tinyint(1) NOT NULL,
  `requires_2fa_email` tinyint(1) NOT NULL,
  `requires_2fa_static` tinyint(1) NOT NULL,
  `totp_secret_key` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `profile_picture` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `spoken_languages` json DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `nationality_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `university_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `user_app_user_nationality_id_66fde1c0_fk_countries_id` (`nationality_id`),
  KEY `user_app_user_university_id_5a69d19f_fk_universities_id` (`university_id`),
  KEY `user_app_user_role_id_c712dbeb_fk_user_app_role_id` (`role_id`),
  CONSTRAINT `user_app_user_nationality_id_66fde1c0_fk_countries_id` FOREIGN KEY (`nationality_id`) REFERENCES `countries` (`id`),
  CONSTRAINT `user_app_user_role_id_c712dbeb_fk_user_app_role_id` FOREIGN KEY (`role_id`) REFERENCES `user_app_role` (`id`),
  CONSTRAINT `user_app_user_university_id_5a69d19f_fk_universities_id` FOREIGN KEY (`university_id`) REFERENCES `universities` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_app_user_groups`
--

DROP TABLE IF EXISTS `user_app_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_app_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_app_user_groups_user_id_group_id_13ac6bde_uniq` (`user_id`,`group_id`),
  KEY `user_app_user_groups_group_id_77b237a8_fk_auth_group_id` (`group_id`),
  CONSTRAINT `user_app_user_groups_group_id_77b237a8_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `user_app_user_groups_user_id_9ac3bba9_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_app_user_residence`
--

DROP TABLE IF EXISTS `user_app_user_residence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_app_user_residence` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `colline_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_app_user_residence_user_id_colline_id_da41f4d8_uniq` (`user_id`,`colline_id`),
  KEY `user_app_user_residence_colline_id_301e1ba9_fk_collines_id` (`colline_id`),
  CONSTRAINT `user_app_user_residence_colline_id_301e1ba9_fk_collines_id` FOREIGN KEY (`colline_id`) REFERENCES `collines` (`id`),
  CONSTRAINT `user_app_user_residence_user_id_8860d0fc_fk_user_app_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_app_user_user_permissions`
--

DROP TABLE IF EXISTS `user_app_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_app_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_app_user_user_permi_user_id_permission_id_46c11fb3_uniq` (`user_id`,`permission_id`),
  KEY `user_app_user_user_p_permission_id_66c16b85_fk_auth_perm` (`permission_id`),
  CONSTRAINT `user_app_user_user_p_permission_id_66c16b85_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_app_user_user_p_user_id_6099c7a4_fk_user_app_` FOREIGN KEY (`user_id`) REFERENCES `user_app_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wordings`
--

DROP TABLE IF EXISTS `wordings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wordings` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `wording_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `zones`
--

DROP TABLE IF EXISTS `zones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `zones` (
  `id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `zone_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `commune_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `zones_commune_id_a3e36f33_fk_communes_id` (`commune_id`),
  CONSTRAINT `zones_commune_id_a3e36f33_fk_communes_id` FOREIGN KEY (`commune_id`) REFERENCES `communes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-30  6:57:09
