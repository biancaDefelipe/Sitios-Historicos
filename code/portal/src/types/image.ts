export interface Image {
  id: number;
  public_url: string;
  alt_text: string;
  description: string | null;
  order: number;
  is_cover: boolean;
}