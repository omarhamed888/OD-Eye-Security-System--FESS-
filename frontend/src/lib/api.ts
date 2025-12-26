const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };

    // Merge headers from options if they exist
    if (options.headers) {
        const extraHeaders = options.headers as Record<string, string>;
        Object.assign(headers, extraHeaders);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (response.status === 401 && typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        if (!window.location.pathname.startsWith('/login')) {
            window.location.href = '/login';
        }
    }

    return response;
}

export const api = {
    get: (endpoint: string) => fetchWithAuth(endpoint, { method: 'GET' }),
    post: (endpoint: string, data: any) => fetchWithAuth(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    patch: (endpoint: string, data: any) => fetchWithAuth(endpoint, {
        method: 'PATCH',
        body: JSON.stringify(data)
    }),
    delete: (endpoint: string) => fetchWithAuth(endpoint, { method: 'DELETE' }),
};
