import { obtenerDiagnosticoOpenAI } from "../ai/openaiAPI.js";

export const submitSurvey = async (req, res) => {
  console.log("📝 Recibida nueva solicitud de encuesta");
  
  try {
    // Validar campos requeridos
    const camposRequeridos = [
      'nombre', 'apellido', 'identificacion', 'telefono', 'correo',
      'edad', 'peso', 'estatura', 'presion_arterial', 'sintomas'
    ];

    const camposFaltantes = camposRequeridos.filter(campo => !req.body[campo]);
    if (camposFaltantes.length > 0) {
      return res.status(400).json({
        success: false,
        error: 'Campos requeridos faltantes',
        campos: camposFaltantes
      });
    }

    console.log("🤖 Obteniendo diagnóstico con OpenAI...");
    const diagnosticoResult = await obtenerDiagnosticoOpenAI(
      req.body.sintomas,
      req.body.peso,
      req.body.estatura,
      req.body.presion_arterial,
      req.body.edad,
      req.body.nivel_energia || 5,
      req.body.observaciones || ''
    );
    console.log("✅ Diagnóstico obtenido correctamente");

    // Preparar datos del paciente
    const datosPaciente = {
      nombre: req.body.nombre,
      apellido: req.body.apellido,
      identificacion: req.body.identificacion,
      telefono: req.body.telefono,
      correo: req.body.correo,
      edad: req.body.edad,
      peso: req.body.peso,
      estatura: req.body.estatura,
      presion_arterial: req.body.presion_arterial,
      nivel_energia: req.body.nivel_energia || 5,
      sintomas: req.body.sintomas,
      observaciones: req.body.observaciones || null
    };

    // Generar un ID único para la sesión
    const sessionId = Date.now().toString(36) + Math.random().toString(36).substr(2);

    // Preparar respuesta
    const response = {
      success: true,
      message: 'Diagnóstico generado correctamente',
      sessionId: sessionId,
      datosPaciente: datosPaciente,
      diagnostico: diagnosticoResult.diagnostico,
      recomendaciones: diagnosticoResult.recomendaciones
    };

    console.log("📤 Enviando respuesta al cliente:", {
      success: response.success,
      sessionId: response.sessionId,
      datosPaciente: response.datosPaciente,
      diagnosticoLength: response.diagnostico.length,
      recomendacionesLength: response.recomendaciones.length
    });

    res.json(response);
  } catch (error) {
    console.error('Error al procesar la encuesta:', error);
    res.status(500).json({
      success: false,
      error: 'Error al procesar la encuesta'
    });
  }
};

export async function getDiagnostico(req, res) {
  try {
    const { id } = req.params;
    console.log('🔍 Obteniendo diagnóstico para sesión ID:', id);

    // En este caso, como no estamos usando la base de datos,
    // simplemente devolvemos un error 404
    return res.status(404).json({
      success: false,
      error: 'Diagnóstico no encontrado'
    });

  } catch (error) {
    console.error('❌ Error al obtener el diagnóstico:', error);
    res.status(500).json({
      success: false,
      error: 'Error al obtener el diagnóstico'
    });
  }
}

export async function getEncuesta(req, res) {
  try {
    const { id } = req.params;
    console.log('🔍 Obteniendo datos de la sesión ID:', id);

    // En este caso, como no estamos usando la base de datos,
    // simplemente devolvemos un error 404
    return res.status(404).json({
      success: false,
      error: 'Datos no encontrados'
    });

  } catch (error) {
    console.error('❌ Error al obtener los datos:', error);
    res.status(500).json({
      success: false,
      error: 'Error al obtener los datos'
    });
  }
}
