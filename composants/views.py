from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from .models import Composant
from .serializers import ComposantSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.exceptions import ValidationError
from energy.permissions import IsAdminOrReadOnly
from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.decorators import action
from django.contrib.auth.decorators import login_required

# Create your views here.

@extend_schema(tags=['Composants'])
class ComposantViewSet(viewsets.ModelViewSet):
    queryset = Composant.objects.all()
    serializer_class = ComposantSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'marque']
    search_fields = ['modele', 'marque']
    ordering_fields = ['prix_eur']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        prix_min = self.request.query_params.get('prix_min')
        prix_max = self.request.query_params.get('prix_max')
        try:
            if prix_min is not None:
                queryset = queryset.filter(prix_eur__gte=float(prix_min))
            if prix_max is not None:
                queryset = queryset.filter(prix_eur__lte=float(prix_max))
        except ValueError:
            raise ValidationError("Les paramètres prix_min et prix_max doivent être des valeurs numériques.")
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        if request.headers.get('HX-Request'):
            composants = Composant.objects.all().order_by('-created_at')
            html = render_to_string('composants_list_fragment.html', {'composants': composants}, request=request)
            # Dispatch an event that the form was successful
            response = HttpResponse(html, content_type='text/html')
            response['HX-Trigger'] = 'newComponent' # So the list updates
            return response
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='type', description='Type de composant (panneau, batterie, regulateur, onduleur)'),
            OpenApiParameter(name='marque', description='Filtrer par marque'),
            OpenApiParameter(name='prix_min', description='Prix minimum en EUR'),
            OpenApiParameter(name='prix_max', description='Prix maximum en EUR')
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if request.headers.get('HX-Request'):
            html = render_to_string('composants_list_fragment.html', {'composants': queryset}, request=request)
            return HttpResponse(html, content_type='text/html')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# View for the component management tab content
@login_required
def composants_management_view(request):
    return render(request, 'composants_management.html')
