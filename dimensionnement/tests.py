from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from authentication.models import User
from .models import Dimensionnement

class DimensionnementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Test123!@#'
        )
        
        # Login and get token
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'Test123!@#'
        }, format='json')
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Test data (all required fields, correct profil_charge format)
        self.dimensionnement_data = {
            'consommation_journaliere_wh': 5000,
            'profil_charge': {
                '0': 100,
                '6': 200,
                '12': 500,
                '18': 300,
                '22': 100
            },
            'latitude': 48.8566,
            'longitude': 2.3522,
            'marge_securite_pct': 20,
            'rendement_systeme_pct': 85
        }
        
        # Mock AI service response
        self.mock_ai_response = {
            'nombre_panneaux': 4,
            'puissance_panneau_w': 400,
            'capacite_batterie_ah': 200,
            'tension_systeme_v': 24,
            'regulateur': {'type': 'MPPT', 'courant_max_a': 40},
            'onduleur': {'puissance_nominale_w': 2000, 'rendement_pct': 95.5},
            'irradiation_moyenne_kwh_m2_j': 4.2,
            'explication': 'Test explanation'
        }
    
    @patch('dimensionnement.services.ai_service.DimensionnementAIService.calculer_dimensionnement')
    def test_create_dimensionnement_success(self, mock_calculer):
        """Test successful dimensionnement creation"""
        mock_calculer.return_value = self.mock_ai_response
        
        response = self.client.post(
            reverse('dimensionnement-list'),
            self.dimensionnement_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['dimensionnement']['nombre_panneaux'], 4)
        self.assertEqual(response.data['dimensionnement']['capacite_batterie_ah'], 200)
        self.assertEqual(response.data['dimensionnement']['puissance_panneau_w'], 400)
        self.assertEqual(response.data['dimensionnement']['tension_systeme_v'], 24)
        
        # Verify dimensionnement was created in database
        dimensionnement = Dimensionnement.objects.get(user=self.user)
        self.assertEqual(dimensionnement.nombre_panneaux, 4)
        self.assertEqual(dimensionnement.capacite_batterie_ah, 200)
        self.assertEqual(dimensionnement.puissance_panneau_w, 400)
        self.assertEqual(dimensionnement.tension_systeme_v, 24)
    
    def test_create_dimensionnement_invalid_data(self):
        """Test dimensionnement creation with invalid data"""
        invalid_data = self.dimensionnement_data.copy()
        invalid_data['latitude'] = 200  # Invalid latitude
        
        response = self.client.post(
            reverse('dimensionnement-list'),
            invalid_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('dimensionnement.services.ai_service.DimensionnementAIService.calculer_dimensionnement')
    def test_list_dimensionnements(self, mock_calculer):
        """Test listing user's dimensionnements"""
        mock_calculer.return_value = self.mock_ai_response
        
        # Create multiple dimensionnements
        for _ in range(3):
            self.client.post(
                reverse('dimensionnement-list'),
                self.dimensionnement_data,
                format='json'
            )
        
        response = self.client.get(reverse('dimensionnement-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    @patch('dimensionnement.services.ai_service.DimensionnementAIService.calculer_dimensionnement')
    def test_retrieve_dimensionnement(self, mock_calculer):
        """Test retrieving a specific dimensionnement"""
        mock_calculer.return_value = self.mock_ai_response
        
        # Create a dimensionnement
        create_response = self.client.post(
            reverse('dimensionnement-list'),
            self.dimensionnement_data,
            format='json'
        )
        dimensionnement_id = create_response.data['dimensionnement']['id']
        
        # Retrieve it
        response = self.client.get(
            reverse('dimensionnement-detail', args=[dimensionnement_id])
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre_panneaux'], 4)
        self.assertEqual(response.data['capacite_batterie_ah'], 200)
        self.assertEqual(response.data['puissance_panneau_w'], 400)
        self.assertEqual(response.data['tension_systeme_v'], 24)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to dimensionnements"""
        # Remove authentication
        self.client.credentials()
        
        response = self.client.get(reverse('dimensionnement-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('dimensionnement.services.ai_service.DimensionnementAIService.calculer_dimensionnement')
    def test_ai_service_error(self, mock_calculer):
        """Test handling of AI service errors"""
        mock_calculer.side_effect = Exception("AI service error")
        
        response = self.client.post(
            reverse('dimensionnement-list'),
            self.dimensionnement_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
