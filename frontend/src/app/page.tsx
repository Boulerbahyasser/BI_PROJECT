"use client"
import React, { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import { ShoppingCart, Users, DollarSign, TrendingUp, BrainCircuit } from 'lucide-react'
import Link from 'next/link'
import LoyaltyStats from '@/components/LoyaltyStats'
import CountryStats from '@/components/CountryStats'

const API_BASE = "http://localhost:8000/api/v1"

export default function Dashboard() {
  const [kpis, setKpis] = useState<any>(null)
  const [topProducts, setTopProducts] = useState<any[]>([])
  const [timeseries, setTimeseries] = useState<any>(null)
  const [loyalty, setLoyalty] = useState<any>(null)
  const [countries, setCountries] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchData = async () => {
      try {
        const [kpiRes, topRes, tsRes, loyaltyRes, countryRes] = await Promise.all([
          fetch(`${API_BASE}/kpis/overview`),
          fetch(`${API_BASE}/sales/top-products`),
          fetch(`${API_BASE}/sales/timeseries`),
          fetch(`${API_BASE}/ml/loyalty`),
          fetch(`${API_BASE}/stats/countries?limit=6`)
        ])

        if (!kpiRes.ok || !topRes.ok || !tsRes.ok || !loyaltyRes.ok || !countryRes.ok) throw new Error("Backend still loading")

        const kData = await kpiRes.json()
        const tData = await topRes.json()
        const tsData = await tsRes.json()
        const lData = await loyaltyRes.json()
        const cData = await countryRes.json()

        if (Object.keys(kData).length === 0) throw new Error("Empty data")

        setKpis(kData)
        setTopProducts(tData)
        setTimeseries(Object.entries(tsData).map(([name, value]) => ({ name, value })))
        setLoyalty(lData)
        setCountries(cData)
        setLoading(false)
        clearInterval(interval)
      } catch (e) {
        console.log("Waiting for data...", e)
      }
    }

    fetchData()
    interval = setInterval(fetchData, 5000) // Retry every 5s
    return () => clearInterval(interval)
  }, [])

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-white space-y-4">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      <h2 className="text-xl font-semibold">Chargement du Dashboard BI...</h2>
      <p className="text-slate-400 animate-pulse">Traitement du dataset Online Retail (540k lignes) en cours...</p>
      <p className="text-xs text-slate-500">Cela peut prendre 1 à 2 minutes lors du premier démarrage.</p>
    </div>
  )

  return (
    <div className="p-8 space-y-8 bg-slate-950 min-h-screen text-slate-100 font-sans">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-indigo-600 bg-clip-text text-transparent">BI E-commerce Dashboard</h1>
          <p className="text-slate-400">Analyse des ventes et segmentation clients</p>
        </div>
        <div className="flex gap-4">
          <Link href="/ml" className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-xl transition-colors font-medium">
            <BrainCircuit size={20} />
            Machine Learning
          </Link>
        </div>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KpiCard title="Chiffre d'Affaires" value={`${kpis?.ca_total?.toLocaleString()} €`} icon={<DollarSign className="text-green-400" />} />
        <KpiCard title="Commandes" value={kpis?.nb_commandes} icon={<ShoppingCart className="text-blue-400" />} />
        <KpiCard title="Panier Moyen" value={`${kpis?.panier_moyen} €`} icon={<TrendingUp className="text-purple-400" />} />
        <KpiCard title="Clients Uniques" value={kpis?.clients_uniques} icon={<Users className="text-orange-400" />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Sales Timeseries */}
        <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-2xl">
          <h2 className="text-xl font-semibold mb-6 uppercase tracking-wider text-slate-400 text-xs">Évolution du CA par mois</h2>
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeseries}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `${val / 1000}k`} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: 'solid 1px #1e293b', borderRadius: '12px' }} />
                <Line type="monotone" dataKey="value" stroke="#60a5fa" strokeWidth={4} dot={false} activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Products */}
        <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-2xl">
          <h2 className="text-xl font-semibold mb-6 uppercase tracking-wider text-slate-400 text-xs">Top Produits (CA)</h2>
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topProducts}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="Description" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: 'solid 1px #1e293b', borderRadius: '12px' }} />
                <Bar dataKey="TotalPrice" fill="#818cf8" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* New Stats Row */}
        <LoyaltyStats data={loyalty} />
        <CountryStats data={countries} />
      </div>
    </div>
  )
}

function KpiCard({ title, value, icon }: any) {
  return (
    <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-lg hover:border-indigo-500/30 transition-all duration-300 group">
      <div className="flex justify-between items-start mb-4">
        <span className="text-slate-400 text-sm font-semibold uppercase tracking-wider">{title}</span>
        <div className="bg-slate-800 p-2 rounded-xl group-hover:scale-110 transition-transform">{icon}</div>
      </div>
      <div className="text-3xl font-bold tracking-tight">{value}</div>
    </div>
  )
}
