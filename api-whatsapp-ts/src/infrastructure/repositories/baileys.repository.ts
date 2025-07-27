import * as Baileys from "@whiskeysockets/baileys";
import LeadExternal from "../../domain/lead-external.repository";
import pino from "pino";
import fs from 'fs';
import path from 'path';
import axios from 'axios';

export class BaileysTransporter implements LeadExternal {
  private sessionName: string = "tokens/default";
  public connection: Baileys.WASocket | null = null;
  public connectionState: Partial<Baileys.ConnectionState> | null = null;
  private isEnd: boolean = false;
  private closedMessage: string = "Connection closed";
  private onReady: Array<(connection: Baileys.WASocket) => void> = [];
  private qrCode: string | null = null;
  private isReconnecting: boolean = false;
  private isConnected: boolean = false;
  private webhook_url: string = process.env.WEBHOOK_URL || 'http://localhost:8000/webhook/whatsapp';

  constructor(sessionName: string = "default", private baileys: typeof Baileys = Baileys) {
    this.sessionName = `tokens/${sessionName}`;
    // Asegurarse de que el directorio de tokens exista
    const tokenDir = path.join(process.cwd(), this.sessionName);
    if (!fs.existsSync(tokenDir)) {
      fs.mkdirSync(tokenDir, { recursive: true });
    }
    this.start();
  }

  private async getAuth(): Promise<any> {
    try {
      return await this.baileys.useMultiFileAuthState(this.sessionName);
    } catch (error) {
      console.log(error);
      // Si hay un error al cargar el estado de autenticación, creamos uno nuevo
      this.cleanAuthFiles();
      return await this.baileys.useMultiFileAuthState(this.sessionName);
    }
  }

  // Método para limpiar los archivos de autenticación
  private cleanAuthFiles(): void {
    try {
      const tokensPath = path.join(process.cwd(), this.sessionName);
      
      if (fs.existsSync(tokensPath)) {
        const files = fs.readdirSync(tokensPath);
        for (const file of files) {
          const filePath = path.join(tokensPath, file);
          fs.unlinkSync(filePath);
          console.log(`Archivo eliminado: ${filePath}`);
        }
        console.log('Archivos de autenticación eliminados correctamente');
      } else {
        console.log('No existe directorio de tokens, se creará uno nuevo');
        fs.mkdirSync(tokensPath, { recursive: true });
      }
    } catch (error) {
      console.error('Error al limpiar archivos de autenticación:', error);
    }
  }

  set onready(cb: (conection: Baileys.WASocket) => void) {
    if (this.connectionState?.connection == "open") cb(this.connection!);
    this.onReady.push(cb);
  }

  // Método para obtener el código QR
  getQrCode(): string | null {
    return this.qrCode;
  }

  // Método para reiniciar la conexión (desconectar y volver a conectar)
  restart(): void {
    console.log("Reiniciando la conexión y forzando un nuevo QR...");
    
    // Evitamos reiniciar si ya estamos en proceso de reconexión
    if (this.isReconnecting) {
      console.log("Ya hay una reconexión en progreso, esperando...");
      return;
    }
    
    this.isReconnecting = true;
    this.isConnected = false;
    
    // Desconectar limpiamente
    if (this.connection) {
      try {
        this.isEnd = true;
        this.connection.end(undefined);
        console.log("Conexión finalizada correctamente");
      } catch (error) {
        console.error("Error al finalizar la conexión:", error);
      }
    }
    
    // Limpiamos los archivos de autenticación
    this.cleanAuthFiles();
    
    // Reiniciamos variables
    this.qrCode = null;
    this.isEnd = false;
    
    // Esperamos un poco antes de iniciar nueva conexión
    setTimeout(() => {
      console.log("Iniciando nueva conexión...");
      this.connection = null;
      this.connectionState = null;
      this.start();
      this.isReconnecting = false;
    }, 2000);
  }

