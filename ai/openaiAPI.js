import OpenAI from 'openai';
import { config } from '../backend/config.js';

console.log("🔑 Inicializando OpenAI API...");

// Verificar que la API key esté definida
if (!config.openai.apiKey) {
  console.error("❌ Error: API key de OpenAI no definida en la configuración");
  throw new Error("API key de OpenAI no definida");
}

const openai = new OpenAI({
  apiKey: config.openai.apiKey
});

const ASSISTANT_ID = config.openai.assistantId;

// Verificar que el ID del asistente esté definido
if (!ASSISTANT_ID) {
  console.warn("⚠️ Advertencia: ASSISTANT_ID no definido, se usará el modelo GPT-4o-mini directamente");
}

// Función para obtener diagnóstico usando el asistente pre-entrenado
export async function obtenerDiagnosticoConAsistente(sintomas, peso, estatura, presion, edad, nivel_energia = 5, observaciones = "") {
  console.log("🤖 Iniciando obtención de diagnóstico usando asistente pre-entrenado...");
  
  // Calcular IMC
  const imc = peso / (estatura * estatura);
  
  const promptDiagnostico = `
  Basado en la informacion de los documentos adjuntos y como distribuidor experto en bienestar, nutrición y alimentación saludable, analiza los siguientes datos del usuario y proporciona un diagnóstico resumido:

  Estos son los datos a analizar:
  - Edad: ${edad} años,
  - Peso: ${peso} kg,
  - Estatura: ${estatura} m,
  - IMC: ${imc.toFixed(2)},
  - Presión arterial: ${presion},
  - Nivel de energía: ${nivel_energia}/10,
  - Síntomas Reportados: ${sintomas.map(s => `- ${s}`).join('\n')},
  - Observaciones Adicionales: ${observaciones},

  Para realizar este diagnóstico, sigue los siguientes pasos:
  1. Estrictamente debes realizar el diagnosito tomando de referencia la informacion de los documentos adjuntos y los datos proporcionados por el usuario.
  2. No inventes nada, solo debes usar la informacion proporcionada, como un experto en nutrición y alimentación saludable.
  3. Analiza las posibles causas y condiciones relacionadas con los síntomas reportados.
  4. Identifica los factores de riesgos y todo lo que se pueda relacionar con el nivel de salud, nutricion y bienestar del usuario.

  Presenta todo en un parrafo resumido, compacto, personalizado, claro y entendible para ${nombre}.
  `;

  try {
    // Crear un thread para la conversación
    const thread = await openai.beta.threads.create();
    console.log("✅ Thread creado:", thread.id);

    // Obtener diagnóstico
    await openai.beta.threads.messages.create(thread.id, {
      role: "user",
      content: promptDiagnostico
    });

    const runDiagnostico = await openai.beta.threads.runs.create(thread.id, {
      assistant_id: ASSISTANT_ID
    });

    // Esperar a que el run se complete
    let runStatus = await openai.beta.threads.runs.retrieve(thread.id, runDiagnostico.id);
    while (runStatus.status === "in_progress" || runStatus.status === "queued") {
      await new Promise(resolve => setTimeout(resolve, 1000));
      runStatus = await openai.beta.threads.runs.retrieve(thread.id, runDiagnostico.id);
    }

    if (runStatus.status === "completed") {
      const messages = await openai.beta.threads.messages.list(thread.id);
      const diagnostico = messages.data[0].content[0].text.value;

      // Obtener recomendaciones
      const promptRecomendaciones = `
      Basado en el siguiente diagnóstico, proporciona recomendaciones específicas, personalizadas y accionables para ${nombre}:

      Diagnóstico: ${diagnostico}

      Por favor, considera los siguientes puntos para proporcionar las recomendaciones:
      1. Debe estar basado estrictamente en el diagnostico y la informacion de los documentos adjuntos.
      2. Aborda la importancia de empezar cambios positivos desde el nivel de estilo de vida, nutrición y alimentación.
      3. Aborda lo hábitos alimenticios recomendados, actividades físicas sugeridas y productos de herbalife recomendados.
      4. No debes inventar nada, solo debes usar la informacion proporcionada, como un experto en nutrición y alimentación saludable.
      5. Debes recomendar los productos herbalife especificos que sean necesarios para el usuario, no debes recomendar todos los productos de herbalife, y solo los que tienes en los documentos adjuntos, con sus precios correspondientes.
      6. La recomendacion debe generar fomo e incentivar la compra de los productos herbalife, no debes ser ambiguo, debes ser claro y directo.

  Presenta todo en un parrafo resumido, compacto, personalizado, claro y entendible para ${nombre}.
      `;

      await openai.beta.threads.messages.create(thread.id, {
        role: "user",
        content: promptRecomendaciones
      });

      const runRecomendaciones = await openai.beta.threads.runs.create(thread.id, {
        assistant_id: ASSISTANT_ID
      });

      runStatus = await openai.beta.threads.runs.retrieve(thread.id, runRecomendaciones.id);
      while (runStatus.status === "in_progress" || runStatus.status === "queued") {
        await new Promise(resolve => setTimeout(resolve, 1000));
        runStatus = await openai.beta.threads.runs.retrieve(thread.id, runRecomendaciones.id);
      }

      if (runStatus.status === "completed") {
        const messages = await openai.beta.threads.messages.list(thread.id);
        const recomendaciones = messages.data[0].content[0].text.value;

        // Eliminar el thread
        await openai.beta.threads.del(thread.id);
        console.log("✅ Thread eliminado");

        return {
          diagnostico,
          recomendaciones
        };
      }
    }
    throw new Error(`El run no se completó correctamente. Estado: ${runStatus.status}`);
  } catch (error) {
    console.error("❌ Error al usar el asistente:", error);
    throw error;
  }
}

