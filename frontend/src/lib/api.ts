import axios from "axios";

const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL + "/api/v1",
  headers: { "Content-Type": "application/json" },
});

API.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("farmer_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("farmer_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data: RegisterData) => API.post("/auth/register", data),
  login:    (data: LoginData)    => API.post("/auth/login", data),
  getMe:    ()                   => API.get("/farmer/me"),
  updateMe: (data: Partial<FarmerProfile>) => API.patch("/farmer/me", data),
};

export const chatAPI = {
  ask:        (query: string) => API.post("/chat/ask", { query }),
  getHistory: ()              => API.get("/chat/history"),
};

export const farmerAPI = {
  getHistory:    ()     => API.get("/farmer/me/history"),
  addCropRecord: (data: any) => API.post("/farmer/me/history", data),
};

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  phone?: string;
  state?: string;
  district?: string;
  language?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface FarmerProfile {
  name?: string;
  latitude?: number;
  longitude?: number;
  district?: string;
  state?: string;
  land_area_acres?: number;
  soil_type?: string;
  irrigation?: string;
  language?: string;
}

export default API;
