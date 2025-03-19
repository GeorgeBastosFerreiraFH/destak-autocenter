import logging
from typing import List, Dict, Any, Optional
from database.db_manager import get_connection
import config

logger = logging.getLogger(config.APP_NAME)

class VehicleController:
    """Controlador para operações relacionadas a veículos"""
    
    def get_all_vehicles(self) -> List[Dict[str, Any]]:
        """Retorna todos os veículos com informações do cliente"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT v.*, c.name as client_name
            FROM vehicles v
            LEFT JOIN clients c ON v.client_id = c.id
            ORDER BY v.plate
            '''
            
            cursor.execute(query)
            vehicles = cursor.fetchall()
            conn.close()
            
            return vehicles
        except Exception as e:
            logger.error(f"Erro ao obter veículos: {str(e)}")
            return []
    
    def get_vehicle_by_id(self, vehicle_id: int) -> Optional[Dict[str, Any]]:
        """Retorna um veículo pelo ID"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT v.*, c.name as client_name
            FROM vehicles v
            LEFT JOIN clients c ON v.client_id = c.id
            WHERE v.id = ?
            '''
            
            cursor.execute(query, (vehicle_id,))
            vehicle = cursor.fetchone()
            conn.close()
            
            return vehicle
        except Exception as e:
            logger.error(f"Erro ao obter veículo {vehicle_id}: {str(e)}")
            return None
    
    def get_vehicles_by_client(self, client_id: int) -> List[Dict[str, Any]]:
        """Retorna os veículos de um cliente específico"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM vehicles
            WHERE client_id = ?
            ORDER BY plate
            '''
            
            cursor.execute(query, (client_id,))
            vehicles = cursor.fetchall()
            conn.close()
            
            return vehicles
        except Exception as e:
            logger.error(f"Erro ao obter veículos do cliente {client_id}: {str(e)}")
            return []
    
    def add_vehicle(self, vehicle_data: Dict[str, Any]) -> Optional[int]:
        """Adiciona um novo veículo"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            INSERT INTO vehicles (plate, brand, model, year, color, client_id)
            VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            cursor.execute(query, (
                vehicle_data['plate'],
                vehicle_data['brand'],
                vehicle_data['model'],
                vehicle_data['year'],
                vehicle_data['color'],
                vehicle_data['client_id']
            ))
            
            vehicle_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Veículo adicionado com ID {vehicle_id}")
            return vehicle_id
        except Exception as e:
            logger.error(f"Erro ao adicionar veículo: {str(e)}")
            return None
    
    def update_vehicle(self, vehicle_id: int, vehicle_data: Dict[str, Any]) -> bool:
        """Atualiza um veículo existente"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            UPDATE vehicles
            SET plate = ?, brand = ?, model = ?, year = ?, color = ?, client_id = ?
            WHERE id = ?
            '''
            
            cursor.execute(query, (
                vehicle_data['plate'],
                vehicle_data['brand'],
                vehicle_data['model'],
                vehicle_data['year'],
                vehicle_data['color'],
                vehicle_data['client_id'],
                vehicle_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Veículo {vehicle_id} atualizado")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar veículo {vehicle_id}: {str(e)}")
            return False
    
    def delete_vehicle(self, vehicle_id: int) -> bool:
        """Exclui um veículo"""
        try:
            # Verificar se o veículo está em alguma ordem de serviço
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM service_orders WHERE vehicle_id = ?", (vehicle_id,))
            result = cursor.fetchone()
            
            if result['count'] > 0:
                logger.warning(f"Veículo {vehicle_id} não pode ser excluído pois está em uso em ordens de serviço")
                conn.close()
                return False
            
            # Excluir o veículo
            cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Veículo {vehicle_id} excluído")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir veículo {vehicle_id}: {str(e)}")
            return False
    
    def search_vehicles(self, search_term: str) -> List[Dict[str, Any]]:
        """Busca veículos por placa, marca ou modelo"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT v.*, c.name as client_name
            FROM vehicles v
            LEFT JOIN clients c ON v.client_id = c.id
            WHERE v.plate LIKE ? OR v.brand LIKE ? OR v.model LIKE ?
            ORDER BY v.plate
            '''
            
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            
            vehicles = cursor.fetchall()
            conn.close()
            
            return vehicles
        except Exception as e:
            logger.error(f"Erro ao buscar veículos: {str(e)}")
            return []