// Función principal para obtener diagnóstico
export async function obtenerDiagnosticoOpenAI(sintomas, peso, estatura, presion, edad, nivel_energia = 5, observaciones = "") {
  console.log("🤖 Iniciando obtención de diagnóstico...");
  console.log("📊 Datos recibidos para diagnóstico:");
  console.log(`  → Edad: ${edad} años`);
  console.log(`  → Peso: ${peso} kg`);
  console.log(`  → Estatura: ${estatura} m`);
  console.log(`  → Presión: ${presion}`);
  console.log(`  → Nivel de energía: ${nivel_energia}/10`);
  console.log(`  → Síntomas: ${sintomas.join(", ")}`);
  
  // Calcular IMC
  const imc = peso / (estatura * estatura);
  console.log(`  → IMC calculado: ${imc.toFixed(2)}`);

  const promptDiagnostico = `
  Como experto en bienestar y nutrición, analiza los siguientes datos del paciente y proporciona un diagnóstico detallado en formato de párrafo continuo:

  **Datos del Paciente:**
  - Edad: ${edad} años
  - Peso: ${peso} kg
  - Estatura: ${estatura} m
  - IMC: ${imc.toFixed(2)}
  - Presión arterial: ${presion}
  - Nivel de energía: ${nivel_energia}/10
  
  **Síntomas Reportados:**
  ${sintomas.map(s => `- ${s}`).join('\n')}
  
  **Observaciones Adicionales:**
  ${observaciones || "Ninguna"}

  Por favor, proporciona un diagnóstico detallado en formato de párrafo continuo que incluya:
  1. Análisis de los síntomas reportados
  2. Posibles condiciones relacionadas
  3. Factores de riesgo identificados

  IMPORTANTE: 
  - Escribe todo en un solo párrafo continuo
  - No uses viñetas ni listas
  - No uses títulos ni subtítulos
  - Asegúrate de que el diagnóstico se complete completamente
  - Concluye con una recomendación clara sobre la necesidad de consultar a un profesional de la salud
  - Mantén un tono profesional pero accesible
  - No cortes el texto a mitad de una idea
  `;

  try {
    console.log("📤 Enviando solicitud de diagnóstico a OpenAI...");
    const startTime = Date.now();
    
    const responseDiagnostico = await Promise.race([
      openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { 
            role: "system", 
            content: "Eres un experto en bienestar y nutrición especializado en diagnósticos preliminares. Proporciona diagnósticos en formato de párrafo continuo, sin estructuras ni listas. Asegúrate de que cada diagnóstico se complete completamente y concluya con una recomendación clara sobre la necesidad de consultar a un profesional de la salud." 
          },
          { 
            role: "user", 
            content: promptDiagnostico 
          }
        ],
        max_tokens: 500,
        temperature: 0.7
      }),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Timeout en la llamada a OpenAI')), 30000)
      )
    ]);

    const diagnostico = responseDiagnostico.choices[0].message.content;

    // Obtener recomendaciones
    const promptRecomendaciones = `
    Basado en el siguiente diagnóstico, proporciona recomendaciones específicas y accionables en formato de párrafo continuo:

    **Diagnóstico:**
    ${diagnostico}

    Por favor, proporciona recomendaciones que incluyan:
    1. Cambios en el estilo de vida
    2. Hábitos alimenticios recomendados
    3. Actividad física sugerida
    4. Suplementos o productos recomendados (si aplica)

    IMPORTANTE:
    - Escribe todo en un solo párrafo continuo
    - No uses viñetas ni listas
    - No uses títulos ni subtítulos
    - Asegúrate de que las recomendaciones se completen completamente
    - Mantén un tono motivador y accesible
    - No cortes el texto a mitad de una idea
    - Concluye con una nota positiva y motivadora
    - Incluye recomendaciones específicas de productos Herbalife cuando sea relevante
    `;

    console.log("📤 Enviando solicitud de recomendaciones a OpenAI...");
    const responseRecomendaciones = await Promise.race([
      openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { 
            role: "system", 
            content: "Eres un experto en salud, bienestar y Herbalife. Proporciona recomendaciones en formato de párrafo continuo, sin estructuras ni listas. Asegúrate de que cada recomendación se complete completamente y concluya con una nota positiva y motivadora. Incluye recomendaciones específicas de productos Herbalife cuando sea relevante." 
          },
          { 
            role: "user", 
            content: promptRecomendaciones 
          }
        ],
        max_tokens: 500,
        temperature: 0.7
      }),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Timeout en la llamada a OpenAI')), 30000)
      )
    ]);

    const responseTime = Date.now() - startTime;
    console.log(`✅ Respuestas recibidas de OpenAI en ${responseTime}ms`);

    return {
      diagnostico: diagnostico,
      recomendaciones: responseRecomendaciones.choices[0].message.content
    };

  } catch (error) {
    console.error("❌ Error al obtener diagnóstico de OpenAI:", error);
    if (error.message === 'Timeout en la llamada a OpenAI') {
      throw new Error("La solicitud a OpenAI tardó demasiado tiempo. Por favor, intente nuevamente.");
    }
    throw new Error("Error al obtener el diagnóstico. Por favor, intente nuevamente más tarde.");
  }
}
