import { Attachment } from "./attachment";

export interface Message  {
  id: string;
  role: "user" | "assistant";
  content: string;
  attachments?: Attachment[];
};
