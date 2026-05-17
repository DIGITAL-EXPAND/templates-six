import type { ApiErrorPayload } from './types';

export class ApiError extends Error {
  status: number;
  payload: ApiErrorPayload | null;

  constructor(status: number, payload: ApiErrorPayload | null) {
    const detail = payload?.detail;
    const message = typeof detail === 'string' ? detail : `Request failed with status ${status}`;
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.payload = payload;
  }
}

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';

export function apiUrl(path: string) {
  if (path.startsWith('http')) {
    return path;
  }

  const normalisedPath = path.startsWith('/') ? path : `/${path}`;

  if (!apiBaseUrl) {
    return normalisedPath;
  }

  return `${apiBaseUrl}${normalisedPath}`;
}

type RequestOptions = Omit<RequestInit, 'body'> & {
  body?: unknown;
  token?: string | null;
};

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Accept', 'application/json');

  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;

  if (options.body !== undefined && !isFormData) {
    headers.set('Content-Type', 'application/json');
  }

  if (options.token) {
    headers.set('Authorization', `Bearer ${options.token}`);
  }

  const requestBody =
    options.body === undefined
      ? undefined
      : isFormData
        ? options.body as BodyInit
        : JSON.stringify(options.body);

  const response = await fetch(apiUrl(path), {
    ...options,
    headers,
    body: requestBody,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type') ?? '';
  const payload = contentType.includes('application/json')
    ? ((await response.json()) as ApiErrorPayload)
    : null;

  if (!response.ok) {
    throw new ApiError(response.status, payload);
  }

  return payload as T;
}
