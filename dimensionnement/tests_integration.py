from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from .models import Dimensionnement
from .services.ai_service import DimensionnementAIService

class DimensionnementIntegrationTests(TestCase):
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
        
        # Test data with real-world values
        self.dimensionnement_data = {
            'consommation_journaliere_wh': 5000,  # 5 kWh daily consumption
            'profil_charge': {
                '0': 100,   # Night: 100W
                '6': 200,   # Morning: 200W
                '12': 500,  # Midday: 500W
                '18': 300,  # Evening: 300W
                '22': 100   # Night: 100W
            },
            'latitude': 48.8566,  # Paris coordinates
            'longitude': 2.3522,
            'marge_securite_pct': 20,
            'rendement_systeme_pct': 85
        }
    
    def test_create_dimensionnement_with_real_ai(self):
        """Test dimensionnement creation with real AI service"""
        response = self.client.post(
            reverse('dimensionnement-list'),
            self.dimensionnement_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('dimensionnement', response.data)
        self.assertIn('explication', response.data)
        
        # Verify the response contains all required fields
        dimensionnement = response.data['dimensionnement']
        self.assertIn('nombre_panneaux', dimensionnement)
        self.assertIn('puissance_panneau_w', dimensionnement)
        self.assertIn('capacite_batterie_ah', dimensionnement)
        self.assertIn('tension_systeme_v', dimensionnement)
        self.assertIn('regulateur_data', dimensionnement)
        self.assertIn('onduleur_data', dimensionnement)
        self.assertIn('irradiation_moyenne_kwh_m2_j', dimensionnement)
        
        # Verify values are reasonable
        self.assertGreater(dimensionnement['nombre_panneaux'], 0)
        self.assertGreater(dimensionnement['puissance_panneau_w'], 0)
        self.assertGreater(dimensionnement['capacite_batterie_ah'], 0)
        self.assertGreater(dimensionnement['tension_systeme_v'], 0)
        self.assertGreater(dimensionnement['irradiation_moyenne_kwh_m2_j'], 0)
        
        # Verify the dimensionnement was created in database
        db_dimensionnement = Dimensionnement.objects.get(user=self.user)
        self.assertEqual(db_dimensionnement.nombre_panneaux, dimensionnement['nombre_panneaux'])
        self.assertEqual(db_dimensionnement.puissance_panneau_w, dimensionnement['puissance_panneau_w'])
        self.assertEqual(db_dimensionnement.capacite_batterie_ah, dimensionnement['capacite_batterie_ah'])
    
    def test_different_consumption_profiles(self):
        """Test dimensionnement with different consumption profiles"""
        # High consumption profile
        high_consumption_data = self.dimensionnement_data.copy()
        high_consumption_data['consommation_journaliere_wh'] = 10000  # 10 kWh
        high_consumption_data['profil_charge'] = {
            '0': 200,
            '6': 500,
            '12': 1000,
            '18': 800,
            '22': 300
        }
        
        response = self.client.post(
            reverse('dimensionnement-list'),
            high_consumption_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        high_consumption_result = response.data['dimensionnement']
        
        # Low consumption profile
        low_consumption_data = self.dimensionnement_data.copy()
        low_consumption_data['consommation_journaliere_wh'] = 2000  # 2 kWh
        low_consumption_data['profil_charge'] = {
            '0': 50,
            '6': 100,
            '12': 200,
            '18': 150,
            '22': 50
        }
        
        response = self.client.post(
            reverse('dimensionnement-list'),
            low_consumption_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        low_consumption_result = response.data['dimensionnement']
        
        # Verify that higher consumption leads to larger system
        self.assertGreater(
            high_consumption_result['nombre_panneaux'],
            low_consumption_result['nombre_panneaux']
        )
        self.assertGreater(
            high_consumption_result['capacite_batterie_ah'],
            low_consumption_result['capacite_batterie_ah']
        )
    
    def test_different_locations(self):
        """Test dimensionnement with different locations"""
        # Test with Paris coordinates (lower irradiation)
        paris_data = {
            'consommation_journaliere_wh': 5000,
            'profil_charge': {'0': 100, '6': 200, '12': 500, '18': 300, '22': 100},
            'latitude': 48.8566,
            'longitude': 2.3522,
            'marge_securite_pct': 20,
            'rendement_systeme_pct': 85
        }
        
        # Test with Dakar coordinates (higher irradiation)
        dakar_data = {
            'consommation_journaliere_wh': 5000,
            'profil_charge': {'0': 100, '6': 200, '12': 500, '18': 300, '22': 100},
            'latitude': 14.7167,
            'longitude': -17.4677,
            'marge_securite_pct': 20,
            'rendement_systeme_pct': 85
        }
        
        # Get dimensionnement for Paris
        paris_response = self.client.post(
            reverse('dimensionnement-list'),
            paris_data,
            format='json'
        )
        self.assertEqual(paris_response.status_code, 201)
        paris_result = paris_response.json()
        
        # Get dimensionnement for Dakar
        dakar_response = self.client.post(
            reverse('dimensionnement-list'),
            dakar_data,
            format='json'
        )
        self.assertEqual(dakar_response.status_code, 201)
        dakar_result = dakar_response.json()
        
        # Verify that Dakar needs fewer panels due to higher irradiation
        self.assertGreater(
            paris_result['irradiation_moyenne_kwh_m2_j'],
            dakar_result['irradiation_moyenne_kwh_m2_j']
        )
        
        # Calculate expected panel difference based on irradiation ratio
        irradiation_ratio = dakar_result['irradiation_moyenne_kwh_m2_j'] / paris_result['irradiation_moyenne_kwh_m2_j']
        expected_panels_dakar = int(paris_result['nombre_panneaux'] / irradiation_ratio)
        
        # Allow for some margin of error (20%)
        margin = 0.2
        min_expected_panels = int(expected_panels_dakar * (1 - margin))
        max_expected_panels = int(expected_panels_dakar * (1 + margin))
        
        self.assertGreaterEqual(dakar_result['nombre_panneaux'], min_expected_panels)
        self.assertLessEqual(dakar_result['nombre_panneaux'], max_expected_panels) 