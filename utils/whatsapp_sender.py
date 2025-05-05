import os
import json
import logging
import requests
import time
import re
from config import Config

logger = logging.getLogger(__name__)

class WhatsappSender:
    """Clase para enviar mensajes por WhatsApp usando la API existente"""
    
    def __init__(self):
        """Inicializa el servicio de envío de WhatsApp"""
        self.api_url = f"{Config.WHATSAPP_API_URL}/lead"
        
    def send_message(self, para, mensaje=None, pdf_path=None, datos=None):
        """
        Envía un mensaje de WhatsApp y opcionalmente un archivo PDF adjunto.
        
        Args:
            para (str): Número de teléfono del destinatario (formato: 593982840685)
            mensaje (str, optional): Texto del mensaje a enviar o None para generar mensaje personalizado
            pdf_path (str, optional): Ruta al archivo PDF para adjuntar
            datos (dict, optional): Datos para personalizar el mensaje si mensaje es None
        
        Returns:
            dict: Respuesta del servidor
        """
        try:
            # Limpiar el número de teléfono (eliminar +, -, espacios)
            para = para.replace('+', '').replace('-', '').replace(' ', '')
            
            # Códigos de país comunes para países hispanohablantes
            country_codes = ['593', '52', '57', '34', '1', '51', '56', '54', '502', '503', '504', '505', '506', '507', '809', '58']
            
            # Verificar si el número comienza con un código de país y eliminar 0 inicial si es necesario
            for code in country_codes:
                if para.startswith(code):
                    # Obtener la parte nacional del número (después del código de país)
                    national_part = para[len(code):]
                    
                    # Eliminar el 0 inicial si existe
                    if national_part.startswith('0'):
                        para = code + national_part[1:]
                    break
            
            logger.info(f"Número formateado para WhatsApp: {para}")
            
            # Si no hay mensaje pero hay datos, generar mensaje personalizado
            if mensaje is None and datos:
                mensaje_final = self._generar_mensaje_personalizado(datos)
            else:
                mensaje_final = mensaje or "Tu diagnóstico de bienestar está listo."
            
            data = {
                'message': mensaje_final,
                'phone': para
            }
            
            # Si hay un archivo PDF para enviar, verificar que exista
            if pdf_path:
                if os.path.exists(pdf_path):
                    data['pdfPath'] = pdf_path
                    logger.info(f"Enviando archivo adjunto: {pdf_path}")
                else:
                    logger.error(f"Error: El archivo no existe: {pdf_path}")
                    return {"status": "error", "message": f"El archivo no existe: {pdf_path}"}
                
            headers = {
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Enviando mensaje a {para}: {mensaje_final[:100]}...")
            
            response = requests.post(self.api_url, json=data, headers=headers, timeout=30)
            time.sleep(3)  # Reducimos el tiempo de espera a 3 segundos
            
            # Intentar decodificar la respuesta JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                return {
                    "status": "error", 
                    "message": "No se pudo decodificar la respuesta JSON",
                    "http_status": response.status_code,
                    "response_text": response.text[:200]  # Primeros 200 caracteres para diagnóstico
                }
                
        except requests.RequestException as e:
            logger.error(f"Error al enviar mensaje por WhatsApp: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"Error de conexión: {str(e)}"}
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"Error inesperado: {str(e)}"}
    
    def _generar_mensaje_personalizado(self, datos):
        """
        Genera un mensaje personalizado para WhatsApp basado en los datos del usuario.
        
        Args:
            datos (dict): Datos del usuario y el diagnóstico
        
        Returns:
            str: Mensaje personalizado
        """
        # Extraer datos relevantes
        nombre = datos.get('nombre', datos.get('first_name', 'Cliente'))
        
        # Generar mensaje personalizado con emojis
        mensaje = f"""¡Hola {nombre}! 👋

Tu diagnóstico de bienestar está listo. ✅

Hemos analizado a fondo tu información y te adjuntamos el informe detallado en PDF para que puedas revisar nuestros hallazgos.

El informe incluye:
📊 Evaluación de tu bienestar general
💪 Análisis de hábitos de vida
🌿 Recomendaciones personalizadas
🚀 Pasos a seguir para mejorar tu bienestar

También te hemos enviado este informe a tu correo electrónico.

¿Te gustaría agendar una llamada para revisar juntos los resultados y explicarte cómo podemos ayudarte a implementar las mejoras?

Estamos a tu disposición para cualquier consulta. 😊
"""
        
        return mensaje 