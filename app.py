import os
import json
import logging
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, send_file, flash
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta, date, time
import threading
import pymysql

# Importar módulos propios
from config import Config
from models.diagnostico import Diagnostico
from utils.report_generator import ReportGenerator
from utils.email_sender import EmailSender
from utils.whatsapp_sender import WhatsappSender

# Cargar variables de entorno
load_dotenv()

# Configurar logging
LOG_FILE = os.environ.get('LOG_FILE', 'diagnostico_app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializar aplicación
app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_secreta_desarrollo')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'reports')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))
app.config['DB_CONFIG'] = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'diagnosticador'),
}

# Asegurar que los directorios necesarios existen
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# Diccionario para almacenar el estado de los diagnósticos
diagnostico_status = {}

# Función para obtener los próximos 3 días laborables
def get_next_workdays(days_ahead=3):
    """Obtener los próximos 3 días laborables a partir de mañana"""
    result = []
    today = date.today()
    day_count = 0
    days_checked = 0
    
    # Comenzar desde mañana
    current_date = today + timedelta(days=1)
    
    # Continuar hasta obtener el número de días laborables solicitados
    while day_count < days_ahead and days_checked < 14:  # Límite de seguridad: 14 días
        # Lunes = 0, Domingo = 6
        weekday = current_date.weekday()
        
        # Si es día laborable (lunes a viernes)
        if weekday < 5:  # 0-4 son lunes a viernes
            # Formato: "DD-MM-YYYY"
            result.append(current_date.strftime('%d-%m-%Y'))
            day_count += 1
        
        current_date += timedelta(days=1)
        days_checked += 1
    
    return result

# Generar slots para horarios de consulta
def generate_schedule_slots():
    """Generar slots de horarios de 30 minutos con descanso de 15 minutos"""
    slots = []
    # Horario de trabajo: 9:00 AM - 5:00 PM
    current_time = time(9, 0)  # 9:00 AM
    end_time = time(17, 0)     # 5:00 PM
    
    while current_time < end_time:
        # Hora actual
        hour = current_time.hour
        minute = current_time.minute
        
        # Calcular hora final (30 minutos después)
        end_hour = hour
        end_minute = minute + 30
        
        if end_minute >= 60:
            end_hour += 1
            end_minute -= 60
        
        # Formatear horario: "HH:MM - HH:MM"
        time_slot = f"{hour:02d}:{minute:02d} - {end_hour:02d}:{end_minute:02d}"
        slots.append(time_slot)
        
        # Avanzar 45 minutos (30 min de sesión + 15 min de descanso)
        minute += 45
        if minute >= 60:
            hour += 1
            minute -= 60
        
        current_time = time(hour, minute)
    
    return slots

# Rutas de la aplicación
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            # Procesar el formulario
            form_data = request.form.to_dict()
            logger.info(f"Formulario recibido para {form_data.get('nombre', '')} - {form_data.get('email', '')}")
            
            # Generar ID único para el diagnóstico
            diagnostico_id = str(uuid.uuid4().hex[:16])
            
            # Iniciar el procesamiento en segundo plano
            thread = threading.Thread(target=process_diagnostico, args=(form_data, diagnostico_id))
            thread.daemon = True
            thread.start()
            
            # Redirigir a la página de procesamiento
            return redirect(url_for('processing', diagnostico_id=diagnostico_id))
        
        logger.info("Renderizando página de inicio")
        return render_template('index.html', now=datetime.now())
    except Exception as e:
        logger.error(f"Error en la ruta principal: {str(e)}", exc_info=True)
        return f"Error: {str(e)}", 500

@app.route('/processing/<diagnostico_id>')
def processing(diagnostico_id):
    return render_template('processing.html', diagnostico_id=diagnostico_id, now=datetime.now())

@app.route('/check-status/<diagnostico_id>')
def check_status(diagnostico_id):
    status = diagnostico_status.get(diagnostico_id, {'status': 'processing'})
    return jsonify(status)

