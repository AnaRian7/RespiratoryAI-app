import { useState } from 'react'
import { Loader2, Scan, UserCog } from 'lucide-react'
import XrayUploader from '../components/XrayUploader'
import PredictionResult from '../components/PredictionResult'
import RiskFactorForm from '../components/RiskFactorForm'
import { predictImage, predictFull } from '../api/client'
import type { PredictionResult as PredictionResultType, RiskFactors } from '../types'

type AnalysisMode = 'image' | 'fusion'

export default function HomePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>('image')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PredictionResultType | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setResult(null)
    setError(null)
  }

  const handleImageAnalysis = async () => {
    if (!selectedFile) return

    setLoading(true)
    setError(null)

    try {
      const prediction = await predictImage(selectedFile)
      setResult(prediction)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleFusionAnalysis = async (riskFactors: RiskFactors) => {
    if (!selectedFile) return

    setLoading(true)
    setError(null)

    try {
      const prediction = await predictFull(selectedFile, riskFactors)
      setResult(prediction)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Chest X-Ray Analysis
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Upload a chest X-ray image to detect respiratory diseases including
          COVID-19, Pneumonia, and Tuberculosis using our AI-powered analysis.
        </p>
      </div>

      <div className="flex justify-center">
        <div className="inline-flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setAnalysisMode('image')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all ${
              analysisMode === 'image'
                ? 'bg-white shadow text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Scan className="w-4 h-4" />
            Image Only
          </button>
          <button
            onClick={() => setAnalysisMode('fusion')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all ${
              analysisMode === 'fusion'
                ? 'bg-white shadow text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <UserCog className="w-4 h-4" />
            With Risk Factors
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Upload X-Ray Image
            </h2>
            <XrayUploader onFileSelect={handleFileSelect} disabled={loading} />
          </div>

          {analysisMode === 'image' && selectedFile && (
            <button
              onClick={handleImageAnalysis}
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Scan className="w-5 h-5" />
                  Analyze X-Ray
                </>
              )}
            </button>
          )}

          {analysisMode === 'fusion' && selectedFile && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Patient Risk Factors
              </h2>
              <RiskFactorForm onSubmit={handleFusionAnalysis} disabled={loading} />
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          )}
        </div>

        <div>
          {loading && (
            <div className="card flex flex-col items-center justify-center py-16">
              <Loader2 className="w-12 h-12 animate-spin text-primary-600 mb-4" />
              <p className="text-gray-600 font-medium">Analyzing X-ray...</p>
              <p className="text-gray-500 text-sm mt-1">This may take a few seconds</p>
            </div>
          )}

          {result && !loading && <PredictionResult result={result} />}

          {!result && !loading && (
            <div className="card flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Scan className="w-8 h-8 text-gray-400" />
              </div>
              <p className="text-gray-600 font-medium">No analysis yet</p>
              <p className="text-gray-500 text-sm mt-1">
                Upload an X-ray image to get started
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-amber-800 text-sm">
        <strong>Disclaimer:</strong> This tool is for research and educational purposes only.
        It should not be used as a substitute for professional medical diagnosis.
        Always consult a qualified healthcare provider for medical advice.
      </div>
    </div>
  )
}
