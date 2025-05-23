from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Dimensionnement
from .serializers import DimensionnementSerializer
from .services.ai_service import DimensionnementAIService
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Create your views here.

@extend_schema(tags=['Dimensionnement'])
class DimensionnementViewSet(viewsets.ModelViewSet):
    serializer_class = DimensionnementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Dimensionnement.objects.filter(user=self.request.user)
    
    @extend_schema(
        description='Calcule le dimensionnement d\'un système PV avec l\'IA',
        responses={201: DimensionnementSerializer}
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Sauvegarde initiale
        dimensionnement = serializer.save(user=request.user)
        
        # Calcul via IA
        ai_service = DimensionnementAIService()
        try:
            resultats = ai_service.calculer_dimensionnement(serializer.validated_data)
            
            # Mise à jour avec les résultats
            update_data = {
                'nombre_panneaux': resultats['nombre_panneaux'],
                'puissance_panneau_w': resultats['puissance_panneau_w'],
                'capacite_batterie_ah': resultats['capacite_batterie_ah'],
                'tension_systeme_v': resultats['tension_systeme_v'],
                'regulateur_data': resultats['regulateur'],
                'onduleur_data': resultats['onduleur'],
                'irradiation_moyenne_kwh_m2_j': resultats['irradiation_moyenne_kwh_m2_j']
            }
            
            for key, value in update_data.items():
                setattr(dimensionnement, key, value)
            dimensionnement.save()
            
            return Response(
                {
                    'dimensionnement': self.get_serializer(dimensionnement).data,
                    'explication': resultats['explication']
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            dimensionnement.delete()
            return Response(
                {'error': f'Erreur lors du calcul: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
