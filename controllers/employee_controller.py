import logging
from typing import List, Dict, Any, Optional
from database.db_manager import get_connection
import config

logger = logging.getLogger(config.APP_NAME)

class EmployeeController:
    """Controlador para operações relacionadas a funcionários"""
    
    def get_all_employees(self) -> List[Dict[str, Any]]:
        """Retorna todos os funcionários"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM employees
            ORDER BY name
            '''
            
            cursor.execute(query)
            employees = cursor.fetchall()
            conn.close()
            
            return employees
        except Exception as e:
            logger.error(f"Erro ao obter funcionários: {str(e)}")
            return []
    
    def get_employee_by_id(self, employee_id: int) -> Optional[Dict[str, Any]]:
        """Retorna um funcionário pelo ID"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM employees
            WHERE id = ?
            '''
            
            cursor.execute(query, (employee_id,))
            employee = cursor.fetchone()
            conn.close()
            
            return employee
        except Exception as e:
            logger.error(f"Erro ao obter funcionário {employee_id}: {str(e)}")
            return None
    
    def add_employee(self, employee_data: Dict[str, Any]) -> Optional[int]:
        """Adiciona um novo funcionário"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            INSERT INTO employees (name, document, role, hire_date, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            '''
            
            cursor.execute(query, (
                employee_data['name'],
                employee_data['document'],
                employee_data['role'],
                employee_data['hire_date']
            ))
            
            employee_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Funcionário adicionado com ID {employee_id}")
            return employee_id
        except Exception as e:
            logger.error(f"Erro ao adicionar funcionário: {str(e)}")
            return None
    
    def update_employee(self, employee_id: int, employee_data: Dict[str, Any]) -> bool:
        """Atualiza um funcionário existente"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
            UPDATE employees
            SET name = ?, document = ?, role = ?, hire_date = ?
            WHERE id = ?
            '''
            
            cursor.execute(query, (
                employee_data['name'],
                employee_data['document'],
                employee_data['role'],
                employee_data['hire_date'],
                employee_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Funcionário {employee_id} atualizado")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar funcionário {employee_id}: {str(e)}")
            return False
    
    def delete_employee(self, employee_id: int) -> bool:
        """Exclui um funcionário"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Verificar se o funcionário está em alguma ordem de serviço
            cursor.execute("SELECT COUNT(*) as count FROM service_orders WHERE employee_id = ?", (employee_id,))
            result = cursor.fetchone()
            
            if result['count'] > 0:
                logger.warning(f"Funcionário {employee_id} não pode ser excluído pois está em uso em ordens de serviço")
                conn.close()
                return False
            
            # Excluir o funcionário
            cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Funcionário {employee_id} excluído")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir funcionário {employee_id}: {str(e)}")
            return False