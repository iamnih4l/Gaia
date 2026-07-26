import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatProbability(val: number): string {
  return `${(val * 100).toFixed(1)}%`;
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat("en-US").format(num);
}
