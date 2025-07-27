import "dotenv/config"
import express from "express"
import cors from "cors"
import routes from "./infrastructure/router"
import path from "path"
import fs from "fs"

// Asegurar que el directorio tmp exista
const tmpDir = path.join(process.cwd(), 'tmp');
if (!fs.existsSync(tmpDir)) {
    fs.mkdirSync(tmpDir, { recursive: true });
    console.log('Directorio tmp creado:', tmpDir);
} else {
    console.log('Directorio tmp existente:', tmpDir);
}

const port = process.env.PORT || 3001
const app = express()

app.use(cors())
app.use(express.json())
app.use(express.static('tmp'))
app.use(express.static(path.join(__dirname, 'infrastructure/views')))
app.use(`/`,routes)

app.listen(port, () => {
  console.log(`=======================================================`)
  console.log(`🚀 API de WhatsApp iniciada en el puerto: ${port}`)
  console.log(`📱 Para escanear el código QR, visita: http://localhost:${port}/qr`)
  console.log(`=======================================================`)
})