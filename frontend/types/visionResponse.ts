import { Attachment } from "./attachment";

export interface VisionResponse {
  chat_id: number;
  message: string;
  attachments: Attachment[];
}