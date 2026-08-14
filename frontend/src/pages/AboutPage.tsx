import { Brain, Scan, Shield, LayoutDashboard } from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: 'ResNet-50 Architecture',
    description:
      '50-layer residual CNN with skip connections, trained to classify chest X-rays into four respiratory classes.',
  },
  {
    icon: Scan,
    title: 'Four-Class Diagnosis',
    description:
      'COVID-19, Pneumonia, Tuberculosis, and Normal — the disease set described in the ICAIEHS 2025 paper.',
  },
  {
    icon: Shield,
    title: 'Grad-CAM Explainability',
    description:
      'Heatmaps highlighting the X-ray regions that most influenced the predicted class.',
  },
  {
    icon: LayoutDashboard,
    title: 'Web Diagnostic Report',
    description:
      'Upload an image, receive the predicted class, confidence scores, and a Grad-CAM overlay in the browser.',
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
          An end-to-end deep learning system for detecting and classifying respiratory
          diseases from chest X-ray images, following the ICAIEHS 2025 paper pipeline.
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
              <li>• Base: ResNet-50 (ImageNet pre-trained, residual blocks)</li>
              <li>• Input: 224 × 224 × 3, softmax 4-class output</li>
              <li>• Loss: categorical cross-entropy; Adam optimizer</li>
              <li>• Explainability: Grad-CAM class activation maps</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Training Data</h3>
            <ul className="text-gray-600 space-y-2 text-sm">
              <li>• COVID-19 Radiography Database</li>
              <li>• Tuberculosis Chest X-ray Dataset</li>
              <li>• Chest X-ray Images (Pneumonia)</li>
              <li>• Augmentation: rotation, zoom, horizontal flip</li>
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
    </div>
  )
}
