import { Attachment } from "./attachment";

export interface MessageSource {
  document_id: number;
  document_name: string;
  page_number: number | null;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  attachments?: Attachment[];
  sources?: MessageSource[];
}