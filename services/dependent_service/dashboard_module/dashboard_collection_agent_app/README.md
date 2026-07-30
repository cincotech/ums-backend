# Dashboard Collection Agent App — Module Finance & Recouvrement

> Application Django faisant partie du système **UMS (University Management System)**, chargée de la gestion financière des étudiants : frais académiques, plans de paiement, paiements, bordereaux bancaires, relances de recouvrement et tableau de bord financier.

Emplacement : `services/dependent_service/dashboard_module/dashboard_collection_agent_app`

---

## 1. Résumé exécutif

Ce module gère tout le cycle de vie financier d'un étudiant :

1. Définition des frais (`FeesSheet`) par classe, département ou faculté.
2. Construction de plans de paiement (`PaymentPlan`) et d'échéanciers (`PaymentInstallement`).
3. Enregistrement des paiements (`Payment`) par dépôt bancaire, virement, chèque ou mobile money, avec vérification obligatoire par le service financier.
4. Rapprochement bancaire par bordereau (`Bordereau` / `BordereauLine`) — un bordereau peut couvrir plusieurs étudiants/frais et être fractionné (`split`).
5. Relances automatiques (`PaymentReminder`) par Celery Beat, avec escalade (J+7 → J+30 → mise en demeure J+60 → dernier avis).
6. Tableau de bord KPI (`FinanceDashboardAPIView`) : montants attendus/collectés, taux de recouvrement, tendances, répartition par faculté/méthode de paiement, et un aperçu du patrimoine (bâtiments, salles, équipements) emprunté au module infrastructure.

Le code est fonctionnellement riche et couvre des cas métier complexes (redistribution automatique des surplus entre plans, priorité des plans antérieurs, promesses de paiement). C'est aussi un module qui porte les traces d'un développement rapide et itératif : logique métier dense dans les `save()` de modèles, absence de tests actifs, et une intégration asynchrone encore rudimentaire pour les ambitions de l'université (1M+ étudiants, enseignants, personnel).

---

## 2. Où se situe cette app dans l'architecture UMS

Le projet n'est **pas une architecture microservices** malgré le nom des dossiers (`core_service`, `dependent_service`, `foundational_service`). C'est un **monolithe modulaire Django** : chaque « service » est un ensemble d'apps Django dans le même processus, la même base de données, avec des `ForeignKey` directes entre modules (ex. `Payment.inscription` pointe vers `student_module.inscription_app`, `FeesSheet.class_fk` vers `academic_module.class_app`).

```
services/
├── foundational_service/   → auth, utilisateurs, rôles, géo (fondation, dépendance de tout)
├── core_service/           → académique, étudiants (domaine métier central)
└── dependent_service/      → dashboards, documents, examens, infrastructure, notifications
    └── dashboard_module/
        └── dashboard_collection_agent_app/   ← ce module (finance/recouvrement)
```

Conséquence directe pour la suite de ce document : les « intégrations » dont il est question plus bas ne sont pas des appels réseau inter-services, mais (a) des tâches asynchrones internes (Celery) et (b) des intégrations externes (email, futur SMS/mobile money/passerelles bancaires). C'est là que se joue la question de « ne pas bloquer les autres intégrations en priorisant les actions étudiants/enseignants ».

### Dépendances directes de ce module
- `services.core_service.academic_module` (Class, Department, Faculty, AcademicYear)
- `services.core_service.student_module` (Student, Inscription)
- `services.foundational_service.auth_module` (User, Role)
- `services.dependent_service.infrastructure_module` (Building, Room, Equipment) — uniquement pour la partie "assets" du dashboard
- `core.permissions`, `core.views.BaseViewSet`, `core.response_handler`, `core.pagination`

---

## 3. Modèle de données (`models.py`)

