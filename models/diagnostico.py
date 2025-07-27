import os
import json
import logging
import pymysql
import openai
from config import Config
import time

logger = logging.getLogger(__name__)

class Diagnostico:
    """Modelo para gestionar diagnósticos de bienestar"""
    
    def __init__(self, form_data):
        """
        Inicializa un nuevo diagnóstico con los datos del formulario.
        
        Args:
            form_data (dict): Datos del formulario enviado por el usuario.
        """
        # Guardar datos básicos
        self.nombre = form_data.get('nombre', '')
        self.apellido = form_data.get('apellido', '')
        self.email = form_data.get('email', '') or form_data.get('correo', '')
        self.telefono = form_data.get('telefono', '')
        self.edad = form_data.get('edad', '')
        self.genero = form_data.get('genero', '')
        
        # Nuevos campos de medidas físicas
        self.peso = form_data.get('peso', '')
        self.estatura = form_data.get('estatura', '')
        self.imc = self._calcular_imc()
        self.presion_arterial = form_data.get('presion_arterial', '')
        self.pulso = form_data.get('pulso', '')
        self.nivel_energia = form_data.get('nivel_energia', '')
        
        # Datos sobre hábitos y estado de salud
        self.habitos_sueno = form_data.get('habitos_sueno', '')
        self.habitos_alimentacion = form_data.get('habitos_alimentacion', '')
        self.actividad_fisica = form_data.get('actividad_fisica', '')
        self.estres = form_data.get('estres', '')
        
        # Procesamiento de síntomas (ahora pueden ser una lista desde checkboxes)
        sintomas_lista = form_data.getlist('sintomas') if hasattr(form_data, 'getlist') else form_data.get('sintomas', [])
        if isinstance(sintomas_lista, str):
            # Si viene como string, intentar dividir por comas
            self.sintomas = sintomas_lista
        elif isinstance(sintomas_lista, list):
            # Si viene como lista, unir con comas
            self.sintomas = ', '.join(sintomas_lista)
        else:
            self.sintomas = ''
            
        self.antecedentes = form_data.get('antecedentes', '')
        
        # Datos adicionales
        self.objetivos = form_data.get('objetivos', '')
        self.comentarios = form_data.get('comentarios', '') or form_data.get('observaciones', '')
        
        # Datos de encuestador
        self.nombre_encuestador = form_data.get('nombre_encuestador', 'Encuestador por Defecto')
        self.encuestador_id = form_data.get('encuestador_id', 'default')
        
        # Almacenar datos brutos para procesamiento
        self.form_data = form_data
        
        # Diagnóstico y recomendaciones (se generan más tarde)
        self.diagnostico = ''
        self.recomendaciones = ''
        
        # Configurar OpenAI API
        openai.api_key = Config.OPENAI_API_KEY
    
    def _calcular_imc(self):
        """Calcula el IMC basado en peso y estatura"""
        try:
            if self.peso and self.estatura and float(self.estatura) > 0:
                imc = float(self.peso) / (float(self.estatura) ** 2)
                return round(imc, 2)
        except (ValueError, TypeError):
            pass
        return None
    
    def generar_diagnostico(self):
        """
        Genera un diagnóstico personalizado utilizando IA (OpenAI).
        
        Returns:
            dict: Diagnóstico generado con recomendaciones.
        """
        try:
            # Validar la conexión con OpenAI
            if not Config.OPENAI_API_KEY:
                raise ValueError("No se ha configurado la API key de OpenAI")
            
            # Preparar prompt para OpenAI según el nuevo formato
            prompt_diagnostico = self._preparar_prompt_diagnostico()
            prompt_recomendaciones = None  # Se preparará después de obtener el diagnóstico
            
            # Validar datos antes de enviar
            logger.info(f"Validando datos para diagnóstico de {self.nombre} {self.apellido}")
            logger.info(f"→ Edad: {self.edad} años")
            logger.info(f"→ Peso: {self.peso} kg")
            logger.info(f"→ Estatura: {self.estatura} m")
            logger.info(f"→ IMC: {self.imc}")
            logger.info(f"→ Presión: {self.presion_arterial}")
            logger.info(f"→ Pulso: {self.pulso} lpm")
            logger.info(f"→ Nivel de energía: {self.nivel_energia}/10")
            
            # Verificar si hay un ID de asistente configurado
            if Config.OPENAI_ASSISTANT_ID:
                logger.info(f"Usando OpenAI Assistant ID: {Config.OPENAI_ASSISTANT_ID}")
                # Implementación para usar el asistente será añadida en el futuro
                # Por ahora, usar el método tradicional
            
            # Llamar a la API de OpenAI con el nuevo formato (>=1.0.0)
            client = openai.OpenAI(
                api_key=Config.OPENAI_API_KEY,
                base_url="https://api.openai.com/v1"
            )
            
            # 1. Generar diagnóstico
            start_time = time.time()
            response_diagnostico = client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un experto en bienestar y nutrición especializado en diagnósticos preliminares. "
                                                 "Proporciona diagnósticos en formato de párrafo continuo, sin estructuras ni listas. "
                                                 "Asegúrate de que cada diagnóstico se complete completamente y concluya con una "
                                                 "recomendación clara sobre la necesidad de consultar con un profesional. "
                                                 "Usa los datos exactos proporcionados, no inventes ni modifiques valores."},
                    {"role": "user", "content": prompt_diagnostico}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extraer diagnóstico del resultado
            diagnostico_texto = response_diagnostico.choices[0].message.content
            self.diagnostico = diagnostico_texto
            
            logger.info(f"Diagnóstico generado en {time.time() - start_time:.2f} segundos")
            
            # 2. Generar recomendaciones basadas en el diagnóstico
            prompt_recomendaciones = self._preparar_prompt_recomendaciones(diagnostico_texto)
            
            response_recomendaciones = client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un experto en bienestar y nutrición. "
                                                 "Proporciona recomendaciones en formato de párrafo continuo, sin estructuras ni listas. "
                                                 "Asegúrate de que cada recomendación sea específica, accionable y personalizada. "
                                                 "Concluye con una nota positiva y motivadora."},
                    {"role": "user", "content": prompt_recomendaciones}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extraer recomendaciones
            self.recomendaciones = response_recomendaciones.choices[0].message.content
            
            logger.info(f"Diagnóstico completo generado para {self.nombre} {self.apellido}")
            
            return {
                "diagnostico": self.diagnostico,
                "recomendaciones": self.recomendaciones
            }
            
        except Exception as e:
            logger.error(f"Error al generar diagnóstico: {str(e)}", exc_info=True)
            self.diagnostico = "No se pudo generar un diagnóstico en este momento."
            self.recomendaciones = "Por favor, consulta con un profesional de la salud."
            return {
                "error": str(e),
                "diagnostico": self.diagnostico,
                "recomendaciones": self.recomendaciones
            }
    
    def _preparar_prompt_diagnostico(self):
        """
        Prepara el prompt para generar el diagnóstico.
        
        Returns:
            str: Prompt formateado.
        """
        # Preparar interpretación del IMC si está disponible
        interpretacion_imc = ""
        if self.imc:
            if self.imc < 18.5:
                interpretacion_imc = "Bajo peso"
            elif 18.5 <= self.imc < 25:
                interpretacion_imc = "Peso normal"
            elif 25 <= self.imc < 30:
                interpretacion_imc = "Sobrepeso"
            elif 30 <= self.imc < 35:
                interpretacion_imc = "Obesidad grado I"
            elif 35 <= self.imc < 40:
                interpretacion_imc = "Obesidad grado II"
            else:
                interpretacion_imc = "Obesidad grado III"
        
        # Formatear los síntomas como lista
        if isinstance(self.sintomas, list):
            sintomas_texto = "\n".join([f"- {s}" for s in self.sintomas])
        else:
            # Si es string, dividir por comas
            sintomas_lista = [s.strip() for s in self.sintomas.split(',')] if self.sintomas else []
            sintomas_texto = "\n".join([f"- {s}" for s in sintomas_lista])
        
        prompt = f"""
        Como experto en bienestar, nutrición y salud integral de WellTechFlow, analiza exhaustivamente los siguientes datos del encuestado para proporcionar un diagnóstico detallado, profundo y personalizado en formato de párrafo continuo:

        **Datos Personales del Encuestado:**
        - Edad: {self.edad} años
        - Género: {self.genero}
        - Peso: {self.peso} kg
        - Estatura: {self.estatura} m
        - IMC: {self.imc} ({interpretacion_imc})
        - Presión arterial: {self.presion_arterial}
        - Pulso: {self.pulso} lpm
        - Nivel de energía: {self.nivel_energia}/10
        
        **Hábitos y Estilo de Vida:**
        - Hábitos de sueño: {self.habitos_sueno}
        - Hábitos de alimentación: {self.habitos_alimentacion}
        - Actividad física: {self.actividad_fisica}
        - Nivel de estrés: {self.estres}
        
        **Síntomas Reportados:**
        {sintomas_texto}
        
        **Antecedentes médicos:**
        {self.antecedentes}
        
        **Objetivos de bienestar:**
        {self.objetivos}
        
        **Observaciones Adicionales:**
        {self.comentarios}

        Por favor, proporciona un diagnóstico extenso, detallado y personalizado en formato de párrafo continuo que incluya:
        1. Análisis exhaustivo de los síntomas reportados y su posible origen
        2. Evaluación completa del estado físico actual basado en los datos proporcionados
        3. Relación entre hábitos, estilo de vida y los síntomas/condiciones identificados
        4. Identificación de posibles deficiencias nutricionales o metabólicas
        5. Análisis de factores de riesgo para la salud a corto y largo plazo
        6. Evaluación del estado de bienestar integral (físico, mental y emocional)
        7. Impacto del nivel de estrés en su salud general
        8. Relación entre calidad del sueño y niveles de energía
        9. Factores que pueden estar impactando negativamente en su calidad de vida

        IMPORTANTE: 
        - Utiliza un tono profesional pero comprensible para alguien sin conocimientos médicos
        - Escribe párrafos fluidos con transiciones naturales entre ideas
        - Proporciona un análisis verdaderamente personalizado, evitando generalizaciones
        - Referencia específicamente los valores y datos proporcionados por el encuestado
        - Mantén un enfoque holístico, considerando la interconexión entre todos los factores
        - Incluye una evaluación global del estado de bienestar de la persona
        - Asegúrate de que el diagnóstico sea completo y exhaustivo (mínimo 300 palabras)
        - No recomiendes productos específicos todavía, esto se hará en la siguiente etapa
        """
        return prompt
    
    def _preparar_prompt_recomendaciones(self, diagnostico):
        """
        Prepara el prompt para generar recomendaciones basadas en el diagnóstico.
        
        Args:
            diagnostico (str): El diagnóstico generado previamente
            
        Returns:
            str: Prompt formateado para recomendaciones
        """
        prompt = f"""
        Como especialista certificado en nutrición y bienestar de WellTechFlow, basado en el siguiente diagnóstico completo, proporciona recomendaciones altamente específicas, personalizadas y accionables:

        Diagnóstico: {diagnostico}

        **Datos del Encuestado:**
        - Edad: {self.edad} años
        - Género: {self.genero}
        - Peso: {self.peso} kg
        - Estatura: {self.estatura} m
        - IMC: {self.imc}
        - Nivel de energía: {self.nivel_energia}/10
        - Objetivos: {self.objetivos}
        - Hábitos de alimentación: {self.habitos_alimentacion}
        - Actividad física: {self.actividad_fisica}
        - Síntomas: {self.sintomas}

        Proporciona recomendaciones completas, detalladas y personalizadas que incluyan:

        1. PLAN NUTRICIONAL:
           - Patrón alimenticio óptimo para su condición específica
           - Alimentos específicos a incluir y evitar, con justificación
           - Frecuencia y tamaño recomendado de comidas
           - Necesidades de hidratación personalizadas

        2. SUPLEMENTACIÓN HERBALIFE ESPECÍFICA:
           - Recomienda productos Herbalife específicos que puedan beneficiar su condición particular
           - Para cada producto, explica claramente por qué lo necesita, cómo funciona y sus beneficios
           - Incluye específicamente estos productos si son relevantes para su condición:
             * Batido Nutricional Fórmula 1 (para control de peso/nutrición)
             * Proteína en Polvo Personalizada (para desarrollo muscular/recuperación)
             * Té Concentrado de Hierbas (para energía/metabolismo)
             * Fibra Activa (para digestión/saciedad)
             * Bebida Multivitamínica Aloe (para digestión/inmunidad)
             * Complemento Proteínico (recuperación muscular)
             * CR7 Drive (hidratación/rendimiento)
             * Herbalifeline (salud cardiovascular)
             * Niteworks (circulación/energía nocturna)
             * Cell Activator (absorción de nutrientes)
             * Multivitamínico Complex (para deficiencias específicas)
             * Prolessa Duo (control de grasa/apetito)
           - Especifica dosis y momento exacto del día para cada producto

        3. ACTIVIDAD FÍSICA:
           - Tipo exacto de ejercicio adecuado para su condición
           - Duración, frecuencia e intensidad específicas
           - Progresión recomendada según su nivel actual
           - Consideraciones especiales basadas en su condición

        4. GESTIÓN DEL ESTRÉS Y SUEÑO:
           - Técnicas específicas para mejorar la calidad del sueño
           - Estrategias de manejo del estrés personalizadas
           - Rutina de descanso recomendada

        5. SEGUIMIENTO Y PROGRESIÓN:
           - Métricas concretas para monitorear el progreso
           - Plazos realistas para ver resultados
           - Ajustes anticipados según la evolución

        IMPORTANTE:
        - Mantén un tono motivador y empoderador
        - Sé muy específico y directivo; evita generalidades
        - Adapta cada recomendación a su condición única
        - Menciona claramente cómo los productos Herbalife específicos abordan sus necesidades particulares
        - Relaciona tus recomendaciones con los objetivos que ha manifestado
        - Incluye información sobre cómo los productos Herbalife complementan (no reemplazan) un estilo de vida saludable
        - Especifica dosis, cantidades y frecuencias exactas

        Finaliza con un plan de acción claro, priorizando los cambios más importantes a implementar primero.

        Presenta todo como texto fluido y bien estructurado, con párrafos claros y organizados por áreas.
        EVITA usar viñetas o listas con números. Todo debe presentarse como párrafos de texto continuo.
        """
        return prompt
    
    def guardar_en_db(self, diagnostico_id):
        """
        Guarda el diagnóstico en la base de datos.
        
        Args:
            diagnostico_id (str): ID único del diagnóstico.
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario.
        """
        try:
            # Conectar a la base de datos remota
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
                # Crear la consulta SQL
                sql = """
                INSERT INTO diagnosticos 
                (id, nombre, apellido, email, telefono, edad, genero, 
                peso, estatura, imc, presion_arterial, pulso, nivel_energia,
                habitos_sueno, habitos_alimentacion, actividad_fisica, estres,
                sintomas, antecedentes, objetivos, comentarios,
                diagnostico, recomendaciones,
                nombre_encuestador, encuestador_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Ejecutar la consulta
                cursor.execute(sql, (
                    diagnostico_id,
                    self.nombre,
                    self.apellido,
                    self.email,
                    self.telefono,
                    self.edad,
                    self.genero,
                    self.peso,
                    self.estatura,
                    self.imc,
                    self.presion_arterial,
                    self.pulso,
                    self.nivel_energia,
                    self.habitos_sueno,
                    self.habitos_alimentacion,
                    self.actividad_fisica,
                    self.estres,
                    self.sintomas,
                    self.antecedentes,
                    self.objetivos,
                    self.comentarios,
                    self.diagnostico,
                    self.recomendaciones,
                    self.nombre_encuestador,
                    self.encuestador_id
                ))
                
                # Confirmar los cambios
                conn.commit()
                
                logger.info(f"Diagnóstico guardado en la base de datos: {diagnostico_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error al guardar diagnóstico en la base de datos: {str(e)}", exc_info=True)
            
            # Guardar en un archivo JSON local como respaldo en caso de error con la BD
            try:
                import json
                import os
                data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
                os.makedirs(data_dir, exist_ok=True)
                
                data_file = os.path.join(data_dir, f"diagnostico_{diagnostico_id}.json")
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(self.get_data(), f, ensure_ascii=False, indent=4)
                
                logger.warning(f"Diagnóstico guardado localmente como respaldo en {data_file}")
            except Exception as json_error:
                logger.error(f"No se pudo guardar el diagnóstico localmente: {str(json_error)}")
            
            return False
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()
    
    def get_data(self):
        """
        Obtiene todos los datos del diagnóstico.
        
        Returns:
            dict: Datos completos del diagnóstico.
        """
        return {
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_completo": f"{self.nombre} {self.apellido}",
            "email": self.email,
            "telefono": self.telefono,
            "edad": self.edad,
            "genero": self.genero,
            "peso": self.peso,
            "estatura": self.estatura,
            "imc": self.imc,
            "presion_arterial": self.presion_arterial,
            "pulso": self.pulso,
            "nivel_energia": self.nivel_energia,
            "habitos_sueno": self.habitos_sueno,
            "habitos_alimentacion": self.habitos_alimentacion,
            "actividad_fisica": self.actividad_fisica,
            "estres": self.estres,
            "sintomas": self.sintomas,
            "antecedentes": self.antecedentes,
            "objetivos": self.objetivos,
            "comentarios": self.comentarios,
            "diagnostico": self.diagnostico,
            "recomendaciones": self.recomendaciones,
            "nombre_encuestador": self.nombre_encuestador,
            "encuestador_id": self.encuestador_id
        } 