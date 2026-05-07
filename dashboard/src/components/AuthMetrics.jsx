import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#22c55e', '#ef4444']

export default function AuthMetrics({ data }) {
  if (!data) return null

  const pieData = [
    { name: 'Successful', value: data.pin_success_count ?? 0 },
    { name: 'Failed / Locked', value: data.lockout_count ?? 0 },
  ]

  const cards = [
    { label: 'Total Auth Attempts', value: data.total_auth_attempts ?? 0 },
    { label: 'PIN Success Rate', value: `${((data.success_rate ?? 0) * 100).toFixed(1)}%` },
    { label: 'Lockout Events', value: data.lockout_count ?? 0 },
    { label: 'Avg Biometric Score', value: data.avg_biometric_score ? `${data.avg_biometric_score}/100` : '—' },
  ]

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Authentication Analytics (Last 7 Days)</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {cards.map(c => (
          <div key={c.label} className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500 mb-1">{c.label}</p>
            <p className="text-2xl font-bold text-indigo-700">{c.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-medium text-gray-700 mb-4">PIN Auth Outcome</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={3}
                dataKey="value"
              >
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-medium text-gray-700 mb-4">Biometric Score Guide</h3>
          <div className="space-y-3 text-sm">
            {[
              { range: '85 – 100', label: 'Verified', color: 'green' },
              { range: '60 – 84', label: 'Partial match — soft flag', color: 'yellow' },
              { range: 'Below 60', label: 'Mismatch — manager alert', color: 'red' },
              { range: 'No enrollment', label: 'Skipped', color: 'gray' },
            ].map(r => (
              <div key={r.range} className="flex items-center gap-3">
                <span className={`w-3 h-3 rounded-full bg-${r.color}-500 flex-shrink-0`} />
                <span className="font-mono text-xs text-gray-500 w-20">{r.range}</span>
                <span className="text-gray-600">{r.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
