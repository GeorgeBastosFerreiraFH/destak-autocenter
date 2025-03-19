import logging
from typing import List, Dict, Any, Optional
from database.db_manager import get_connection
import config

logger = logging.getLogger(config.APP_NAME)

class ClientController:
    """Controlador para operações relacionadas a clientes"""
    
    def get_all_clients(self) -> List[Dict[str, Any]]:
        """Retorna todos os clientes"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM clients
            ORDER BY name
            '''
            
            cursor.execute(query)
            clients = cursor.fetchall()
            conn.close()
            
            return clients
        except Exception as e:
            logger.error(f"Erro ao obter clientes: {str(e)}")
            return []
    
    def get_client_by_id(self, client_id: int) -> Optional[Dict[str, Any]]:
        """Retorna um cliente pelo ID"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM clients
            WHERE id = ?
            '''
            
            cursor.execute(query, (client_id,))
            client = cursor.fetchone()
            conn.close()
            
            return client
        except Exception as e:
            logger.error(f"Erro ao obter cliente {client_id}: {str(e)}")
            return None
    
    def add_client(self, client_data: Dict[str, Any]) -> Optional[int]:
        """Adiciona um novo cliente"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            INSERT INTO clients (name, document, address, phone, email, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            '''
            
            cursor.execute(query, (
                client_data['name'],
                client_data['document'],
                client_data['address'],
                client_data['phone'],
                client_data['email']
            ))
            
            client_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Cliente adicionado com ID {client_id}")
            return client_id
        except Exception as e:
            logger.error(f"Erro ao adicionar cliente: {str(e)}")
            return None
    
    def update_client(self, client_id: int, client_data: Dict[str, Any]) -> bool:
        """Atualiza um cliente existente"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            UPDATE clients
            SET name = ?, document = ?, address = ?, phone = ?, email = ?
            WHERE id = ?
            '''
            
            cursor.execute(query, (
                client_data['name'],
                client_data['document'],
                client_data['address'],
                client_data['phone'],
                client_data['email'],
                client_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cliente {client_id} atualizado")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente {client_id}: {str(e)}")
            return False
    
    def delete_client(self, client_id: int) -> bool:
        """Exclui um cliente"""
        try:
            # Verificar se o cliente tem veículos
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM vehicles WHERE client_id = ?", (client_id,))
            result = cursor.fetchone()
            
            if result['count'] > 0:
                logger.warning(f"Cliente {client_id} não pode ser excluído pois possui veículos cadastrados")
                conn.close()
                return False
            
            # Excluir o cliente
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Cliente {client_id} excluído")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir cliente {client_id}: {str(e)}")
            return False
    
    def search_clients(self, search_term: str) -> List[Dict[str, Any]]:
        """Busca clientes por nome, documento ou email"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM clients
            WHERE name LIKE ? OR document LIKE ? OR email LIKE ?
            ORDER BY name
            '''
            
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            
            clients = cursor.fetchall()
            conn.close()
            
            return clients
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {str(e)}")
            return []