# Tests d'inscription — Documentation

## Architecture

```
BaseInscriptionTestCase          ← setUp() partagé : geo, université, académie, classes, étudiant, infos lycée
 ├── TestMatriculeGeneration          (4 tests) — génération des matricules à la sauvegarde
 ├── TestDuplicateInscription         (1 test)  — règle 3 : pas de doublon même classe/même année
 ├── TestNoHigherLevelSameYear        (3 tests) — règle 4 : pas d'inscription à un niveau inférieur
  ├── TestNoLevelSkip                  (5 tests) — règle 5 : pas de saut de niveau sans background
  ├── TestReplace                      (5 tests) — remplacement de classe avec conservation du matricule
  ├── TestStudentMatriculeEndpoint     (2 tests) — API REST des matricules
  ├── TestEmailMatricule               (3 tests) — matricule correct dans les emails
  ├── TestAutoActivationByStudentService (3 tests) — activation automatique par student_service
  └── TestRegistrationEligibility      (4 tests) — règles d'éligibilité (se_mark, background Master)
```

**Total : 30 tests**

---

## setUp() partagé — `BaseInscriptionTestCase`

Données créées automatiquement avant chaque test :

| Catégorie | Éléments |
|-----------|----------|
| **Géo** | Burundi → Gitega → (province, commune, zone, colline) |
| **Université** | UPG, année 2024-2025 (civil 2025) |
| **TypeFormation** | Faculté (F), Master (M), Institut (I) |
| **Facultés** | Sciences (F), Master Sciences (M), Institut Tech (I) |
| **Départements** | Informatique, Mathématiques (F) — Dev Master (M) — Génie Civil (I) |
| **Classes** | L1/L2/L3 Info, L1/L2 Maths, M1 Dev, G1 GC, G2 GC |
| **Étudiant** | Jean Dupont (jean@test.com) |
| **Infos lycée** | Lycée de Gitega, Diplôme d'État section Scientifique, se_mark=75 |

### `_save_bypass_clean(insc)`

Sauvegarde une inscription **sans passer par `clean()`** (contourne les validateurs métier) tout en générant le `StudentMatricule` associé. Utilisée par les tests pour créer des inscriptions de base sans déclencher les règles de validation.

---

## 1. `TestMatriculeGeneration` — 4 tests

### `test_matricule_generated_on_save`
Crée une inscription Pending en L1 Info → vérifie qu'un `StudentMatricule` est créé avec le préfixe `F2025`.

### `test_matricule_not_duplicated_same_type`
Crée deux inscriptions (L1 Info + L1 Maths) dans le même TypeFormation (Faculté) → vérifie qu'un seul `StudentMatricule` existe.

### `test_different_matricule_per_type_formation`
Crée une inscription Faculté (L1 Info) et une inscription Master (M1 Dev) → vérifie que deux matricules distincts sont créés : `F...` et `M...`.

### `test_generate_matricule_returns_existing`
Appelle `generate_matricule()` deux fois → vérifie qu'on obtient le même matricule et qu'aucun doublon n'est créé.

---

## 2. `TestDuplicateInscription` — 1 test

### `test_duplicate_inscription_same_class_blocked`
Crée une inscription Pending en L1 Info, puis tente d'en créer une seconde identique → `ValidationError` attendue (règle 3 : pas deux inscriptions Active/Pending pour la même classe/même année).

---

## 3. `TestNoHigherLevelSameYear` — 3 tests

### `test_higher_level_same_year_blocked`
Crée une inscription Active en L2 Info, puis tente une inscription en L1 Info (même année, même département) → `ValidationError` attendue (règle 4 : pas de niveau inférieur dans le même département).

### `test_same_level_different_department_same_faculty_allowed`
Crée une inscription Active en L1 Info, puis une inscription en L1 Maths (même faculté, département différent) → aucune erreur (autorisé : années communes où les étudiants se répartissent dans les départements).

### `test_different_type_formation_same_year_allowed`
Crée une inscription Active en L1 Info (Faculté), puis une inscription en M1 Dev (Master) — nécessite `StudentGraduateInfo` → aucune erreur (autorisé : types de formation différents).

---

## 4. `TestNoLevelSkip` — 5 tests

### `test_level_skip_blocked_without_background`
Tente une inscription en L2 Info sans L1 préalable et sans `StudentGraduateInfo` → `ValidationError` avec message contenant "niveau 1" (règle 5 : pas de saut de niveau).

### `test_level_skip_allowed_with_graduate_infos_same_type`
Ajoute `StudentGraduateInfo` pour le même TypeFormation (Faculté), puis tente L2 Info → aucune erreur (parcours universitaire antérieur autorise le saut).

### `test_level_skip_blocked_with_graduate_infos_different_type`
Ajoute `StudentGraduateInfo` pour l'Institut (GC), puis tente L2 Faculté → `ValidationError` (les infos de l'Institut ne permettent pas de sauter des niveaux en Faculté — types différents).

