"use client"
import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

const COLORS = ['#60a5fa', '#818cf8', '#c084fc']

export default function LoyaltyStats({ data }: { data: any }) {
    if (!data || !data.segments) return null

    const chartData = data.segments.map((s: any) => ({
        name: s.name,
        value: s.percentage,
        count: s.count
    }))

    return (
        <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-2xl">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold uppercase tracking-wider text-slate-400 text-xs">Analyse RFM (Clients)</h2>
                <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-400">{data.total_clients.toLocaleString()} Clients</span>
            </div>

            <div className="flex flex-col md:flex-row items-center gap-8">
                <div className="h-[250px] w-full md:w-1/2">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {chartData.map((entry: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', border: 'solid 1px #1e293b', borderRadius: '12px' }}
                                itemStyle={{ color: '#f1f5f9' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                <div className="w-full md:w-1/2 space-y-4">
                    {chartData.map((s: any, index: number) => (
                        <div key={s.name} className="flex flex-col">
                            <div className="flex justify-between items-center mb-1">
                                <span className="text-sm font-medium text-slate-300">{s.name}</span>
                                <span className="text-sm font-bold text-slate-100">{s.value}%</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-2">
                                <div
                                    className="h-2 rounded-full"
                                    style={{ width: `${s.value}%`, backgroundColor: COLORS[index % COLORS.length] }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
