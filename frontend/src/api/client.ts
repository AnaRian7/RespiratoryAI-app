import axios from 'axios'
import type {
  PredictionResult,
  HistoryResponse,
  HealthStatus,
} from '../types'

const BACKEND_URL = import.meta.env.VITE_API_URL ?? ''

const api = axios.create({
  baseURL: BACKEND_URL ? `${BACKEND_URL}/api` : '/api',
  timeout: 120000,
})

export async function predictImage(file: File): Promise<PredictionResult> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post<PredictionResult>('/predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  return response.data
}

export async function getHistory(
  page = 1,
  pageSize = 20
): Promise<HistoryResponse> {
  const response = await api.get<HistoryResponse>('/history', {
    params: { page, page_size: pageSize },
  })

  return response.data
}

export async function getHealth(): Promise<HealthStatus> {
  const response = await api.get<HealthStatus>('/health')
  return response.data
}

export function getGradcamUrl(filename: string): string {
  const origin = BACKEND_URL || ''
  return `${origin}/api/gradcam/${filename}`
}

export default api
