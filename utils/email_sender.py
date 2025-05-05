import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from config import Config

logger = logging.getLogger(__name__)

class EmailSender:
    """Clase para enviar correos electrónicos con diagnósticos"""
    
    def __init__(self):
        """Inicializa el servicio de correo electrónico"""
        self.smtp_server = Config.MAIL_SERVER
        self.smtp_port = Config.MAIL_PORT
        self.smtp_user = Config.MAIL_USERNAME
        self.smtp_password = Config.MAIL_PASSWORD
        self.sender_email = Config.MAIL_DEFAULT_SENDER
        self.use_tls = Config.MAIL_USE_TLS
    
    def send_email(self, to_email, subject, nombre, diagnostico_id, pdf_path=None):
        """
        Envía un correo electrónico con el diagnóstico.
        
        Args:
            to_email (str): Dirección de correo electrónico del destinatario
            subject (str): Asunto del correo
            nombre (str): Nombre del destinatario
            diagnostico_id (str): ID del diagnóstico
            pdf_path (str, optional): Ruta al archivo PDF para adjuntar
            
        Returns:
            bool: True si el correo se envió correctamente, False en caso contrario
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = f'"{Config.COMPANY_NAME}" <{self.sender_email}>'
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Cuerpo del mensaje HTML
            html_content = self._generar_plantilla_email(nombre, diagnostico_id)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Adjuntar PDF si existe
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as file:
                    pdf_part = MIMEApplication(file.read(), Name=os.path.basename(pdf_path))
                
                pdf_part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
                msg.attach(pdf_part)
                logger.info(f"PDF adjuntado: {pdf_path}")
            
            # Conectar al servidor SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()
            
            if self.use_tls:
                server.starttls()
                server.ehlo()
            
            # Iniciar sesión
            server.login(self.smtp_user, self.smtp_password)
            
            # Enviar correo
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Correo enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar correo electrónico: {str(e)}", exc_info=True)
            return False
    
    def _generar_plantilla_email(self, nombre, diagnostico_id):
        """
        Genera la plantilla HTML para el correo electrónico.
        
        Args:
            nombre (str): Nombre del destinatario
            diagnostico_id (str): ID del diagnóstico
            
        Returns:
            str: Contenido HTML del correo
        """
        # URL base de la aplicación (ajustar según configuración)
        base_url = os.environ.get('APP_URL', 'http://localhost:5000')
        
        # Crear la plantilla HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Tu Diagnóstico de Bienestar</title>
            <style>
                body {{
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    max-width: 150px;
                    height: auto;
                }}
                h1 {{
                    color: #2c3e50;
                    font-size: 24px;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 25px;
                    border-radius: 8px;
                }}
                p {{
                    margin-bottom: 15px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #3498db;
                    color: white;
                    text-decoration: none;
                    padding: 12px 25px;
                    border-radius: 4px;
                    margin: 15px 0;
                    font-weight: bold;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 12px;
                    color: #7f8c8d;
                }}
                .social {{
                    margin-top: 15px;
                }}
                .social a {{
                    margin: 0 10px;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <img src="https://placehold.co/150x50/3498db/FFFFFF/png?text=Logo" alt="{Config.COMPANY_NAME}" class="logo">
            </div>
            
            <div class="content">
                <h1>¡Hola {nombre}!</h1>
                
                <p>Tu diagnóstico de bienestar está listo. Hemos analizado a fondo tu información y generado un informe personalizado para ti.</p>
                
                <p>En el informe encontrarás:</p>
                <ul>
                    <li>Una evaluación de tu bienestar general</li>
                    <li>Análisis de tus hábitos de vida actuales</li>
                    <li>Recomendaciones personalizadas</li>
                    <li>Pasos a seguir para mejorar tu bienestar</li>
                </ul>
                
                <p>Puedes consultar tu diagnóstico en cualquier momento haciendo clic en el botón de abajo:</p>
                
                <p style="text-align: center;">
                    <a href="{base_url}/view-report/{diagnostico_id}" class="button">Ver mi diagnóstico</a>
                </p>
                
                <p>También hemos adjuntado una copia del informe en formato PDF para tu comodidad.</p>
                
                <p>Si deseas programar una sesión de consulta para discutir los resultados en detalle, puedes hacerlo a través de este enlace:</p>
                
                <p style="text-align: center;">
                    <a href="{base_url}/schedule/{diagnostico_id}" class="button" style="background-color: #27ae60;">Agendar consulta</a>
                </p>
            </div>
            
            <div class="footer">
                <p>{Config.COMPANY_NAME} - Especialistas en bienestar</p>
                <p>Contacto: {Config.CONTACT_EMAIL} | {Config.CONTACT_PHONE}</p>
                
                <div class="social">
                    <a href="{Config.SOCIAL_FACEBOOK}">Facebook</a> |
                    <a href="{Config.SOCIAL_TWITTER}">Twitter</a> |
                    <a href="{Config.SOCIAL_INSTAGRAM}">Instagram</a> |
                    <a href="{Config.SOCIAL_LINKEDIN}">LinkedIn</a>
                </div>
                
                <p>Si no solicitaste este diagnóstico, por favor ignora este correo.</p>
            </div>
        </body>
        </html>
        """
        
        return html 