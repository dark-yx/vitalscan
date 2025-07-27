import { image as imageQr } from "qr-image";
import LeadExternal from "../../domain/lead-external.repository";
import { create, Whatsapp } from "venom-bot";
import fs from 'fs';
import path from 'path';

export class VenomTransporter implements LeadExternal {
  intance: Whatsapp | undefined;

  constructor() {
    create({ session: "session" }).then((client) => (this.intance = client));
  }
  
  sendMsg(lead: { message: string; phone: string }): Promise<any> {
    try {
      const { message, phone } = lead;
      const response = this.intance?.sendText(`${phone}@c.us`, message);
      return Promise.resolve(response);
    } catch (error: any) {
      return Promise.reject(error);
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
      if (!this.intance) {
        return Promise.reject("No hay instancia de Venom disponible");
      }
      
      // Crear directorio temporal si no existe
      const tmpDir = path.join(process.cwd(), 'tmp');
      if (!fs.existsSync(tmpDir)) {
        fs.mkdirSync(tmpDir, { recursive: true });
      }
      
      // Guardar buffer a archivo temporal
      const filePath = path.join(tmpDir, fileName);
      fs.writeFileSync(filePath, buffer);
      
      console.log(`Archivo guardado en: ${filePath}`);
      console.log(`Intentando enviar a: ${phone}@c.us`);
      
      // Enviar el archivo como documento
      const response = await this.intance.sendFile(
        `${phone}@c.us`,
        filePath,
        fileName,
        caption || ''
      );
      
      // Eliminar archivo temporal después de enviar
      try {
        fs.unlinkSync(filePath);
      } catch (unlinkError) {
        console.error('Error al eliminar archivo temporal:', unlinkError);
      }
      
      return Promise.resolve(response);
    } catch (error: any) {
      console.error('Error al enviar media:', error);
      return Promise.reject(error);
    }
  }
}
