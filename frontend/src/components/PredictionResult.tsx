import { CheckCircle, AlertTriangle, AlertCircle, Activity } from 'lucide-react'
import type { PredictionResult as PredictionResultType, DiseaseClass, DISEASE_COLORS } from '../types'

interface PredictionResultProps {
  result: PredictionResultType
}

const diseaseIcons: Record<DiseaseClass, typeof CheckCircle> = {
  NORMAL: CheckCircle,
  COVID: AlertCircle,
  PNEUMONIA: AlertTriangle,
  TUBERCULOSIS: AlertCircle,
}

const _DISEASE_COLORS: Record<DiseaseClass, string> = {
  COVID: 'text-red-500 bg-red-50 border-red-200',
  NORMAL: 'text-green-500 bg-green-50 border-green-200',
  PNEUMONIA: 'text-amber-500 bg-amber-50 border-amber-200',
  TUBERCULOSIS: 'text-purple-500 bg-purple-50 border-purple-200',
}

const barColors: Record<DiseaseClass, string> = {
  COVID: 'bg-red-500',
  NORMAL: 'bg-green-500',
  PNEUMONIA: 'bg-amber-500',
  TUBERCULOSIS: 'bg-purple-500',
}

export default function PredictionResult({ result }: PredictionResultProps) {
  const predictedClass = result.predicted_class as DiseaseClass
  const Icon = diseaseIcons[predictedClass]
  const colorClasses = diseaseColors[predictedClass]

  const sortedProbabilities = Object.entries(result.probabilities).sort(
    ([, a], [, b]) => b - a
  )

  return (
    <div className="card space-y-6">
      <div className={`p-6 rounded-xl border-2 ${colorClasses}`}>
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-full bg-white shadow-sm">
            <Icon className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <h3 className="text-2xl font-bold">{predictedClass}</h3>
            <p className="text-sm opacity-75">
              {predictedClass === 'NORMAL'
                ? 'No respiratory disease detected'
                : `${predictedClass} detected in X-ray`}
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">{(result.confidence * 100).toFixed(1)}%</p>
            <p className="text-sm opacity-75">Confidence</p>
          </div>
        </div>
      </div>

      <div>
        <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
          Probability Distribution
        </h4>
        <div className="space-y-3">
          {sortedProbabilities.map(([className, probability]) => (
            <div key={className}>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium text-gray-700">{className}</span>
                <span className="text-gray-500">{(probability * 100).toFixed(1)}%</span>
              </div>
              <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    barColors[className as DiseaseClass]
                  }`}
                  style={{ width: `${probability * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {result.gradcam_url && (
        <div>
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
            Model Focus (Grad-CAM)
          </h4>
          <div className="bg-gray-900 rounded-xl p-4">
            <img
              src={result.gradcam_url}
              alt="Grad-CAM visualization"
              className="w-full rounded-lg"
            />
            <p className="text-gray-400 text-xs mt-3 text-center">
              Heatmap showing regions that influenced the model's decision
            </p>
          </div>
        </div>
      )}

      <div className="pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            <span>Model: {result.model_type}</span>
          </div>
          <span>ID: {result.prediction_id.slice(0, 8)}...</span>
        </div>
      </div>
    </div>
  )
}

