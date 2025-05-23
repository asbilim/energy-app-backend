from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from .models import Composant
import json

class ComposantTests(TestCase):
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
        
        # Create test composants
        self.composant1 = Composant.objects.create(
            type='panneau', marque='SunPower', modele='SP-400',
            specifications={"puissance_w": 400, "tension_mpp_v": 40, "courant_mpp_a": 10, "technologie": "Mono"},
            prix_eur=250.00
        )
        self.composant2 = Composant.objects.create(
            type='batterie', marque='Victron', modele='BAT-200',
            specifications={"capacite_ah": 200, "tension_v": 24, "technologie": "LiFePO4", "cycles_vie": 3000},
            prix_eur=800.00
        )
        self.composant3 = Composant.objects.create(
            type='panneau', marque='Jinko', modele='JK-350',
            specifications={"puissance_w": 350, "tension_mpp_v": 38, "courant_mpp_a": 9.2, "technologie": "Poly"},
            prix_eur=180.00
        )
    
    def assertHasFields(self, obj, fields, context=''): 
        for field in fields:
            self.assertIn(field, obj, f"Missing field '{field}' in response {context}: {json.dumps(obj, ensure_ascii=False)}")

    def test_list_composants(self):
        """Test listing all composants"""
        response = self.client.get(reverse('composant-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Unexpected status code: {response.status_code}, response: {response.data}")
        self.assertGreaterEqual(len(response.data['results']), 3, f"Expected at least 3 composants, got {len(response.data['results'])}, response: {response.data}")
        for composant in response.data['results']:
            self.assertHasFields(composant, ['id', 'type', 'marque', 'modele', 'specifications', 'prix_eur'])
    
    def test_filter_composants_by_type(self):
        """Test filtering composants by type"""
        response = self.client.get(reverse('composant-list'), {'type': 'panneau'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Unexpected status code: {response.status_code}, response: {response.data}")
        for composant in response.data['results']:
            self.assertEqual(composant['type'], 'panneau', f"Expected type 'panneau', got {composant['type']}, response: {composant}")
    
    def test_filter_composants_by_marque(self):
        """Test filtering composants by marque"""
        response = self.client.get(reverse('composant-list'), {'marque': 'SunPower'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Unexpected status code: {response.status_code}, response: {response.data}")
        for composant in response.data['results']:
            self.assertEqual(composant['marque'], 'SunPower', f"Expected marque 'SunPower', got {composant['marque']}, response: {composant}")
    
    def test_filter_composants_by_price_range(self):
        """Test filtering composants by price range"""
        response = self.client.get(reverse('composant-list'), {'prix_min': 200, 'prix_max': 300})
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Unexpected status code: {response.status_code}, response: {response.data}")
        for composant in response.data['results']:
            self.assertGreaterEqual(float(composant['prix_eur']), 200, f"Expected prix_eur >= 200, got {composant['prix_eur']}, response: {composant}")
            self.assertLessEqual(float(composant['prix_eur']), 300, f"Expected prix_eur <= 300, got {composant['prix_eur']}, response: {composant}")
    
    def test_retrieve_composant(self):
        """Test retrieving a specific composant"""
        response = self.client.get(reverse('composant-detail', args=[self.composant1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Unexpected status code: {response.status_code}, response: {response.data}")
        self.assertHasFields(response.data, ['id', 'type', 'marque', 'modele', 'specifications', 'prix_eur'])
    
    def test_unauthorized_access(self):
        """Test unauthorized access to composants"""
        # Remove authentication
        self.client.credentials()
        
        response = self.client.get(reverse('composant-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, f"Expected 401 Unauthorized, got {response.status_code}, response: {response.data}")
    
    def test_invalid_composant_specifications(self):
        """Test validation of composant specifications"""
        invalid_data = {
            'type': 'panneau',
            'marque': 'TestBrand',
            'modele': 'TestModel',
            'specifications': {"puissance_w": -100, "tension_mpp_v": 40},  # Missing fields, negative value
            'prix_eur': 100.00
        }
        
        response = self.client.post(reverse('composant-list'), invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request, got {response.status_code}, response: {response.data}")
        self.assertTrue('specifications' in response.data or 'non_field_errors' in response.data, f"Expected error in 'specifications', got {response.data}")
    
    def test_missing_required_specifications(self):
        """Test validation of required specifications"""
        missing_spec_data = {
            'type': 'batterie',
            'marque': 'TestBrand',
            'modele': 'TestModel',
            'specifications': {"capacite_ah": 100},  # Missing required fields
            'prix_eur': 200.00
        }
        
        response = self.client.post(reverse('composant-list'), missing_spec_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400 Bad Request, got {response.status_code}, response: {response.data}")
        self.assertTrue('specifications' in response.data or 'non_field_errors' in response.data, f"Expected error in 'specifications', got {response.data}")
