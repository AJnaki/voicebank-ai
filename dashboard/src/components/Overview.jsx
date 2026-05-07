export default function Overview({ data }) {
  if (!data) return null

  const cards = [
    { label: 'Total Calls Today', value: data.total_calls_today ?? 0, color: 'indigo' },
    { label: 'Active Calls', value: data.active_calls ?? 0, color: 'green', live: true },
    {
      label: 'Containment Rate',
      value: `${((data.containment_rate ?? 0) * 100).toFixed(1)}%`,
      color: 'blue',
    },
    {
      label: 'Avg Handle Time',
      value: data.avg_handle_time_seconds
        ? `${Math.floor(data.avg_handle_time_seconds / 60)}m ${data.avg_handle_time_seconds % 60}s`
        : '—',
      color: 'purple',
    },
    { label: 'Escalated Calls', value: data.escalated_calls ?? 0, color: 'red' },
    { label: 'Top Intent', value: data.top_intent ?? '—', color: 'yellow', text: true },
  ]

  const colorMap = {
    indigo: 'bg-indigo-50 text-indigo-800 border-indigo-200',
    green: 'bg-green-50 text-green-800 border-green-200',
    blue: 'bg-blue-50 text-blue-800 border-blue-200',
    purple: 'bg-purple-50 text-purple-800 border-purple-200',
    red: 'bg-red-50 text-red-800 border-red-200',
    yellow: 'bg-yellow-50 text-yellow-800 border-yellow-200',
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Overview — Today</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
        {cards.map(card => (
          <div key={card.label} className={`rounded-xl border p-6 ${colorMap[card.color]}`}>
            <p className="text-sm font-medium opacity-70 mb-1">{card.label}</p>
            <div className="flex items-center gap-2">
              <p className={`font-bold ${card.text ? 'text-xl capitalize' : 'text-3xl'}`}>
                {card.value}
              </p>
              {card.live && (
                <span className="inline-flex h-2.5 w-2.5 rounded-full bg-green-500 animate-pulse" />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
