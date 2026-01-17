import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function to merge Tailwind CSS classes with proper precedence.
 *
 * Uses clsx to handle conditional classes and tailwind-merge to resolve
 * conflicting Tailwind classes.
 *
 * @param inputs - Class values to merge
 * @returns Merged class string
 *
 * @example
 * cn("text-blue-500", condition && "bg-red-500", "p-4")
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
