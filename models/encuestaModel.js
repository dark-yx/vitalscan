import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { pool } from '../backend/db.js';
import { config } from '../backend/config.js';
import { obtenerDiagnosticoOpenAI } from '../ai/openaiAPI.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export async function guardarEncuesta(datos) {
  console.log("🔄 Iniciando guardarEncuesta...");
  console.log("📦 Preparando datos para guardar...");
  
  let connection;
  try {
    // Obtener una nueva conexión del pool
    connection = await pool.getConnection();
    console.log("✅ Conexión obtenida del pool");
    
    // Iniciar transacción
    await connection.beginTransaction();
    console.log("✅ Transacción iniciada");

    // Verificar si el usuario existe
    const [usuarioExistente] = await connection.execute(
      'SELECT usuario_id FROM usuarios WHERE identificacion = ?',
      [datos.identificacion]
    );

    let usuarioId;
    if (usuarioExistente.length > 0) {
      usuarioId = usuarioExistente[0].usuario_id;
      console.log("Usuario existente encontrado, ID:", usuarioId);
    } else {
      // Crear nuevo usuario
      const [resultadoUsuario] = await connection.execute(
        'INSERT INTO usuarios (nombre, apellido, identificacion, telefono, correo) VALUES (?, ?, ?, ?, ?)',
        [datos.nombre, datos.apellido, datos.identificacion, datos.telefono, datos.correo]
      );
      usuarioId = resultadoUsuario.insertId;
      console.log("Nuevo usuario creado, ID:", usuarioId);
    }

    // Guardar encuesta
    const [resultadoEncuesta] = await connection.execute(
      'INSERT INTO encuestas (usuario_id, nombre_encuestado, telefono, correo, edad, peso, estatura, presion_arterial, nivel_energia, sintomas, observaciones, nombre_encuestador, encuestador_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [
        usuarioId,
        `${datos.nombre} ${datos.apellido}`,
        datos.telefono,
        datos.correo,
        datos.edad,
        datos.peso,
        datos.estatura,
        datos.presion_arterial,
        datos.nivel_energia || 5,
        JSON.stringify(datos.sintomas),
        datos.observaciones || null,
        datos.nombre_encuestador || null,
        datos.encuestador_id ? String(datos.encuestador_id) : null
      ]
    );
    const encuestaId = resultadoEncuesta.insertId;
    console.log("Encuesta guardada, ID:", encuestaId);

    // Obtener diagnóstico
    console.log("🤖 Obteniendo diagnóstico con OpenAI...");
    const diagnosticoResult = await obtenerDiagnosticoOpenAI(
      datos.sintomas,
      datos.peso,
      datos.estatura,
      datos.presion_arterial,
      datos.edad,
      datos.nivel_energia || 5,
      datos.observaciones || ''
    );
    console.log("✅ Diagnóstico obtenido correctamente");

    // Guardar diagnóstico
    await connection.execute(
      'INSERT INTO diagnosticos (usuario_id, encuesta_id, diagnostico, recomendaciones) VALUES (?, ?, ?, ?)',
      [
        usuarioId,
        encuestaId,
        diagnosticoResult.diagnostico,
        diagnosticoResult.recomendaciones
      ]
    );
    console.log("✅ Diagnóstico guardado correctamente");

    // Confirmar transacción
    await connection.commit();
    console.log("✅ Transacción confirmada");

    return { 
      success: true, 
      encuestaId: encuestaId,
      diagnostico: diagnosticoResult.diagnostico,
      recomendaciones: diagnosticoResult.recomendaciones
    };
  } catch (error) {
    console.error("❌ Error en guardarEncuesta:", error);
    if (connection) {
      try {
        await connection.rollback();
        console.log("✅ Rollback realizado");
      } catch (rollbackError) {
        console.error("Error al hacer rollback:", rollbackError);
      }
    }
    throw error;
  } finally {
    if (connection) {
      try {
        connection.release();
        console.log("✅ Conexión liberada al pool");
      } catch (releaseError) {
        console.error("Error al liberar la conexión:", releaseError);
      }
    }
  }
}

