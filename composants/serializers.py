from rest_framework import serializers
from .models import Composant

class ComposantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composant
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_specifications(self, value):
        """
        Valide que les spécifications contiennent les champs requis selon le type
        """
        type_composant = self.initial_data.get('type')
        
        required_specs = {
            'panneau': ['puissance_w', 'tension_mpp_v', 'courant_mpp_a', 'technologie'],
            'batterie': ['capacite_ah', 'tension_v', 'technologie', 'cycles_vie'],
            'regulateur': ['type', 'tension_entree_max_v', 'courant_max_a', 'rendement_pct'],
            'onduleur': ['puissance_nominale_w', 'tension_entree_v', 'rendement_pct', 'type_onde']
        }
        
        if type_composant not in required_specs:
            raise serializers.ValidationError("Type de composant invalide")
            
        for field in required_specs[type_composant]:
            if field not in value:
                raise serializers.ValidationError(f"Spécification manquante: {field}")
            
            # Validation des valeurs numériques
            if field.endswith(('_w', '_v', '_a', '_ah', '_pct')):
                try:
                    val = float(value[field])
                    if val <= 0:
                        raise ValueError
                except (TypeError, ValueError):
                    raise serializers.ValidationError(f"Valeur invalide pour {field}")
                    
        return value 