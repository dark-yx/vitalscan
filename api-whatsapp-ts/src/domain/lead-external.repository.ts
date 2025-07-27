export default interface LeadExternal {
    sendMsg({message, phone}:{message:string, phone:string}):Promise<any>
    sendMedia(media: { 
        phone: string; 
        buffer: Buffer; 
        fileName: string; 
        caption?: string;
    }): Promise<any>
}