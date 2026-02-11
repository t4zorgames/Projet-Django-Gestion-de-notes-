from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Departement(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class Filiere(models.Model):
    nom = models.CharField(max_length=100)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('nom', 'departement')

    def __str__(self):
        return f"{self.nom} ({self.departement.nom})"


class Niveau(models.Model):
    # e.g., L1, L2, L3
    nom = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.nom


class Etudiant(models.Model):
    nom = models.CharField(max_length=100)
    matricule = models.CharField(max_length=20, unique=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True, blank=True)
    niveau = models.ForeignKey(Niveau, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.matricule})"


from django.conf import settings


class UE(models.Model):
    SEMESTER_CHOICES = [(1, 'Semestre 1'), (2, 'Semestre 2')]
    
    code = models.CharField(max_length=10, unique=True)
    nom = models.CharField(max_length=100)
    credit = models.IntegerField()
    filiere = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True, blank=True)
    niveau = models.ForeignKey(Niveau, on_delete=models.SET_NULL, null=True, blank=True)
    semester = models.IntegerField(choices=SEMESTER_CHOICES, default=1)

    # instructors (teachers) — can be non-staff users
    instructors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='ues')

    # weights in percent (must sum to 100)
    cc_weight = models.PositiveIntegerField(default=20)
    tp_weight = models.PositiveIntegerField(default=30)
    sn_weight = models.PositiveIntegerField(default=50)

    def clean(self):
        total = self.cc_weight + self.tp_weight + self.sn_weight
        if total != 100:
            raise ValidationError('Les poids CC/TP/SN doivent totaliser 100%')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.nom}"


class Note(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    ue = models.ForeignKey(UE, on_delete=models.CASCADE)

    # component notes (scale 0-20). Null means missing (élève éliminé pour cette UE)
    cc = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(20)])
    tp = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(20)])
    sn = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(20)])

    class Meta:
        unique_together = ('etudiant', 'ue')

    def __str__(self):
        return f"{self.etudiant.nom} - {self.ue.code}"

    @property
    def is_eliminated(self):
        # eliminated if any component is missing
        return self.cc is None or self.tp is None or self.sn is None

    @property
    def final(self):
        # returns final score computed from component weights, or None if missing
        if self.is_eliminated:
            return None
        total = (
            (self.cc * self.ue.cc_weight / 100.0)
            + (self.tp * self.ue.tp_weight / 100.0)
            + (self.sn * self.ue.sn_weight / 100.0)
        )
        return round(total, 2)
