
import { useEffect, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './App.css'

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

type Metrics = {
  month: string
  cutoff_hours: number
  matched_periods: number
  coverage_percent: number
  mae_mw: number
  rmse_mw: number
  bias_mw: number
  mean_lead_hours: number
  underforecast_hours: number
  overforecast_hours: number
}

type SeriesPoint = {
  startTime: string
  forecast_mw: number
  actual_mw: number
  error_mw: number
}

type ErrorPeriod = SeriesPoint & {
  absolute_error_mw: number
  forecast_publish_time: string
  lead_hours: number
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('en-GB', {
    maximumFractionDigits: 1,
  }).format(value)
}

function formatTime(value: string) {
  return new Date(value).toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short',
  })
}

function App() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [series, setSeries] = useState<SeriesPoint[]>([])
  const [periods, setPeriods] = useState<ErrorPeriod[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true)
        setError('')

        const responses = await Promise.all([
          fetch(`${API}/api/overview`),
          fetch(`${API}/api/series?limit=744`),
          fetch(`${API}/api/periods?limit=10`),
        ])

        if (responses.some((response) => !response.ok)) {
          throw new Error('The API returned an error. Check that your backend is running.')
        }

        const [overviewData, seriesData, periodsData] = await Promise.all(
          responses.map((response) => response.json()),
        )

        setMetrics(overviewData as Metrics)
        setSeries(seriesData.data as SeriesPoint[])
        setPeriods(periodsData.data as ErrorPeriod[])
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load dashboard data.',
        )
      } finally {
        setLoading(false)
      }
    }

    void loadDashboard()
  }, [])

  const chartData = series.filter((_, index) => index % 6 === 0)

  if (loading) {
    return <main className="status-screen">Loading WindLens dashboard...</main>
  }

  if (error || !metrics) {
    return (
      <main className="status-screen">
        <h1>WindLens</h1>
        <p>{error || 'Dashboard data is unavailable.'}</p>
        <p>Make sure the FastAPI backend is running on port 8000.</p>
        <button onClick={() => window.location.reload()}>Try again</button>
      </main>
    )
  }

  return (
    <main className="dashboard">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-icon">W</span>
          WindLens
        </a>
        <span className="period-badge">JANUARY 2026</span>
      </header>

      <section className="intro">
        <p className="eyebrow">WIND FORECAST INTELLIGENCE</p>
        <h1>See the gap between forecast and reality.</h1>
        <p className="subtitle">
          UK wind generation forecast accuracy, measured against actual
          generation data from Elexon BMRS.
        </p>
        <p className="assumption">
          Evaluation assumption: latest forecast published at least{' '}
          {metrics.cutoff_hours} hours before delivery. All timestamps are UTC.
        </p>
      </section>

      <section className="kpi-grid" aria-label="Forecast accuracy metrics">
        <article className="kpi-card">
          <p>Mean absolute error</p>
          <h2>{formatNumber(metrics.mae_mw)} <small>MW</small></h2>
          <span>Average forecast deviation</span>
        </article>
        <article className="kpi-card">
          <p>Root mean squared error</p>
          <h2>{formatNumber(metrics.rmse_mw)} <small>MW</small></h2>
          <span>Penalises larger errors</span>
        </article>
        <article className="kpi-card">
          <p>Forecast bias</p>
          <h2 className={metrics.bias_mw >= 0 ? 'positive' : 'negative'}>
            {metrics.bias_mw > 0 ? '+' : ''}
            {formatNumber(metrics.bias_mw)} <small>MW</small>
          </h2>
          <span>{metrics.bias_mw >= 0 ? 'Net overforecast' : 'Net underforecast'}</span>
        </article>
        <article className="kpi-card">
          <p>Data coverage</p>
          <h2>{formatNumber(metrics.coverage_percent)}<small>%</small></h2>
          <span>{metrics.matched_periods} matched hourly periods</span>
        </article>
      </section>

      <section className="panel chart-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">PERFORMANCE OVER TIME</p>
            <h2>Forecast vs actual generation</h2>
          </div>
          <span className="unit-label">MW · UTC</span>
        </div>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 12, right: 18, left: 4, bottom: 8 }}>
              <CartesianGrid stroke="#e8edf3" strokeDasharray="4 4" />
              <XAxis
                dataKey="startTime"
                tickFormatter={(value: string) =>
                  new Date(value).toLocaleDateString('en-GB', {
                    day: '2-digit',
                    month: 'short',
                    timeZone: 'UTC',
                  })
                }
                tick={{ fill: '#64748b', fontSize: 11 }}
                minTickGap={30}
              />
              <YAxis
                tickFormatter={(value: number) => `${Math.round(value / 1000)}k`}
                tick={{ fill: '#64748b', fontSize: 11 }}
                width={48}
              />
              <Tooltip
                labelFormatter={(value) => formatTime(String(value))}
                formatter={(value) => [`${formatNumber(Number(value))} MW`]}
                contentStyle={{
                  borderRadius: 10,
                  border: '1px solid #e2e8f0',
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="actual_mw"
                name="Actual"
                stroke="#0d9488"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="forecast_mw"
                name="Forecast"
                stroke="#6366f1"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="chart-note">
          Showing every sixth hourly period for readability. KPI calculations
          use all matched periods.
        </p>
      </section>

      <section className="secondary-grid">
        <article className="panel summary-panel">
          <p className="eyebrow">DIRECTIONAL ACCURACY</p>
          <h2>Which way did the forecast miss?</h2>
          <div className="direction-row">
            <div>
              <span className="direction-dot teal" />
              Underforecast hours
            </div>
            <strong>{metrics.underforecast_hours}</strong>
          </div>
          <div className="direction-row">
            <div>
              <span className="direction-dot purple" />
              Overforecast hours
            </div>
            <strong>{metrics.overforecast_hours}</strong>
          </div>
          <p className="footnote">
            Error = forecast minus actual. Positive bias means generation was
            generally forecast higher than observed.
          </p>
        </article>

        <article className="panel summary-panel">
          <p className="eyebrow">EVALUATION SETUP</p>
          <h2>How to read these results</h2>
          <div className="detail-row">
            <span>Delivery month</span>
            <strong>January 2026</strong>
          </div>
          <div className="detail-row">
            <span>Publication cutoff</span>
            <strong>{metrics.cutoff_hours} hours</strong>
          </div>
          <div className="detail-row">
            <span>Mean forecast lead</span>
            <strong>{formatNumber(metrics.mean_lead_hours)} hours</strong>
          </div>
          <p className="footnote">
            Wind forecast accuracy is one input to procurement decisions, not
            a complete trading recommendation.
          </p>
        </article>
      </section>

      <section className="panel table-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">INVESTIGATE THE DEVIATIONS</p>
            <h2>10 largest forecast errors</h2>
          </div>
          <span className="unit-label">Sorted by absolute error</span>
        </div>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Delivery time (UTC)</th>
                <th>Forecast (MW)</th>
                <th>Actual (MW)</th>
                <th>Error (MW)</th>
                <th>Lead time</th>
              </tr>
            </thead>
            <tbody>
              {periods.map((period) => (
                <tr key={period.startTime}>
                  <td>{formatTime(period.startTime)}</td>
                  <td>{formatNumber(period.forecast_mw)}</td>
                  <td>{formatNumber(period.actual_mw)}</td>
                  <td className={period.error_mw >= 0 ? 'positive' : 'negative'}>
                    {period.error_mw > 0 ? '+' : ''}
                    {formatNumber(period.error_mw)}
                  </td>
                  <td>{formatNumber(period.lead_hours)} h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="footer">
        <span>WindLens · Forecast accuracy explorer</span>
        <span>Data: Elexon BMRS · January 2026</span>
      </footer>
    </main>
  )
}

export default App
