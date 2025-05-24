from django.contrib import admin
from .models import Composant

@admin.register(Composant)
class ComposantAdmin(admin.ModelAdmin):
    list_display = ('type', 'marque', 'modele', 'prix_eur', 'updated_at')
    list_filter = ('type', 'marque')
    search_fields = ('marque', 'modele', 'specifications')
    ordering = ('type', 'marque', 'modele')
