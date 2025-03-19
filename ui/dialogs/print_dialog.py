from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QScrollArea, QWidget, QMessageBox)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
import logging
import os
import tempfile
from services.pdf_generator import generate_service_order_pdf
from controllers.service_order_controller import ServiceOrderController
from ui.widgets.signature_widget import SignatureWidget
import config

logger = logging.getLogger(config.APP_NAME)

class PrintDialog(QDialog):
    """Diálogo para impressão de ordens de serviço"""
    
    def __init__(self, parent=None, order_id=None):
        super().__init__(parent)
        self.order_id = order_id
        self.order = None
        self.service_order_controller = ServiceOrderController()
        self.pdf_path = None
        
        self.setWindowTitle("Imprimir Ordem de Serviço")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.setup_ui()
        
        if self.order_id:
            self.load_order()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Área de visualização
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # Assinaturas
        signatures_layout = QHBoxLayout()
        
        # Assinatura do cliente
        self.client_signature = SignatureWidget(title="Assinatura do Cliente")
        signatures_layout.addWidget(self.client_signature)
        
        # Assinatura do mecânico
        self.mechanic_signature = SignatureWidget(title="Assinatura do Mecânico")
        signatures_layout.addWidget(self.mechanic_signature)
        
        layout.addLayout(signatures_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.reject)
        
        self.save_signatures_button = QPushButton("Salvar Assinaturas")
        self.save_signatures_button.clicked.connect(self.save_signatures)
        
        self.print_button = QPushButton("Imprimir")
        self.print_button.clicked.connect(self.print_order)
        
        self.preview_button = QPushButton("Visualizar Impressão")
        self.preview_button.clicked.connect(self.preview_print)
        
        self.save_pdf_button = QPushButton("Salvar como PDF")
        self.save_pdf_button.clicked.connect(self.save_as_pdf)
        
        button_layout.addWidget(self.close_button)
        button_layout.addWidget(self.save_signatures_button)
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.print_button)
        button_layout.addWidget(self.save_pdf_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_order(self):
        """Carrega os dados da ordem de serviço"""
        try:
            self.order = self.service_order_controller.get_order_by_id(self.order_id)
            
            if not self.order:
                QMessageBox.critical(self, "Erro", "Ordem de serviço não encontrada.")
                self.reject()
                return
            
            # Preencher o conteúdo
            self.fill_content()
            
            # Carregar assinaturas existentes
            if self.order.get('client_signature'):
                self.client_signature.set_signature_from_base64(self.order['client_signature'])
            
            if self.order.get('mechanic_signature'):
                self.mechanic_signature.set_signature_from_base64(self.order['mechanic_signature'])
            
        except Exception as e:
            logger.error(f"Erro ao carregar ordem de serviço: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível carregar a ordem de serviço: {str(e)}")
            self.reject()
    
    def fill_content(self):
        """Preenche o conteúdo da visualização"""
        if not self.order:
            return
        
        # Limpar layout existente
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Título
        title = QLabel(f"<h1>Ordem de Serviço #{self.order['number']}</h1>")
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        
        # Informações básicas
        info_label = QLabel(f"""
        <div style='font-size: 14px; margin: 10px;'>
            <p><b>Data de Abertura:</b> {self.order['open_date'].split()[0]}</p>
            <p><b>Status:</b> {self.order['status']}</p>
            <p><b>Veículo:</b> {self.order.get('vehicle_plate', 'N/A')}</p>
            <p><b>Cliente:</b> {self.order.get('client_name', 'N/A')}</p>
            <p><b>Funcionário:</b> {self.order.get('employee_name', 'N/A')}</p>
            <p><b>Descrição:</b> {self.order['description']}</p>
            <p><b>Valor Total:</b> R$ {self.order['total_value']:.2f}</p>
            <p><b>Forma de Pagamento:</b> {self.order['payment_method']}</p>
        </div>
        """)
        
        self.content_layout.addWidget(info_label)
        
        # Peças utilizadas
        if 'parts' in self.order and self.order['parts']:
            parts_html = "<h2>Peças Utilizadas</h2>"
            parts_html += "<table border='1' cellspacing='0' cellpadding='5' width='100%'>"
            parts_html += "<tr><th>Código</th><th>Descrição</th><th>Quantidade</th><th>Valor Unit.</th><th>Subtotal</th></tr>"
            
            total_parts = 0
            for part in self.order['parts']:
                subtotal = part['quantity'] * part['price']
                total_parts += subtotal
                parts_html += f"<tr><td>{part['code']}</td><td>{part['description']}</td><td>{part['quantity']}</td><td>R$ {part['price']:.2f}</td><td>R$ {subtotal:.2f}</td></tr>"
            
            parts_html += f"<tr><td colspan='4' align='right'><b>Total Peças:</b></td><td>R$ {total_parts:.2f}</td></tr>"
            parts_html += "</table>"
            
            parts_label = QLabel(parts_html)
            self.content_layout.addWidget(parts_label)
        
        # Espaço para assinaturas
        signatures_label = QLabel("<h2>Assinaturas</h2>")
        signatures_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(signatures_label)
    
    def save_signatures(self):
        """Salva as assinaturas na ordem de serviço"""
        if not self.order:
            return
        
        try:
            order_data = {}
            
            if self.client_signature.has_signature():
                order_data['client_signature'] = self.client_signature.get_signature_base64()
            
            if self.mechanic_signature.has_signature():
                order_data['mechanic_signature'] = self.mechanic_signature.get_signature_base64()
            
            if order_data:
                success = self.service_order_controller.update_order(self.order['id'], order_data)
                
                if success:
                    QMessageBox.information(self, "Sucesso", "Assinaturas salvas com sucesso!")
                else:
                    QMessageBox.critical(self, "Erro", "Não foi possível salvar as assinaturas.")
            else:
                QMessageBox.warning(self, "Aviso", "Nenhuma assinatura para salvar.")
                
        except Exception as e:
            logger.error(f"Erro ao salvar assinaturas: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar as assinaturas: {str(e)}")
    
    def generate_pdf(self):
        """Gera o PDF da ordem de serviço"""
        if not self.order:
            return None
        
        try:
            # Atualizar assinaturas no objeto da ordem
            if self.client_signature.has_signature():
                self.order['client_signature'] = self.client_signature.get_signature_base64()
            
            if self.mechanic_signature.has_signature():
                self.order['mechanic_signature'] = self.mechanic_signature.get_signature_base64()
            
            # Gerar PDF em arquivo temporário
            fd, path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            
            generate_service_order_pdf(self.order, path)
            
            self.pdf_path = path
            return path
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível gerar o PDF: {str(e)}")
            return None
    
    def print_order(self):
        """Imprime a ordem de serviço"""
        pdf_path = self.generate_pdf()
        if not pdf_path:
            return
        
        try:
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec_() == QPrintDialog.Accepted:
                from PyQt5.QtPdf import QPdfDocument
                
                document = QPdfDocument()
                document.load(pdf_path)
                
                # Imprimir todas as páginas
                for i in range(document.pageCount()):
                    page = document.render(i, printer.pageRect().size())
                    painter = QPainter(printer)
                    painter.drawImage(0, 0, page)
                    
                    if i < document.pageCount() - 1:
                        printer.newPage()
                    
                    painter.end()
                
                QMessageBox.information(self, "Sucesso", "Documento enviado para impressão!")
                
        except Exception as e:
            logger.error(f"Erro ao imprimir: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível imprimir: {str(e)}")
    
    def preview_print(self):
        """Mostra a visualização de impressão"""
        pdf_path = self.generate_pdf()
        if not pdf_path:
            return
        
        try:
            printer = QPrinter(QPrinter.HighResolution)
            preview = QPrintPreviewDialog(printer, self)
            preview.paintRequested.connect(self.on_preview_paint)
            preview.exec_()
            
        except Exception as e:
            logger.error(f"Erro na visualização de impressão: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível mostrar a visualização: {str(e)}")
    
    def on_preview_paint(self, printer):
        """Callback para pintar a visualização de impressão"""
        if not self.pdf_path:
            return
        
        try:
            from PyQt5.QtPdf import QPdfDocument
            from PyQt5.QtGui import QPainter
            
            document = QPdfDocument()
            document.load(self.pdf_path)
            
            # Pintar todas as páginas
            for i in range(document.pageCount()):
                page = document.render(i, printer.pageRect().size())
                painter = QPainter(printer)
                painter.drawImage(0, 0, page)
                
                if i < document.pageCount() - 1:
                    printer.newPage()
                
                painter.end()
                
        except Exception as e:
            logger.error(f"Erro ao pintar visualização: {str(e)}")
    
    def save_as_pdf(self):
        """Salva a ordem de serviço como PDF"""
        from PyQt5.QtWidgets import QFileDialog
        
        pdf_path = self.generate_pdf()
        if not pdf_path:
            return
        
        try:
            file_name = f"Ordem_de_Servico_{self.order['number']}.pdf"
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar PDF", file_name, "Arquivos PDF (*.pdf)"
            )
            
            if save_path:
                # Copiar o arquivo temporário para o destino escolhido
                import shutil
                shutil.copy2(pdf_path, save_path)
                
                QMessageBox.information(self, "Sucesso", f"PDF salvo em:\n{save_path}")
                
                # Perguntar se deseja abrir o arquivo
                reply = QMessageBox.question(
                    self, "Abrir PDF", "Deseja abrir o arquivo PDF?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(save_path))
                
        except Exception as e:
            logger.error(f"Erro ao salvar PDF: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar o PDF: {str(e)}")