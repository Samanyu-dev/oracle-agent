import { CreateSessionPayload, OracleStatePayload } from './oracle-types'

const API_BASE = process.env.NEXT_PUBLIC_ORACLE_API_URL ?? 'http://localhost:8000'

class OracleApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
    ...init,
  })

  if (!response.ok) {
    let reason = response.statusText
    try {
      const payload = await response.json()
      reason = payload.detail ?? payload.message ?? reason
    } catch {
      // Keep fallback status text.
    }
    throw new OracleApiError(response.status, `API ${response.status}: ${reason}`)
  }

  return (await response.json()) as T
}

export async function createSession(payload: CreateSessionPayload): Promise<OracleStatePayload> {
  return request<OracleStatePayload>('/sessions', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function getSession(sessionId: string): Promise<OracleStatePayload> {
  return request<OracleStatePayload>(`/sessions/${sessionId}`, {
    method: 'GET',
  })
}

export async function stepSession(sessionId: string, action?: string): Promise<OracleStatePayload> {
  return request<OracleStatePayload>(`/sessions/${sessionId}/step`, {
    method: 'POST',
    body: JSON.stringify({ action: action ?? null }),
  })
}

export async function resetSession(sessionId: string): Promise<OracleStatePayload> {
  return request<OracleStatePayload>(`/sessions/${sessionId}/reset`, {
    method: 'POST',
  })
}

export { OracleApiError }
