/**
 * Runtime API configuration
 * This file handles API URL detection for both development and production
 */

// Helper to detect if we're in Railway production
function isRailwayProduction(): boolean {
  return (
    typeof window !== 'undefined' &&
    (window.location.hostname.includes('railway.app') ||
     window.location.hostname.includes('.up.railway.app'))
  );
}

// Helper to infer backend URL from Railway frontend URL
function inferBackendUrlFromRailway(): string | null {
  if (!isRailwayProduction() || typeof window === 'undefined') {
    return null;
  }

  const hostname = window.location.hostname;
  
  // Common Railway patterns:
  // Frontend: frontend-production-xxx.up.railway.app
  // Backend: backend-production-xxx.up.railway.app OR cursor-ai-lead-scoring-system-v10-production-backend-xxx.up.railway.app
  
  // Pattern 1: Replace 'frontend' with 'backend'
  let backendHostname = hostname.replace(/frontend(-production)?/i, 'backend$1');
  
  // Pattern 2: If that didn't work, try replacing 'frontend-production' with 'backend-production'
  if (backendHostname === hostname) {
    backendHostname = hostname.replace(/frontend-production/i, 'backend-production');
  }
  
  // Pattern 3: Try known backend service name pattern
  if (backendHostname === hostname && hostname.includes('cursor-ai-lead-scoring-system-v10-production')) {
    // Try different backend service name patterns
    const patterns = [
      hostname.replace(/frontend-production/, 'backend-production'),
      hostname.replace(/-frontend-/, '-backend-'),
      hostname.replace(/frontend/, 'backend'),
    ];
    
    for (const pattern of patterns) {
      if (pattern !== hostname) {
        backendHostname = pattern;
        break;
      }
    }
  }
  
  // If we found a different hostname, construct the URL
  if (backendHostname !== hostname && backendHostname) {
    return `https://${backendHostname}`;
  }
  
  return null;
}

// Helper to get backend URL from Railway service discovery or config
async function getBackendUrl(): Promise<string> {
  // Priority 1: Vite env var (set at build time)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // Priority 2: Runtime environment variable (if Railway injects it)
  if (typeof window !== 'undefined' && (window as any).__BACKEND_URL__) {
    return (window as any).__BACKEND_URL__;
  }

  // Priority 3: Try to infer from Railway URL pattern
  if (isRailwayProduction()) {
    const inferredUrl = inferBackendUrlFromRailway();
    if (inferredUrl) {
      // Try to fetch config from backend to confirm it exists
      try {
        const configUrl = `${inferredUrl}/api/config`;
        const response = await fetch(configUrl, { 
          method: 'GET',
          signal: AbortSignal.timeout(2000) // 2 second timeout
        });
        if (response.ok) {
          const config = await response.json();
          if (config.apiBaseUrl) {
            return config.apiBaseUrl;
          }
          return `${inferredUrl}/api`;
        }
      } catch (error) {
        console.warn('Could not verify inferred backend URL, using it anyway:', error);
      }
      return `${inferredUrl}/api`;
    }
  }

  // Priority 4: Development fallback
  return 'http://localhost:8000/api';
}

// Format the URL properly
function formatApiUrl(url: string): string {
  let apiUrl = url.trim();

  // Ensure protocol
  if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
    apiUrl = `https://${apiUrl}`;
  }

  // Ensure /api suffix
  if (!apiUrl.endsWith('/api')) {
    apiUrl = apiUrl.replace(/\/$/, '');
    if (!apiUrl.endsWith('/api')) {
      apiUrl = `${apiUrl}/api`;
    }
  }

  return apiUrl;
}

// Store API config (will be set asynchronously)
let apiConfigCache: { baseUrl: string } | null = null;

// Initialize API config
export async function initializeApiConfig(): Promise<void> {
  if (apiConfigCache) {
    return; // Already initialized
  }
  
  const url = await getBackendUrl();
  apiConfigCache = {
    baseUrl: formatApiUrl(url),
  };
  
  // Log for debugging
  if (typeof window !== 'undefined') {
    console.log('🔗 API Configuration:', {
      baseUrl: apiConfigCache.baseUrl,
      viteEnv: import.meta.env.VITE_API_URL,
      hostname: window.location.hostname,
      isRailway: isRailwayProduction(),
    });
  }
}

// Synchronous getter (returns cached or inferred immediately)
export function getApiConfig(): { baseUrl: string } {
  if (!apiConfigCache) {
    // Synchronously infer URL (no async needed for initial load)
    let defaultUrl: string;
    
    if (import.meta.env.VITE_API_URL) {
      // Priority: Use build-time env var if available
      defaultUrl = import.meta.env.VITE_API_URL;
    } else if (isRailwayProduction()) {
      // For Railway: Infer backend URL from frontend URL
      const inferred = inferBackendUrlFromRailway();
      defaultUrl = inferred ? `${inferred}/api` : 'http://localhost:8000/api';
    } else {
      // Development fallback
      defaultUrl = 'http://localhost:8000/api';
    }
    
    apiConfigCache = {
      baseUrl: formatApiUrl(defaultUrl),
    };
    
    // Optionally verify/refine async (non-blocking)
    initializeApiConfig().catch(() => {
      // Silently fail - we already have a working URL
    });
  }
  
  return apiConfigCache;
}

export const API_CONFIG = getApiConfig();

