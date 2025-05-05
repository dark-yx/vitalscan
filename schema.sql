-- Esquema de la base de datos para la aplicación de diagnóstico de bienestar
-- Ejecutar este script para crear las tablas necesarias

-- Crear tabla de diagnósticos
CREATE TABLE IF NOT EXISTS diagnosticos (
    id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    email VARCHAR(150) NOT NULL,
    telefono VARCHAR(50),
    edad VARCHAR(3),
    genero VARCHAR(50),
    
    -- Medidas físicas
    peso DECIMAL(5,2),
    estatura DECIMAL(3,2),
    imc DECIMAL(4,2),
    presion_arterial VARCHAR(20),
    pulso INT,
    nivel_energia INT,
    
    -- Hábitos y estado de salud
    habitos_sueno VARCHAR(100),
    habitos_alimentacion VARCHAR(100),
    actividad_fisica VARCHAR(100),
    estres VARCHAR(100),
    sintomas TEXT,
    antecedentes TEXT,
    objetivos TEXT,
    comentarios TEXT,
    
    -- Resultados del diagnóstico
    diagnostico TEXT,
    recomendaciones TEXT,
    
    -- Información del encuestador
    nombre_encuestador VARCHAR(150),
    encuestador_id VARCHAR(50),
    
    -- Metadatos
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'completado'
);

-- Índices
CREATE INDEX idx_diagnosticos_email ON diagnosticos(email);
CREATE INDEX idx_diagnosticos_fecha ON diagnosticos(fecha_creacion);
CREATE INDEX idx_diagnosticos_encuestador ON diagnosticos(encuestador_id); 