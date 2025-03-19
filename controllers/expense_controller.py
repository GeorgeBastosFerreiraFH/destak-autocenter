import logging
from typing import List, Dict, Any, Optional
from database.db_manager import get_connection
import config

logger = logging.getLogger(config.APP_NAME)

class ExpenseController:
    """Controlador para operações relacionadas a gastos"""
    
    def get_all_expenses(self) -> List[Dict[str, Any]]:
        """Retorna todos os gastos"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM expenses
            ORDER BY date DESC
            '''
            
            cursor.execute(query)
            expenses = cursor.fetchall()
            conn.close()
            
            return expenses
        except Exception as e:
            logger.error(f"Erro ao obter gastos: {str(e)}")
            return []
    
    def get_expense_by_id(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """Retorna um gasto pelo ID"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM expenses
            WHERE id = ?
            '''
            
            cursor.execute(query, (expense_id,))
            expense = cursor.fetchone()
            conn.close()
            
            return expense
        except Exception as e:
            logger.error(f"Erro ao obter gasto {expense_id}: {str(e)}")
            return None
    
    def add_expense(self, expense_data: Dict[str, Any]) -> Optional[int]:
        """Adiciona um novo gasto"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            INSERT INTO expenses (date, description, value, category, payment_method, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            '''
            
            cursor.execute(query, (
                expense_data['date'],
                expense_data['description'],
                expense_data['value'],
                expense_data['category'],
                expense_data['payment_method']
            ))
            
            expense_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Gasto adicionado com ID {expense_id}")
            return expense_id
        except Exception as e:
            logger.error(f"Erro ao adicionar gasto: {str(e)}")
            return None
    
    def update_expense(self, expense_id: int, expense_data: Dict[str, Any]) -> bool:
        """Atualiza um gasto existente"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            UPDATE expenses
            SET date = ?, description = ?, value = ?, category = ?, payment_method = ?
            WHERE id = ?
            '''
            
            cursor.execute(query, (
                expense_data['date'],
                expense_data['description'],
                expense_data['value'],
                expense_data['category'],
                expense_data['payment_method'],
                expense_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Gasto {expense_id} atualizado")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar gasto {expense_id}: {str(e)}")
            return False
    
    def delete_expense(self, expense_id: int) -> bool:
        """Exclui um gasto"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Gasto {expense_id} excluído")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir gasto {expense_id}: {str(e)}")
            return False
    
    def get_expense_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre os gastos"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Total de gastos por categoria
            cursor.execute('''
            SELECT category, SUM(value) as total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
            ''')
            category_totals = cursor.fetchall()
            
            # Total de gastos por mês
            cursor.execute('''
            SELECT strftime('%Y-%m', date) as month, SUM(value) as total
            FROM expenses
            GROUP BY month
            ORDER BY month DESC
            ''')
            monthly_totals = cursor.fetchall()
            
            # Total de gastos por forma de pagamento
            cursor.execute('''
            SELECT payment_method, SUM(value) as total
            FROM expenses
            GROUP BY payment_method
            ORDER BY total DESC
            ''')
            payment_method_totals = cursor.fetchall()
            
            # Total geral
            cursor.execute('''
            SELECT SUM(value) as total
            FROM expenses
            ''')
            total = cursor.fetchone()
            
            conn.close()
            
            return {
                'category_totals': category_totals,
                'monthly_totals': monthly_totals,
                'payment_method_totals': payment_method_totals,
                'total': total['total'] if total['total'] else 0
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de gastos: {str(e)}")
            return {
                'category_totals': [],
                'monthly_totals': [],
                'payment_method_totals': [],
                'total': 0
            }