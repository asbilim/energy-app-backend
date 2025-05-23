import os
import json
import logging
import re
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)

class DimensionnementAIService:
    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not configured in settings")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.AI_MODEL
        logger.info(f"Initialized AI service with model: {self.model}")
    
    def calculer_dimensionnement(self, params):
        """
        Utilise l'IA pour calculer le dimensionnement optimal du système PV
        """
        prompt = self._build_prompt(params)
        logger.info("Calculating dimensionnement with params: %s", params)
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en dimensionnement de systèmes photovoltaïques autonomes. "
                                 "Réponds UNIQUEMENT avec un objet JSON valide, sans aucun autre texte ou formatage. "
                                 "Ne mets pas de ```json``` ou autre marqueur de code."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1
            )
            
            response = completion.choices[0].message.content
            logger.info("Received AI response: %s", response)
            
            # Clean up the response
            cleaned_response = self._clean_response(response)
            logger.info("Cleaned response: %s", cleaned_response)
            
            result = self._parse_ai_response(cleaned_response)
            logger.info("Parsed AI response: %s", result)
            return result
            
        except Exception as e:
            logger.error("Error in AI calculation: %s", str(e), exc_info=True)
            raise Exception(f"Erreur lors du calcul IA: {str(e)}")
    
    def _clean_response(self, response):
        """
        Nettoie la réponse de l'IA pour extraire uniquement le JSON
        """
        # Remove any text before the first {
        response = re.sub(r'^[^{]*', '', response)
        # Remove any text after the last }
        response = re.sub(r'[^}]*$', '', response)
        # Remove any markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        return response.strip()
    
    def _build_prompt(self, params):
        prompt = f"""
        Dimensionne un système photovoltaïque autonome avec ces paramètres :
        - Consommation journalière : {params['consommation_journaliere_wh']} Wh
        - Profil de charge : {json.dumps(params['profil_charge'], ensure_ascii=False)}
        - Localisation : {params['latitude']}, {params['longitude']}
        - Marge de sécurité : {params['marge_securite_pct']}%
        - Rendement système : {params['rendement_systeme_pct']}%
        
        Réponds UNIQUEMENT avec un objet JSON qui contient ces champs :
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
        logger.debug("Built prompt: %s", prompt)
        return prompt
    
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
            
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON response: %s", response)
            raise Exception(f"La réponse de l'IA n'est pas un JSON valide: {str(e)}")
        except Exception as e:
            logger.error("Error parsing AI response: %s", str(e))
            raise Exception(f"Erreur lors du parsing de la réponse: {str(e)}") 