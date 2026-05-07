import { useState, useEffect, useCallback } from 'react'
import { api } from './api'
import Overview from './components/Overview'
import IntentChart from './components/IntentChart'
import SentimentChart from './components/SentimentChart'
import RecentCalls from './components/RecentCalls'
import AuthMetrics from './components/AuthMetrics'

const NAV = ['Overview', 'Intents', 'Sentiment', 'Recent Calls', 'Auth']

export default function App() {
  const [active, setActive] = useState('Overview')
  const [data, setData] = useState({})
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(null)

  const fetchAll = useCallback(async () => {
    setLoading(true)
    try {
      const [overview, intents, sentiment, calls, auth] = await Promise.all([
        api.overview(),
        api.intents(),
        api.sentiment(),
        api.recentCalls(),
        api.auth(),
      ])
      setData({ overview, intents, sentiment, calls, auth })
      setLastRefresh(new Date().toLocaleTimeString())
    } catch (e) {
      console.error('Failed to fetch analytics:', e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAll()
    const interval = setInterval(fetchAll, 30000) // auto-refresh every 30s
    return () => clearInterval(interval)
  }, [fetchAll])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-indigo-900 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">VoiceBank AI</h1>
            <p className="text-indigo-300 text-sm">Manager Analytics Dashboard</p>
          </div>
          <div className="flex items-center gap-4">
            {lastRefresh && (
              <span className="text-indigo-300 text-xs">Last updated: {lastRefresh}</span>
            )}
            <button
              onClick={fetchAll}
              className="bg-indigo-700 hover:bg-indigo-600 px-4 py-2 rounded-lg text-sm font-medium transition"
            >
              Refresh
            </button>
          </div>
        </div>
      </header>

      {/* Nav */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex space-x-1">
            {NAV.map(tab => (
              <button
                key={tab}
                onClick={() => setActive(tab)}
                className={`px-5 py-3 text-sm font-medium border-b-2 transition ${
                  active === tab
                    ? 'border-indigo-600 text-indigo-700'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {loading && !data.overview ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-400 text-lg">Loading analytics...</div>
          </div>
        ) : (
          <>
            {active === 'Overview' && <Overview data={data.overview} />}
            {active === 'Intents' && <IntentChart data={data.intents} />}
            {active === 'Sentiment' && <SentimentChart data={data.sentiment} />}
            {active === 'Recent Calls' && <RecentCalls data={data.calls} />}
            {active === 'Auth' && <AuthMetrics data={data.auth} />}
          </>
        )}
      </main>
    </div>
  )
}
