# Core Models Documentation

## University
- **name**: CharField, max_length=255, unique=True
- **acronym**: CharField, max_length=50, unique=True
- **country**: CharField, default="France"
- **city**: CharField
- **created_at**: DateTimeField, auto_now_add=True

## Program
- **university**: ForeignKey to University (on_delete=models.CASCADE)
- **name**: CharField, max_length=255
- **code**: CharField, max_length=50, unique=True
- **description**: TextField, blank=True
- **created_at**: DateTimeField, auto_now_add=True

## Department
- **program**: ForeignKey to Program (on_delete=models.CASCADE)
- **name**: CharField, max_length=255
- **dean**: CharField, blank=True
- **created_at**: DateTimeField, auto_now_add=True

## Class
- **department**: ForeignKey to Department (on_delete=models.CASCADE)
- **name**: CharField, max_length=100
- **academic_year**: ForeignKey to UniversityYear (on_delete=models.CASCADE)
- **created_at**: DateTimeField, auto_now_add=True

## Module
- **code**: CharField, max_length=50, unique=True
- **name**: CharField, max_length=255
- **credit_hours**: IntegerField
- **department**: ForeignKey to Department (on_delete=models.SET_NULL, null=True)
- **created_at**: DateTimeField, auto_now_add=True

## Course
- **module**: ForeignKey to Module (on_delete=models.CASCADE)
- **teacher**: ForeignKey to User (on_delete=models.SET_NULL, null=True)
- **schedule**: JSONField (e.g., {"CM": [{"time": "10h", "room": "A101"}]})
- **created_at**: DateTimeField, auto_now_add=True

### Relationships
```
University 1 --< Program  --< Department  --< Class  --< Module  --< Course
```
