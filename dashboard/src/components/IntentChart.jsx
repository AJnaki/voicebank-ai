import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell,
} from 'recharts'

const COLORS = ['#4f46e5', '#7c3aed', '#2563eb', '#0891b2', '#059669', '#d97706', '#dc2626']

export default function IntentChart({ data }) {
  if (!data || data.length === 0)
    return <p className="text-gray-400 text-center py-16">No intent data yet.</p>

  const top10 = data.slice(0, 10)

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Intent Analytics (Last 7 Days)</h2>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Total Intents</p>
          <p className="text-3xl font-bold text-indigo-700">
            {data.reduce((s, d) => s + d.count, 0)}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Unique Intent Types</p>
          <p className="text-3xl font-bold text-indigo-700">{data.length}</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <p className="text-sm text-gray-500">Total Escalations</p>
          <p className="text-3xl font-bold text-red-600">
            {data.reduce((s, d) => s + (d.escalated || 0), 0)}
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={top10} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="intent" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" name="Total" radius={[4, 4, 0, 0]}>
              {top10.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Bar>
            <Bar dataKey="escalated" name="Escalated" fill="#fca5a5" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table */}
      <div className="mt-6 bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-5 py-3 text-left font-medium text-gray-600">Intent</th>
              <th className="px-5 py-3 text-right font-medium text-gray-600">Calls</th>
              <th className="px-5 py-3 text-right font-medium text-gray-600">Escalated</th>
              <th className="px-5 py-3 text-right font-medium text-gray-600">Escalation %</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map(row => (
              <tr key={row.intent} className="hover:bg-gray-50">
                <td className="px-5 py-3 font-medium capitalize">{row.intent.replace('_', ' ')}</td>
                <td className="px-5 py-3 text-right">{row.count}</td>
                <td className="px-5 py-3 text-right text-red-600">{row.escalated || 0}</td>
                <td className="px-5 py-3 text-right text-gray-500">
                  {row.count ? `${((row.escalated / row.count) * 100).toFixed(1)}%` : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
