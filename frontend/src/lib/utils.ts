import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function isLoggedIn(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("farmer_token");
}

export function getFarmerName(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("farmer_name") || "Farmer";
}

export function logout() {
  localStorage.removeItem("farmer_token");
  localStorage.removeItem("farmer_name");
  localStorage.removeItem("farmer_id");
  window.location.href = "/login";
}
