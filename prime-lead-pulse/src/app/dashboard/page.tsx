'use client';

import { useDashboardData, ProcessedEmail } from '@/hooks/useDashboardData';
import Sidebar from '@/components/Sidebar';
import { Mail, Eye, MousePointerClick, BarChart3, Clock } from 'lucide-react';

function StatCard({ label, value, icon: Icon, color }: { label: string; value: string | number; icon: any; color: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5 flex items-start justify-between shadow-sm">
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-1">{label}</p>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
      </div>
      <div className={`p-2 rounded-lg ${color}`}>
        <Icon size={20} className="text-white" />
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
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-gray-500">Loading...</div>
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
    <div className="flex items-center gap-3 text-sm">
      <span className="w-28 text-gray-500 text-xs">{label}</span>
      <div className="flex-1 bg-gray-100 rounded-full h-2">
        <div className={`${color} h-2 rounded-full`} style={{ width: `${pct(count)}%` }} />
      </div>
      <span className="w-16 text-right text-gray-700 font-medium text-xs">{pct(count)}% · {count}</span>
    </div>
  );

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar userEmail={user?.email || ''} onLogout={logout} />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">Track your email performance and engagement metrics.</p>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Emails" value={totalEmails} icon={Mail} color="bg-indigo-500" />
          <StatCard label="Opens" value={totalOpens} icon={Eye} color="bg-blue-500" />
          <StatCard label="Clicks" value={totalClicks} icon={MousePointerClick} color="bg-green-500" />
          <StatCard label="Open Rate" value={`${openRate}%`} icon={BarChart3} color="bg-pink-500" />
        </div>

        {/* Two-column section */}
        <div className="grid grid-cols-2 gap-6">
          {/* Time to First Open */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-gray-500" />
                <h2 className="font-semibold text-gray-900 text-sm">Time to First Open</h2>
              </div>
              <span className="text-xs text-gray-400">{totalEmails} emails</span>
            </div>
            {withOpens.length > 0 && (
              <div className="flex items-center gap-4 mb-4">
                <span className="text-sm font-medium text-gray-700">⏱ Avg {getTimeToOpenLabel(avgMs)}</span>
                <span className="text-xs text-green-600 font-medium">⚡ {pct(buckets.under4h + buckets.under1h)}% opened within 4h</span>
              </div>
            )}
            <div className="space-y-3">
              <BucketBar label="Within 1 hour" count={buckets.under1h} color="bg-green-500" />
              <BucketBar label="1 – 4 hours" count={buckets.under4h} color="bg-yellow-400" />
              <BucketBar label="Within 2 days" count={buckets.under2d} color="bg-orange-400" />
              <BucketBar label="2+ days" count={buckets.over2d} color="bg-red-400" />
              <BucketBar label="Never opened" count={buckets.never} color="bg-gray-300" />
            </div>
          </div>

          {/* Engagement Rates */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
            <h2 className="font-semibold text-gray-900 text-sm mb-5">Engagement Rates</h2>
            <div className="space-y-6">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Eye size={14} className="text-blue-500" />
                    Open Rate
                  </div>
                  <span className="font-bold text-gray-900 text-lg">{openRate}%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${openRate}%` }} />
                </div>
                <p className="text-xs text-gray-400 mt-1">{openedEmails} opened</p>
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <MousePointerClick size={14} className="text-green-500" />
                    Click Rate
                  </div>
                  <span className="font-bold text-gray-900 text-lg">{clickRate}%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: `${clickRate}%` }} />
                </div>
                <p className="text-xs text-gray-400 mt-1">{totalClicks} clicks</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
