"use client"
import React, { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, AreaChart, Area } from 'recharts'
import { BrainCircuit, Target, TrendingUp, ChevronLeft } from 'lucide-react'
import Link from 'next/link'

const API_BASE = "http://localhost:8000/api/v1"
const COLORS = ['#60a5fa', '#818cf8', '#a78bfa', '#f472b6']

export default function MLPage() {
    const [segments, setSegments] = useState<any>(null)
    const [forecast, setForecast] = useState<any[]>([])
    const [xgbForecast, setXgbForecast] = useState<any[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        let interval: NodeJS.Timeout;

        const fetchML = async () => {
            try {
                const [segRes, foreRes, xgbRes] = await Promise.all([
                    fetch(`${API_BASE}/ml/segments/summary`),
                    fetch(`${API_BASE}/ml/predict/forecast`),
                    fetch(`${API_BASE}/ml/predict/xgboost-forecast`, { method: 'POST' })
                ])

                if (!segRes.ok || !foreRes.ok || !xgbRes.ok) throw new Error("ML results not ready")

                const sData = await segRes.json()
                const fData = await foreRes.json()
                const xData = await xgbRes.json()

                if (!sData.summary || Object.keys(sData.summary).length === 0) throw new Error("Empty ML data")

                setSegments(sData)
                setForecast(fData)
                setXgbForecast(xData)
                setLoading(false)
                clearInterval(interval)
            } catch (e) {
                console.log("Waiting for ML data...", e)
            }
        }

        fetchML()
        interval = setInterval(fetchML, 5000)
        return () => clearInterval(interval)
    }, [])

    if (loading) return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-white space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
            <h2 className="text-xl font-semibold">Analyse des modèles en cours...</h2>
            <p className="text-slate-400 animate-pulse">Extraction des segments RFM et calcul des prévisions...</p>
        </div>
    )

    const pieData = Object.entries(segments?.summary?.Monetary_count || {}).map(([name, value]) => ({
        name: `Segment ${name}`,
        value
    }))

    // Merge forecasts for comparison
    const comparisonData = forecast.map((f, i) => ({
        date: f.date,
        simple: f.prediction,
        xgboost: xgbForecast[i]?.prediction
    }))

    return (
        <div className="p-8 space-y-8 bg-slate-950 min-h-screen text-slate-100 font-sans">
            <header className="flex justify-between items-center mb-8">
                <div className="flex items-center gap-4">
                    <Link href="/" className="bg-slate-900 p-2 rounded-lg border border-slate-800 hover:bg-slate-800 transition-colors">
                        <ChevronLeft />
                    </Link>
                    <div>
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">Machine Learning Insights</h1>
                        <p className="text-slate-400">Intelligence prédictive et segmentation stratégique (XGBoost)</p>
                    </div>
                </div>
                <div className="bg-slate-900 p-3 rounded-2xl border border-slate-800 shadow-xl">
                    <BrainCircuit className="text-purple-400" size={32} />
                </div>
            </header>

            <div className="bg-slate-900/50 p-6 rounded-2xl border border-indigo-500/30 mb-8">
                <h3 className="text-indigo-400 font-bold mb-2">Pourquoi XGBoost ?</h3>
                <p className="text-sm text-slate-300 leading-relaxed">
                    XGBoost est un algorithme de Gradient Boosting puissant capable de capturer des relations non-linéaires complexes et des saisonnalités que les modèles de régression linéaire simples ignorent.
                    En utilisant des features temporelles (année, mois, trimestre), il offre une précision accrue pour la planification stratégique du stock et des revenus.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Customer Segmentation */}
                <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 shadow-2xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Target size={120} className="text-pink-400" />
                    </div>
                    <div className="flex items-center gap-2 mb-8 text-xl font-bold">
                        <Target className="text-pink-400" />
                        <h2>Répartition des Segments RFM</h2>
                    </div>
                    <div className="h-[350px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie data={pieData} innerRadius={80} outerRadius={120} paddingAngle={8} dataKey="value" stroke="none">
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: 'solid 1px #1e293b', borderRadius: '12px' }} />
                                <Legend verticalAlign="bottom" height={36} iconType="circle" />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Sales Forecast Comparison */}
                <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 shadow-2xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <TrendingUp size={120} className="text-green-400" />
                    </div>
                    <div className="flex items-center gap-2 mb-8 text-xl font-bold">
                        <TrendingUp className="text-green-400" />
                        <h2>Comparaison des Prévisions (Chiffre d'Affaires)</h2>
                    </div>
                    <div className="h-[350px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={comparisonData}>
                                <defs>
                                    <linearGradient id="colorSimple" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#64748b" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#64748b" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorXgb" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: 'solid 1px #1e293b', borderRadius: '12px' }} />
                                <Legend />
                                <Area type="monotone" name="Modèle de Base" dataKey="simple" stroke="#64748b" fillOpacity={1} fill="url(#colorSimple)" strokeWidth={2} strokeDasharray="5 5" />
                                <Area type="monotone" name="XGBoost Forecasting" dataKey="xgboost" stroke="#10b981" fillOpacity={1} fill="url(#colorXgb)" strokeWidth={3} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    )
}
