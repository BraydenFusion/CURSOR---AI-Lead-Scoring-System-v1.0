/**
 * Runtime API configuration
 * This file handles API URL detection for both development and production
 */

// Helper to detect if we're in production
function isProduction(): boolean {
  if (typeof window === 'undefined') return false;
  const hostname = window.location.hostname;
  return (
    hostname.includes('railway.app') ||
    hostname.includes('.up.railway.app') ||
    hostname === 'ventrix.tech' ||
    hostname.includes('ventrix.tech')
  );
}

// Helper to detect if we're in Railway production (legacy)
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
  // Backend: backend-production-xxx.up.railway.app OR backend-base.up.railway.app
  
  // Try multiple backend URL patterns in order of likelihood
  const backendPatterns = [
    // Pattern 1: backend-base (common Railway naming)
    'backend-base.up.railway.app',
    // Pattern 2: Replace frontend-production with backend-production
    hostname.replace(/frontend-production/i, 'backend-production'),
    // Pattern 3: Replace frontend with backend
    hostname.replace(/frontend(-production)?/i, 'backend$1'),
    // Pattern 4: Try known backend service name pattern
    hostname.replace(/-frontend-/, '-backend-'),
  ];
  
  // Remove duplicates and the original hostname
  const uniquePatterns = [...new Set(backendPatterns)].filter(p => p !== hostname);
  
  // Try each pattern by attempting to connect
  for (const backendHostname of uniquePatterns) {
    if (backendHostname && backendHostname.includes('railway.app')) {
      return `https://${backendHostname}`;
    }
  }
  
  return null;
}

// Helper to test if a backend URL is accessible
async function testBackendUrl(url: string): Promise<boolean> {
  try {
    const configUrl = `${url}/api/config`;
    const response = await fetch(configUrl, { 
      method: 'GET',
      signal: AbortSignal.timeout(3000), // 3 second timeout
      mode: 'cors',
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

// Helper to get backend URL from Railway service discovery or config
async function getBackendUrl(): Promise<string> {
  // Priority 1: Vite env var (set at build time)
  if (import.meta.env.VITE_API_URL) {
    const envUrl = import.meta.env.VITE_API_URL;
    if (await testBackendUrl(envUrl.replace('/api', ''))) {
      return envUrl;
    }
  }

  // Priority 2: Runtime environment variable (if Railway injects it)
  if (typeof window !== 'undefined' && (window as any).__BACKEND_URL__) {
    const runtimeUrl = (window as any).__BACKEND_URL__;
    if (await testBackendUrl(runtimeUrl.replace('/api', ''))) {
      return runtimeUrl;
    }
  }

  // Priority 3: Check if we're on ventrix.tech domain
  if (typeof window !== 'undefined' && 
      (window.location.hostname === 'ventrix.tech' || window.location.hostname.includes('ventrix.tech'))) {
    // Use backend-base for ventrix.tech domain
    const backendUrl = 'https://backend-base.up.railway.app';
    if (await testBackendUrl(backendUrl)) {
      return `${backendUrl}/api`;
    }
  }
  
  // Priority 4: Try to infer from Railway URL pattern and test each
  if (isRailwayProduction()) {
    // Try multiple backend URL patterns - backend-base FIRST (most reliable)
    const backendUrls = [
      'https://backend-base.up.railway.app', // Always try this first - it's the correct URL
      ...(inferBackendUrlFromRailway() ? [inferBackendUrlFromRailway()!] : []),
    ].filter(Boolean);
    
    for (const backendUrl of backendUrls) {
      if (await testBackendUrl(backendUrl)) {
        const configUrl = `${backendUrl}/api/config`;
        try {
          const response = await fetch(configUrl, { 
            method: 'GET',
            signal: AbortSignal.timeout(2000)
          });
          if (response.ok) {
            const config = await response.json();
            if (config.apiBaseUrl) {
              return config.apiBaseUrl;
            }
          }
        } catch (error) {
          console.warn('Could not fetch config, using inferred URL:', error);
        }
        return `${backendUrl}/api`;
      }
    }
    
    // If inference failed, try the most common pattern anyway
    const inferredUrl = inferBackendUrlFromRailway();
    if (inferredUrl) {
      console.warn('Using inferred backend URL without verification:', inferredUrl);
      return `${inferredUrl}/api`;
    }
  }

  // Priority 4: Development fallback
  return 'http://localhost:8000/api';
}

// Format the URL properly
function formatApiUrl(url: string): string {
  let apiUrl = url.trim();

  // Remove trailing slashes
  apiUrl = apiUrl.replace(/\/+$/, '');

  // Ensure protocol
  if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
    apiUrl = `https://${apiUrl}`;
  }

  // Ensure /api suffix (add it if not present)
  if (!apiUrl.endsWith('/api')) {
    // Remove any trailing slash before adding /api
    apiUrl = apiUrl.replace(/\/+$/, '');
    apiUrl = `${apiUrl}/api`;
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
      // Priority 1: Use build-time env var if available
      defaultUrl = import.meta.env.VITE_API_URL;
    } else if (typeof window !== 'undefined' && 
               (window.location.hostname === 'ventrix.tech' || window.location.hostname.includes('ventrix.tech'))) {
      // Priority 2: Use backend-base for ventrix.tech domain
      defaultUrl = 'https://backend-base.up.railway.app/api';
    } else if (isRailwayProduction()) {
      // Priority 3: Use hardcoded backend-base (most reliable for this deployment)
      defaultUrl = 'https://backend-base.up.railway.app/api';
      
      // Fallback: Infer from frontend URL if needed
      // But prefer backend-base which we know is correct
      const inferred = inferBackendUrlFromRailway();
      if (inferred && inferred.includes('backend-base')) {
        defaultUrl = `${inferred}/api`;
      }
    } else {
      // Development fallback
      defaultUrl = 'http://localhost:8000/api';
    }
    
    apiConfigCache = {
      baseUrl: formatApiUrl(defaultUrl),
    };
    
    // Log for debugging
    if (typeof window !== 'undefined') {
      console.log('🔗 API Config (sync):', {
        baseUrl: apiConfigCache.baseUrl,
        viteEnv: import.meta.env.VITE_API_URL,
        hostname: window.location.hostname,
      });
    }
    
    // Optionally verify/refine async (non-blocking)
    initializeApiConfig().catch(() => {
      // Silently fail - we already have a working URL
    });
  }
  
  return apiConfigCache;
}

export const API_CONFIG = getApiConfig();

