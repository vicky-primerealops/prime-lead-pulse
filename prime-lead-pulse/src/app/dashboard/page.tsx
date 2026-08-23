'use client';

import { useDashboardData } from '@/hooks/useDashboardData';
import DashboardLayout from '@/components/DashboardLayout';
import HighInterest from '@/components/HighInterest';
import RecentActivity from '@/components/RecentActivity';
import ActivityTrends from '@/components/ActivityTrends';
import { Mail, Eye, MousePointerClick, BarChart3, Clock, ChevronDown, TrendingUp } from 'lucide-react';

function StatCard({ label, value, icon: Icon, colorClass, iconColor, trend }: { label: string; value: string | number; icon: any; colorClass: string; iconColor: string; trend?: boolean }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-start justify-between shadow-sm hover:shadow-md transition-shadow duration-300">
      <div>
        <p className="text-[11px] text-slate-500 uppercase tracking-widest font-bold mb-1.5">{label}</p>
        <p className="text-3xl font-extrabold text-slate-900">{value}</p>
      </div>
      <div className={`p-2.5 rounded-xl ${colorClass}`}>
        <Icon size={18} className={iconColor} />
      </div>
    </div>
  );
}

function getTimeToOpenLabel(ms: number) {
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  if (h >= 48) return `${Math.floor(h / 24)}d`;
  if (h >= 1) return `${h}h ${m}m`;
  return `${m}m`;
}