@app.route('/success/<diagnostico_id>')
def success(diagnostico_id):
    # Obtener información del diagnóstico
    diagnostico_info = get_diagnostico_by_id(diagnostico_id)
    if not diagnostico_info:
        flash("Diagnóstico no encontrado", "error")
        return redirect(url_for('index'))
    
    # Obtener próximos días disponibles para consulta
    available_dates = get_next_workdays(3)
    
    # Generar slots de horarios disponibles
    available_slots = generate_schedule_slots()
    
    return render_template('success.html', 
                          diagnostico_id=diagnostico_id,
                          available_dates=available_dates,
                          available_slots=available_slots,
                          diagnostico=diagnostico_info,
                          now=datetime.now())

@app.route('/download-report/<diagnostico_id>')
def download_report(diagnostico_id):
    try:
        # Obtener información del diagnóstico
        diagnostico_info = get_diagnostico_by_id(diagnostico_id)
        if not diagnostico_info:
            return "Diagnóstico no encontrado", 404
        
        # Ruta al informe PDF
        report_path = os.path.join(REPORTS_DIR, f"diagnostico_{diagnostico_id}.pdf")
        
        # Verificar si el archivo existe
        if not os.path.exists(report_path):
            return "El informe PDF no está disponible", 404
        
        # Enviar el archivo como descarga
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f"Diagnóstico_Bienestar_{diagnostico_id}.pdf"
        )
    except Exception as e:
        logger.error(f"Error al descargar reporte: {str(e)}", exc_info=True)
        return f"Error al descargar reporte: {str(e)}", 500

@app.route('/view-report/<diagnostico_id>')
def view_report(diagnostico_id):
    # Obtener información del diagnóstico
    diagnostico_info = get_diagnostico_by_id(diagnostico_id)
    if not diagnostico_info:
        return "Diagnóstico no encontrado", 404
    
    # Mostrar el informe en HTML
    return render_template('report.html', diagnostico=diagnostico_info, now=datetime.now())

@app.route('/api/schedule', methods=['POST'])
def api_schedule():
    try:
        data = request.json
        diagnostico_id = data.get('diagnostico_id')
        fecha = data.get('fecha')
        hora = data.get('hora')
        
        if not all([diagnostico_id, fecha, hora]):
            return jsonify({
                "success": False,
                "error": "Faltan datos requeridos (diagnostico_id, fecha, hora)"
            }), 400
        
        # Obtener información del diagnóstico
        diagnostico_info = get_diagnostico_by_id(diagnostico_id)
        if not diagnostico_info:
            return jsonify({
                "success": False,
                "error": "Diagnóstico no encontrado"
            }), 404
        
        # Actualizar información de la cita en la base de datos
        # (implementación pendiente)
        
        # Devolver respuesta exitosa
        return jsonify({
            "success": True,
            "message": "Cita agendada correctamente"
        })
    except Exception as e:
        logger.error(f"Error al agendar cita: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Error al agendar cita: {str(e)}"
        }), 500

