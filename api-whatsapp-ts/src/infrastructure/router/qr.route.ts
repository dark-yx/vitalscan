import express, { Router, Request, Response } from "express";
import container from "../ioc";
import { BaileysTransporter } from "../repositories/baileys.repository";
import path from "path";
import fs from "fs";

const router: Router = Router();

/**
 * http://localhost/qr GET - Muestra la página HTML con el código QR
 */
router.get("/", (req: Request, res: Response) => {
  res.sendFile(path.join(process.cwd(), "src/infrastructure/views/qr.html"));
});

/**
 * http://localhost/qr/status GET - Devuelve el estado actual y el QR si está disponible
 */
router.get("/status", (req: Request, res: Response) => {
  const wsTransporter: BaileysTransporter = container.get("ws.transporter");
  const qrCode = wsTransporter.getQrCode();
  const connectionState = wsTransporter.connectionState;
  
  res.json({
    qr: qrCode,
    state: connectionState
  });
});

/**
 * http://localhost/qr/reset GET - Elimina las credenciales y fuerza un nuevo código QR
 */
router.get("/reset", (req: Request, res: Response) => {
  try {
    // Simplemente llamamos al método restart que ahora maneja todo el proceso
    const wsTransporter: BaileysTransporter = container.get("ws.transporter");
    wsTransporter.restart();
    
    // Enviamos respuesta inmediata para no bloquear al cliente
    res.json({ 
      success: true, 
      message: "Sesión en proceso de reinicio. El nuevo código QR estará disponible en unos segundos." 
    });
  } catch (error) {
    console.error("Error al reiniciar la sesión:", error);
    res.status(500).json({ 
      success: false, 
      message: "Error al reiniciar la sesión", 
      error: String(error) 
    });
  }
});

export { router }; 