export default function DashboardPage() {
  const { emails, loading, user, logout } = useDashboardData();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#f8f9fa]">
        <div className="text-slate-500 font-medium">Loading Dashboard...</div>
      </div>
    );
  }

  const totalEmails = emails.length;
  const totalOpens = emails.reduce((s, e) => s + e.opens, 0);
  const totalClicks = emails.reduce((s, e) => s + e.clicks, 0);
  const openedEmails = emails.filter(e => e.opens > 0).length;
  const openRate = totalEmails > 0 ? ((openedEmails / totalEmails) * 100).toFixed(1) : '0.0';

  // Time to first open analysis
  const withOpens = emails.filter(e => e.first_opened_at);
  let avgMs = 0;
  const buckets = { under1h: 0, under4h: 0, under2d: 0, over2d: 0, never: emails.filter(e => e.opens === 0).length };

  if (withOpens.length > 0) {
    const times = withOpens.map(e => new Date(e.first_opened_at!).getTime() - new Date(e.created_at).getTime());
    avgMs = times.reduce((a, b) => a + b, 0) / times.length;
    times.forEach(t => {
      if (t < 3600000) buckets.under1h++;
      else if (t < 14400000) buckets.under4h++;
      else if (t < 172800000) buckets.under2d++;
      else buckets.over2d++;
    });
  }

  const pct = (n: number) => totalEmails > 0 ? Math.round((n / totalEmails) * 100) : 0;
  const clickRate = totalEmails > 0 ? ((emails.filter(e => e.clicks > 0).length / totalEmails) * 100).toFixed(1) : '0.0';

  const BucketBar = ({ label, count, color }: { label: string; count: number; color: string }) => (
    <div className="flex items-center gap-4 text-sm mb-3.5 last:mb-0">
      <span className="w-24 text-slate-500 text-[11px] font-medium">{label}</span>
      <div className="flex-1 bg-slate-100 rounded-full h-[6px]">
        <div className={`${color} h-[6px] rounded-full`} style={{ width: `${pct(count)}%` }} />
      </div>
      <span className="w-16 text-right text-slate-500 font-bold text-[11px] bg-slate-50 px-2 py-0.5 rounded-full">{count} emails</span>
    </div>
  );

  const allEvents = emails.flatMap(e => e.events);

  return (
    <DashboardLayout userEmail={user?.email || ''} onLogout={logout}>
      <div className="p-8 max-w-7xl mx-auto space-y-6 pb-20">
        
        {/* Header Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Dashboard</h1>
            <p className="text-slate-500 text-[13px] mt-1 font-medium">Track your email performance and engagement metrics.</p>
          </div>
          <button className="flex items-center gap-2 bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-[13px] font-bold shadow-sm hover:bg-slate-50 transition-colors">
            Last 30 Days <ChevronDown size={14} className="text-slate-400" />
          </button>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-4 gap-6">
          <StatCard label="Total Emails" value={totalEmails} icon={Mail} colorClass="bg-indigo-50" iconColor="text-indigo-500" />
          <StatCard label="Opens" value={totalOpens} icon={Eye} colorClass="bg-blue-50" iconColor="text-blue-500" />
          <StatCard label="Clicks" value={totalClicks} icon={MousePointerClick} colorClass="bg-emerald-50" iconColor="text-emerald-500" />
          <StatCard label="Open Rate" value={`${openRate}%`} icon={TrendingUp} colorClass="bg-pink-50" iconColor="text-pink-500" />
        </div>

        {/* Middle Section (Time to Open & Engagement) */}
        <div className="grid grid-cols-2 gap-6">
          {/* Time to First Open */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 hover:shadow-md transition-shadow duration-300">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-slate-400" />
                <h2 className="font-bold text-slate-900 text-sm">Time to First Open</h2>
              </div>
              <span className="text-[11px] font-bold text-slate-500 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-100">{totalEmails} emails</span>
            </div>
            
            {withOpens.length > 0 && (
              <div className="flex items-center gap-3 mb-6">
                <span className="text-[11px] font-bold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md flex items-center gap-1">
                  <Clock size={12} /> Avg {getTimeToOpenLabel(avgMs)}
                </span>
                <span className="text-[11px] text-[#10b981] font-bold bg-[#f0fdf4] px-2.5 py-1 rounded-md flex items-center gap-1 border border-[#bbf7d0]">
                  ⚡ {pct(buckets.under4h + buckets.under1h)}% opened within 4h
                </span>
              </div>
            )}
            
            {/* The main bar */}
            <div className="w-full flex h-2 rounded-full overflow-hidden mb-6 gap-0.5">
              <div className="bg-[#10b981]" style={{ width: `${pct(buckets.under1h)}%` }} />
              <div className="bg-[#fbbf24]" style={{ width: `${pct(buckets.under4h)}%` }} />
              <div className="bg-[#f97316]" style={{ width: `${pct(buckets.under2d)}%` }} />
              <div className="bg-[#f43f5e]" style={{ width: `${pct(buckets.over2d)}%` }} />
              <div className="bg-slate-200" style={{ width: `${pct(buckets.never)}%` }} />
            </div>

            <div>
              <BucketBar label="Within 1 hour" count={buckets.under1h} color="bg-[#10b981]" />
              <BucketBar label="1 - 4 hours" count={buckets.under4h} color="bg-[#fbbf24]" />
              <BucketBar label="Within 2 days" count={buckets.under2d} color="bg-[#f97316]" />
              <BucketBar label="2+ days" count={buckets.over2d} color="bg-[#f43f5e]" />
              <BucketBar label="Never opened" count={buckets.never} color="bg-slate-300" />
            </div>
          </div>

          {/* Engagement Rates */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 hover:shadow-md transition-shadow duration-300">
            <h2 className="font-bold text-slate-900 text-base mb-6">Engagement Rates</h2>
            <div className="space-y-8">
              <div>
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-2 text-[13px] font-semibold text-slate-700">
                    <div className="bg-blue-50 p-1.5 rounded-md"><Eye size={14} className="text-blue-500" /></div>
                    Open Rate
                  </div>
                  <span className="font-extrabold text-slate-900 text-xl">{openRate}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5">
                  <div className="bg-blue-500 h-2.5 rounded-full" style={{ width: `${openRate}%` }} />
                </div>
                <p className="text-[11px] font-medium text-slate-400 mt-2">{openedEmails} open</p>
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-2 text-[13px] font-semibold text-slate-700">
                    <div className="bg-emerald-50 p-1.5 rounded-md"><MousePointerClick size={14} className="text-emerald-500" /></div>
                    Click Rate
                  </div>
                  <span className="font-extrabold text-slate-900 text-xl">{clickRate}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5">
                  <div className="bg-emerald-500 h-2.5 rounded-full" style={{ width: `${clickRate}%` }} />
                </div>
                <p className="text-[11px] font-medium text-slate-400 mt-2">{totalClicks} click</p>
              </div>
            </div>
          </div>
        </div>

        {/* Lower Section (High Interest & Recent Activity) */}
        <div className="grid grid-cols-2 gap-6">
          <HighInterest emails={emails} />
          <RecentActivity emails={emails} />
        </div>

        {/* Chart Section */}
        <ActivityTrends events={allEvents} />
        
        {/* Templates Section */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-base font-bold text-slate-900">Email Templates</h2>
            <button className="text-[12px] font-bold text-slate-500 hover:text-slate-900 transition-colors flex items-center gap-1">
              View All <TrendingUp size={14} />
            </button>
          </div>
          <div className="text-center py-10">
            <p className="text-[13px] text-slate-400 font-medium">No email templates yet</p>
            <button className="mt-3 text-[12px] font-bold text-slate-900 hover:text-indigo-600 transition-colors">
              Create your first email template
            </button>
          </div>
        </div>

      </div>
    </DashboardLayout>
  );
}
