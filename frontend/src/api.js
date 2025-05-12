import { getToken } from './auth';

const API = "http://localhost:8000";

export async function post(endpoint, data) {
  const res = await fetch(`${API}${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`
    },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function get(endpoint) {
  const res = await fetch(`${API}${endpoint}`, {
    headers: {
      Authorization: `Bearer ${getToken()}`
    }
  });
  return res.json();
}
