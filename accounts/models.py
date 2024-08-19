from django.db import models

class Term(models.Model):
    # Your fields here
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


# Create your models here.
