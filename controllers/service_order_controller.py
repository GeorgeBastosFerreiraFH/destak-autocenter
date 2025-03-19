import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from database.db_manager import get_connection
import config

logger = logging.getLogger(config.APP_NAME)

class ServiceOrderController:
    """Controlador para operações relacionadas a ordens de serviço"""
    
    def get_all_service_orders(self):
        # Lógica para retornar todas as ordens de serviço
        # Exemplo usando uma consulta a um banco de dados
        orders = [
            {"status": "em andamento", "total_value": 100.00},
            {"status": "concluído", "total_value": 150.00},
            {"status": "entregue", "total_value": 200.00},
        ]
        return orders
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Retorna todas as ordens de serviço com informações relacionadas"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT so.*, v.plate as vehicle_plate, c.name as client_name, e.name as employee_name
            FROM service_orders so
            LEFT JOIN vehicles v ON so.vehicle_id = v.id
            LEFT JOIN clients c ON v.client_id = c.id
            LEFT JOIN employees e ON so.employee_id = e.id
            ORDER BY so.open_date DESC
            '''
            
            cursor.execute(query)
            orders = cursor.fetchall()
            conn.close()
            
            return orders
        except Exception as e:
            logger.error(f"Erro ao obter ordens de serviço: {str(e)}")
            return []
    
    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Retorna uma ordem de serviço pelo ID"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT so.*, v.plate as vehicle_plate, c.name as client_name, e.name as employee_name
            FROM service_orders so
            LEFT JOIN vehicles v ON so.vehicle_id = v.id
            LEFT JOIN clients c ON v.client_id = c.id
            LEFT JOIN employees e ON so.employee_id = e.id
            WHERE so.id = ?
            '''
            
            cursor.execute(query, (order_id,))
            order = cursor.fetchone()
            
            if order:
                # Obter peças usadas nesta ordem
                cursor.execute(''' 
                SELECT op.*, p.code, p.description
                FROM order_parts op
                JOIN parts p ON op.part_id = p.id
                WHERE op.order_id = ? 
                ''', (order_id,))
                
                order_parts = cursor.fetchall()
                order['parts'] = order_parts
            
            conn.close()
            
            return order
        except Exception as e:
            logger.error(f"Erro ao obter ordem de serviço {order_id}: {str(e)}")
            return None
    
    def add_order(self, order_data: Dict[str, Any]) -> Optional[int]:
        """Adiciona uma nova ordem de serviço"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Inserir a ordem
            query = '''
            INSERT INTO service_orders (
                number, open_date, vehicle_id, description, status, 
                employee_id, completion_date, total_value, payment_method, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            '''
            
            cursor.execute(query, (
                order_data['number'],
                order_data.get('open_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                order_data['vehicle_id'],
                order_data['description'],
                order_data['status'],
                order_data['employee_id'],
                order_data.get('completion_date'),
                order_data['total_value'],
                order_data['payment_method']
            ))
            
            order_id = cursor.lastrowid
            
            # Inserir peças usadas, se houver
            if 'parts' in order_data and order_data['parts']:
                for part in order_data['parts']:
                    cursor.execute('''
                    INSERT INTO order_parts (order_id, part_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        order_id,
                        part['part_id'],
                        part['quantity'],
                        part['price']
                    ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Ordem de serviço adicionada com ID {order_id}")
            return order_id
        except Exception as e:
            logger.error(f"Erro ao adicionar ordem de serviço: {str(e)}")
            return None
    
    def update_order(self, order_id: int, order_data: Dict[str, Any]) -> bool:
        """Atualiza uma ordem de serviço existente"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Atualizar a ordem
            query = '''
            UPDATE service_orders
            SET number = ?, vehicle_id = ?, description = ?, status = ?, 
                employee_id = ?, completion_date = ?, total_value = ?, payment_method = ?
            WHERE id = ?
            '''
            
            cursor.execute(query, (
                order_data['number'],
                order_data['vehicle_id'],
                order_data['description'],
                order_data['status'],
                order_data['employee_id'],
                order_data.get('completion_date'),
                order_data['total_value'],
                order_data['payment_method'],
                order_id
            ))
            
            # Atualizar assinaturas, se fornecidas
            if 'client_signature' in order_data:
                cursor.execute('''
                UPDATE service_orders
                SET client_signature = ?
                WHERE id = ?
                ''', (order_data['client_signature'], order_id))
            
            if 'mechanic_signature' in order_data:
                cursor.execute('''
                UPDATE service_orders
                SET mechanic_signature = ?
                WHERE id = ?
                ''', (order_data['mechanic_signature'], order_id))
            
            # Atualizar peças usadas, se houver
            if 'parts' in order_data:
                # Remover peças existentes
                cursor.execute("DELETE FROM order_parts WHERE order_id = ?", (order_id,))
                
                # Adicionar novas peças
                for part in order_data['parts']:
                    cursor.execute('''
                    INSERT INTO order_parts (order_id, part_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        order_id,
                        part['part_id'],
                        part['quantity'],
                        part['price']
                    ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Ordem de serviço {order_id} atualizada")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar ordem de serviço {order_id}: {str(e)}")
            return False
    
    def delete_order(self, order_id: int) -> bool:
        """Exclui uma ordem de serviço"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Excluir peças relacionadas
            cursor.execute("DELETE FROM order_parts WHERE order_id = ?", (order_id,))
            
            # Excluir a ordem
            cursor.execute("DELETE FROM service_orders WHERE id = ?", (order_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Ordem de serviço {order_id} excluída")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir ordem de serviço {order_id}: {str(e)}")
            return False
    
    def get_order_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre as ordens de serviço"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Total de ordens por status
            cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM service_orders
            GROUP BY status
            ''')
            status_counts = cursor.fetchall()
            
            # Total de receita
            cursor.execute('''
            SELECT SUM(total_value) as total_revenue
            FROM service_orders
            ''')
            revenue = cursor.fetchone()
            
            # Média de valor por ordem
            cursor.execute('''
            SELECT AVG(total_value) as avg_value
            FROM service_orders
            ''')
            avg_value = cursor.fetchone()
            
            # Formas de pagamento
            cursor.execute('''
            SELECT payment_method, COUNT(*) as count
            FROM service_orders
            GROUP BY payment_method
            ''')
            payment_methods = cursor.fetchall()
            
            conn.close()
            
            return {
                'status_counts': status_counts,
                'total_revenue': revenue['total_revenue'] if revenue['total_revenue'] else 0,
                'avg_value': avg_value['avg_value'] if avg_value['avg_value'] else 0,
                'payment_methods': payment_methods
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de ordens: {str(e)}")
            return {
                'status_counts': [],
                'total_revenue': 0,
                'avg_value': 0,
                'payment_methods': []
            }
