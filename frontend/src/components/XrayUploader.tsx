import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, Image as ImageIcon } from 'lucide-react'

interface XrayUploaderProps {
  onFileSelect: (file: File) => void
  disabled?: boolean
}

export default function XrayUploader({ onFileSelect, disabled }: XrayUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (file) {
        setSelectedFile(file)
        setPreview(URL.createObjectURL(file))
        onFileSelect(file)
      }
    },
    [onFileSelect]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxFiles: 1,
    disabled,
  })

  const clearSelection = () => {
    setSelectedFile(null)
    setPreview(null)
  }

  return (
    <div className="w-full">
      {!preview ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          {isDragActive ? (
            <p className="text-primary-600 font-medium">Drop the X-ray image here...</p>
          ) : (
            <>
              <p className="text-gray-600 font-medium mb-2">
                Drag and drop a chest X-ray image here
              </p>
              <p className="text-gray-500 text-sm">or click to browse files</p>
              <p className="text-gray-400 text-xs mt-4">
                Supported formats: JPEG, PNG (max 10MB)
              </p>
            </>
          )}
        </div>
      ) : (
        <div className="relative rounded-xl overflow-hidden bg-gray-900">
          <button
            onClick={clearSelection}
            className="absolute top-3 right-3 z-10 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full shadow-lg transition-colors"
            disabled={disabled}
          >
            <X className="w-4 h-4" />
          </button>
          <div className="flex items-center justify-center p-4">
            <img
              src={preview}
              alt="Uploaded X-ray"
              className="max-h-80 object-contain rounded-lg"
            />
          </div>
          <div className="bg-gray-800 px-4 py-3 flex items-center gap-3">
            <ImageIcon className="w-5 h-5 text-gray-400" />
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-medium truncate">
                {selectedFile?.name}
              </p>
              <p className="text-gray-400 text-xs">
                {selectedFile && (selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
