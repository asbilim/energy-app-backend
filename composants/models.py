from django.db import models

# Create your models here.

class Composant(models.Model):
    TYPES = [
        ('panneau', 'Panneau'),
        ('batterie', 'Batterie'),
        ('regulateur', 'Régulateur'),
        ('onduleur', 'Onduleur')
    ]
    
    type = models.CharField(max_length=20, choices=TYPES)
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    specifications = models.JSONField()
    prix_eur = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['type', 'marque', 'modele']
        verbose_name = 'Composant'
        verbose_name_plural = 'Composants'
        unique_together = ['type', 'marque', 'modele']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.marque} {self.modele}"
