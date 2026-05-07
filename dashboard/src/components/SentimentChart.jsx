import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const SENTIMENT_COLORS = {
  neutral: '#94a3b8',
  satisfied: '#22c55e',
  frustrated: '#f97316',
  angry: '#ef4444',
  confused: '#a855f7',
}

export default function SentimentChart({ data }) {
  if (!data || data.length === 0)
    return <p className="text-gray-400 text-center py-16">No sentiment data yet.</p>

  const formatted = data.map(d => ({
    ...d,
    hour: d.hour.split('T')[1] || d.hour,
  }))

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Sentiment Trends (Last 24h)</h2>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={formatted} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="hour" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            {Object.entries(SENTIMENT_COLORS).map(([key, color]) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Sentiment legend */}
      <div className="grid grid-cols-5 gap-3">
        {Object.entries(SENTIMENT_COLORS).map(([label, color]) => (
          <div key={label} className="bg-white rounded-lg border border-gray-200 p-3 text-center">
            <div className="w-4 h-4 rounded-full mx-auto mb-1" style={{ background: color }} />
            <p className="text-xs font-medium capitalize text-gray-600">{label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
