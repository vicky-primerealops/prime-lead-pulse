'use client';

import { Flame } from 'lucide-react';
import { ProcessedEmail } from '@/hooks/useDashboardData';
import { format } from 'date-fns';

export default function HighInterest({ emails }: { emails: ProcessedEmail[] }) {
  const highInterest = emails
    .filter(e => e.opens > 1)
    .sort((a, b) => b.opens - a.opens)
    .slice(0, 7);

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-orange-100/50 to-transparent rounded-full -mr-10 -mt-10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      <div className="flex items-center gap-2 mb-2 relative z-10">
        <div className="bg-gradient-to-br from-orange-400 to-red-500 p-1.5 rounded-lg shadow-sm text-white">
          <Flame size={16} strokeWidth={2.5} />
        </div>
        <h2 className="text-base font-extrabold text-slate-900 tracking-tight">High Interest</h2>
      </div>
      <p className="text-[12px] font-medium text-slate-500 mb-5 relative z-10">Recipients who opened your email multiple times are likely warm leads worth following up on.</p>

      <div className="space-y-4 relative z-10">
        {highInterest.length === 0 ? (
          <p className="text-sm text-slate-400 py-4 text-center">No high interest emails yet.</p>
        ) : (
          highInterest.map(email => (
            <div key={email.id} className="flex items-start justify-between group cursor-pointer">
              <div className="overflow-hidden pr-4">
                <p className="text-[13px] font-semibold text-slate-900 truncate group-hover:text-indigo-600 transition-colors">{email.subject}</p>
                <p className="text-[11px] text-slate-500 truncate">{email.recipient}</p>
              </div>
              <div className="text-right whitespace-nowrap shrink-0">
                <p className="text-[12px] font-bold text-red-500 flex items-center justify-end gap-1">
                  <EyeIcon /> {email.opens} opens
                </p>
                <p className="text-[10px] text-slate-400 mt-0.5 text-right flex items-center justify-end gap-1">
                  <ClockIcon /> {format(new Date(email.last_opened!), 'MMM d')}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function EyeIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function ClockIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}
