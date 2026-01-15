"use client"
import React from 'react'
import { Globe } from 'lucide-react'

export default function CountryStats({ data }: { data: any[] }) {
    if (!data || data.length === 0) return null

    const maxRevenue = Math.max(...data.map(d => d.revenue))

    return (
        <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-2xl">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold uppercase tracking-wider text-slate-400 text-xs">Analyse géographique (pays)</h2>
                <Globe size={16} className="text-slate-500" />
            </div>

            <div className="space-y-4">
                {data.map((c: any) => (
                    <div key={c.country} className="group cursor-default">
                        <div className="flex justify-between items-center mb-1">
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-medium text-slate-300">{c.country}</span>
                            </div>
                            <span className="text-sm font-semibold text-slate-100">{c.revenue.toLocaleString()} €</span>
                        </div>
                        <div className="relative w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                            <div
                                className="absolute left-0 top-0 h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-1000"
                                style={{ width: `${(c.revenue / maxRevenue) * 100}%` }}
                            />
                        </div>
                        <div className="flex justify-between mt-1">
                            <span className="text-[10px] text-slate-500">{c.orders} Commandes</span>
                            <span className="text-[10px] text-slate-500">{Math.round((c.revenue / maxRevenue) * 100)}% du leader</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
