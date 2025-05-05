# Diagnóstico de Bienestar

Aplicación web para la recolección de datos de salud y diagnóstico personalizado basado en IA. La aplicación permite a un usuario ingresar sus datos y síntomas, los cuales se almacenan en una base de datos. Además, se utiliza la API de OpenAI para generar un diagnóstico y recomendaciones personalizadas, mostrándolos en línea y enviando los resultados tanto por correo electrónico como por WhatsApp.

## Características

- **Frontend**: Interfaz moderna y responsiva desarrollada con HTML, CSS y JavaScript.
- **Backend**: Servidor Flask (Python) para el diagnóstico y generación de informes.
- **API de WhatsApp**: Servicio en Node.js para enviar diagnósticos vía WhatsApp.
- **Base de Datos**: MySQL para almacenamiento de diagnósticos y citas.
- **Integración de IA**: Utiliza la API de OpenAI para generar diagnósticos personalizados.
- **Envío de Informes**: Genera informes PDF y los envía por correo electrónico y WhatsApp.
- **Agenda de Citas**: Sistema para agendar citas de seguimiento.

## Estructura del Proyecto

```
diagnosticador/
│
├── app.py                    # Punto de entrada de la aplicación Flask
├── config.py                 # Configuración de la aplicación
├── requirements.txt          # Dependencias de Python
│
├── models/                   # Modelos de datos
│   └── diagnostico.py        # Modelo para gestionar diagnósticos
│
├── utils/                    # Utilidades
│   ├── email_sender.py       # Servicio para enviar correos
│   ├── report_generator.py   # Generador de informes PDF
│   └── whatsapp_sender.py    # Integración con API de WhatsApp
│
├── static/                   # Archivos estáticos
│   ├── css/                  # Hojas de estilo
│   ├── js/                   # Scripts JavaScript
│   └── img/                  # Imágenes
│
├── templates/                # Plantillas HTML
│   ├── index.html            # Página principal con formulario
│   ├── processing.html       # Página de procesamiento
│   ├── success.html          # Página de éxito y agenda
│   └── report.html           # Visualización del diagnóstico
│
├── reports/                  # Carpeta para almacenar informes generados
│
└── api-whatsapp-ts/          # API de WhatsApp (Node.js)
    ├── src/                  # Código fuente de la API
    └── package.json          # Dependencias de Node.js
```

## Requisitos Previos

- Python 3.8+
- Node.js 14+
- MySQL 5.7+
- Cuenta de OpenAI para API Key

## Instalación

### 1. Configurar el entorno Python

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/diagnosticador.git
cd diagnosticador

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar la API de WhatsApp

```bash
# Entrar al directorio de la API
cd api-whatsapp-ts

# Instalar dependencias
npm install

# Volver al directorio principal
cd ..
```

### 3. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env-example .env

# Editar el archivo .env con tus datos
# Configurar claves de API, conexión a base de datos, etc.
```

### 4. Configurar la base de datos

```bash
# Acceder a MySQL
mysql -u root -p

# Crear base de datos
CREATE DATABASE diagnosticador;

# La aplicación creará las tablas necesarias automáticamente al iniciar
```

## Ejecución

### 1. Ejecutar la API de WhatsApp

```bash
# En una terminal
cd api-whatsapp-ts
npm start
```

### 2. Ejecutar la aplicación Flask

```bash
# En otra terminal
source venv/bin/activate  # En Windows: venv\Scripts\activate
python app.py
```

La aplicación estará disponible en: http://localhost:5000

## Uso

1. Acceder a la página principal
2. Completar el formulario con los datos de salud y bienestar
3. Esperar a que se procese el diagnóstico
4. Recibir el diagnóstico por correo electrónico y WhatsApp
5. Acceder al diagnóstico en línea y/o descargar el PDF
6. Opcionalmente, agendar una cita de seguimiento

## Contribuciones

Las contribuciones son bienvenidas. Por favor, asegúrate de actualizar las pruebas según corresponda.

## Licencia

[MIT](https://choosealicense.com/licenses/mit/)
