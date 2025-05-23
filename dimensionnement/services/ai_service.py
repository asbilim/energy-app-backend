import os
import json
from openai import OpenAI
from django.conf import settings

class DimensionnementAIService:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.AI_MODEL
    
    def calculer_dimensionnement(self, params):
        """
        Utilise l'IA pour calculer le dimensionnement optimal du système PV
        """
        prompt = self._build_prompt(params)
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en dimensionnement de systèmes photovoltaïques autonomes. "
                                 "Réponds uniquement en JSON valide avec les calculs appropriés basés sur les "
                                 "meilleures pratiques du domaine."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1
            )
            
            response = completion.choices[0].message.content
            return self._parse_ai_response(response)
            
        except Exception as e:
            raise Exception(f"Erreur lors du calcul IA: {str(e)}")
    
    def _build_prompt(self, params):
        return f"""
        Dimensionne un système photovoltaïque autonome avec ces paramètres :
        - Consommation journalière : {params['consommation_journaliere_wh']} Wh
        - Profil de charge : {json.dumps(params['profil_charge'], ensure_ascii=False)}
        - Localisation : {params['latitude']}, {params['longitude']}
        - Marge de sécurité : {params['marge_securite_pct']}%
        - Rendement système : {params['rendement_systeme_pct']}%
        
        Réponds en JSON avec cette structure :
        {{
            "nombre_panneaux": int,
            "puissance_panneau_w": int,
            "capacite_batterie_ah": int,
            "tension_systeme_v": int,
            "regulateur": {{"type": "MPPT/PWM", "courant_max_a": int}},
            "onduleur": {{"puissance_nominale_w": int, "rendement_pct": float}},
            "irradiation_moyenne_kwh_m2_j": float,
            "explication": "string"
        }}
        
        Assure-toi que :
        1. Les calculs prennent en compte l'irradiation solaire locale
        2. La capacité batterie couvre 2 jours d'autonomie
        3. Le dimensionnement respecte les marges de sécurité
        4. Les composants sont compatibles entre eux
        """
    
    def _parse_ai_response(self, response):
        """
        Parse et valide la réponse de l'IA
        """
        try:
            data = json.loads(response)
            required_fields = [
                'nombre_panneaux', 'puissance_panneau_w', 'capacite_batterie_ah',
                'tension_systeme_v', 'regulateur', 'onduleur',
                'irradiation_moyenne_kwh_m2_j', 'explication'
            ]
            
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Champ manquant dans la réponse: {field}")
            
            return data
            
        except json.JSONDecodeError:
            raise Exception("La réponse de l'IA n'est pas un JSON valide")
        except Exception as e:
            raise Exception(f"Erreur lors du parsing de la réponse: {str(e)}") 