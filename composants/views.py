from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Composant
from .serializers import ComposantSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Create your views here.

@extend_schema(tags=['Composants'])
class ComposantViewSet(viewsets.ModelViewSet):
    queryset = Composant.objects.all()
    serializer_class = ComposantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'marque']
    search_fields = ['modele', 'marque']
    ordering_fields = ['prix_eur']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        prix_min = self.request.query_params.get('prix_min')
        prix_max = self.request.query_params.get('prix_max')
        if prix_min is not None:
            queryset = queryset.filter(prix_eur__gte=float(prix_min))
        if prix_max is not None:
            queryset = queryset.filter(prix_eur__lte=float(prix_max))
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name='type', description='Type de composant (panneau, batterie, regulateur, onduleur)'),
            OpenApiParameter(name='marque', description='Filtrer par marque'),
            OpenApiParameter(name='prix_min', description='Prix minimum en EUR'),
            OpenApiParameter(name='prix_max', description='Prix maximum en EUR'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
