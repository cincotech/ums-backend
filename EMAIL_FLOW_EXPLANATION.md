# Comment le système trouve l'email d'un étudiant

## Structure des relations :

1. **PaymentReminder** (Rappel de paiement)
   ↓ (ForeignKey)
2. **Student** (Étudiant)
   ↓ (OneToOneField)
3. **User** (Utilisateur)
   ↓ (EmailField)
4. **email** (Adresse email)

## Dans le code :

```python
# Dans services.py ligne 32
recipient_list=[student.user.email]

# Où :
# - student = reminder.student (modèle Student)
# - student.user = relation OneToOneField vers User
# - student.user.email = champ EmailField du modèle User
```

## Exemple concret :

```python
# Si on a un rappel pour l'étudiant Jean Dupont
reminder = PaymentReminder.objects.get(id="some-uuid")

# Le système fait :
student = reminder.student  # Récupère l'étudiant (Jean Dupont)
user = student.user        # Récupère l'utilisateur lié (User de Jean)
email = user.email         # Récupère l'email (jean.dupont@email.com)

# Donc : student.user.email = "jean.dupont@email.com"
```

## Vérification que l'email existe :

```python
if student.user.email:
    # Envoyer l'email
    send_mail(...)
else:
    # Log erreur : étudiant sans email
    logger.error(f"Étudiant {student.matricule} n'a pas d'email")
```
