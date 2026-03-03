export interface PredictionProbabilities {
  COVID: number
  NORMAL: number
  PNEUMONIA: number
  TUBERCULOSIS: number
}

export interface PredictionResult {
  prediction_id: string
  timestamp: string
  predicted_class: string
  confidence: number
  probabilities: PredictionProbabilities
  model_type: string
  gradcam_url?: string
}

export interface RiskFactors {
  age: number
  gender: 'male' | 'female'
  smoker: boolean
  asthma: boolean
  genetic_risk: boolean
  congenital_lung_defect: boolean
}

export interface FusionPredictionResult extends PredictionResult {
  risk_factors: RiskFactors
}

export interface HistoryItem {
  id: number
  prediction_id: string
  predicted_class: string
  confidence: number
  model_type: string
  created_at: string
  image_filename?: string
  gradcam_filename?: string
}

export interface HistoryResponse {
  items: HistoryItem[]
  total: number
  page: number
  page_size: number
}

export interface HealthStatus {
  status: string
  version: string
  models_loaded: {
    image_model: boolean
    risk_model: boolean
    fusion_model: boolean
  }
}

export type DiseaseClass = 'COVID' | 'NORMAL' | 'PNEUMONIA' | 'TUBERCULOSIS'

export const DISEASE_COLORS: Record<DiseaseClass, string> = {
  COVID: '#ef4444',
  NORMAL: '#22c55e',
  PNEUMONIA: '#f59e0b',
  TUBERCULOSIS: '#8b5cf6'
}

export const DISEASE_DESCRIPTIONS: Record<DiseaseClass, string> = {
  COVID: 'COVID-19 infection detected',
  NORMAL: 'No respiratory disease detected',
  PNEUMONIA: 'Pneumonia detected',
  TUBERCULOSIS: 'Tuberculosis detected'
}
