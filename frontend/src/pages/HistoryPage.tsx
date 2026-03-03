import { useEffect, useState } from 'react'
import { Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import { getHistory } from '../api/client'
import type { HistoryItem } from '../types'

const classColors: Record<string, string> = {
  COVID: 'bg-red-100 text-red-700',
  NORMAL: 'bg-green-100 text-green-700',
  PNEUMONIA: 'bg-amber-100 text-amber-700',
  TUBERCULOSIS: 'bg-purple-100 text-purple-700',
}

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 10

  useEffect(() => {
    fetchHistory()
  }, [page])

  const fetchHistory = async () => {
    setLoading(true)
    try {
      const response = await getHistory(page, pageSize)
      setItems(response.items)
      setTotal(response.total)
    } catch (err) {
      setError('Failed to load prediction history')
    } finally {
      setLoading(false)
    }
  }

  const totalPages = Math.ceil(total / pageSize)

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString()
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Prediction History</h1>
        <p className="text-gray-600">View past X-ray analysis results</p>
      </div>

      {loading && (
        <div className="card flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}

      {!loading && items.length === 0 && (
        <div className="card text-center py-12">
          <p className="text-gray-600">No predictions yet</p>
          <p className="text-gray-500 text-sm mt-1">
            Analyze an X-ray to see results here
          </p>
        </div>
      )}

      {!loading && items.length > 0 && (
        <>
          <div className="card overflow-hidden p-0">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Date</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Prediction</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Confidence</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">Model</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600">ID</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {formatDate(item.created_at)}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                          classColors[item.predicted_class] || 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {item.predicted_class}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary-500 rounded-full"
                            style={{ width: `${item.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-gray-600">
                          {(item.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">{item.model_type}</td>
                    <td className="py-3 px-4 text-sm text-gray-500 font-mono">
                      {item.prediction_id.slice(0, 8)}...
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Showing {(page - 1) * pageSize + 1} to{' '}
                {Math.min(page * pageSize, total)} of {total} results
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn-secondary flex items-center gap-1 disabled:opacity-50"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </button>
                <span className="px-4 text-gray-600">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="btn-secondary flex items-center gap-1 disabled:opacity-50"
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
