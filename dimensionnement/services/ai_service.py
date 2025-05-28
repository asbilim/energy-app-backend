import os
import json
import logging
import re
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)

class DimensionnementAIService:
    def __init__(self):
        if not settings.OPENROUTER_API_KEY and not settings.DEBUG:
            raise ValueError("OPENROUTER_API_KEY is not configured in settings")
            
        # During development with DEBUG=True, we can use a mock client
        if settings.DEBUG and not settings.OPENROUTER_API_KEY:
            self.client = None
            self.model = "mock-model"
            logger.info("Using mock AI service in debug mode")
        else:
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
            # If in debug mode without API key, return mock data
            if settings.DEBUG and self.client is None:
                logger.info("Using mock AI response in debug mode")
                return {
                    "nombre_panneaux": 4,
                    "puissance_panneau_w": 400,
                    "capacite_batterie_ah": 200,
                    "tension_systeme_v": 24,
                    "regulateur": {"type": "MPPT", "courant_max_a": 40},
                    "onduleur": {"puissance_nominale_w": 2000, "rendement_pct": 95.5},
                    "irradiation_moyenne_kwh_m2_j": 4.2,
                    "explication": "Ceci est une réponse de test générée automatiquement en mode DEBUG."
                }
            
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
Analyze the following parameters for an autonomous photovoltaic system:
- Daily Consumption: {params['consommation_journaliere_wh']} Wh
- Load Profile (hourly distribution): {json.dumps(params['profil_charge'], ensure_ascii=False)}
- Location (Latitude, Longitude): {params['latitude']}, {params['longitude']}
- Safety Margin: {params['marge_securite_pct']}%
- System Efficiency: {params['rendement_systeme_pct']}%

Based on this data, generate a SINGLE, VALID JSON OBJECT containing the sizing results.
The JSON object MUST strictly follow this structure and include all specified fields:

{{
    "nombre_panneaux": <integer>,
    "puissance_panneau_w": <integer>,        // Typical power of a single panel in Watts
    "capacite_batterie_ah": <integer>,   // Total battery capacity in Ampere-hours
    "tension_systeme_v": <integer>,          // System voltage (e.g., 12, 24, 48)
    "regulateur": {{
        "type": "<string: MPPT or PWM>",
        "courant_max_a": <integer>          // Maximum current handling capacity in Amperes
    }},
    "onduleur": {{
        "puissance_nominale_w": <integer>, // Nominal power output in Watts
        "rendement_pct": <float>           // Efficiency in percentage (e.g., 95.5)
    }},
    "irradiation_moyenne_kwh_m2_j": <float>, // Average daily solar irradiation in kWh/m²/day for the location
    "explication": "<string>"              // Brief technical explanation of the sizing choices. Must be a simple JSON string.
}}

IMPORTANT INSTRUCTIONS:
1.  Your entire response MUST be ONLY the JSON object, IN FRENCH.
2.  The 'explication' field MUST be in FRENCH and provide a detailed technical justification for the main sizing choices (panels, battery, system voltage), including how they relate to consumption, autonomy, and location.
3.  Do NOT include any introductory text, concluding remarks, apologies, or any characters before the opening '{{' or after the closing '}}' of the JSON.
4.  Ensure all numerical values are actual numbers (integer or float) and not strings.
5.  The calculations should consider local solar irradiation for the given coordinates and ensure the battery capacity covers at least 2 days of autonomy, respecting the safety margin.
6.  All components (panels, battery, regulator, inverter) must be compatible with each other and the system voltage.
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