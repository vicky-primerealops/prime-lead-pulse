'use client';

import { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format, subDays, startOfDay } from 'date-fns';

export default function ActivityTrends({ events }: { events: any[] }) {
  const data = useMemo(() => {
    const last30Days = Array.from({ length: 30 }).map((_, i) => {
      const d = startOfDay(subDays(new Date(), 29 - i));
      return {
        date: d.getTime(),
        label: format(d, 'MMM d'),
        Opens: 0,
        Clicks: 0
      };
    });

    events.forEach(ev => {
      const evDate = startOfDay(new Date(ev.created_at)).getTime();
      const bucket = last30Days.find(b => b.date === evDate);
      if (bucket) {
        if (ev.event_type === 'open') bucket.Opens++;
        if (ev.event_type === 'click') bucket.Clicks++;
      }
    });

    return last30Days;
  }, [events]);

  const totalOpens = data.reduce((a, b) => a + b.Opens, 0);
  const totalClicks = data.reduce((a, b) => a + b.Clicks, 0);

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 col-span-2 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-bl from-blue-50/50 to-transparent rounded-full -mr-32 -mt-32 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
      <div className="flex justify-between items-start mb-6 relative z-10">
        <div>
          <h2 className="text-base font-extrabold text-slate-900 tracking-tight">Activity Trends (Last 30 Days)</h2>
          <p className="text-[12px] font-medium text-slate-500 mt-1">Monitor your email engagement metrics over time</p>
        </div>
        <div className="flex items-center gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5 text-slate-600">
            <div className="w-2.5 h-2.5 rounded-full bg-[#3b82f6]"></div>
            {totalOpens} Opens
          </div>
          <div className="flex items-center gap-1.5 text-slate-600">
            <div className="w-2.5 h-2.5 rounded-full bg-[#10b981]"></div>
            {totalClicks} Clicks
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorOpens" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorClicks" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis 
              dataKey="label" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 11, fill: '#94a3b8' }} 
              dy={10}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              tickCount={5}
            />
            <Tooltip
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)' }}
              itemStyle={{ fontSize: '13px', fontWeight: 500 }}
              labelStyle={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}
            />
            <Area type="monotone" dataKey="Opens" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorOpens)" />
            <Area type="monotone" dataKey="Clicks" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorClicks)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
