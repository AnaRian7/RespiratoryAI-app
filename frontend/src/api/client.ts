import axios from 'axios'
import type { PredictionResult, FusionPredictionResult, HistoryResponse, HealthStatus, RiskFactors } from '../types'

const api = axios.create({
  baseURL: 'https://railway.com/project/8d492a50-fab8-49d5-a409-28fabe4598e1/service/d88eeeee-0142-48cc-b8e9-1690e950b8e9?environmentId=53b8d017-6215-4a37-8e9f-d3fe15918591',
  timeout: 60000,
})

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
  return `/api/gradcam/${filename}`
}

export default api