### `test_level_1_always_allowed`
Crée une inscription en L1 Info sans aucun prérequis → aucune erreur (le niveau 1 est toujours accessible).

### `test_level_2_allowed_after_level_1_completed`
Crée une inscription Completed en L1 Info, ferme l'année, crée une nouvelle année, puis tente L2 Info → aucune erreur (L1 complété autorise le passage en L2).

---

## 5. `TestReplace` — 5 tests

Mécanisme : changer un étudiant de classe (ex. passer de Faculté à Institut) tout en conservant l'historique.

### `test_replace_preserves_original_matricule`
Crée une inscription en L1 Info avec matricule F, remplace vers G1 GC (Institut) → le matricule F d'origine est conservé.

### `test_replace_creates_new_matricule_for_new_type`
Crée une inscription en L1 Info (Faculté), remplace vers G1 GC (Institut) → un nouveau matricule avec préfixe `I` est créé pour l'Institut.

### `test_replace_marks_old_inscription_as_replaced`
Crée une inscription Active en L1 Info, la remplace → l'inscription d'origine passe au statut `Replaced`.

### `test_replace_creates_new_active_inscription`
Crée une inscription Active en L1 Info, remplace vers G1 GC → une nouvelle inscription Active est créée pour G1 GC.

### `test_replace_does_not_duplicate_matricule_on_return`
Crée une inscription Faculté, remplace vers Institut, puis remplace vers Faculté (L1 Maths) → un seul matricule Faculté existe (pas de duplication).

---

## 6. `TestStudentMatriculeEndpoint` — 2 tests

API REST : `/api/student/students/{id}/matricules/`

### `test_get_all_matricules`
Crée deux `StudentMatricule` (F et M) → `GET /api/student/students/{id}/matricules/` → 200, 2 matricules retournés.

### `test_filter_matricules_by_status`
Crée deux `StudentMatricule` (F et M), crée une inscription Active en Faculté → `GET /...?status=Active` → 200, seul le code `F` est retourné.

---

## 7. `TestEmailMatricule` — 3 tests

Teste `_get_matricule_for_inscription()` dans `email_utils.py` : retrouver le bon matricule pour une inscription donnée.

### `test_email_context_uses_correct_matricule_for_faculte`
Crée une inscription en L1 Info → le matricule retourné est `F2025/00001` (préfixe F).

### `test_email_context_uses_correct_matricule_for_master`
Crée une inscription en M1 Dev → le matricule retourné est `M2025/00001` (préfixe M).

### `test_email_context_fallback_when_no_student_matricule`
Crée un nouvel étudiant **sans aucun matricule**, l'inscrit en G1 GC → le matricule retourné est `"En attente"` (fallback quand aucun matricule n'existe).

---

## 8. `TestAutoActivationByStudentService` — 3 tests

Teste l'auto-activation des inscriptions quand le créateur/modificateur a le rôle `student_service`.

Logique testée : `InscriptionAutomation.prepare()` dans `services/inscription_automation.py`.

### `test_student_service_auto_activates_pending`
Crée une inscription `Pending` via `Inscription.save(user=student_service_user)` → le statut passe automatiquement à `Active`.

### `test_non_student_service_stays_pending`
Crée une inscription `Pending` via `Inscription.save(user=normal_user)` → le statut reste `Pending` (pas de rôle `student_service`).

### `test_student_service_auto_activates_on_update`
Crée une inscription `Pending` via `Model.save()` (sans user, `created_by=None`), puis `Inscription.save(user=student_service_user)` avec `has_verified_payment` mocké → le statut passe à `Active` (auto-activation déclenchée par la mise à jour).

---

## 9. `TestRegistrationEligibility` — 4 tests

Teste `_validate_registration_eligibility()` dans `models.py:137-181` : règles d'admission basées sur le score au lycée (`se_mark`) et le parcours universitaire (`StudentGraduateInfo`).

Logique :
- **Master/Doctorat** : toujours besoin d'un parcours universitaire
- **Faculté (F)** : besoin de `se_mark` ≥ 50
- **Institut (I)** : accessible même avec `se_mark` < 50
- **`se_mark` manquant** : bloqué pour F et I

### `test_master_blocked_without_graduate_info`
Étudiant avec `se_mark=75` mais sans `StudentGraduateInfo` → `ValidationError` contenant `"Master"` (règle 4 : Master sans parcours universitaire est bloqué).

### `test_bac_blocked_when_se_mark_below_50`
Étudiant avec `se_mark=30` → tentative d'inscription en Faculté (L1 Info) → `ValidationError` contenant `"50%"` (règle 5 : score < 50% limité à l'Institut).

### `test_institut_allowed_when_se_mark_below_50`
Même étudiant avec `se_mark=30` → inscription en Institut (G1 GC) → **aucune erreur** (exception : l'Institut est toujours accessible).

### `test_blocked_when_se_mark_missing`
Étudiant **sans aucun `StudentHsInfo`** → tentative d'inscription en Faculté (L1 Info) → `ValidationError` contenant `"lycée"` (règle 2 : informations lycée manquantes).
