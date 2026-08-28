const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface User {
  id: number;
  email: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export async function register(email: string, password: string) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string" ? data.detail : "Registration failed",
    );
  }

  return data;
}

export async function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  const formData = new URLSearchParams();

  formData.append("username", email);
  formData.append("password", password);
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string" ? data.detail : "Login failed",
    );
  }

  localStorage.setItem("access_token", data.access_token);

  return data;
}

export function logout() {
  localStorage.removeItem("access_token");
}

export function getAccessToken(): string | null {
  return localStorage.getItem("access_token");
}

export function getAuthHeaders(): Record<string, string> {
  const token = getAccessToken();

  if (!token) {
    throw new Error("You must be logged in");
  }

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function getCurrentUser(): Promise<User | null> {
  const token = getAccessToken();

  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${API_URL}/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      logout();
      return null;
    }

    return response.json();
  } catch (error) {
    console.error("Failed to validate session:", error);

    logout();
    return null;
  }
}
