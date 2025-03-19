import logging
from typing import List, Dict, Any, Optional
from database.db_manager import get_connection
import config

logger = logging.getLogger(config.APP_NAME)

class PartController:
    """Controlador para operações relacionadas a peças"""
    
    def get_all_parts(self) -> List[Dict[str, Any]]:
        """Retorna todas as peças"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM parts
            ORDER BY code
            '''
            
            cursor.execute(query)
            parts = cursor.fetchall()
            conn.close()
            
            return parts
        except Exception as e:
            logger.error(f"Erro ao obter peças: {str(e)}")
            return []
    
    def get_part_by_id(self, part_id: int) -> Optional[Dict[str, Any]]:
        """Retorna uma peça pelo ID"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM parts
            WHERE id = ?
            '''
            
            cursor.execute(query, (part_id,))
            part = cursor.fetchone()
            conn.close()
            
            return part
        except Exception as e:
            logger.error(f"Erro ao obter peça {part_id}: {str(e)}")
            return None
    
    def add_part(self, part_data: Dict[str, Any]) -> Optional[int]:
        """Adiciona uma nova peça"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            INSERT INTO parts (code, description, stock_quantity, buy_price, sell_price, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            '''
            
            cursor.execute(query, (
                part_data['code'],
                part_data['description'],
                part_data['stock_quantity'],
                part_data['buy_price'],
                part_data['sell_price']
            ))
            
            part_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Peça adicionada com ID {part_id}")
            return part_id
        except Exception as e:
            logger.error(f"Erro ao adicionar peça: {str(e)}")
            return None
    
    def update_part(self, part_id: int, part_data: Dict[str, Any]) -> bool:
        """Atualiza uma peça existente"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            UPDATE parts
            SET code = ?, description = ?, stock_quantity = ?, buy_price = ?, sell_price = ?
            WHERE id = ?
            '''
            
            cursor.execute(query, (
                part_data['code'],
                part_data['description'],
                part_data['stock_quantity'],
                part_data['buy_price'],
                part_data['sell_price'],
                part_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Peça {part_id} atualizada")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar peça {part_id}: {str(e)}")
            return False
    
    def delete_part(self, part_id: int) -> bool:
        """Exclui uma peça"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Verificar se a peça está em alguma ordem de serviço
            cursor.execute("SELECT COUNT(*) as count FROM order_parts WHERE part_id = ?", (part_id,))
            result = cursor.fetchone()
            
            if result['count'] > 0:
                logger.warning(f"Peça {part_id} não pode ser excluída pois está em uso em ordens de serviço")
                conn.close()
                return False
            
            # Excluir a peça
            cursor.execute("DELETE FROM parts WHERE id = ?", (part_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Peça {part_id} excluída")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir peça {part_id}: {str(e)}")
            return False
    
    def update_stock(self, part_id: int, quantity_change: int) -> bool:
        """Atualiza o estoque de uma peça"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Obter quantidade atual
            cursor.execute("SELECT stock_quantity FROM parts WHERE id = ?", (part_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Peça {part_id} não encontrada")
                conn.close()
                return False
            
            current_quantity = result['stock_quantity']
            new_quantity = current_quantity + quantity_change
            
            if new_quantity < 0:
                logger.warning(f"Estoque insuficiente para peça {part_id}")
                conn.close()
                return False
            
            # Atualizar estoque
            cursor.execute('''
            UPDATE parts
            SET stock_quantity = ?
            WHERE id = ?
            ''', (new_quantity, part_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Estoque da peça {part_id} atualizado: {current_quantity} -> {new_quantity}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar estoque da peça {part_id}: {str(e)}")
            return False