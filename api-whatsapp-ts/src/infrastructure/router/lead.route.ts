import express, { Router } from "express";
import LeadCtrl from "../controller/lead.ctrl";
import container from "../ioc";
const router: Router = Router();

/**
 * http://localhost/lead POST - Envía un mensaje
 */
const leadCtrl: LeadCtrl = container.get("lead.ctrl");
router.post("/", leadCtrl.sendCtrl);

/**
 * http://localhost/lead/webhook POST - Recibe mensajes entrantes
 */
router.post("/webhook", leadCtrl.handleIncomingMessage);

export { router };
