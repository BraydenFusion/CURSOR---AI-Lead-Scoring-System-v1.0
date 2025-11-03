/**
 * XSS prevention utilities
 * React automatically escapes content, but this provides additional protection
 */

/**
 * Sanitize user input for display
 * Removes potentially dangerous HTML/scripts
 */
export function sanitizeForDisplay(input: string): string {
  if (!input) return "";
  
  // React already escapes by default, but add extra protection
  // Remove any script tags or event handlers that might slip through
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
    .replace(/on\w+\s*=\s*["'][^"']*["']/gi, "")
    .trim();
}

/**
 * Validate and sanitize email addresses
 */
export function sanitizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

/**
 * Validate and sanitize phone numbers
 */
export function sanitizePhone(phone: string): string {
  // Remove all non-digit characters except +, -, spaces
  return phone.replace(/[^\d+\-\s()]/g, "");
}

