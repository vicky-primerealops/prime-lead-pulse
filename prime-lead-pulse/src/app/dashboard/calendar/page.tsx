'use client';

import { useDashboardData } from '@/hooks/useDashboardData';
import DashboardLayout from '@/components/DashboardLayout';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';

export default function CalendarPage() {
  const { user, loading, logout } = useDashboardData();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#f8f9fa]">
        <div className="text-slate-500 font-medium">Loading Calendar...</div>
      </div>
    );
  }

  const days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
  
  return (
    <DashboardLayout userEmail={user?.email || ''} onLogout={logout}>
      <div className="p-8 max-w-7xl mx-auto h-full flex flex-col">
        
        {/* We recreate the look of the calendar in the video */}
        <div className="flex-1 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          
          {/* Calendar Toolbar */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
            <div className="flex items-center gap-4">
              <button className="bg-white border border-slate-200 text-slate-700 px-3 py-1.5 rounded text-[13px] font-bold hover:bg-slate-50 transition-colors">
                Today
              </button>
              <div className="flex items-center gap-2">
                <button className="text-slate-400 hover:text-slate-600"><ChevronLeft size={20} /></button>
                <button className="text-slate-400 hover:text-slate-600"><ChevronRight size={20} /></button>
              </div>
              <h2 className="text-[16px] font-bold text-slate-900 ml-2">August 2026</h2>
            </div>
            
            <div className="flex items-center gap-6 text-[12px] font-medium text-slate-600">
              <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-slate-300"></div> Trending</div>
              <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-indigo-200"></div> Scheduled</div>
              <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-emerald-200"></div> Sent</div>
              <select className="border border-slate-200 rounded px-2 py-1 bg-white focus:outline-none">
                <option>India ▼</option>
              </select>
            </div>
          </div>

          <div className="flex flex-1 overflow-hidden">
            {/* Main Calendar Grid */}
            <div className="flex-1 border-r border-slate-200 flex flex-col overflow-y-auto">
              {/* Days Header */}
              <div className="flex border-b border-slate-100 sticky top-0 bg-white z-10">
                <div className="w-16 border-r border-slate-100 shrink-0 flex flex-col items-center justify-center p-2 text-center">
                  <span className="text-[10px] text-slate-400 font-bold">GMT<br/>+05:30</span>
                </div>
                {days.map((day, i) => (
                  <div key={day} className="flex-1 border-r border-slate-100 last:border-r-0 py-3 text-center">
                    <p className="text-[11px] font-bold text-slate-500 mb-1">{day}</p>
                    <div className={`text-[16px] font-semibold w-8 h-8 mx-auto flex items-center justify-center rounded-full ${i === 0 ? 'bg-indigo-600 text-white' : 'text-slate-900'}`}>
                      {24 + i}
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Hours Grid */}
              {Array.from({ length: 24 }).map((_, hour) => (
                <div key={hour} className="flex border-b border-slate-100 min-h-[60px] group">
                  <div className="w-16 border-r border-slate-100 shrink-0 flex flex-col items-end pr-2 py-2">
                    <span className="text-[10px] text-slate-400 font-medium">{hour === 0 ? '12 AM' : hour < 12 ? `${hour} AM` : hour === 12 ? '12 PM' : `${hour - 12} PM`}</span>
                  </div>
                  {days.map((day, i) => (
                    <div key={`${day}-${hour}`} className={`flex-1 border-r border-slate-100 last:border-r-0 ${
                      // Highlight the current time cell roughly like the screenshot
                      i === 0 && hour >= 10 && hour <= 12 ? 'bg-[#fef3c7]/30' : 'hover:bg-slate-50 transition-colors'
                    }`}>
                      {/* Empty cells for mockup */}
                    </div>
                  ))}
                </div>
              ))}
            </div>

            {/* Right Side Info Panel */}
            <div className="w-80 bg-slate-50/50 p-6 flex flex-col">
              <h3 className="font-bold text-slate-900 text-[14px]">Monday, Aug 24 - 2am</h3>
              <p className="text-slate-500 text-[12px] mb-6">Past slot</p>
              
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
                  <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wide mb-1 flex items-center gap-1.5"><CalendarIcon size={12}/> Sent</p>
                  <p className="text-xl font-extrabold text-slate-900">0</p>
                </div>
                <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
                  <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wide mb-1">Opens</p>
                  <p className="text-xl font-extrabold text-slate-900">0</p>
                </div>
                <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
                  <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wide mb-1">Clicks</p>
                  <p className="text-xl font-extrabold text-slate-900">0</p>
                </div>
                <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
                  <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wide mb-1">Open Rate</p>
                  <p className="text-xl font-extrabold text-slate-900">0%</p>
                </div>
              </div>

              <div className="flex-1 flex flex-col items-center justify-center text-center">
                <p className="text-[13px] font-medium text-slate-500 mb-8">No emails sent at this time</p>
                
                <div className="w-full border-t border-slate-200 pt-6">
                  <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4">Scheduled for this slot</p>
                  {/* Empty state line */}
                  <div className="w-full border-b-2 border-dashed border-slate-200 my-4"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
