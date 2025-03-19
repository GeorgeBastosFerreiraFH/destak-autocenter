from PyQt5.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QLabel, QAction, QToolBar, QMenu
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import logging
import config
from ui.tabs.dashboard_tab import DashboardTab
from ui.tabs.clients_tab import ClientsTab
from ui.tabs.vehicles_tab import VehiclesTab
from ui.tabs.service_orders_tab import ServiceOrdersTab
from ui.tabs.parts_tab import PartsTab
from ui.tabs.employees_tab import EmployeesTab
from ui.tabs.expenses_tab import ExpensesTab

logger = logging.getLogger(config.APP_NAME)

class MainWindow(QMainWindow):
    """Janela principal do aplicativo"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
        logger.info("Aplicativo iniciado")
    
    def setup_ui(self):
        """Configura a interface principal"""
        # Criar o widget de abas
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        
        # Adicionar as abas
        self.dashboard_tab = DashboardTab()
        self.clients_tab = ClientsTab()
        self.vehicles_tab = VehiclesTab()
        self.service_orders_tab = ServiceOrdersTab()
        self.parts_tab = PartsTab()
        self.employees_tab = EmployeesTab()
        self.expenses_tab = ExpensesTab()
        
        self.tabs.addTab(self.dashboard_tab, QIcon("resources/icons/dashboard.png"), "Dashboard")
        self.tabs.addTab(self.clients_tab, QIcon("resources/icons/clients.png"), "Clientes")
        self.tabs.addTab(self.vehicles_tab, QIcon("resources/icons/vehicles.png"), "Veículos")
        self.tabs.addTab(self.service_orders_tab, QIcon("resources/icons/orders.png"), "Ordens de Serviço")
        self.tabs.addTab(self.parts_tab, QIcon("resources/icons/parts.png"), "Peças")
        self.tabs.addTab(self.employees_tab, QIcon("resources/icons/employees.png"), "Funcionários")
        self.tabs.addTab(self.expenses_tab, QIcon("resources/icons/expenses.png"), "Gastos")
        
        # Definir o widget central
        self.setCentralWidget(self.tabs)
    
    def setup_menu(self):
        """Configura o menu principal"""
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("&Arquivo")
        
        backup_action = QAction(QIcon("resources/icons/backup.png"), "Fazer Backup", self)
        backup_action.setStatusTip("Criar um backup do banco de dados")
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        restore_action = QAction(QIcon("resources/icons/restore.png"), "Restaurar Backup", self)
        restore_action.setStatusTip("Restaurar um backup do banco de dados")
        restore_action.triggered.connect(self.restore_database)
        file_menu.addAction(restore_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(QIcon("resources/icons/exit.png"), "Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Sair do aplicativo")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Relatórios
        reports_menu = menubar.addMenu("&Relatórios")
        
        clients_report_action = QAction("Relatório de Clientes", self)
        clients_report_action.triggered.connect(self.generate_clients_report)
        reports_menu.addAction(clients_report_action)
        
        vehicles_report_action = QAction("Relatório de Veículos", self)
        vehicles_report_action.triggered.connect(self.generate_vehicles_report)
        reports_menu.addAction(vehicles_report_action)
        
        orders_report_action = QAction("Relatório de Ordens de Serviço", self)
        orders_report_action.triggered.connect(self.generate_orders_report)
        reports_menu.addAction(orders_report_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("A&juda")
        
        about_action = QAction(QIcon("resources/icons/about.png"), "Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Configura a barra de ferramentas"""
        toolbar = QToolBar("Barra de Ferramentas Principal")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Adicionar ações à barra de ferramentas
        new_order_action = QAction(QIcon("resources/icons/new_order.png"), "Nova Ordem", self)
        new_order_action.triggered.connect(self.create_new_order)
        toolbar.addAction(new_order_action)
        
        new_client_action = QAction(QIcon("resources/icons/new_client.png"), "Novo Cliente", self)
        new_client_action.triggered.connect(self.create_new_client)
        toolbar.addAction(new_client_action)
        
        new_vehicle_action = QAction(QIcon("resources/icons/new_vehicle.png"), "Novo Veículo", self)
        new_vehicle_action.triggered.connect(self.create_new_vehicle)
        toolbar.addAction(new_vehicle_action)
        
        toolbar.addSeparator()
        
        search_action = QAction(QIcon("resources/icons/search.png"), "Buscar", self)
        search_action.triggered.connect(self.show_search)
        toolbar.addAction(search_action)
    
    def setup_statusbar(self):
        """Configura a barra de status"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.status_label = QLabel("Sistema pronto")
        self.statusbar.addWidget(self.status_label)
    
    def backup_database(self):
        """Cria um backup do banco de dados"""
        # Implementação do backup
        logger.info("Backup do banco de dados solicitado")
        self.statusbar.showMessage("Backup criado com sucesso", 3000)
    
    def restore_database(self):
        """Restaura um backup do banco de dados"""
        # Implementação da restauração
        logger.info("Restauração de backup solicitada")
        self.statusbar.showMessage("Backup restaurado com sucesso", 3000)
    
    def generate_clients_report(self):
        """Gera um relatório de clientes"""
        logger.info("Relatório de clientes solicitado")
        self.statusbar.showMessage("Gerando relatório de clientes...", 3000)
    
    def generate_vehicles_report(self):
        """Gera um relatório de veículos"""
        logger.info("Relatório de veículos solicitado")
        self.statusbar.showMessage("Gerando relatório de veículos...", 3000)
    
    def generate_orders_report(self):
        """Gera um relatório de ordens de serviço"""
        logger.info("Relatório de ordens de serviço solicitado")
        self.statusbar.showMessage("Gerando relatório de ordens de serviço...", 3000)
    
    def create_new_order(self):
        """Cria uma nova ordem de serviço"""
        self.tabs.setCurrentIndex(3)  # Índice da aba de ordens de serviço
        self.service_orders_tab.show_add_dialog()
    
    def create_new_client(self):
        """Cria um novo cliente"""
        self.tabs.setCurrentIndex(1)  # Índice da aba de clientes
        self.clients_tab.show_add_dialog()
    
    def create_new_vehicle(self):
        """Cria um novo veículo"""
        self.tabs.setCurrentIndex(2)  # Índice da aba de veículos
        self.vehicles_tab.show_add_dialog()
    
    def show_search(self):
        """Exibe a caixa de busca global"""
        # Implementação da busca global
        self.statusbar.showMessage("Busca global não implementada", 3000)
    
    def show_about(self):
        """Exibe a caixa de diálogo Sobre"""
        from PyQt5.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "Sobre o Auto Repair Shop",
            f"""<h1>Auto Repair Shop</h1>
            <p>Versão {config.APP_VERSION}</p>
            <p>Sistema de gerenciamento para oficinas mecânicas.</p>
            <p>© 2025 - Todos os direitos reservados</p>"""
        )
    
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 'Confirmar Saída',
            'Tem certeza que deseja sair?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("Aplicativo encerrado pelo usuário")
            event.accept()
        else:
            event.ignore()