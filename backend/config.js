import dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Cargar variables de entorno desde el archivo .env en la raíz del proyecto
dotenv.config({ path: join(__dirname, "../.env") });

// Verificar que las variables de entorno necesarias estén definidas
const requiredEnvVars = [
  "DB_HOST",
  "DB_USER",
  "DB_PASSWORD",
  "DB_NAME",
  "OPENAI_API_KEY",
  "ASSISTANT_ID"
];

const missingEnvVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingEnvVars.length > 0) {
  throw new Error(`Faltan las siguientes variables de entorno: ${missingEnvVars.join(', ')}`);
}

console.log("✅ Variables de entorno cargadas correctamente");

// Configuración de la base de datos
const dbConfig = {
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

// Configuración de OpenAI
const openaiConfig = {
  apiKey: process.env.OPENAI_API_KEY,
  assistantId: process.env.ASSISTANT_ID
};

// Configuración del servidor
const serverConfig = {
  port: process.env.PORT || 3000,
  host: process.env.HOST || 'localhost'
};

// Configuración general
const config = {
  db: dbConfig,
  openai: openaiConfig,
  server: serverConfig
};

export { config };

// Verificar que las variables de entorno necesarias estén definidas
if (!config.openai.apiKey) {
  console.error("❌ Error: OPENAI_API_KEY no está definida en el archivo .env");
  process.exit(1);
}

if (!config.openai.assistantId) {
  console.error("❌ Error: ASSISTANT_ID no está definido en el archivo .env");
  process.exit(1);
}

console.log("✅ Configuración cargada correctamente");

// export const huggingFaceApiKey = process.env.HUGGINGFACE_API_KEY;
export const openaiApiKey = process.env.OPENAI_API_KEY; // Agregar clave de OpenAI