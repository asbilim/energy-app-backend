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
        
        # Sauvegarde initiale est supprimée pour sauvegarder après le calcul IA
        # dimensionnement = serializer.save(user=request.user)
        
        # Calcul via IA
        ai_service = None # Initialiser à None
        dimensionnement = None # Initialiser à None
        try:
            ai_service = DimensionnementAIService()
            resultats = ai_service.calculer_dimensionnement(serializer.validated_data)
            
            # Création de l'objet Dimensionnement avec toutes les données
            dimensionnement_data = serializer.validated_data
            dimensionnement_data['user'] = request.user
            dimensionnement_data['nombre_panneaux'] = resultats['nombre_panneaux']
            dimensionnement_data['puissance_panneau_w'] = resultats['puissance_panneau_w']
            dimensionnement_data['capacite_batterie_ah'] = resultats['capacite_batterie_ah']
            dimensionnement_data['tension_systeme_v'] = resultats['tension_systeme_v']
            dimensionnement_data['regulateur_data'] = resultats['regulateur']
            dimensionnement_data['onduleur_data'] = resultats['onduleur']
            dimensionnement_data['irradiation_moyenne_kwh_m2_j'] = resultats['irradiation_moyenne_kwh_m2_j']
            dimensionnement_data['explication'] = resultats.get('explication') # Sauvegarde de l'explication
            
            dimensionnement = Dimensionnement.objects.create(**dimensionnement_data)
            
            return Response(
                {
                    'dimensionnement': self.get_serializer(dimensionnement).data,
                    'explication': resultats.get('explication')
                },
                status=status.HTTP_201_CREATED
            )
            
        except ValueError as ve: # Pour l'erreur d'initialisation de AI Service si OPENROUTER_API_KEY manque
            return Response(
                {'error': f'Erreur de configuration du service AI: {str(ve)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # Pas besoin de supprimer dimensionnement car il n'est créé qu'en cas de succès
            return Response(
                {'error': f'Erreur lors du calcul: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'La modification des dimensionnements existants n\'est pas autorisée. Veuillez créer un nouveau dimensionnement.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'La modification partielle des dimensionnements existants n\'est pas autorisée. Veuillez créer un nouveau dimensionnement.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