export const guardarDiagnostico = async (encuestaId, diagnostico, recomendaciones, usuarioId) => {
  console.log("🔄 Iniciando guardarDiagnostico...");
  const connection = await pool.getConnection();
  
  try {
    // Verificar si existe la tabla diagnosticos
    const [tablaCheck] = await connection.query(`
      SELECT COUNT(*) as count 
      FROM information_schema.tables 
      WHERE table_schema = ? AND table_name = 'diagnosticos'
    `, [config.db.database]);
    
    if (tablaCheck[0].count === 0) {
      console.log("⚠️ La tabla 'diagnosticos' no existe. Creándola...");
      await connection.query(`
        CREATE TABLE IF NOT EXISTS diagnosticos (
          id INT AUTO_INCREMENT PRIMARY KEY,
          usuario_id INT NOT NULL,
          encuesta_id INT NOT NULL,
          diagnostico TEXT NOT NULL,
          recomendaciones TEXT,
          fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (encuesta_id) REFERENCES encuestas(id),
          FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id)
        )
      `);
      console.log("✅ Tabla 'diagnosticos' creada");
    }

    // Si no se proporciona usuarioId, intentamos obtenerlo de la encuesta
    if (!usuarioId) {
      const [encuestaResult] = await connection.query(
        `SELECT usuario_id FROM encuestas WHERE id = ?`,
        [encuestaId]
      );
      
      if (encuestaResult.length > 0) {
        usuarioId = encuestaResult[0].usuario_id;
        console.log("✅ Usuario ID obtenido de la encuesta:", usuarioId);
      } else {
        throw new Error(`No se encontró la encuesta con ID: ${encuestaId}`);
      }
    }

    console.log("💾 Guardando diagnóstico para encuesta:", encuestaId, "y usuario:", usuarioId);
    await connection.execute(
      `INSERT INTO diagnosticos (usuario_id, encuesta_id, diagnostico, recomendaciones)
       VALUES (?, ?, ?, ?)`,
      [usuarioId, encuestaId, diagnostico, recomendaciones]
    );
    console.log("✅ Diagnóstico guardado exitosamente");
  } catch (error) {
    console.error("❌ Error en guardarDiagnostico:", error);
    console.error("Stack trace:", error.stack);
    throw error;
  } finally {
    connection.release();
  }
};

export const obtenerEncuesta = async (encuestaId) => {
  console.log("🔍 Iniciando obtenerEncuesta...");
  const connection = await pool.getConnection();
  
  try {
    console.log("📊 Buscando encuesta con ID:", encuestaId);
    const [rows] = await connection.execute(
      `SELECT e.*, u.nombre, u.apellido, u.identificacion, u.telefono, u.correo
       FROM encuestas e
       JOIN usuarios u ON e.usuario_id = u.usuario_id
       WHERE e.id = ?`,
      [encuestaId]
    );

    if (rows.length === 0) {
      console.error("❌ No se encontró la encuesta");
      throw new Error('Encuesta no encontrada');
    }

    const encuesta = rows[0];
    try {
      encuesta.sintomas = JSON.parse(encuesta.sintomas);
    } catch (e) {
      console.warn("⚠️ Error al parsear los síntomas JSON:", e);
      encuesta.sintomas = [];
    }
    console.log("✅ Encuesta encontrada y procesada");

    return encuesta;
  } catch (error) {
    console.error("❌ Error en obtenerEncuesta:", error);
    console.error("Stack trace:", error.stack);
    throw error;
  } finally {
    connection.release();
  }
};

export const obtenerDiagnostico = async (encuestaId) => {
  console.log("🔍 Iniciando obtenerDiagnostico...");
  const connection = await pool.getConnection();
  
  try {
    console.log("📊 Buscando diagnóstico para encuesta ID:", encuestaId);
    const [rows] = await connection.execute(
      `SELECT d.*, u.nombre, u.apellido, u.identificacion
       FROM diagnosticos d
       JOIN encuestas e ON d.encuesta_id = e.id
       JOIN usuarios u ON d.usuario_id = u.usuario_id
       WHERE d.encuesta_id = ?`,
      [encuestaId]
    );
    
    if (rows.length === 0) {
      console.log("⚠️ No se encontró diagnóstico para la encuesta ID:", encuestaId);
      return null;
    }
    
    console.log("✅ Diagnóstico encontrado");
    return rows[0];
  } catch (error) {
    console.error("❌ Error en obtenerDiagnostico:", error);
    console.error("Stack trace:", error.stack);
    throw error;
  } finally {
    connection.release();
  }
};