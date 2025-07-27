import "dotenv/config";
import axios from "axios";
import LeadExternal from "../../domain/lead-external.repository";
import fs from 'fs';

const META_TOKEN = process.env.META_TOKEN || "";
const META_ID_NUMBER = process.env.META_ID_NUMBER || "";
const URL = `https://graph.facebook.com/v13.0/${META_ID_NUMBER}/messages`;

export default class MetaRepository implements LeadExternal {
  async sendMsg({
    message,
    phone,
  }: {
    message: string;
    phone: string;
  }): Promise<any> {
    try{
        const body = this.parseBody({message, phone})
        const response = await axios.post(URL,body, {
          headers: {
            Authorization: `Bearer ${META_TOKEN}`,
          },
        }) as any;
    
        return response.data
    }catch(e){
        return Promise.resolve(e)
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
      // Para Meta WhatsApp API, primero necesitamos subir el archivo multimedia
      // y luego usamos el ID para enviarlo como mensaje
      
      // Construir el cuerpo de la solicitud para medios
      const body = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "document",
        "document": {
          "link": "", // Aquí iría un enlace público al archivo
          "caption": caption || fileName
        }
      };
      
      console.log(`Intentando enviar media a ${phone}`);
      console.log(`Media no implementado completamente en Meta API`);
      
      // En un entorno real, necesitaríamos:
      // 1. Subir el archivo a un almacenamiento accesible con URL pública
      // 2. Usar esa URL en el campo "link" de document
      
      return Promise.resolve({
        success: false,
        message: "Envío de archivos no implementado completamente en Meta API"
      });
    } catch (e) {
      console.error(`Error en sendMedia: ${e}`);
      return Promise.resolve({
        success: false,
        error: e
      });
    }
  }

  private parseBody ({message, phone}:{message:string,phone:string}){
    const body = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {
                "code": "en_US"
            }
        }
    }
    return body
  }
}
