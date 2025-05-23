from django.db import models
from django.conf import settings

class Dimensionnement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    consommation_journaliere_wh = models.IntegerField()
    profil_charge = models.JSONField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    marge_securite_pct = models.IntegerField(default=20)
    rendement_systeme_pct = models.IntegerField(default=85)
    
    # Résultats calculés par l'IA
    nombre_panneaux = models.IntegerField(null=True)
    puissance_panneau_w = models.IntegerField(null=True)
    capacite_batterie_ah = models.IntegerField(null=True)
    tension_systeme_v = models.IntegerField(null=True)
    regulateur_data = models.JSONField(null=True)
    onduleur_data = models.JSONField(null=True)
    irradiation_moyenne_kwh_m2_j = models.FloatField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Dimensionnement'
        verbose_name_plural = 'Dimensionnements'
    
    def __str__(self):
        return f"Dimensionnement {self.id} - {self.user.email}"
