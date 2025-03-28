import mysql from "mysql2/promise";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import { config } from './config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

// Crear pool de conexiones con configuración optimizada
const pool = mysql.createPool({
  host: config.db.host,
  user: config.db.user,
  password: config.db.password,
  database: config.db.database,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  enableKeepAlive: true,
  keepAliveInitialDelay: 0,
  // Configuración de timeouts
  connectTimeout: 10000
});

// Función para verificar la conexión con reintentos
async function verificarConexion() {
  let intentos = 0;
  const maxIntentos = 3;
  
  while (intentos < maxIntentos) {
    try {
      const connection = await pool.getConnection();
      connection.release();
      console.log("✅ Conexión a la base de datos establecida");
      return true;
    } catch (error) {
      intentos++;
      console.log(`❌ Intento ${intentos} de conexión fallido:`, error.message);
      if (intentos < maxIntentos) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
  }
  
  throw new Error("No se pudo establecer conexión con la base de datos después de varios intentos");
}

// Función para verificar y crear tablas con reintentos
async function verificarYCrearTablas() {
  let intentos = 0;
  const maxIntentos = 3;
  
  while (intentos < maxIntentos) {
    try {
      const connection = await pool.getConnection();
      
      // Verificar y crear tabla usuarios
      await connection.query(`
        CREATE TABLE IF NOT EXISTS usuarios (
          usuario_id INT AUTO_INCREMENT PRIMARY KEY,
          nombre VARCHAR(100) NOT NULL,
          apellido VARCHAR(100) NOT NULL,
          identificacion VARCHAR(20) UNIQUE NOT NULL,
          telefono VARCHAR(20),
          correo VARCHAR(100),
          fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `);
      
      // Verificar y crear tabla encuestas
      await connection.query(`
        CREATE TABLE IF NOT EXISTS encuestas (
          id INT AUTO_INCREMENT PRIMARY KEY,
          usuario_id INT NOT NULL,
          nombre_encuestado VARCHAR(200) NOT NULL,
          telefono VARCHAR(20),
          correo VARCHAR(100),
          edad INT,
          peso DECIMAL(5,2),
          estatura DECIMAL(3,2),
          presion_arterial VARCHAR(10),
          nivel_energia INT DEFAULT 5,
          sintomas JSON,
          observaciones TEXT,
          nombre_encuestador VARCHAR(200),
          encuestador_id VARCHAR(50),
          fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id)
        )
      `);
      
      // Verificar y crear tabla diagnosticos
      await connection.query(`
        CREATE TABLE IF NOT EXISTS diagnosticos (
          id INT AUTO_INCREMENT PRIMARY KEY,
          usuario_id INT NOT NULL,
          encuesta_id INT NOT NULL,
          diagnostico TEXT NOT NULL,
          recomendaciones TEXT,
          fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id),
          FOREIGN KEY (encuesta_id) REFERENCES encuestas(id)
        )
      `);
      
      connection.release();
      console.log("✅ Tablas verificadas y creadas correctamente");
      return true;
    } catch (error) {
      intentos++;
      console.log(`❌ Intento ${intentos} de verificación de tablas fallido:`, error.message);
      if (intentos < maxIntentos) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
  }
  
  throw new Error("No se pudo verificar o crear las tablas después de varios intentos");
}

// Verificar la conexión al iniciar
pool.getConnection()
  .then(async connection => {
    console.log("✅ Conectado a MySQL correctamente");
    console.log(`  → Host: ${process.env.DB_HOST}`);
    console.log(`  → Base de datos: ${process.env.DB_NAME}`);
    
    // Liberar la conexión antes de verificar las tablas
    connection.release();
    
    // Verificar y crear tablas si es necesario
    await verificarYCrearTablas();
  })
  .catch(err => {
    console.error("❌ Error al conectar a MySQL:", err.message);
    if (err.code === 'ECONNREFUSED') {
      console.error("  → Asegúrate de que el servidor MySQL esté corriendo");
    } else if (err.code === 'ER_ACCESS_DENIED_ERROR') {
      console.error("  → Verifica las credenciales de acceso (usuario/contraseña)");
    } else if (err.code === 'ER_BAD_DB_ERROR') {
      console.error("  → La base de datos no existe. Asegúrate de crearla primero");
    }
  });

// Exportar las variables y funciones necesarias
export { pool, verificarConexion, verificarYCrearTablas }; 
