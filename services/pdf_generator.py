import logging
import os
import base64
import tempfile
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
import config

logger = logging.getLogger(config.APP_NAME)

# Registrar fontes
try:
    # Tentar registrar fontes padrão
    pdfmetrics.registerFont(TTFont('Roboto', os.path.join(config.RESOURCES_DIR, 'fonts', 'Roboto-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Roboto-Bold', os.path.join(config.RESOURCES_DIR, 'fonts', 'Roboto-Bold.ttf')))
except Exception as e:
    logger.warning(f"Não foi possível registrar fontes personalizadas: {str(e)}")
    logger.warning("Usando fontes padrão do ReportLab")

def generate_service_order_pdf(order, output_path):
    """Gera um PDF para uma ordem de serviço"""
    try:
        # Configurar documento
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Title',
            fontName='Helvetica-Bold',
            fontSize=16,
            alignment=1,  # Centralizado
            spaceAfter=12
        ))
        styles.add(ParagraphStyle(
            name='Heading2',
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=6
        ))
        styles.add(ParagraphStyle(
            name='Normal',
            fontName='Helvetica',
            fontSize=12,
            spaceAfter=6
        ))
        
        # Elementos do documento
        elements = []
        
        # Cabeçalho
        elements.append(Paragraph("AUTO REPAIR SHOP", styles['Title']))
        elements.append(Paragraph("CNPJ: 00.000.000/0001-00", styles['Normal']))
        elements.append(Paragraph("Rua Exemplo, 123 - Cidade - Estado", styles['Normal']))
        elements.append(Paragraph("Tel: (00) 0000-0000", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Título da OS
        elements.append(Paragraph(f"ORDEM DE SERVIÇO Nº {order['number']}", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Informações básicas
        data = [
            ["Data de Abertura:", order['open_date'].split()[0]],
            ["Status:", order['status']]
        ]
        
        if order['status'] != "em andamento" and order.get('completion_date'):
            data.append(["Data de Conclusão:", order['completion_date'].split()[0]])
        
        table = Table(data, colWidths=[150, 300])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        
        # Informações de pagamento
        data = [
            ["Forma de Pagamento:", order['payment_method']],
            ["Valor Total:", f"R$ {order['total_value']:.2f}"]
        ]
        
        table = Table(data, colWidths=[150, 300])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        
        # Dados do veículo
        elements.append(Paragraph("DADOS DO VEÍCULO", styles['Heading2']))
        
        if order.get('vehicle_plate'):
            data = [
                ["Placa:", order['vehicle_plate']],
                ["Cliente:", order.get('client_name', 'N/A')]
            ]
            
            table = Table(data, colWidths=[150, 300])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Veículo não encontrado", styles['Normal']))
        
        elements.append(Spacer(1, 12))
        
        # Descrição dos serviços
        elements.append(Paragraph("DESCRIÇÃO DOS SERVIÇOS", styles['Heading2']))
        elements.append(Paragraph(order['description'], styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Peças utilizadas
        elements.append(Paragraph("PEÇAS UTILIZADAS", styles['Heading2']))
        
        if 'parts' in order and order['parts']:
            # Cabeçalho da tabela
            data = [["Código", "Descrição", "Quantidade", "Valor Unit.", "Subtotal"]]
            
            # Dados das peças
            total_parts = 0
            for part in order['parts']:
                subtotal = part['quantity'] * part['price']
                total_parts += subtotal
                data.append([
                    part['code'],
                    part['description'],
                    str(part['quantity']),
                    f"R$ {part['price']:.2f}",
                    f"R$ {subtotal:.2f}"
                ])
            
            # Linha de total
            data.append(["", "", "", "Total Peças:", f"R$ {total_parts:.2f}"])
            
            # Criar tabela
            table = Table(data, colWidths=[60, 200, 70, 80, 80])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Nenhuma peça utilizada", styles['Normal']))
        
        elements.append(Spacer(1, 12))
        
        # Resumo financeiro
        elements.append(Paragraph("RESUMO FINANCEIRO", styles['Heading2']))
        
        total_parts = 0
        if 'parts' in order and order['parts']:
            for part in order['parts']:
                total_parts += part['quantity'] * part['price']
        
        labor_cost = order['total_value'] - total_parts
        
        data = [
            ["Total Peças:", f"R$ {total_parts:.2f}"],
            ["Mão de Obra:", f"R$ {labor_cost:.2f}"],
            ["Valor Total:", f"R$ {order['total_value']:.2f}"]
        ]
        
        table = Table(data, colWidths=[150, 300])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        
        # Responsáveis
        elements.append(Paragraph("RESPONSÁVEIS", styles['Heading2']))
        elements.append(Paragraph(f"Mecânico Responsável: {order.get('employee_name', 'N/A')}", styles['Normal']))
        elements.append(Spacer(1, 24))
        
        # Assinaturas
        signature_data = []
        
        # Assinatura do cliente
        if order.get('client_signature'):
            try:
                # Converter base64 para imagem
                img_data = base64.b64decode(order['client_signature'])
                img_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                img_temp.write(img_data)
                img_temp.close()
                
                # Redimensionar imagem
                img = PILImage.open(img_temp.name)
                img = img.resize((200, 100), PILImage.LANCZOS)
                img_resized = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                img.save(img_resized.name)
                
                # Adicionar à tabela
                signature_data.append([Image(img_resized.name, width=200, height=100), Image(img_resized.name, width=200, height=100)])
                signature_data.append(["Assinatura do Cliente", "Assinatura do Mecânico"])
                
                # Limpar arquivos temporários
                os.unlink(img_temp.name)
                os.unlink(img_resized.name)
            except Exception as e:
                logger.error(f"Erro ao processar assinaturas: {str(e)}")
                signature_data.append(["________________", "________________"])
                signature_data.append(["Assinatura do Cliente", "Assinatura do Mecânico"])
        else:
            signature_data.append(["________________", "________________"])
            signature_data.append(["Assinatura do Cliente", "Assinatura do Mecânico"])
        
        # Tabela de assinaturas
        table = Table(signature_data, colWidths=[250, 250])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        
        # Rodapé
        elements.append(Spacer(1, 36))
        elements.append(Paragraph("Este documento é um comprovante de serviço prestado.", styles['Normal']))
        elements.append(Paragraph("Auto Repair Shop - Todos os direitos reservados.", styles['Normal']))
        
        # Gerar PDF
        doc.build(elements)
        
        logger.info(f"PDF gerado com sucesso: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
        return False