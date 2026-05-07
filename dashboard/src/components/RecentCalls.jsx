const SENTIMENT_BADGE = {
  neutral: 'bg-gray-100 text-gray-600',
  satisfied: 'bg-green-100 text-green-700',
  frustrated: 'bg-orange-100 text-orange-700',
  angry: 'bg-red-100 text-red-700',
  confused: 'bg-purple-100 text-purple-700',
}

function dominant(log) {
  if (!log || log.length === 0) return 'neutral'
  const counts = {}
  log.forEach(s => (counts[s] = (counts[s] || 0) + 1))
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0]
}

function fmt(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(undefined, {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

export default function RecentCalls({ data }) {
  if (!data || data.length === 0)
    return <p className="text-gray-400 text-center py-16">No calls recorded yet.</p>

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Recent Calls</h2>
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-5 py-3 text-left font-medium text-gray-600">Call SID</th>
              <th className="px-5 py-3 text-left font-medium text-gray-600">Time</th>
              <th className="px-5 py-3 text-left font-medium text-gray-600">Duration</th>
              <th className="px-5 py-3 text-left font-medium text-gray-600">Intents</th>
              <th className="px-5 py-3 text-left font-medium text-gray-600">Sentiment</th>
              <th className="px-5 py-3 text-left font-medium text-gray-600">Lang</th>
              <th className="px-5 py-3 text-left font-medium text-gray-600">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map(call => {
              const sent = dominant(call.sentiment_log)
              return (
                <tr key={call.call_sid} className="hover:bg-gray-50">
                  <td className="px-5 py-3 font-mono text-xs text-gray-500">
                    {call.call_sid.slice(0, 12)}…
                  </td>
                  <td className="px-5 py-3 text-gray-600">{fmt(call.started_at)}</td>
                  <td className="px-5 py-3">
                    {call.duration_seconds
                      ? `${Math.floor(call.duration_seconds / 60)}m ${call.duration_seconds % 60}s`
                      : '—'}
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex flex-wrap gap-1">
                      {(call.intent_log || []).slice(0, 3).map((i, idx) => (
                        <span key={idx} className="bg-indigo-100 text-indigo-700 text-xs px-2 py-0.5 rounded-full capitalize">
                          {i.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${SENTIMENT_BADGE[sent] || SENTIMENT_BADGE.neutral}`}>
                      {sent}
                    </span>
                  </td>
                  <td className="px-5 py-3 uppercase text-xs font-medium text-gray-500">
                    {call.language || 'en'}
                  </td>
                  <td className="px-5 py-3">
                    {call.escalated
                      ? <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">Escalated</span>
                      : <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Contained</span>}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