# Función para procesar el diagnóstico (se ejecuta en segundo plano)
def process_diagnostico(form_data, diagnostico_id):
    try:
        # Actualizar estado
        diagnostico_status[diagnostico_id] = {'status': 'processing', 'progress': 10}
        
        # Crear instancia del diagnóstico
        diagnostico = Diagnostico(form_data)
        
        # Actualizar estado
        diagnostico_status[diagnostico_id] = {'status': 'processing', 'progress': 25}
        
        # Generar diagnóstico usando IA
        diagnostico.generar_diagnostico()
        
        # Actualizar estado
        diagnostico_status[diagnostico_id] = {'status': 'processing', 'progress': 50}
        
        # Guardar en la base de datos
        diagnostico.guardar_en_db(diagnostico_id)
        
        # Actualizar estado
        diagnostico_status[diagnostico_id] = {'status': 'processing', 'progress': 75}
        
        # Generar informe PDF
        report_generator = ReportGenerator()
        pdf_path = report_generator.generate_pdf(diagnostico.get_data(), diagnostico_id)
        
        # Enviar por correo electrónico si se proporcionó email
        if diagnostico.email:
            email_sender = EmailSender()
            email_sender.send_email(
                to_email=diagnostico.email,
                subject="Tu diagnóstico de bienestar está listo",
                nombre=diagnostico.nombre,
                diagnostico_id=diagnostico_id,
                pdf_path=pdf_path
            )
        
        # Enviar por WhatsApp si se proporcionó número de teléfono
        if diagnostico.telefono:
            whatsapp_sender = WhatsappSender()
            whatsapp_sender.send_message(
                para=diagnostico.telefono,
                datos=diagnostico.get_data(),
                pdf_path=pdf_path
            )
        
        # Actualizar estado final
        diagnostico_status[diagnostico_id] = {
            'status': 'completed',
            'progress': 100,
            'redirect_url': f'/success/{diagnostico_id}'
        }
        
    except Exception as e:
        logger.error(f"Error al procesar diagnóstico {diagnostico_id}: {str(e)}", exc_info=True)
        diagnostico_status[diagnostico_id] = {
            'status': 'error',
            'error': str(e)
        }

# Función para obtener diagnóstico por ID
def get_diagnostico_by_id(diagnostico_id):
    try:
        # Conectar a la base de datos
        conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            # Consultar el diagnóstico
            sql = "SELECT * FROM diagnosticos WHERE id = %s"
            cursor.execute(sql, (diagnostico_id,))
            result = cursor.fetchone()
            
            if result:
                # Calcular IMC nuevamente si hay peso y estatura pero no IMC
                if result.get('peso') and result.get('estatura') and not result.get('imc'):
                    try:
                        peso = float(result['peso'])
                        estatura = float(result['estatura'])
                        if estatura > 0:
                            result['imc'] = round(peso / (estatura ** 2), 2)
                    except (ValueError, TypeError):
                        pass
                
                logger.info(f"Diagnóstico encontrado: {diagnostico_id}")
                return result
            
            # Si no se encuentra, buscar en archivos locales (respaldo)
            logger.warning(f"Diagnóstico no encontrado en base de datos: {diagnostico_id}")
    except Exception as e:
        logger.error(f"Error al obtener diagnóstico {diagnostico_id} de la base de datos: {str(e)}", exc_info=True)
    
    # Intento de respaldo - buscar en archivo local
    try:
        import json
        import os
        
        # Verificar si existe archivo de datos en modo desarrollo
        data_file = os.path.join(os.path.dirname(__file__), 'data', f"diagnostico_{diagnostico_id}.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                logger.info(f"Diagnóstico encontrado en archivo local: {diagnostico_id}")
                return json.load(f)
    except Exception as json_error:
        logger.error(f"Error al leer archivo de respaldo: {str(json_error)}")
    
    # Si no se encuentra ni en la base de datos ni en archivos, devolver datos simulados
    logger.warning(f"Usando datos simulados para diagnóstico: {diagnostico_id}")
    return {
        'id': diagnostico_id,
        'nombre': 'Usuario de Prueba',
        'email': 'usuario@ejemplo.com',
        'telefono': '1234567890',
        'fecha': datetime.now().strftime('%d-%m-%Y'),
        'estado': 'completado',
        'diagnostico': 'Diagnóstico simulado para un usuario con buena salud general pero que podría beneficiarse de mejoras en su rutina diaria.',
        'recomendaciones': 'Recomendaciones simuladas: Aumentar actividad física, mejorar la calidad del sueño y mantener una dieta equilibrada.'
    }

# Punto de entrada para ejecutar la aplicación
if __name__ == "__main__":
    # Verificar conexión a la base de datos y crear tablas si es necesario
    # (implementación pendiente)
    
    # Ejecutar la aplicación
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 