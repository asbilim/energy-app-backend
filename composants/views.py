from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from .models import Composant
from .serializers import ComposantSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Create your views here.

class ComposantFilter(filters.FilterSet):
    marque = filters.CharFilter(lookup_expr='icontains')
    prix_min = filters.NumberFilter(field_name='prix_eur', lookup_expr='gte')
    prix_max = filters.NumberFilter(field_name='prix_eur', lookup_expr='lte')
    
    class Meta:
        model = Composant
        fields = ['type', 'marque']

@extend_schema(tags=['Composants'])
class ComposantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Composant.objects.all()
    serializer_class = ComposantSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ComposantFilter
    
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
