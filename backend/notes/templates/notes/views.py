from django.db import models

class Etudiant(models.Model):
    nom = models.CharField(max_length=100)
    matricule = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.nom} ({self.matricule})"


class UE(models.Model):
    code = models.CharField(max_length=10, unique=True)
    nom = models.CharField(max_length=100)
    credit = models.IntegerField()

    def __str__(self):
        return f"{self.code} - {self.nom}"


class Note(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    ue = models.ForeignKey(UE, on_delete=models.CASCADE)
    valeur = models.FloatField()

    class Meta:
        unique_together = ('etudiant', 'ue')

    def __str__(self):
        return f"{self.etudiant.nom} - {self.ue.code} : {self.valeur}"