  async start(socketConfig: Baileys.UserFacingSocketConfig = {} as any) {
    try {
      // Si ya estamos conectados, no necesitamos volver a iniciar
      if (this.isConnected && this.connection) {
        console.log("Ya existe una conexión activa");
        return;
      }
      
      console.log("Iniciando conexión a WhatsApp...");
      
      const { saveCreds, state } = await this.getAuth();

      this.connection = this.baileys.makeWASocket({
        printQRInTerminal: true, // Esto imprime el QR en la terminal
        browser: this.baileys.Browsers.macOS("Desktop"),
        //@ts-ignore
        logger: pino({ level: "silent" }),
        ...socketConfig,
        auth: socketConfig.auth || state,
      });

      // Manejar actualizaciones de credenciales
      this.connection.ev.on("creds.update", async (creds) => {
        // Evitar guardado frecuente de credenciales
        if (this.isConnected) {
          // Solo guardar cada 30 segundos si ya estamos conectados
          saveCreds();
        } else {
          saveCreds();
        }
      });

      // Manejar actualizaciones de conexión
      this.connection.ev.on("connection.update", (state) => {
        this.connectionState = state;
        
        // Almacenar el código QR cuando esté disponible
        if (state.qr && !this.isConnected) {
          this.qrCode = state.qr;
          console.log("==============================================");
          console.log("📱 Nuevo código QR generado!");
          console.log("📲 Accede a http://localhost:3001/qr para escanearlo");
          console.log("==============================================");
        }
        
        if (state.connection === "open") {
          this.isConnected = true;
          this.qrCode = null; // Limpiar el QR cuando se conecta
          this.onReady.forEach((cb) => cb(this.connection!));
          
          if (!this.isReconnecting) {
            console.log("==============================================");
            console.log("✅ Conexión exitosa! WhatsApp conectado.");
            console.log("==============================================");
          }
        }

        if (state.connection !== "close") return;
        
        if (this.isEnd) {
          console.log(this.closedMessage);
          return;
        }
        
        if (!this.isEnd && !this.isReconnecting) {
          this.isConnected = false;
          this.reconnect();
        }
      });

      // NUEVO: Configurar el manejador de mensajes entrantes
      this.connection.ev.on("messages.upsert", async (m) => {
        try {
          const mensaje = m.messages[0];
          
          // Solo procesar mensajes recibidos, no enviados por nosotros
          if (mensaje.key.fromMe) return;
          
          // Verificar que sea un mensaje de texto
          if (!mensaje.message?.conversation && !mensaje.message?.extendedTextMessage?.text) return;
          
          const from = mensaje.key.remoteJid || '';
          const text = mensaje.message.conversation || 
                      mensaje.message.extendedTextMessage?.text || '';
          
          console.log(`Mensaje recibido de ${from}: ${text}`);
          
          // Intentar buscar el audit_id asociado con este número de teléfono
          // Esta parte la deberías adaptar según tu lógica de negocio
          
          // Reenviar al webhook
          try {
            const response = await axios.post(this.webhook_url, {
              message: text,
              phone_number: from.replace('@c.us', ''),
              audit_id: null  // Aquí podrías pasar el audit_id si lo tienes
            });
            
            console.log('Mensaje reenviado al webhook:', response.data);
          } catch (error) {
            console.error('Error al reenviar mensaje al webhook:', error);
          }
          
        } catch (error) {
          console.error('Error al procesar mensaje entrante:', error);
        }
      });
    } catch (error) {
      console.error("Error al iniciar la conexión:", error);
      this.isReconnecting = false;
      this.isConnected = false;
    }
  }

  end() {
    if (!this.connection) return;
    
    this.isEnd = true;
    this.isConnected = false;
    try {
      this.connection.end(undefined);
    } catch (error) {
      console.error("Error al cerrar la conexión:", error);
    }
  }

  private reconnect(socketConfig: Baileys.UserFacingSocketConfig = {} as any) {
    if (this.isReconnecting) return;
    
    this.isReconnecting = true;
    this.isConnected = false;
    console.log("Reconectando...");
    
    setTimeout(() => {
      this.start(socketConfig);
      this.isReconnecting = false;
    }, 2000);
  }

  async sendMsg({
    message,
    phone,
  }: {
    message: string;
    phone: string;
  }): Promise<any> {
    try {
      if (!this.connection) {
        return Promise.reject("No hay conexión activa");
      }
      
      if (!this.isConnected) {
        return Promise.reject("WhatsApp no está conectado todavía");
      }
      
      const response = await this.connection.sendMessage(phone + "@c.us", {
        text: message,
      });
      return Promise.resolve(response);
    } catch (error) {
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
      if (!this.connection) {
        return Promise.reject("No hay conexión activa");
      }
      
      if (!this.isConnected) {
        return Promise.reject("WhatsApp no está conectado todavía");
      }

      // Determinar el tipo MIME basado en la extensión del archivo
      const mimetype = fileName.toLowerCase().endsWith('.pdf') 
        ? 'application/pdf' 
        : 'application/octet-stream';
      
      // Enviar como documento
      const response = await this.connection.sendMessage(phone + "@c.us", {
        document: buffer,
        mimetype: mimetype,
        fileName: fileName,
        caption: caption
      });
      
      return Promise.resolve(response);
    } catch (error) {
      console.error('Error al enviar media:', error);
      return Promise.reject(error);
    }
  }
}