| Modèle | Rôle | Points d'attention |
|---|---|---|
| `Bank` | Référentiel des banques partenaires | Simple, correct |
| `Wording` | Libellé de frais ("Frais d'inscription", etc.) | OK |
| `FeesSheet` | Grille de frais, rattachée à **exactement un** niveau (classe **ou** département **ou** faculté) | Règle métier bien validée (`clean()` + validation serializer) |
| `PaymentPlan` | Plan de paiement (tranche) lié à une `FeesSheet` | `get_plans_for_student` fait une recherche hiérarchique classe→département→faculté |
| `PaymentInstallement` | Échéance de paiement d'un étudiant sur un plan | Logique de recalcul automatique du statut et des surplus **dans `save()`** |
| `Payment` | Paiement individuel, vérifié par le service financier | Contient la logique métier la plus dense du module (voir §6) |
| `PaymentReminder` | Historique des relances envoyées | Généré par la tâche Celery `send_payment_reminders` |
| `PaymentPromise` | Promesse de paiement (engagement oral/écrit d'un étudiant) | Simple |
| `Bordereau` / `BordereauLine` | Bordereau de versement bancaire, pouvant financer plusieurs lignes de frais et être fractionné (`split`) | Ajouté récemment (migrations 0007/0008), bonne modélisation du fractionnement |
| `CollectionCorrespondence` | Trace des communications de recouvrement (email/SMS/courrier/téléphone/rencontre) | Seul le canal email est réellement implémenté |

Toutes les clés primaires sont des `UUIDField`. C'est un bon choix pour éviter les collisions et faciliter une éventuelle sharding/réplication future, mais voir la remarque de performance au §7 (index MySQL sur UUID aléatoires).

---

## 4. Flux métier clé : cycle de vie d'un paiement

```
Création Payment (unverified)
        │
        ▼
Vérification par finance_service ──► Payment.verify() / PaymentService.verify_payment()
        │
        ▼
Payment.save() détecte le changement de statut
        │
        ├─► Recalcule PaymentInstallement.paid_amount
        ├─► Si paid_amount > montant dû → surplus détecté
        │        └─► PaymentService._handle_surplus()
        │              ├─ cherche un plan précédent non soldé (priorité)
        │              ├─ sinon un plan suivant non soldé
        │              └─ sinon crédite le dernier plan connu
        └─► Si rejet (verified → unverified/rejected)
                 └─► Supprime les paiements auto-générés (surplus/redistribution)
                      et recalcule TOUS les installments de l'étudiant
```

C'est une mécanique de redistribution hiérarchique assez sophistiquée et bien pensée fonctionnellement (`services/paymentService.py`). Le problème n'est pas la logique elle-même mais **où** elle vit — voir §6.

---

## 5. API exposée (`urls.py`)

| Endpoint | ViewSet | Notes |
|---|---|---|
| `/overview/` | `FinanceDashboardAPIView` | KPI finance + patrimoine |
| `/banks/` | `BankViewSet` | |
| `/wordings/` | `WordingViewSet` | |
| `/fees-sheets/` | `FeesSheetViewSet` | + `grouped-options` |
| `/payment-installements/` | `PaymentInstallementViewSet` | + `available_filters`, `unpaid_installments`, `incomplete_payments_by_class`, `overdue_payments` |
| `/payment-reminders/` | `PaymentReminderViewSet` | |
| `/payment-plans/` | `PaymentPlanViewSet` | |
| `/payment-promises/` | `PaymentPromiseViewSet` | |
| `/payments/` | `PaymentViewSet` | + `by-inscription/<id>/` |
| `/collection-correspondence/` | `CollectionCorrespondenceViewSet` | |
| `/bordereaux/` | `BordereauViewSet` | + `verify`, `split` |
| `/bordereau-lines/` | `BordereauLineViewSet` | création déclenche automatiquement un `Payment` |

Toutes les routes DRF standards passent par `router = DefaultRouter()`, ce qui les rend prévisibles et bien documentées via `drf-spectacular`.

---

## 6. Points forts (ce qui est bon aujourd'hui)

1. **Modélisation métier fidèle à la réalité universitaire** : hiérarchie classe/département/faculté, plans de paiement multiples, surplus redistribués intelligemment plutôt que perdus ou bloqués — c'est un vrai atout différenciant.
2. **Permissions par rôle cohérentes** : `IsFinanceService`, `IsStudentOrFinance`, `IsFinanceOrDirection` (`core/permissions.py`) sont appliquées systématiquement et les querysets sont filtrés par rôle (`get_queryset()` dans chaque ViewSet), pas seulement par permission — bonne défense en profondeur.
3. **`BaseViewSet` centralisé** (`core/views.py`) : réponses API standardisées (`success_response`/`error_response`), pagination activée par défaut (`StandardResultsSetPagination`, 10/page, max 100).
4. **Bordereau/split bien pensé** : le fractionnement d'un bordereau en plusieurs lignes avec génération automatique du `Payment` et du code de transaction (`views.py:1097-1131`) est une fonctionnalité comptable avancée correctement implémentée avec `transaction.atomic()`.
5. **Escalade de relance progressive** (J+7, J+30, mise en demeure J+60, dernier avis) avec anti-doublon (`sent_at__date=today`) — logique de recouvrement réaliste.
6. **Requêtes optimisées à plusieurs endroits** : `select_related`/`prefetch_related` présents sur la plupart des querysets de listing (`PaymentViewSet`, `PaymentPlanViewSet`, `BordereauViewSet`), `.distinct().order_by(...)` pour éviter les `UnorderedObjectListWarning`.
7. **Admin Django riche** : import/export (`django-import-export`), actions en masse (activer/désactiver banques, renvoyer relances, recalculer statuts), bon pour l'opérationnel back-office.
8. **`FinanceDashboardService` bien structuré** : agrégations SQL (pas de boucle Python sur de gros volumes), fallback propre sur l'année académique active, gestion des périodes daily/weekly/monthly.

---

## 7. Ce qui doit changer avant une mise en production à l'échelle (1M+ étudiants, enseignants, personnel)

### 7.1 Scalabilité et performance — critique

- **`PaymentInstallementViewSet.list()` n'est PAS paginé** (`views.py:374-382`) : il appelle `_format_installments_data()` sur **tout** le queryset filtré et fait une boucle Python avec accès `.get_active_matricule()` par étudiant (requête supplémentaire par ligne). Sur une base de 1M étudiants, un appel sans filtre serait catastrophique (timeout, OOM). **À corriger en priorité** : réutiliser `super().list()` avec pagination, ou paginer manuellement avant `_format_installments_data`.
- **N+1 déguisés** dans `_format_installments_data` (`views.py:389-479`) et `FinanceDashboardService.get_overview` (`recent_payments`, `finance_dashboard_service.py:369-389`) : chaque étudiant déclenche un accès `get_active_matricule()` non préchargé. À grande échelle, précharger via `prefetch_related` avec `Prefetch` ciblé, ou dénormaliser le matricule actif.
- **UUID comme clé primaire sur MySQL** : très bon pour l'unicité distribuée, mais un `UUIDField` aléatoire (v4) en `PRIMARY KEY` sur InnoDB fragmente l'index cluster et dégrade les écritures/lectures à mesure que la table grossit (des tables `payments`, `payment_installments` à plusieurs dizaines de millions de lignes en souffriront). À évaluer : UUID v7 (ordonnable dans le temps) ou clé technique `BigAutoField` + UUID en champ secondaire indexé pour l'API publique.
- **Pas de cache applicatif** : aucune configuration `CACHES` dans `ums/settings/base.py` ou `production.py`. Le dashboard (`overview/`) recalcule des agrégations lourdes à chaque appel. Pour 1M+ utilisateurs consultant régulièrement leur solde, un cache Redis avec invalidation ciblée (par étudiant/plan) réduirait fortement la charge DB.
- **Pas de `CONN_MAX_AGE`** ni de pool de connexions configuré pour MySQL (`ums/settings/production.py`) : à ce volume, des connexions persistantes ou un pooler (PgBouncer-like / ProxySQL pour MySQL) deviennent nécessaires.

### 7.2 Fiabilité transactionnelle et cohérence des données

- **Logique métier critique dans `Model.save()`** (`models.py`, `Payment.save()` lignes 460-688 et `PaymentInstallement.save()` lignes 287-371) : mélange validation, effets de bord (recalcul, création de paiements automatiques) et accès à `PaymentService` directement dans la couche modèle. Conséquences concrètes :
  - Une `ValueError` levée dans `save()` (ex. "Seul le service financier peut modifier le statut") remonte comme une **erreur 500**, pas une 400/403 propre côté API — mauvaise expérience pour le frontend et bruit inutile dans les logs d'erreur serveur.
  - Le bloc de recalcul après `super().save()` (branches "changement de statut", "rejet", "changement de montant", "changement de plan") **n'est pas englobé dans une seule transaction atomique au niveau `Payment.save()`** — seules certaines sous-méthodes de `PaymentService` ouvrent leur propre `transaction.atomic()`. En cas d'erreur à mi-parcours (ex. panne DB pendant la boucle de recalcul des installments après un rejet), l'état peut rester incohérent (paiement rejeté mais installments partiellement recalculés).
  - Recommandation : extraire cette logique dans des services explicites (déjà commencé avec `PaymentService`) appelés depuis les vues/serializers, garder les modèles « fins », et englober chaque opération métier complète dans un unique `transaction.atomic()` avec des exceptions DRF (`ValidationError`, `PermissionDenied`) plutôt que des `ValueError` génériques.
- **`tasks.py:68` — `sent_by_id=1` codé en dur** pour représenter un "utilisateur système". Fragile : si cet enregistrement est supprimé/modifié, la tâche plante silencieusement. À remplacer par un compte système dédié référencé par variable d'environnement/constante nommée, ou par un champ `sent_by = null=True` avec un flag `is_automated=True`.
- **`HistoricalRecords` commenté** sur `Payment` (`models.py:421`, `# history = HistoricalRecords()`) alors que `django-simple-history` est une dépendance du projet. Pour un système financier universitaire, l'absence de piste d'audit complète (qui a modifié quoi, quand) est un risque de conformité et de litige (contestations d'étudiants, audits internes).
- **Incohérence de devise** : les messages de relance affichent `€` (`tasks.py:56-59`) alors que les bordereaux mentionnent `BIF` (`models.py:840` — franc burundais). Cela suggère soit un copier-coller depuis un template générique, soit une confusion réelle sur la devise affichée aux étudiants. À corriger avant mise en production : utiliser un paramètre de devise centralisé (settings ou configuration université).

### 7.3 Sécurité

- **Aucun throttling/rate-limiting** configuré (`REST_FRAMEWORK` dans `ums/settings/base.py` ne définit pas `DEFAULT_THROTTLE_CLASSES`). Sur les endpoints financiers (`payments/`, `bordereaux/`) exposés à 1M+ comptes étudiants, l'absence de limitation de débit expose à des abus (scan d'IDs, création massive de paiements factices en `unverified`, DoS applicatif).
- **`PaymentViewSet.create` accessible à tout utilisateur authentifié** (`views.py:759-762`) — cohérent avec le métier (l'étudiant déclare son paiement, la finance vérifie), mais sans validation de montant plancher/plafond ni limitation de fréquence, ce qui peut être utilisé pour polluer la table avec des faux paiements en masse.
- **Upload de fichiers** (`remittance_slip_uri`, `slip_uri` en `ImageField`) sans limite de taille ni de type MIME explicite visible dans ce module — à vérifier au niveau des settings globaux (`FILE_UPLOAD_MAX_MEMORY_SIZE`, validation d'extension) pour éviter l'upload de fichiers malveillants déguisés en image.

### 7.4 Tests — actuellement quasi inexistants

- `tests.py` (56 lignes) est **entièrement commenté**, donc n'exécute rien.
- `test_permissions.py` (permissions) et `test_finance_overview.py` (dashboard) sont corrects mais couvrent une surface minime.
- `test_reminders.py` teste l'envoi d'email mais utilise `print()` pour "vérifier" certaines assertions manuellement plutôt que des `assertEqual` — ce n'est pas un vrai test automatisé sur cette partie.
- **Aucun test** sur : la redistribution de surplus (`PaymentService._handle_surplus`, la logique la plus complexe et la plus risquée du module), le fractionnement de bordereau (`split`), les tâches Celery (`send_payment_reminders`, `update_overdue_installments`), ou les cas d'erreur des ViewSets (permissions refusées, données invalides).
- Pour un module qui déplace de l'argent réel à l'échelle d'une université, c'est le manque le plus urgent à combler — en particulier des tests de non-régression sur `_handle_surplus` avant tout refactoring.

### 7.5 Observabilité

- Les logs utilisent des emojis et `logger.info` en abondance dans la logique métier (`services/paymentService.py`) — utile en développement, bruyant et non structuré en production. Pas de corrélation d'ID de requête, pas de métriques (temps de traitement d'un paiement, taux d'échec des relances, etc.). À industrialiser avec des logs structurés (JSON) et des métriques exportées (Prometheus/OpenTelemetry) si l'objectif est un vrai monitoring à grande échelle.

---

## 8. Le sujet central : Celery et la priorisation des intégrations (étudiants/enseignants) sans blocage mutuel

### 8.1 État actuel — une seule file, sans priorité

```python
# ums/celery.py
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ums/settings/base.py
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_TASK_TIME_LIMIT = 30 * 60
# Pas de CELERY_TASK_ROUTES, pas de queues nommées, pas de priorités
```

Concrètement : **toutes les tâches Celery du projet entier (pas seulement ce module) partagent aujourd'hui la même file par défaut** (`celery`). `send_payment_reminders` et `update_overdue_installments` (`celery_config.py`) tournent dans le même pool de workers que n'importe quelle autre tâche asynchrone future (envoi de bulletins, export massif, notifications d'examens, etc.).

**C'est exactement le problème que vous décrivez** : si demain une intégration lourde (ex. un export de masse, une synchronisation avec une passerelle mobile money, un envoi de SMS en volume) sature la file, elle retarde aussi les relances de paiement et, plus grave, toute future tâche qui touche directement les étudiants/enseignants (notifications d'examens, blocage/déblocage d'accès, etc.) — car il n'existe aucune notion de priorité ou d'isolation.

### 8.2 Recommandation : files nommées + priorité + isolation des workers

L'idée n'est pas de créer plusieurs "microservices" (le monolithe modulaire reste pertinent ici), mais de **router les tâches Celery vers des files distinctes selon leur criticité**, et de dédier des workers à chaque file pour qu'une file lente ne prive jamais les autres de ressources.

```python
# ums/settings/base.py — proposition
CELERY_TASK_ROUTES = {
    # Haute priorité : impact direct et immédiat étudiants/enseignants
    "*.tasks.send_payment_reminders": {"queue": "critical_students"},
    "*.tasks.update_overdue_installments": {"queue": "critical_students"},
    "*dashboard_teacher_app.tasks.*": {"queue": "critical_students"},
    "*exam_module.*.tasks.*": {"queue": "critical_students"},

    # Priorité normale : opérations financières non bloquantes pour l'accès étudiant
    "*dashboard_collection_agent_app.tasks.export_*": {"queue": "finance_batch"},

    # Basse priorité : intégrations externes lourdes/lentes (exports massifs, sync tierces)
    "*.tasks.bulk_*": {"queue": "bulk_low_priority"},
}

CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_ACKS_LATE = True          # évite la perte de tâche si un worker crashe
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # évite qu'un worker "critical" ne pré-charge trop de tâches lourdes
```

Déploiement des workers (isolation physique/CPU, pas seulement logique) :

```bash
# Worker dédié aux actions étudiants/enseignants — jamais saturé par le reste
celery -A ums worker -Q critical_students -c 8 --hostname=critical@%h

# Worker pour la finance en masse, isolé
celery -A ums worker -Q finance_batch -c 4 --hostname=finance@%h

# Worker "best effort" pour les intégrations externes lentes/instables
celery -A ums worker -Q bulk_low_priority -c 2 --hostname=bulk@%h
```

Ainsi, un pic sur `bulk_low_priority` (ex. une passerelle SMS externe qui répond lentement) ne peut jamais consommer les workers de `critical_students`, car ce sont des processus séparés écoutant des files séparées — c'est l'isolation la plus fiable, plus robuste qu'un simple champ `priority` Celery/Redis (qui ne garantit pas grand-chose avec Redis comme broker).

### 8.3 Compléments nécessaires pour des intégrations robustes

- **Retry avec backoff + dead-letter queue** : ajouter `autoretry_for`, `retry_backoff=True`, `max_retries` sur les tâches d'intégration externe (aujourd'hui `send_payment_reminders`/`_create_and_send_reminder` ne fait qu'un `try/except` qui marque `status="failed"` sans jamais réessayer — `tasks.py:73-77`).
- **Idempotence** : les tâches critiques (relances, redistribution de surplus) doivent pouvoir être rejouées sans dupliquer d'effet — actuellement partiellement assuré par la vérification `existing_reminder` mais pas au niveau des tâches Celery elles-mêmes (pas de clé d'idempotence sur retry réseau).
- **Circuit breaker sur les intégrations externes** : si un fournisseur SMS/mobile money tombe, éviter que chaque tâche retente indéfiniment et bloque le worker qui lui est dédié — prévoir un court-circuit temporaire (ex. `pybreaker` ou implémentation maison avec cache Redis d'un flag "provider_down").
- **Séparation claire "notification élève/enseignant" vs "traitement financier lourd"** : actuellement `NotificationService` ne gère que l'email (`services/paymentService.py` co-existe avec `services.py` racine — nommage à clarifier, voir §9) ; le jour où SMS/push sont ajoutés, ils doivent partir sur leur propre file avec leur propre limite de débit (rate limit par fournisseur), sans jamais partager la file `critical_students` si leur fournisseur externe est instable — sinon on réintroduit le couplage qu'on cherche à éviter.

---

## 9. Dette technique mineure / cohérence du code

- **Duplication de nommage** : il existe à la fois `services.py` (racine du module, contient `NotificationService`) et `services/paymentService.py` (contient `PaymentService`), plus `services/logging_config_example.py` et `services/__init__.py`. Cette coexistence d'un fichier `services.py` et d'un package `services/` fonctionne en Python mais prête à confusion pour tout nouvel arrivant — à unifier dans un seul package `services/` avec des modules clairement nommés (`notification_service.py`, `payment_service.py`).
- **`services/logging_config_example.py`** semble être un fichier d'exemple/scratch oublié dans le code de production — à supprimer ou déplacer dans `docs/`.
- **Champ `Payment.remittance_slip_uri`** en `ImageField` alors qu'un bordereau bancaire est souvent un PDF/scan — restreindre à des images empêche l'upload de justificatifs scannés en PDF, ce qui est courant dans un contexte de paiement universitaire (dépôt/virement bancaire).
- **`FeesSheetViewSet.update`/`partial_update`** dupliquent presque intégralement le comportement par défaut de `BaseViewSet` — à supprimer si le comportement standard suffit (moins de code à maintenir), ou à documenter s'il y a une raison spécifique de les avoir réécrits.

---

## 10. Feuille de route suggérée (par ordre d'impact)

| Priorité | Action | Pourquoi |
|---|---|---|
| 🔴 Urgent | Paginer `PaymentInstallementViewSet.list()` | Évite un crash/OOM en production à grande échelle |
| 🔴 Urgent | Réactiver et étoffer les tests, en particulier sur `_handle_surplus` et `Bordereau.split` | Zéro filet de sécurité sur la logique financière la plus critique |
| 🔴 Urgent | Corriger l'incohérence de devise (`€` vs `BIF`) | Confusion directe pour les étudiants recevant une relance |
| 🟠 Important | Introduire les files Celery nommées + workers dédiés (§8.2) | Répond directement au besoin de non-blocage exprimé |
| 🟠 Important | Sortir la logique métier de `Payment.save()`/`PaymentInstallement.save()` vers des services, avec transactions atomiques complètes et exceptions DRF propres | Fiabilité transactionnelle et erreurs HTTP correctes |
| 🟠 Important | Réactiver `HistoricalRecords` sur `Payment` (et étendre à `PaymentInstallement`, `Bordereau`) | Auditabilité indispensable pour un système financier |
| 🟡 Moyen | Ajouter un cache Redis pour le dashboard (`overview/`) avec invalidation ciblée | Réduction de charge DB à grande échelle |
| 🟡 Moyen | Ajouter throttling DRF sur les endpoints financiers sensibles | Anti-abus |
| 🟢 Confort | Nettoyer la duplication `services.py` / `services/` et supprimer les fichiers d'exemple | Lisibilité pour l'équipe |
| 🟢 Confort | Étudier UUID v7 ou clé technique séquentielle pour les tables à très fort volume | Performance d'index à long terme |

---

## 11. Résumé en une phrase

Le module couvre bien le **quoi** (règles métier financières universitaires, redistribution des paiements, recouvrement) mais pas encore assez le **comment à grande échelle** : pagination manquante sur un endpoint sensible, logique métier trop couplée aux modèles, tests désactivés, et une architecture Celery à file unique qui ne priorise aujourd'hui aucune action — exactement le point que ce document propose de corriger en premier via des files Celery dédiées et isolées pour les actions touchant étudiants et enseignants.
