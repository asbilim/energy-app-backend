from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponse
from .models import Dimensionnement
from .serializers import DimensionnementSerializer
from .services.ai_service import DimensionnementAIService
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.template.loader import render_to_string
from django.contrib import messages
import json

# Create your views here.

@extend_schema(tags=['Dimensionnement'])
class DimensionnementViewSet(viewsets.ModelViewSet):
    serializer_class = DimensionnementSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    
    def get_queryset(self):
        return Dimensionnement.objects.filter(user=self.request.user)
    
    @extend_schema(
        description='Calcule le dimensionnement d\'un système PV avec l\'IA',
        responses={201: DimensionnementSerializer}
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ai_service = None
        dimensionnement = None
        try:
            ai_service = DimensionnementAIService()
            resultats = ai_service.calculer_dimensionnement(serializer.validated_data)
            
            dimensionnement_data = serializer.validated_data
            dimensionnement_data['user'] = request.user
            dimensionnement_data['nombre_panneaux'] = resultats['nombre_panneaux']
            dimensionnement_data['puissance_panneau_w'] = resultats['puissance_panneau_w']
            dimensionnement_data['capacite_batterie_ah'] = resultats['capacite_batterie_ah']
            dimensionnement_data['tension_systeme_v'] = resultats['tension_systeme_v']
            dimensionnement_data['regulateur_data'] = resultats['regulateur']
            dimensionnement_data['onduleur_data'] = resultats['onduleur']
            dimensionnement_data['irradiation_moyenne_kwh_m2_j'] = resultats['irradiation_moyenne_kwh_m2_j']
            dimensionnement_data['explication'] = resultats.get('explication')
            
            dimensionnement = Dimensionnement.objects.create(**dimensionnement_data)

            if request.headers.get('HX-Request'):
                simulations = self.get_queryset()
                html = render_to_string('simulations_list.html', {'simulations': simulations}, request=request)
                response = HttpResponse(html, content_type='text/html')
                messages.success(request, "Dimensionnement calculé et sauvegardé avec succès.")
                toast_message = {
                    "message": "Nouveau dimensionnement calculé ! Retrouvez-le dans l'onglet 'Mes Simulations'.",
                    "type": "success"
                }
                response['HX-Trigger-After-Swap'] = json.dumps({"showToast": toast_message})
                return response
            
            return Response(
                {
                    'dimensionnement': self.get_serializer(dimensionnement).data,
                    'explication': resultats.get('explication')
                },
                status=status.HTTP_201_CREATED
            )
            
        except ValueError as ve:
            if request.headers.get('HX-Request'):
                error_html = f"<div class='text-red-700 p-4 bg-red-100 border border-red-400 rounded-md shadow-sm'>Erreur de configuration du service AI: {str(ve)}. Veuillez contacter l'administrateur.</div>"
                return HttpResponse(error_html, content_type='text/html', status=500)
            return Response(
                {'error': f'Erreur de configuration du service AI: {str(ve)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            if request.headers.get('HX-Request'):
                error_html = f"<div class='text-red-700 p-4 bg-red-100 border border-red-400 rounded-md shadow-sm'>Erreur lors du calcul du dimensionnement: {str(e)}. Le service IA a peut-être retourné une réponse inattendue. Veuillez vérifier vos paramètres et réessayer. Si le problème persiste, le service IA est peut-être temporairement surchargé ou indisponible.</div>"
                return HttpResponse(error_html, content_type='text/html', status=500)
            
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
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # For HTMX requests, return HTML
        if request.headers.get('HX-Request'):
            html = render_to_string('simulations_list.html', {'simulations': queryset}, request=request)
            return HttpResponse(html, content_type='text/html')
            
        # For API requests, use standard DRF pagination and serialization
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # For HTMX requests, return HTML
        if request.headers.get('HX-Request'):
            html = render_to_string('simulation_detail.html', {'dimensionnement': instance}, request=request)
            return HttpResponse(html, content_type='text/html')
            
        # For API requests, use standard serialization
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
