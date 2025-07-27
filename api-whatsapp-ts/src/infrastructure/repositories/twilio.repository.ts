import "dotenv/config";
import { Twilio } from "twilio";
import LeadExternal from "../../domain/lead-external.repository";

const accountSid = process.env.TWILIO_SID || "";
const authToken = process.env.TWILIO_TOKEN || "";
const fromNumber = process.env.TWILIO_FROM || "";

export default class TwilioService extends Twilio implements LeadExternal {
  constructor() {
    super(accountSid, authToken);
  }
  async sendMsg({
    message,
    phone,
  }: {
    message: string;
    phone: string;
  }): Promise<any> {
    try{
        const parsePhone = `+${phone}`
        const mapMsg = { body: message, to: parsePhone, from:fromNumber };
        const response = await this.messages.create(mapMsg);
        return response
    }catch(e){
        console.log(e)
        return Promise.reject(e)
    }
  }

  async sendMedia({
    phone,
    buffer,
    fileName,
    caption
  }: {
    phone: string;
    buffer: Buffer;
    fileName: string;
    caption?: string;
  }): Promise<any> {
    try {
      const parsePhone = `+${phone}`;
      
      // Para enviar medios con Twilio, necesitamos una URL pública
      // En un entorno real, guardaríamos temporalmente el archivo
      // o lo subiríamos a un servicio de almacenamiento
      
      console.log(`Intentando enviar media a ${parsePhone}`);
      console.log(`Media no implementado completamente en Twilio API`);
      
      // Implementación básica para cumplir con la interfaz
      return Promise.resolve({
        success: false,
        message: "Envío de archivos no implementado completamente en Twilio API"
      });
    } catch (e) {
      console.error(`Error en sendMedia: ${e}`);
      return Promise.reject(e);
    }
  }
}

