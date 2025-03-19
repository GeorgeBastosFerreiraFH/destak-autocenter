# ui/dialogs/client_dialog.py
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                            QPushButton, QLabel, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt
from controllers.client_controller import ClientController

class ClientDialog(QDialog):
    def __init__(self, parent=None, client_id=None):
        super().__init__(parent)
        self.client_id = client_id
        self.client_controller = ClientController()
        self.init_ui()
        
        if client_id:
            self.setWindowTitle("Editar Cliente")
            self.load_client_data()
        else:
            self.setWindowTitle("Novo Cliente")
    
    def init_ui(self):
        self.setMinimumWidth(400)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Form layout para os campos
        form_layout = QFormLayout()
        
        # Campos de entrada
        self.name_input = QLineEdit()
        self.document_input = QLineEdit()
        self.address_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        
        # Adicionar campos ao form layout
        form_layout.addRow("Nome:", self.name_input)
        form_layout.addRow("CPF/CNPJ:", self.document_input)
        form_layout.addRow("Endereço:", self.address_input)
        form_layout.addRow("Telefone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        
        # Adicionar form layout ao layout principal
        layout.addLayout(form_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_client)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_client_data(self):
        """Carrega os dados do cliente para edição"""
        if not self.client_id:
            return
            
        client = self.client_controller.get_client(self.client_id)
        if client:
            self.name_input.setText(client['name'])
            self.document_input.setText(client['document'])
            self.address_input.setText(client['address'] if client['address'] else "")
            self.phone_input.setText(client['phone'])
            self.email_input.setText(client['email'] if client['email'] else "")
    
    def validate_inputs(self):
        """Valida os campos de entrada"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validação", "O nome é obrigatório.")
            return False
            
        if not self.document_input.text().strip():
            QMessageBox.warning(self, "Validação", "O CPF/CNPJ é obrigatório.")
            return False
            
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "Validação", "O telefone é obrigatório.")
            return False
            
        return True
    
    def save_client(self):
        """Salva os dados do cliente"""
        if not self.validate_inputs():
            return
            
        client_data = {
            'name': self.name_input.text().strip(),
            'document': self.document_input.text().strip(),
            'address': self.address_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'email': self.email_input.text().strip()
        }
        
        try:
            if self.client_id:
                # Atualizar cliente existente
                success = self.client_controller.update_client(self.client_id, client_data)
                message = "Cliente atualizado com sucesso!"
            else:
                # Adicionar novo cliente
                success = self.client_controller.add_client(client_data)
                message = "Cliente adicionado com sucesso!"
                
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.accept()  # Fecha o diálogo com status de aceitação
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível salvar o cliente.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar cliente: {str(e)}")