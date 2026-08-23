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
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 hover:shadow-md transition-shadow duration-300">
      <div className="flex items-center gap-2 mb-2">
        <Flame size={18} className="text-orange-500 fill-orange-500/20" />
        <h2 className="text-base font-bold text-slate-900">High Interest</h2>
      </div>
      <p className="text-[11px] text-slate-500 mb-5">Recipients who opened your email multiple times are likely warm leads worth following up on.</p>

      <div className="space-y-4">
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
