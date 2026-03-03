import { useState } from 'react'
import { User, Cigarette, Wind, Dna, Heart } from 'lucide-react'
import type { RiskFactors } from '../types'

interface RiskFactorFormProps {
  onSubmit: (factors: RiskFactors) => void
  disabled?: boolean
}

export default function RiskFactorForm({ onSubmit, disabled }: RiskFactorFormProps) {
  const [age, setAge] = useState(45)
  const [gender, setGender] = useState<'male' | 'female'>('male')
  const [smoker, setSmoker] = useState(false)
  const [asthma, setAsthma] = useState(false)
  const [geneticRisk, setGeneticRisk] = useState(false)
  const [congenitalLungDefect, setCongenitalLungDefect] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      age,
      gender,
      smoker,
      asthma,
      genetic_risk: geneticRisk,
      congenital_lung_defect: congenitalLungDefect,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <User className="w-4 h-4 inline mr-2" />
          Age
        </label>
        <input
          type="number"
          value={age}
          onChange={(e) => setAge(Number(e.target.value))}
          min={0}
          max={120}
          className="input"
          disabled={disabled}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
        <div className="flex gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="gender"
              value="male"
              checked={gender === 'male'}
              onChange={() => setGender('male')}
              className="w-4 h-4 text-primary-600"
              disabled={disabled}
            />
            <span>Male</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="gender"
              value="female"
              checked={gender === 'female'}
              onChange={() => setGender('female')}
              className="w-4 h-4 text-primary-600"
              disabled={disabled}
            />
            <span>Female</span>
          </label>
        </div>
      </div>

      <div className="space-y-4">
        <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <input
            type="checkbox"
            checked={smoker}
            onChange={(e) => setSmoker(e.target.checked)}
            className="w-5 h-5 rounded text-primary-600"
            disabled={disabled}
          />
          <Cigarette className="w-5 h-5 text-gray-500" />
          <div>
            <span className="font-medium">Smoker</span>
            <p className="text-sm text-gray-500">Current or former smoker</p>
          </div>
        </label>

        <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <input
            type="checkbox"
            checked={asthma}
            onChange={(e) => setAsthma(e.target.checked)}
            className="w-5 h-5 rounded text-primary-600"
            disabled={disabled}
          />
          <Wind className="w-5 h-5 text-gray-500" />
          <div>
            <span className="font-medium">Asthma</span>
            <p className="text-sm text-gray-500">History of asthma</p>
          </div>
        </label>

        <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <input
            type="checkbox"
            checked={geneticRisk}
            onChange={(e) => setGeneticRisk(e.target.checked)}
            className="w-5 h-5 rounded text-primary-600"
            disabled={disabled}
          />
          <Dna className="w-5 h-5 text-gray-500" />
          <div>
            <span className="font-medium">Genetic Risk</span>
            <p className="text-sm text-gray-500">Family history of respiratory disease</p>
          </div>
        </label>

        <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <input
            type="checkbox"
            checked={congenitalLungDefect}
            onChange={(e) => setCongenitalLungDefect(e.target.checked)}
            className="w-5 h-5 rounded text-primary-600"
            disabled={disabled}
          />
          <Heart className="w-5 h-5 text-gray-500" />
          <div>
            <span className="font-medium">Congenital Lung Defect</span>
            <p className="text-sm text-gray-500">Born with lung abnormalities</p>
          </div>
        </label>
      </div>

      <button type="submit" className="btn-primary w-full" disabled={disabled}>
        Analyze with Risk Factors
      </button>
    </form>
  )
}
