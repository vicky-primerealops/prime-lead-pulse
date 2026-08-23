'use client';

import { ProcessedEmail } from '@/hooks/useDashboardData';
import { Eye, MousePointerClick } from 'lucide-react';
import { format } from 'date-fns';

export default function RecentActivity({ emails }: { emails: ProcessedEmail[] }) {
  // Flatten all events
  const allEvents: any[] = [];
  emails.forEach(email => {
    email.events.forEach(ev => {
      allEvents.push({
        ...ev,
        subject: email.subject,
        recipient: email.recipient,
        emailStatus: email.status
      });
    });
  });

  // Sort by date desc
  allEvents.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  
  // Take top 8
  const recent = allEvents.slice(0, 8);

  const StatusBadge = ({ status }: { status: string }) => {
    const styles: any = {
      Clicked: 'bg-[#f0fdf4] text-[#166534] border border-[#bbf7d0]',
      Opened: 'bg-[#f8fafc] text-[#334155] border border-[#e2e8f0]',
      Sent: 'bg-white text-slate-400 border border-slate-200',
    };
    return (
      <span className={`inline-flex items-center px-1.5 py-0.5 rounded-[4px] text-[10px] font-bold uppercase tracking-wider ${styles[status]}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 hover:shadow-md transition-shadow duration-300">
      <h2 className="text-base font-bold text-slate-900 mb-6">Recent Activity</h2>

      <div className="space-y-5">
        {recent.length === 0 ? (
          <p className="text-sm text-slate-400 py-4 text-center">No activity yet.</p>
        ) : (
          recent.map(ev => {
            const isOpen = ev.event_type === 'open';
            return (
              <div key={ev.id} className="flex gap-3 group cursor-pointer">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isOpen ? 'bg-[#eff6ff] text-[#3b82f6]' : 'bg-[#f0fdf4] text-[#10b981]'}`}>
                  {isOpen ? <Eye size={14} /> : <MousePointerClick size={14} />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <p className="text-[13px] font-semibold text-slate-900 truncate group-hover:text-indigo-600 transition-colors">
                      {ev.subject}
                    </p>
                    <StatusBadge status={ev.emailStatus} />
                  </div>
                  <p className="text-[11px] text-slate-500 truncate mb-0.5">{ev.recipient}</p>
                  {ev.url && <p className="text-[11px] text-[#3b82f6] truncate">{ev.url}</p>}
                </div>
                <div className="text-[10px] text-slate-400 whitespace-nowrap pt-1">
                  {format(new Date(ev.created_at), 'MMM d, yyyy, h:mm a')}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
