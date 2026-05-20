Refactor Plan — Shorten inscription_app/models.py Safely (711 → ~280 lines)
Context

services/core_service/student_module/inscription_app/models.py has grown into a large multi-responsibility file (~711 lines).

The goal is to:

reduce model complexity
improve maintainability
isolate business rules
avoid circular imports
preserve the public API
keep Django ORM behavior intact

The refactor must remain fully Django-compatible:

serializers unchanged
admin unchanged
queryset usage unchanged
migrations safe
no breaking API changes
Current Breakdown
Section	Lines	Responsibility
Model declaration	14–75	Fields / Meta / __str__
Status transitions	76–206	activate, withdraw, complete, etc.
Property helpers	208–274	is_complete, can_change_class, eligibility helpers
Matricule logic	275–467	generation / transfer / parsing
Validation (clean)	469–653	business validation rules
Save automation	655–711	auto activation / audit / matricule
Refactor Strategy

The refactor will preserve the public interface:

inscription.clean()
inscription.save()
inscription.activate()

Only the implementation location changes.

The model becomes a thin orchestration layer.

⚠️ Critical Design Constraints
1. Avoid Circular Imports
Danger

This pattern is dangerous:

from .models import Inscription

inside validators/services.

During Django startup, models are imported early and can create partial import states.

Safe Solution

Use string annotations or TYPE_CHECKING.

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Inscription

Then:

def validate(inscription: "Inscription"):

No runtime import required.

2. Avoid Recursive save()
Danger

A service calling:

instance.save()

inside model save() logic creates recursive saves.

Safe Solution

Automation services must only:

mutate fields
prepare data
validate data

They must NEVER call:

save()
clean()

unless explicitly intended.

3. Avoid Creating Side Effects Before Real Save
Danger

Current matricule creation occurs before:

super().save()

If save fails afterward:

matricule exists
inscription does not

Data inconsistency possible.

Safe Solution

Split save automation into:

pre-save preparation
post-save side effects
Final Target Structure
inscription_app/
├── models.py
├── validators/
│   └── inscription_validator.py
├── services/
│   ├── inscription_automation.py
│   ├── matricule_service.py
│   └── transfer_service.py
├── mixins/
│   └── inscription_status.py
├── serializers.py
├── annual_registration_service.py
1. Validation Extraction
File
validators/inscription_validator.py
Responsibility

Move all clean() business rules into a dedicated validator.

BEFORE
def clean(self):
    # 185 lines
AFTER
def clean(self):
    InscriptionValidator.validate(self)
Validator Structure
class InscriptionValidator:
    """
    Centralized business validation rules.
    """

    @staticmethod
    def validate(inscription: "Inscription") -> None:
        # 0 Payment verification
        # 1 Faculty change protection
        # 2 Class change protection
        # 3 Duplicate inscription prevention
        # 4 Higher-level conflict prevention
        # 5 No level skip
        # 6 Registration eligibility
Benefits
keeps model readable
easier unit testing
isolated business rules
easier future extensions
2. Matricule Logic Extraction
File
services/matricule_service.py
⚠️ Important Correction

The matricule logic should NOT become a mixin with heavy ORM side effects.

Large mixins complicate:

MRO
debugging
super()
test isolation
Recommended Design

Use a stateless service class.

BEFORE
self.generate_matricule()
AFTER
MatriculeService.generate_for_inscription(self)
Extracted Responsibilities
Method	Destination
_get_available_matricule	service
_extract_matricule_number	service
generate_matricule	service
transfer_academic_year	service
_transfer_matricule_year_if_needed	service
get_matricule_for_type	service
get_or_create_default_group	service/helper
Example
class MatriculeService:

    @staticmethod
    def generate_for_inscription(inscription: "Inscription") -> str | None:
        ...
3. Save Automation Extraction
File
services/inscription_automation.py
⚠️ Important Correction

The automation layer must be split into two phases.

PRE-SAVE Phase

Mutates instance safely BEFORE database save.

class InscriptionAutomation:

    @staticmethod
    def prepare(inscription, user=None):
        # created_by
        # modified_by
        # modified_at
        # auto activation
        # class group assignment
POST-SAVE Phase

Handles side effects AFTER successful persistence.

class InscriptionAutomation:

    @staticmethod
    def after_save(inscription, created=False):
        # matricule generation
        # logs
        # future notifications
Updated Model Save
def save(self, *args, **kwargs):
    user = kwargs.pop("user", None)

    is_create = self._state.adding

    InscriptionAutomation.prepare(self, user)

    self.clean()

    super().save(*args, **kwargs)

    InscriptionAutomation.after_save(
        inscription=self,
        created=is_create,
    )
Why This Is Safer
Prevents orphan matricules

If database save fails:

no matricule created
no inconsistent state
Keeps responsibilities clean
Phase	Purpose
prepare	mutate model safely
save	persist
after_save	external side effects
4. Status Transition Methods
File
mixins/inscription_status.py
⚠️ Recommended Scope

Only move lightweight transition methods.

Good candidates:

activate()
complete()
withdraw()
drop()
suspend()
cancel()
replace()
Important Rule

Mixin methods may call:

self.save()

because they are public domain actions.

But helper services must NOT trigger recursive saves internally.

Example
class InscriptionStatusMixin:

    def complete(self):
        if self.regist_status == "Active":
            self.regist_status = "Completed"
            self.save()
Why Keep Them Lightweight

Status transitions are:

highly domain-oriented
naturally attached to the entity
expected by Django developers

This keeps the API elegant:

inscription.activate()

instead of:

InscriptionStatusService.activate(inscription)
5. Logging Cleanup
Danger

Current code uses:

print("DEBUG...")

inside models.

This pollutes production logs.

Safe Solution

Use Python logging.

import logging

logger = logging.getLogger(__name__)

Then:

logger.debug("Auto activated inscription %s", inscription.pk)
6. Testing Strategy

After each extraction step:

python manage.py check
python manage.py test inscription_app

Do NOT refactor everything at once.

Recommended Work Order
Step 1

Extract validation rules.

Lowest risk.

Step 2

Extract matricule utilities.

Test transactional behavior carefully.

Step 3

Refactor save automation into:

prepare()
after_save()
Step 4

Move lightweight status transitions.

Step 5

Remove dead comments and compress whitespace.

Final Expected Result
models.py

Should only contain:

fields
Meta
properties
thin delegations
public domain API
Example Final Shape
class Inscription(InscriptionStatusMixin, models.Model):

    # fields ...

    def clean(self):
        InscriptionValidator.validate(self)

    def save(self, *args, **kwargs):
        user = kwargs.pop("user", None)

        is_create = self._state.adding

        InscriptionAutomation.prepare(self, user)

        self.clean()

        super().save(*args, **kwargs)

        InscriptionAutomation.after_save(
            self,
            created=is_create,
        )
Expected Outcome
Before	After
711-line god model	~280-line readable model
mixed responsibilities	isolated domain services
risky save side effects	transactional safety
difficult testing	targeted unit tests
high cognitive load	modular architecture

The model remains the public entry point, but the heavy machinery moves into specialized components. Like turning a crowded warehouse into labeled workshop drawers 🧰