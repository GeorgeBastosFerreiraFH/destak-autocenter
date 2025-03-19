import requests
import json
import logging
from typing import List, Dict, Any, Optional
import config

logger = logging.getLogger(config.APP_NAME)

class VehicleAPIService:
    """Serviço para interagir com a API de veículos FIPE"""
    
    def __init__(self):
        self.base_url = config.VEHICLE_API_URL
        self.cache = {
            'brands': None,
            'models': {}
        }
    
    def get_brands(self) -> List[Dict[str, Any]]:
        """Obtém a lista de marcas de veículos"""
        if self.cache['brands']:
            return self.cache['brands']
        
        try:
            response = requests.get(f"{self.base_url}/carros/marcas")
            response.raise_for_status()
            brands = response.json()
            self.cache['brands'] = brands
            return brands
        except Exception as e:
            logger.error(f"Erro ao obter marcas de veículos: {str(e)}")
            return []
    
    def get_models_by_brand(self, brand_code: str) -> List[Dict[str, Any]]:
        """Obtém a lista de modelos para uma marca específica"""
        if brand_code in self.cache['models']:
            return self.cache['models'][brand_code]
        
        try:
            response = requests.get(f"{self.base_url}/carros/marcas/{brand_code}/modelos")
            response.raise_for_status()
            data = response.json()
            models = data.get('modelos', [])
            self.cache['models'][brand_code] = models
            return models
        except Exception as e:
            logger.error(f"Erro ao obter modelos para a marca {brand_code}: {str(e)}")
            return []
    
    def get_years_by_model(self, brand_code: str, model_code: str) -> List[Dict[str, Any]]:
        """Obtém os anos disponíveis para um modelo específico"""
        try:
            response = requests.get(f"{self.base_url}/carros/marcas/{brand_code}/modelos/{model_code}/anos")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter anos para o modelo {model_code}: {str(e)}")
            return []
    
    def get_vehicle_details(self, brand_code: str, model_code: str, year_code: str) -> Optional[Dict[str, Any]]:
        """Obtém detalhes de um veículo específico"""
        try:
            response = requests.get(
                f"{self.base_url}/carros/marcas/{brand_code}/modelos/{model_code}/anos/{year_code}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do veículo: {str(e)}")
            return None
    
    def search_brand_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Busca uma marca pelo nome"""
        brands = self.get_brands()
        name = name.lower()
        for brand in brands:
            if brand['nome'].lower() == name:
                return brand
        return None
    
    def search_model_by_name(self, brand_code: str, name: str) -> Optional[Dict[str, Any]]:
        """Busca um modelo pelo nome dentro de uma marca"""
        models = self.get_models_by_brand(brand_code)
        name = name.lower()
        for model in models:
            if model['nome'].lower() == name:
                return model
        return None

# Instância global do serviço
vehicle_api = VehicleAPIService()