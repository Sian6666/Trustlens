const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

let authToken = null;

export function setToken(token) {
  authToken = token;
}

export async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.message || data.error || "Request failed");
  }
  return data;
}

export const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || "http://localhost:5000";
