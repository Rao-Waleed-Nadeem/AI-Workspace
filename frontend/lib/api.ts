const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http:///http://127.0.0.1:8000";

export async function getHelloMessage() {
  const response = await fetch(`${API_URL}/`);

  return response.json();
}
