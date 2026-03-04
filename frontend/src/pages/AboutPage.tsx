import { Brain, Database, Shield, Zap } from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: 'ResNet50V2 Architecture',
    description:
      'State-of-the-art deep learning model pre-trained on ImageNet, fine-tuned for chest X-ray classification.',
  },
  {
    icon: Zap,
    title: 'Real-time Analysis',
    description:
      'Get instant predictions with confidence scores and probability distributions across all disease classes.',
  },
  {
    icon: Shield,
    title: 'Grad-CAM Explainability',
    description:
      'Visual heatmaps showing which regions of the X-ray most influenced the model\'s decision.',
  },
  {
    icon: Database,
    title: 'Multi-Modal Fusion',
    description:
      'Combine X-ray analysis with patient risk factors for more accurate predictions.',
  },
]

const diseaseClasses = [
  { name: 'COVID-19', color: 'bg-red-500', description: 'SARS-CoV-2 infection patterns' },
  { name: 'Normal', color: 'bg-green-500', description: 'Healthy chest X-ray' },
  { name: 'Pneumonia', color: 'bg-amber-500', description: 'Bacterial or viral pneumonia' },
  { name: 'Tuberculosis', color: 'bg-purple-500', description: 'TB infection patterns' },
]

export default function AboutPage() {
  return (
    <div className="space-y-12">
      <div className="text-center max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">About RespiratoryAI</h1>
        <p className="text-xl text-gray-600">
          An AI-powered system for detecting respiratory diseases from chest X-ray images
          using deep learning and computer vision.
        </p>
      </div>

      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Key Features</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {features.map((feature) => (
            <div key={feature.title} className="card flex gap-4">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <feature.icon className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{feature.title}</h3>
                <p className="text-gray-600 text-sm mt-1">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Supported Disease Classes
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {diseaseClasses.map((disease) => (
            <div key={disease.name} className="card text-center">
              <div
                className={`w-12 h-12 ${disease.color} rounded-full mx-auto mb-3`}
              />
              <h3 className="font-semibold text-gray-900">{disease.name}</h3>
              <p className="text-gray-600 text-sm mt-1">{disease.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Technical Details</h2>
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Model Architecture</h3>
            <ul className="text-gray-600 space-y-2 text-sm">
              <li>• Base: ResNet50V2 (pre-trained on ImageNet)</li>
              <li>• Custom classification head with dropout</li>
              <li>• Input size: 224 x 224 pixels</li>
              <li>• Output: 4-class softmax probabilities</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Training Data</h3>
            <ul className="text-gray-600 space-y-2 text-sm">
              <li>• COVID-19 Radiography Database</li>
              <li>• Tuberculosis Chest X-ray Dataset</li>
              <li>• RSNA Pneumonia Detection Challenge</li>
              <li>• Class-balanced sampling with augmentation</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="bg-amber-50 border border-amber-200 rounded-xl p-6">
        <h2 className="text-xl font-bold text-amber-900 mb-2">Important Disclaimer</h2>
        <p className="text-amber-800">
          This tool is designed for <strong>research and educational purposes only</strong>.
          It is not intended to be used as a medical diagnostic device and should not
          replace professional medical advice, diagnosis, or treatment. Always consult
          a qualified healthcare provider for any medical concerns.
        </p>
      </section>

      <section className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Technology Stack</h2>
        <div className="flex flex-wrap justify-center gap-3">
          {[
            'Python',
            'TensorFlow',
            'FastAPI',
            'React',
            'TypeScript',
            'Tailwind CSS',
            'SQLite',
          ].map((tech) => (
            <span
              key={tech}
              className="px-4 py-2 bg-gray-100 rounded-full text-gray-700 font-medium"
            >
              {tech}
            </span>
          ))}
        </div>
      </section>
    </div>
  )
}


