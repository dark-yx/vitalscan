import { Request, Response } from "express";
import { LeadCreate } from "../../application/lead.create";
import fs from 'fs';
import path from 'path';
import axios from 'axios';

class LeadCtrl {
  constructor(private readonly leadCreator: LeadCreate) {}

  public sendCtrl = async ({ body }: Request, res: Response) => {
    try {
      const { message, phone, pdfPath } = body;
      
      if (!message || !phone) {
        return res.status(400).send({ error: 'Se requieren los campos message y phone' });
      }

      // Verificar si el archivo PDF existe cuando se proporciona
      let validPdfPath = pdfPath;
      if (pdfPath) {
        // Comprobar si es una ruta absoluta o relativa
        if (!path.isAbsolute(pdfPath)) {
          // Si es relativa, convertirla a absoluta desde la raíz del proyecto
          validPdfPath = path.join(process.cwd(), pdfPath);
        }

        // Verificar si el archivo existe
        if (!fs.existsSync(validPdfPath)) {
          console.warn(`El archivo PDF no existe en la ruta: ${validPdfPath}`);
          validPdfPath = undefined;
        } else {
          console.log(`PDF encontrado: ${validPdfPath}`);
        }
      }
      
      const response = await this.leadCreator.sendMessageAndSave({ 
        message, 
        phone, 
        pdfPath: validPdfPath 
      });
      
      return res.send(response);
    } catch (error) {
      console.error('Error en sendCtrl:', error);
      return res.status(500).send({ error: 'Error interno del servidor' });
    }
  };

  // Nuevo método para manejar mensajes entrantes de WhatsApp
  public handleIncomingMessage = async (req: Request, res: Response) => {
    try {
      console.log('Mensaje entrante de WhatsApp recibido:', req.body);
      
      // Extraer datos del mensaje
      const { message, from, audit_id } = req.body;
      
      if (!message || !from) {
        return res.status(400).send({ error: 'Se requieren los campos message y from' });
      }
      
      // Formatear el número de teléfono (quitar @c.us si existe)
      const phone_number = from.replace('@c.us', '');
      
      console.log(`Reenviando mensaje al webhook. Phone: ${phone_number}, Message: ${message}, AuditID: ${audit_id || 'no proporcionado'}`);
      
      // Reenviar al webhook
      try {
        const webhookUrl = process.env.WEBHOOK_URL || 'http://localhost:8000/webhook/whatsapp';
        const response = await axios.post(webhookUrl, {
          message,
          phone_number,
          audit_id
        });
        
        console.log('Respuesta del webhook:', response.data);
        
        return res.send({
          status: 'success',
          message: 'Mensaje reenviado al webhook',
          webhook_response: response.data
        });
      } catch (error) {
        console.error('Error al reenviar al webhook:', error);
        return res.status(500).send({ 
          error: 'Error al reenviar al webhook',
          details: error instanceof Error ? error.message : 'Error desconocido'
        });
      }
    } catch (error) {
      console.error('Error en handleIncomingMessage:', error);
      return res.status(500).send({ error: 'Error interno del servidor' });
    }
  };
}

export default LeadCtrl;
