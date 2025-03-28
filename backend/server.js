import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import encuestaRoutes from "../routes/encuestaRoutes.js";
import { verificarYCrearTablas, pool } from './db.js';
import { config } from './config.js';

// Configurar __dirname en ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json());

// Servir archivos estáticos desde la carpeta "frontend"
app.use(express.static(path.join(__dirname, "../frontend")));

// Ruta para servir el "index.html" por defecto
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "../frontend/index.html"));
});

// Ruta para manejar cualquier otra ruta y redirigir a index.html
app.get("*", (req, res) => {
  res.redirect("/");
});

app.use("/api", encuestaRoutes);

// Verificar conexión a la base de datos y estructura de tablas
async function inicializarBaseDeDatos() {
  try {
    console.log("🔄 Verificando conexión a la base de datos...");
    const connection = await pool.getConnection();
    console.log("✅ Conexión a la base de datos establecida");
    connection.release();

    // Verificar y crear tablas si es necesario
    await verificarYCrearTablas();
    
    console.log("✅ Inicialización de base de datos completada");
  } catch (error) {
    console.error("❌ Error al inicializar la base de datos:", error.message);
    console.error("Stack trace:", error.stack);
    process.exit(1); // Salir si no podemos conectar a la BD
  }
}

// Iniciar servidor
inicializarBaseDeDatos().then(() => {
  const PORT = config.port || 3000;
  app.listen(PORT, () => {
    console.log(`🚀 Servidor iniciado en http://localhost:${PORT}`);
    console.log(`📂 Archivos estáticos servidos desde la carpeta 'frontend'`);
  });
});
