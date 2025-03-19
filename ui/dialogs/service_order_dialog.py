from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QComboBox, QPushButton, QLabel, 
                            QMessageBox, QDateEdit, QTextEdit, QTableWidget,
                            QTableWidgetItem, QHeaderView, QDoubleSpinBox,
                            QSpinBox, QTabWidget, QWidget)
from PyQt5.QtCore import Qt, QDate
import logging
from controllers.service_order_controller import ServiceOrderController
from controllers.vehicle_controller import VehicleController
from controllers.employee_controller import EmployeeController
from controllers.part_controller import PartController
from ui.widgets.signature_widget import SignatureWidget
import config

logger = logging.getLogger(config.APP_NAME)

class ServiceOrderDialog(QDialog):
    """Diálogo para adicionar ou editar ordens de serviço"""
    
    def __init__(self, parent=None, order=None):
        super().__init__(parent)
        self.order = order
        self.service_order_controller = ServiceOrderController()
        self.vehicle_controller = VehicleController()
        self.employee_controller = EmployeeController()
        self.part_controller = PartController()
        
        self.vehicles = []
        self.employees = []
        self.parts = []
        self.selected_parts = []
        
        self.setWindowTitle("Adicionar Ordem de Serviço" if not order else "Editar Ordem de Serviço")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        self.setup_ui()
        self.load_data()
        
        # Se estiver editando, preencher os campos
        if self.order:
            self.fill_form()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Abas
        self.tabs = QTabWidget()
        
        # Aba de informações básicas
        basic_tab = QWidget()
        basic_layout = QVBoxLayout()
        
        # Formulário básico
        form_layout = QFormLayout()
        
        # Número da OS
        self.number_edit = QLineEdit()
        self.number_edit.setPlaceholderText("OS-001")
        form_layout.addRow("Número:", self.number_edit)
        
        # Data de abertura
        self.open_date_edit = QDateEdit()
        self.open_date_edit.setCalendarPopup(True)
        self.open_date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Data de Abertura:", self.open_date_edit)
        
        # Veículo
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.setMinimumWidth(300)
        form_layout.addRow("Veículo:", self.vehicle_combo)
        
        # Descrição
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Descreva os serviços a serem realizados")
        self.description_edit.setMinimumHeight(100)
        form_layout.addRow("Descrição:", self.description_edit)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["em andamento", "concluído", "entregue"])
        form_layout.addRow("Status:", self.status_combo)
        
        # Funcionário responsável
        self.employee_combo = QComboBox()
        self.employee_combo.setMinimumWidth(300)
        form_layout.addRow("Funcionário:", self.employee_combo)
        
        # Data de conclusão
        self.completion_date_edit = QDateEdit()
        self.completion_date_edit.setCalendarPopup(True)
        self.completion_date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Data de Conclusão:", self.completion_date_edit)
        
        # Valor total
        self.total_value_spin = QDoubleSpinBox()
        self.total_value_spin.setRange(0, 999999.99)
        self.total_value_spin.setDecimals(2)
        self.total_value_spin.setSingleStep(10)
        self.total_value_spin.setPrefix("R$ ")
        form_layout.addRow("Valor Total:", self.total_value_spin)
        
        # Forma de pagamento
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["pix", "cartão", "dinheiro", "boleto"])
        form_layout.addRow("Forma de Pagamento:", self.payment_method_combo)
        
        basic_layout.addLayout(form_layout)
        basic_tab.setLayout(basic_layout)
        
        # Aba de peças
        parts_tab = QWidget()
        parts_layout = QVBoxLayout()
        
        # Tabela de peças selecionadas
        self.parts_table = QTableWidget()
        self.parts_table.setColumnCount(5)
        self.parts_table.setHorizontalHeaderLabels(["Código", "Descrição", "Quantidade", "Valor Unit.", "Subtotal"])
        self.parts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.parts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.parts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        parts_layout.addWidget(self.parts_table)
        
        # Controles para adicionar peças
        parts_form = QHBoxLayout()
        
        self.part_combo = QComboBox()
        self.part_combo.setMinimumWidth(300)
        parts_form.addWidget(QLabel("Peça:"))
        parts_form.addWidget(self.part_combo)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 100)
        self.quantity_spin.setValue(1)
        parts_form.addWidget(QLabel("Quantidade:"))
        parts_form.addWidget(self.quantity_spin)
        
        self.add_part_button = QPushButton("Adicionar")
        self.add_part_button.clicked.connect(self.add_part_to_order)
        parts_form.addWidget(self.add_part_button)
        
        self.remove_part_button = QPushButton("Remover")
        self.remove_part_button.clicked.connect(self.remove_part_from_order)
        parts_form.addWidget(self.remove_part_button)
        
        parts_layout.addLayout(parts_form)
        parts_tab.setLayout(parts_layout)
        
        # Aba de assinaturas
        signatures_tab = QWidget()
        signatures_layout = QVBoxLayout()
        
        # Assinatura do cliente
        self.client_signature = SignatureWidget(title="Assinatura do Cliente")
        signatures_layout.addWidget(self.client_signature)
        
        # Assinatura do mecânico
        self.mechanic_signature = SignatureWidget(title="Assinatura do Mecânico")
        signatures_layout.addWidget(self.mechanic_signature)
        
        signatures_tab.setLayout(signatures_layout)
        
        # Adicionar abas
        self.tabs.addTab(basic_tab, "Informações Básicas")
        self.tabs.addTab(parts_tab, "Peças")
        self.tabs.addTab(signatures_tab, "Assinaturas")
        
        layout.addWidget(self.tabs)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_order)
        self.save_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Carrega os dados necessários para o diálogo"""
        # Carregar veículos
        self.vehicles = self.vehicle_controller.get_all_vehicles()
        self.vehicle_combo.clear()
        for vehicle in self.vehicles:
            self.vehicle_combo.addItem(f"{vehicle['plate']} - {vehicle['brand']} {vehicle['model']}", vehicle['id'])
        
        # Carregar funcionários
        self.employees = self.employee_controller.get_all_employees()
        self.employee_combo.clear()
        for employee in self.employees:
            self.employee_combo.addItem(f"{employee['name']} ({employee['role']})", employee['id'])
        
        # Carregar peças
        self.parts = self.part_controller.get_all_parts()
        self.part_combo.clear()
        for part in self.parts:
            self.part_combo.addItem(f"{part['code']} - {part['description']} (R$ {part['sell_price']:.2f})", part['id'])
    
    def fill_form(self):
        """Preenche o formulário com os dados da ordem de serviço"""
        self.number_edit.setText(self.order['number'])
        
        # Data de abertura
        open_date = QDate.fromString(self.order['open_date'].split()[0], "yyyy-MM-dd")
        self.open_date_edit.setDate(open_date)
        
        # Veículo
        index = self.vehicle_combo.findData(self.order['vehicle_id'])
        if index >= 0:
            self.vehicle_combo.setCurrentIndex(index)
        
        self.description_edit.setText(self.order['description'])
        
        # Status
        index = self.status_combo.findText(self.order['status'])
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        # Funcionário
        index = self.employee_combo.findData(self.order['employee_id'])
        if index >= 0:
            self.employee_combo.setCurrentIndex(index)
        
        # Data de conclusão
        if self.order.get('completion_date'):
            completion_date = QDate.fromString(self.order['completion_date'].split()[0], "yyyy-MM-dd")
            self.completion_date_edit.setDate(completion_date)
        
        self.total_value_spin.setValue(self.order['total_value'])
        
        # Forma de pagamento
        index = self.payment_method_combo.findText(self.order['payment_method'])
        if index >= 0:
            self.payment_method_combo.setCurrentIndex(index)
        
        # Carregar peças da ordem
        if 'parts' in self.order and self.order['parts']:
            self.selected_parts = self.order['parts']
            self.update_parts_table()
        
        # Carregar assinaturas
        if self.order.get('client_signature'):
            self.client_signature.set_signature_from_base64(self.order['client_signature'])
        
        if self.order.get('mechanic_signature'):
            self.mechanic_signature.set_signature_from_base64(self.order['mechanic_signature'])
    
    def add_part_to_order(self):
        """Adiciona uma peça à ordem de serviço"""
        if self.part_combo.currentIndex() < 0:
            return
        
        part_id = self.part_combo.currentData()
        quantity = self.quantity_spin.value()
        
        # Encontrar a peça selecionada
        part = None
        for p in self.parts:
            if p['id'] == part_id:
                part = p
                break
        
        if not part:
            return
        
        # Verificar se a peça já está na lista
        for i, selected_part in enumerate(self.selected_parts):
            if selected_part['part_id'] == part_id:
                # Atualizar quantidade
                self.selected_parts[i]['quantity'] += quantity
                self.update_parts_table()
                return
        
        # Adicionar nova peça
        self.selected_parts.append({
            'part_id': part_id,
            'code': part['code'],
            'description': part['description'],
            'quantity': quantity,
            'price': part['sell_price']
        })
        
        self.update_parts_table()
    
    def remove_part_from_order(self):
        """Remove uma peça da ordem de serviço"""
        selected_rows = self.parts_table.selectedIndexes()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if 0 <= row < len(self.selected_parts):
            del self.selected_parts[row]
            self.update_parts_table()
    
    def update_parts_table(self):
        """Atualiza a tabela de peças"""
        self.parts_table.setRowCount(len(self.selected_parts))
        
        total = 0
        for row, part in enumerate(self.selected_parts):
            self.parts_table.setItem(row, 0, QTableWidgetItem(part['code']))
            self.parts_table.setItem(row, 1, QTableWidgetItem(part['description']))
            self.parts_table.setItem(row, 2, QTableWidgetItem(str(part['quantity'])))
            self.parts_table.setItem(row, 3, QTableWidgetItem(f"R$ {part['price']:.2f}"))
            
            subtotal = part['quantity'] * part['price']
            total += subtotal
            
            self.parts_table.setItem(row, 4, QTableWidgetItem(f"R$ {subtotal:.2f}"))
        
        # Atualizar o valor total
        self.total_value_spin.setValue(total)
    
    def save_order(self):
        """Salva a ordem de serviço no banco de dados"""
        # Validar campos
        if not self.validate_form():
            return
        
        try:
            # Preparar dados da ordem
            order_data = {
                'number': self.number_edit.text().strip(),
                'open_date': self.open_date_edit.date().toString("yyyy-MM-dd"),
                'vehicle_id': self.vehicle_combo.currentData(),
                'description': self.description_edit.toPlainText().strip(),
                'status': self.status_combo.currentText(),
                'employee_id': self.employee_combo.currentData(),
                'total_value': self.total_value_spin.value(),
                'payment_method': self.payment_method_combo.currentText()
            }
            
            # Data de conclusão (apenas se não for "em andamento")
            if order_data['status'] != "em andamento":
                order_data['completion_date'] = self.completion_date_edit.date().toString("yyyy-MM-dd")
            
            # Peças
            order_data['parts'] = self.selected_parts
            
            # Assinaturas
            if self.client_signature.has_signature():
                order_data['client_signature'] = self.client_signature.get_signature_base64()
            
            if self.mechanic_signature.has_signature():
                order_data['mechanic_signature'] = self.mechanic_signature.get_signature_base64()
            
            if self.order:
                # Atualizar ordem existente
                success = self.service_order_controller.update_order(self.order['id'], order_data)
                message = "Ordem de serviço atualizada com sucesso!"
            else:
                # Inserir nova ordem
                order_id = self.service_order_controller.add_order(order_data)
                success = order_id is not None
                message = "Ordem de serviço adicionada com sucesso!"
            
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível salvar a ordem de serviço.")
                
        except Exception as e:
            logger.error(f"Erro ao salvar ordem de serviço: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar a ordem de serviço: {str(e)}")
    
    def validate_form(self):
        """Valida os campos do formulário"""
        if not self.number_edit.text().strip():
            QMessageBox.warning(self, "Validação", "Informe o número da ordem de serviço.")
            return False
        
        if self.vehicle_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validação", "Selecione um veículo.")
            return False
        
        if not self.description_edit.toPlainText().strip():
            QMessageBox.warning(self, "Validação", "Informe a descrição dos serviços.")
            return False
        
        if self.employee_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validação", "Selecione um funcionário responsável.")
            return False
        
        return True