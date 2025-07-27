import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # Configuración general
    ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'
    TESTING = ENV == 'testing'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_desarrollo')
    
    # Directorios
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'reports')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    
    # Configuración de base de datos
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'welltechflow')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # URL para la API de WhatsApp
    WHATSAPP_API_URL = os.environ.get('WHATSAPP_API_URL', 'http://localhost:3001')
    
    # Configuración de email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'info@welltechflow.com')
    
    # Configuración de OpenAI (para generación de diagnósticos)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_ASSISTANT_ID = os.environ.get('OPENAI_ASSISTANT_ID', '')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Configuración de PDF
    PDF_OPTIONS = {
        'page-size': 'A4',
        'margin-top': '1cm',
        'margin-right': '1cm',
        'margin-bottom': '1cm',
        'margin-left': '1cm',
        'encoding': 'UTF-8',
    }
    
    # Configuración de la aplicación
    APP_NAME = 'WellTechFlow - VitalScan'
    COMPANY_NAME = 'WellTechFlow'
    CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'contacto@welltechflow.com')
    CONTACT_PHONE = os.environ.get('CONTACT_PHONE', '+593967080644')
    
    # URLs de redes sociales
    SOCIAL_FACEBOOK = os.environ.get('SOCIAL_FACEBOOK', 'https://facebook.com/welltechflow')
    SOCIAL_TWITTER = os.environ.get('SOCIAL_TWITTER', 'https://twitter.com/welltechflow')
    SOCIAL_INSTAGRAM = os.environ.get('SOCIAL_INSTAGRAM', 'https://instagram.com/welltechflow')
    SOCIAL_LINKEDIN = os.environ.get('SOCIAL_LINKEDIN', 'https://linkedin.com/company/welltechflow')
    
    # Configuración específica de WellTechFlow
    VITALSCAN_VERSION = '1.0.0'
    BRAND_PRIMARY_COLOR = '#2ecc71'  # Verde esmeralda
    BRAND_SECONDARY_COLOR = '#3498db'  # Azul tecnológico
    BRAND_TAGLINE = 'Transformando el bienestar a través de la tecnología'
    
    # Configuración de WhatsApp
    WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '+593967080644')
    WHATSAPP_MESSAGE_TEMPLATE = """¡Hola! 👋

Me interesa conocer más sobre sus servicios de asesoría nutricional y productos Herbalife.

He visto su plataforma WellTechFlow y me gustaría recibir información personalizada sobre:

🌿 Productos Herbalife disponibles
📋 Planes de nutrición personalizados
💪 Programas de bienestar integral
📞 Consultas nutricionales

¿Podrían ayudarme con información detallada?

¡Gracias! 😊"""
    
    @staticmethod
    def init_app(app):
        """Inicializar configuración en la aplicación Flask"""
        # Crear directorios necesarios
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Configurar aplicación
        app.config.from_object(Config)
        
        return app 