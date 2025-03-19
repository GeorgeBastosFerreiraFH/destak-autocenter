from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QComboBox, QPushButton, QLabel, 
                            QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDate
import logging
from services.vehicle_api import vehicle_api
from database.db_manager import get_connection
import config

logger = logging.getLogger(config.APP_NAME)

class ApiLoaderThread(QThread):
    """Thread para carregar dados da API sem bloquear a interface"""
    brands_loaded = pyqtSignal(list)
    models_loaded = pyqtSignal(list)
    
    def __init__(self, parent=None, brand_code=None):
        super().__init__(parent)
        self.brand_code = brand_code
    
    def run(self):
        if self.brand_code is None:
            # Carregar marcas
            brands = vehicle_api.get_brands()
            self.brands_loaded.emit(brands)
        else:
            # Carregar modelos para a marca selecionada
            models = vehicle_api.get_models_by_brand(self.brand_code)
            self.models_loaded.emit(models)

class VehicleDialog(QDialog):
    """Diálogo para adicionar ou editar veículos"""
    
    def __init__(self, parent=None, vehicle=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.clients = []
        self.brands = []
        self.models = []
        self.selected_brand_code = None
        self.selected_model_code = None
        
        self.setWindowTitle("Adicionar Veículo" if not vehicle else "Editar Veículo")
        self.setMinimumWidth(500)
        
        self.setup_ui()
        self.load_clients()
        
        # Iniciar carregamento de marcas
        self.brand_loader = ApiLoaderThread(self)
        self.brand_loader.brands_loaded.connect(self.on_brands_loaded)
        self.brand_loader.start()
        
        # Se estiver editando, preencher os campos
        if self.vehicle:
            self.fill_form()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        
        # Cliente
        self.client_combo = QComboBox()
        self.client_combo.setMinimumWidth(300)
        form_layout.addRow("Cliente:", self.client_combo)
        
        # Placa
        self.plate_edit = QLineEdit()
        self.plate_edit.setPlaceholderText("ABC-1234")
        form_layout.addRow("Placa:", self.plate_edit)
        
        # Marca
        self.brand_combo = QComboBox()
        self.brand_combo.setMinimumWidth(300)
        self.brand_combo.setPlaceholderText("Carregando marcas...")
        self.brand_combo.currentIndexChanged.connect(self.on_brand_changed)
        form_layout.addRow("Marca:", self.brand_combo)
        
        # Modelo
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        self.model_combo.setPlaceholderText("Selecione uma marca primeiro")
        self.model_combo.setEnabled(False)
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        form_layout.addRow("Modelo:", self.model_combo)
        
        # Ano
        self.year_edit = QLineEdit()
        self.year_edit.setPlaceholderText("2023")
        form_layout.addRow("Ano:", self.year_edit)
        
        # Cor
        self.color_edit = QLineEdit()
        self.color_edit.setPlaceholderText("Branco, Preto, Prata, etc.")
        form_layout.addRow("Cor:", self.color_edit)
        
        layout.addLayout(form_layout)
        
        # Status da API
        self.api_status = QLabel("Carregando dados da API de veículos...")
        self.api_status.setStyleSheet("color: blue;")
        layout.addWidget(self.api_status)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_vehicle)
        self.save_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_clients(self):
        """Carrega a lista de clientes do banco de dados"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM clients ORDER BY name")
            self.clients = cursor.fetchall()
            conn.close()
            
            self.client_combo.clear()
            for client in self.clients:
                self.client_combo.addItem(client['name'], client['id'])
            
            # Se estiver editando, selecionar o cliente correto
            if self.vehicle:
                index = self.client_combo.findData(self.vehicle['client_id'])
                if index >= 0:
                    self.client_combo.setCurrentIndex(index)
        
        except Exception as e:
            logger.error(f"Erro ao carregar clientes: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar a lista de clientes: {str(e)}")
    
    def on_brands_loaded(self, brands):
        """Callback quando as marcas são carregadas"""
        self.brands = brands
        self.brand_combo.clear()
        
        for brand in brands:
            self.brand_combo.addItem(brand['nome'], brand['codigo'])
        
        self.api_status.setText("Marcas carregadas com sucesso!")
        
        # Se estiver editando, selecionar a marca correta
        if self.vehicle and self.vehicle.get('brand_code'):
            index = self.brand_combo.findData(self.vehicle['brand_code'])
            if index >= 0:
                self.brand_combo.setCurrentIndex(index)
    
    def on_brand_changed(self, index):
        """Callback quando a marca é alterada"""
        if index < 0:
            return
        
        self.selected_brand_code = self.brand_combo.itemData(index)
        self.model_combo.clear()
        self.model_combo.setEnabled(False)
        self.model_combo.setPlaceholderText("Carregando modelos...")
        self.api_status.setText(f"Carregando modelos para {self.brand_combo.currentText()}...")
        
        # Carregar modelos para a marca selecionada
        self.model_loader = ApiLoaderThread(self, self.selected_brand_code)
        self.model_loader.models_loaded.connect(self.on_models_loaded)
        self.model_loader.start()
    
    def on_models_loaded(self, models):
        """Callback quando os modelos são carregados"""
        self.models = models
        self.model_combo.clear()
        self.model_combo.setEnabled(True)
        
        for model in models:
            self.model_combo.addItem(model['nome'], model['codigo'])
        
        self.api_status.setText(f"Modelos carregados para {self.brand_combo.currentText()}")
        
        # Se estiver editando, selecionar o modelo correto
        if self.vehicle and self.vehicle.get('model_code'):
            index = self.model_combo.findData(self.vehicle['model_code'])
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
    
    def on_model_changed(self, index):
        """Callback quando o modelo é alterado"""
        if index < 0:
            return
        
        self.selected_model_code = self.model_combo.itemData(index)
    
    def fill_form(self):
        """Preenche o formulário com os dados do veículo"""
        self.plate_edit.setText(self.vehicle['plate'])
        self.year_edit.setText(str(self.vehicle['year']))
        self.color_edit.setText(self.vehicle['color'])
        
        # Cliente, marca e modelo são preenchidos nos respectivos métodos de carregamento
    
    def save_vehicle(self):
        """Salva o veículo no banco de dados"""
        # Validar campos
        if not self.validate_form():
            return
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            client_id = self.client_combo.currentData()
            plate = self.plate_edit.text().strip()
            brand = self.brand_combo.currentText()
            model = self.model_combo.currentText()
            year = int(self.year_edit.text())
            color = self.color_edit.text().strip()
            brand_code = self.selected_brand_code
            model_code = self.selected_model_code
            
            if self.vehicle:
                # Atualizar veículo existente
                cursor.execute('''
                UPDATE vehicles 
                SET plate = ?, brand = ?, model = ?, year = ?, color = ?, client_id = ?, brand_code = ?, model_code = ?
                WHERE id = ?
                ''', (plate, brand, model, year, color, client_id, brand_code, model_code, self.vehicle['id']))
                
                message = "Veículo atualizado com sucesso!"
            else:
                # Inserir novo veículo
                cursor.execute('''
                INSERT INTO vehicles (plate, brand, model, year, color, client_id, brand_code, model_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (plate, brand, model, year, color, client_id, brand_code, model_code))
                
                message = "Veículo adicionado com sucesso!"
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Sucesso", message)
            self.accept()
            
        except Exception as e:
            logger.error(f"Erro ao salvar veículo: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar o veículo: {str(e)}")
    
    def validate_form(self):
        """Valida os campos do formulário"""
        if self.client_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validação", "Selecione um cliente.")
            return False
        
        if not self.plate_edit.text().strip():
            QMessageBox.warning(self, "Validação", "Informe a placa do veículo.")
            return False
        
        if self.brand_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validação", "Selecione uma marca.")
            return False
        
        if self.model_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validação", "Selecione um modelo.")
            return False
        
        try:
            year = int(self.year_edit.text())
            current_year = QDate.currentDate().year()
            if year < 1900 or year > current_year + 1:
                QMessageBox.warning(self, "Validação", f"O ano deve estar entre 1900 e {current_year + 1}.")
                return False
        except ValueError:
            QMessageBox.warning(self, "Validação", "Informe um ano válido.")
            return False
        
        if not self.color_edit.text().strip():
            QMessageBox.warning(self, "Validação", "Informe a cor do veículo.")
            return False
        
        return True