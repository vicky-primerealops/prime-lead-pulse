'use client';

import { Eye, MousePointerClick, X } from 'lucide-react';
import { ProcessedEmail } from '@/hooks/useDashboardData';

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit',
  });
}

export default function ActivityModal({ email, onClose }: { email: ProcessedEmail; onClose: () => void }) {
  const events = [...email.events].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[80vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between px-6 py-5 border-b border-gray-100">
          <div>
            <h2 className="font-semibold text-gray-900">Activity Timeline</h2>
            <p className="text-sm text-gray-400 mt-0.5">{email.recipient}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 mt-0.5">
            <X size={18} />
          </button>
        </div>

        {/* Events */}
        <div className="overflow-y-auto px-6 py-4 space-y-3">
          {events.length === 0 ? (
            <p className="text-center text-gray-400 py-8">No activity yet.</p>
          ) : (
            events.map((ev, i) => (
              <div key={ev.id} className="flex gap-3">
                {/* Icon */}
                <div className="flex flex-col items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${ev.event_type === 'open' ? 'bg-blue-50' : 'bg-green-50'}`}>
                    {ev.event_type === 'open'
                      ? <Eye size={14} className="text-blue-500" />
                      : <MousePointerClick size={14} className="text-green-500" />
                    }
                  </div>
                  {i < events.length - 1 && <div className="w-px flex-1 bg-gray-100 my-1" />}
                </div>

                {/* Content */}
                <div className="flex-1 pb-3">
                  <div className="flex items-center justify-between">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${ev.event_type === 'open' ? 'bg-blue-50 text-blue-700' : 'bg-green-50 text-green-700'}`}>
                      {ev.event_type === 'open' ? 'Open' : 'Click'}
                    </span>
                    <span className="text-xs text-gray-400">{formatDate(ev.created_at)}</span>
                  </div>
                  {ev.event_type === 'click' && ev.url && (
                    <div className="mt-2 bg-gray-50 rounded-lg px-3 py-2">
                      <p className="text-xs text-gray-500 font-medium mb-0.5">Clicked Link:</p>
                      <p className="text-xs text-indigo-600 break-all">{ev.url}</p>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
