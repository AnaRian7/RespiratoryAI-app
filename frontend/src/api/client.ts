import axios from 'axios'
import type {
  PredictionResult,
  FusionPredictionResult,
  HistoryResponse,
  HealthStatus,
  RiskFactors,
} from '../types'

const BACKEND_URL = 'https://respiratoryai-app-production.up.railway.app'

const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  timeout: 60000,
})

export function getGradcamUrl(filename: string): string {
  return `${BACKEND_URL}/api/gradcam/${filename}`
}
export async function predictImage(file: File): Promise<PredictionResult> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post<PredictionResult>('/predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  return response.data
}

export async function predictFull(
  file: File,
  riskFactors: RiskFactors
): Promise<FusionPredictionResult> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('age', riskFactors.age.toString())
  formData.append('gender', riskFactors.gender)
  formData.append('smoker', riskFactors.smoker.toString())
  formData.append('asthma', riskFactors.asthma.toString())
  formData.append('genetic_risk', riskFactors.genetic_risk.toString())
  formData.append('congenital_lung_defect', riskFactors.congenital_lung_defect.toString())

  const response = await api.post<FusionPredictionResult>('/predict/full', formData, {
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
  return `${BACKEND_URL}/api/gradcam/${filename}`
}

export default api

