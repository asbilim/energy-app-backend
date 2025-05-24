from rest_framework import serializers
from .models import Dimensionnement

class DimensionnementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dimensionnement
        fields = '__all__'
        read_only_fields = (
            'user', 'nombre_panneaux', 'puissance_panneau_w',
            'capacite_batterie_ah', 'tension_systeme_v',
            'regulateur_data', 'onduleur_data', 'irradiation_moyenne_kwh_m2_j',
            'explication', 'created_at', 'updated_at'
        )
    
    def validate_profil_charge(self, value):
        """
        Valide que le profil de charge est un dictionnaire avec les heures et puissances
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Le profil de charge doit être un dictionnaire")
        
        for hour, power in value.items():
            try:
                hour = int(hour)
                if not (0 <= hour <= 23):
                    raise serializers.ValidationError(f"Heure invalide: {hour}")
            except ValueError:
                raise serializers.ValidationError(f"Format d'heure invalide: {hour}")
            
            if not isinstance(power, (int, float)) or power < 0:
                raise serializers.ValidationError(f"Puissance invalide pour l'heure {hour}: {power}")
        
        return value
    
    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("La latitude doit être entre -90 et 90 degrés")
        return value
    
    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("La longitude doit être entre -180 et 180 degrés")
        return value
    
    def validate_marge_securite_pct(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError("La marge de sécurité doit être entre 0 et 100%")
        return value
    
    def validate_rendement_systeme_pct(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError("Le rendement système doit être entre 0 et 100%")
        return value 