export interface Attachment {
  id?: number;
  attachment_type: string;
  original_name: string;
  mime_type: string;
  storage_path: string;
  size: number;
}