from django.db import models
from django.contrib.auth.models import User

class Professor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Module(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    semester = models.IntegerField()
    professors = models.ManyToManyField(Professor, related_name="modules")

    def __str__(self):
        return f"{self.name} ({self.code})"

class Rating(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="ratings")
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating 1-5

    class Meta:
        unique_together = ('professor', 'module', 'user')  # Prevent duplicate ratings

    def __str__(self):
        return f"{self.professor.name} - {self.module.name}: {self.rating}"