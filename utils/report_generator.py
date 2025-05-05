import os
import logging
import tempfile
from datetime import datetime
import pdfkit
import shutil
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from jinja2 import Template
from config import Config

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Clase para generar informes PDF de diagnósticos"""
    
    def __init__(self):
        """Inicializa el generador de informes"""
        self.reports_dir = Config.UPLOAD_FOLDER
        
        # Asegurar que el directorio existe
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Configurar estilos para ReportLab
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()
        
        # Verificar si wkhtmltopdf está instalado
        self.has_wkhtmltopdf = self._check_wkhtmltopdf()
    
    def _check_wkhtmltopdf(self):
        """Verifica si wkhtmltopdf está instalado en el sistema."""
        logger.info("Verificando instalación de wkhtmltopdf")
        wkhtmltopdf_path = None
        
        # Buscar en PATH
        try:
            wkhtmltopdf_path = shutil.which('wkhtmltopdf')
            if wkhtmltopdf_path:
                logger.info(f"wkhtmltopdf encontrado en: {wkhtmltopdf_path}")
                return True
        except Exception as e:
            logger.warning(f"Error al buscar wkhtmltopdf en PATH: {str(e)}")
        
        # Intentar ejecutar para verificar
        try:
            result = subprocess.run(['wkhtmltopdf', '--version'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            if result.returncode == 0:
                logger.info(f"wkhtmltopdf encontrado, versión: {result.stdout.strip()}")
                return True
            else:
                logger.warning(f"wkhtmltopdf encontrado pero con error: {result.stderr}")
        except Exception as e:
            logger.warning(f"wkhtmltopdf no está disponible: {str(e)}")
            logger.info("Se usará ReportLab como alternativa para generar PDFs")
        
        return False
    
    def generate_pdf(self, diagnostico_data, diagnostico_id):
        """
        Genera un informe PDF con el diagnóstico.
        
        Args:
            diagnostico_data (dict): Datos del diagnóstico
            diagnostico_id (str): ID del diagnóstico
            
        Returns:
            str: Ruta al archivo PDF generado
        """
        try:
            # Definir ruta del archivo
            pdf_path = os.path.join(self.reports_dir, f"diagnostico_{diagnostico_id}.pdf")
            
            # Intentar generar con pdfkit si está disponible
            if self.has_wkhtmltopdf:
                logger.info("Generando PDF con pdfkit (wkhtmltopdf)")
                success = self._generate_with_pdfkit(diagnostico_data, pdf_path)
                if success:
                    return pdf_path
                else:
                    logger.warning("Fallback a ReportLab después de error con pdfkit")
            
            # Generar con ReportLab si pdfkit no está disponible o falló
            logger.info("Generando PDF con ReportLab")
            success = self._generate_with_reportlab(diagnostico_data, pdf_path)
            
            if success:
                logger.info(f"Informe PDF generado: {pdf_path}")
                return pdf_path
            else:
                logger.error("Error al generar el PDF con ambos métodos")
                return None
            
        except Exception as e:
            logger.error(f"Error al generar informe PDF: {str(e)}", exc_info=True)
            return None
    
    def _generate_with_pdfkit(self, diagnostico_data, pdf_path):
        """
        Genera un PDF usando pdfkit (wkhtmltopdf)
        
        Args:
            diagnostico_data (dict): Datos del diagnóstico
            pdf_path (str): Ruta de salida para el PDF
            
        Returns:
            bool: True si se generó correctamente, False en caso contrario
        """
        try:
            # Crear HTML para el informe
            html_content = self._create_html_template(diagnostico_data)
            
            # Opciones para pdfkit
            options = {
                'page-size': 'A4',
                'margin-top': '1cm',
                'margin-right': '1cm',
                'margin-bottom': '1cm',
                'margin-left': '1cm',
                'encoding': 'UTF-8',
                'no-outline': None,
                'quiet': ''
            }
            
            # Generar PDF
            pdfkit.from_string(html_content, pdf_path, options=options)
            
            return os.path.exists(pdf_path)
            
        except Exception as e:
            logger.error(f"Error al generar PDF con pdfkit: {str(e)}", exc_info=True)
            return False
    
    def _create_html_template(self, diagnostico_data):
        """
        Crea una plantilla HTML para el informe
        
        Args:
            diagnostico_data (dict): Datos del diagnóstico
            
        Returns:
            str: Contenido HTML del informe
        """
        # Plantilla básica
        html_template = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Diagnóstico de Bienestar</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    padding: 20px;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .title {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2563eb;
                    margin-bottom: 10px;
                }
                .section {
                    margin-bottom: 30px;
                }
                .section-title {
                    font-size: 18px;
                    font-weight: bold;
                    color: #1e40af;
                    margin-bottom: 15px;
                    border-bottom: 1px solid #e5e7eb;
                    padding-bottom: 5px;
                }
                .info-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                .info-table th, .info-table td {
                    padding: 10px;
                    border: 1px solid #e5e7eb;
                }
                .info-table th {
                    background-color: #f3f4f6;
                    text-align: left;
                    width: 30%;
                }
                .diagnostico, .recomendaciones {
                    background-color: #f9fafb;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #2563eb;
                }
                .footer {
                    text-align: center;
                    font-size: 12px;
                    color: #6b7280;
                    margin-top: 40px;
                    padding-top: 10px;
                    border-top: 1px solid #e5e7eb;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">DIAGNÓSTICO DE BIENESTAR</div>
                <div>Fecha: {{ fecha }}</div>
            </div>
            
            <div class="section">
                <div class="section-title">DATOS PERSONALES</div>
                <table class="info-table">
                    <tr>
                        <th>Nombre</th>
                        <td>{{ diagnostico.nombre }} {{ diagnostico.apellido }}</td>
                    </tr>
                    <tr>
                        <th>Edad</th>
                        <td>{{ diagnostico.edad }}</td>
                    </tr>
                    <tr>
                        <th>Género</th>
                        <td>{{ diagnostico.genero }}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">DIAGNÓSTICO</div>
                <div class="diagnostico">
                    {{ diagnostico.diagnostico|replace('\n', '<br>') }}
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">RECOMENDACIONES</div>
                <div class="recomendaciones">
                    {{ diagnostico.recomendaciones|replace('\n', '<br>') }}
                </div>
            </div>
            
            <div class="footer">
                <div>{{ company_name }} - {{ contact_email }} - {{ contact_phone }}</div>
                <div>Este diagnóstico es informativo y no sustituye la consulta con un profesional de la salud.</div>
            </div>
        </body>
        </html>
        """
        
        # Renderizar plantilla con Jinja2
        template = Template(html_template)
        
        # Datos para la plantilla
        context = {
            'fecha': datetime.now().strftime("%d/%m/%Y"),
            'diagnostico': diagnostico_data,
            'company_name': Config.COMPANY_NAME,
            'contact_email': Config.CONTACT_EMAIL,
            'contact_phone': Config.CONTACT_PHONE
        }
        
        return template.render(**context)
    
    def _generate_with_reportlab(self, diagnostico_data, pdf_path):
        """
        Genera un PDF usando ReportLab como alternativa
        
        Args:
            diagnostico_data (dict): Datos del diagnóstico
            pdf_path (str): Ruta de salida para el PDF
            
        Returns:
            bool: True si se generó correctamente, False en caso contrario
        """
        try:
            # Crear documento
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Contenido del documento
            story = []
            
            # Agregar encabezado
            self._agregar_encabezado(story, diagnostico_data)
            
            # Agregar datos personales
            self._agregar_datos_personales(story, diagnostico_data)
            
            # Agregar diagnóstico
            self._agregar_diagnostico(story, diagnostico_data)
            
            # Agregar recomendaciones
            self._agregar_recomendaciones(story, diagnostico_data)
            
            # Agregar pie de página
            self._agregar_pie_pagina(story)
            
            # Construir documento
            doc.build(story)
            
            return os.path.exists(pdf_path)
        
        except Exception as e:
            logger.error(f"Error al generar PDF con ReportLab: {str(e)}", exc_info=True)
            return False
    
    def _configurar_estilos(self):
        """Configura los estilos para el documento PDF"""
        # Estilo para títulos
        self.styles.add(ParagraphStyle(
            name='Titulo',
            parent=self.styles['Heading1'],
            fontSize=18,
            fontName='Helvetica-Bold',
            alignment=1,  # Centro
            spaceAfter=12
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceBefore=12,
            spaceAfter=6
        ))
        
        # Estilo para secciones
        self.styles.add(ParagraphStyle(
            name='Seccion',
            parent=self.styles['Heading3'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceBefore=8,
            spaceAfter=4
        ))
        
        # Estilo para texto normal (modificamos el nombre para evitar conflictos)
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=4,
            spaceAfter=4
        ))
        
        # Estilo para texto resaltado
        self.styles.add(ParagraphStyle(
            name='Resaltado',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            backColor=colors.lightgrey,
            spaceBefore=4,
            spaceAfter=4
        ))
        
        # Estilo para pie de página
        self.styles.add(ParagraphStyle(
            name='PiePagina',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=1,  # Centro
            textColor=colors.darkgrey
        ))
    
    def _agregar_encabezado(self, story, diagnostico_data):
        """Agrega el encabezado al informe"""
        # Logo (placeholder para este ejemplo)
        # logo_path = os.path.join(Config.STATIC_FOLDER, 'img', 'logo.png')
        # if os.path.exists(logo_path):
        #     logo = Image(logo_path, width=150, height=50)
        #     story.append(logo)
        
        # Título
        story.append(Paragraph("DIAGNÓSTICO DE BIENESTAR", self.styles['Titulo']))
        
        # Fecha
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        story.append(Paragraph(f"Fecha: {fecha_actual}", self.styles['TextoNormal']))
        
        # Separador
        story.append(Spacer(1, 20))
    
    def _agregar_datos_personales(self, story, diagnostico_data):
        """Agrega la sección de datos personales al informe"""
        story.append(Paragraph("DATOS PERSONALES", self.styles['Subtitulo']))
        
        # Tabla de datos personales
        datos = [
            ["Nombre", f"{diagnostico_data.get('nombre', '')} {diagnostico_data.get('apellido', '')}"],
            ["Edad", diagnostico_data.get('edad', '')],
            ["Género", diagnostico_data.get('genero', '')]
        ]
        
        t = Table(datos, colWidths=[100, 350])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey)
        ]))
        
        story.append(t)
        story.append(Spacer(1, 15))
    
    def _agregar_diagnostico(self, story, diagnostico_data):
        """Agrega la sección de diagnóstico al informe"""
        story.append(Paragraph("DIAGNÓSTICO", self.styles['Subtitulo']))
        
        # Diagnóstico
        diagnostico_texto = diagnostico_data.get('diagnostico', 'No se generó un diagnóstico.')
        story.append(Paragraph(diagnostico_texto, self.styles['TextoNormal']))
        
        story.append(Spacer(1, 15))
    
    def _agregar_recomendaciones(self, story, diagnostico_data):
        """Agrega la sección de recomendaciones al informe"""
        story.append(Paragraph("RECOMENDACIONES", self.styles['Subtitulo']))
        
        # Recomendaciones
        recomendaciones_texto = diagnostico_data.get('recomendaciones', 'No se generaron recomendaciones específicas.')
        
        # Dividir las recomendaciones en párrafos
        for parrafo in recomendaciones_texto.split('\n\n'):
            if parrafo.strip():
                story.append(Paragraph(parrafo, self.styles['TextoNormal']))
                story.append(Spacer(1, 5))
        
        story.append(Spacer(1, 15))
    
    def _agregar_pie_pagina(self, story):
        """Agrega el pie de página al informe"""
        story.append(Spacer(1, 30))
        
        # Línea de separación
        story.append(Paragraph("_" * 65, self.styles['TextoNormal']))
        
        # Información de contacto
        story.append(Paragraph(
            f"{Config.COMPANY_NAME} - {Config.CONTACT_EMAIL} - {Config.CONTACT_PHONE}",
            self.styles['PiePagina']
        ))
        
        # Nota legal
        story.append(Paragraph(
            "Este diagnóstico es informativo y no sustituye la consulta con un profesional de la salud.",
            self.styles['PiePagina']
        )) 