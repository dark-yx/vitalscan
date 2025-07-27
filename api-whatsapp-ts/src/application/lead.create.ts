import LeadExternal from "../domain/lead-external.repository";
import LeadRepository from "../domain/lead.repository";
import fs from 'fs';

export class LeadCreate {
  private leadRepository: LeadRepository;
  private leadExternal: LeadExternal;
  constructor(respositories: [LeadRepository, LeadExternal]) {
    const [leadRepository, leadExternal] = respositories;
    this.leadRepository = leadRepository;
    this.leadExternal = leadExternal;
  }

  public async sendMessageAndSave({
    message,
    phone,
    pdfPath
  }: {
    message: string;
    phone: string;
    pdfPath?: string;
  }) {
    try {
      // Guardar en la base de datos
      const responseDbSave = await this.leadRepository.save({ message, phone });//TODO DB
      
      // Variable para almacenar la respuesta del mensaje enviado
      let messageSentResponse = null;
      
      // Verificar si hay un archivo PDF para enviar
      if (pdfPath && fs.existsSync(pdfPath)) {
        try {
          // Leer el archivo PDF
          const mediaBuffer = fs.readFileSync(pdfPath);
          
          // Enviar el archivo como documento con el mensaje como caption
          messageSentResponse = await this.leadExternal.sendMedia({
            phone,
            buffer: mediaBuffer,
            fileName: pdfPath.split('/').pop() || 'auditoria.pdf',
            caption: message
          });
          
          console.log('Mensaje con PDF enviado correctamente');
        } catch (error) {
          console.error('Error al enviar PDF:', error);
          // Si falla el envío con PDF, intentar enviar solo el mensaje de texto
          messageSentResponse = await this.leadExternal.sendMsg({ message, phone });
          console.log('Fallback: Mensaje de texto enviado después de error con PDF');
        }
      } else {
        // Si no hay PDF, enviar solo mensaje de texto
        messageSentResponse = await this.leadExternal.sendMsg({ message, phone });
        console.log('Mensaje de texto enviado correctamente');
      }
      
      return { responseDbSave, messageSentResponse };
    } catch (error) {
      console.error('Error en sendMessageAndSave:', error);
      throw error;
    }
  }
}
