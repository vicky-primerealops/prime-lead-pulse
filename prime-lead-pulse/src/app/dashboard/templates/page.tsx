'use client';

import { useDashboardData } from '@/hooks/useDashboardData';
import DashboardLayout from '@/components/DashboardLayout';
import { MailPlus, LayoutTemplate } from 'lucide-react';

export default function TemplatesPage() {
  const { user, loading, logout } = useDashboardData();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#f8f9fa]">
        <div className="text-slate-500 font-medium">Loading Templates...</div>
      </div>
    );
  }

  return (
    <DashboardLayout userEmail={user?.email || ''} onLogout={logout}>
      <div className="p-8 max-w-7xl mx-auto space-y-6">
        
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Email Templates</h1>
            <p className="text-slate-500 text-[13px] mt-1 font-medium">Create templates with subject and body, then apply them instantly in Gmail while composing.</p>
          </div>
          <button className="flex items-center gap-2 bg-slate-900 text-white px-4 py-2.5 rounded-lg text-[13px] font-bold shadow-sm hover:bg-slate-800 transition-colors">
            <MailPlus size={16} /> New Template
          </button>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/50">
                <th className="text-left px-6 py-3.5 font-bold text-slate-500 text-[11px] uppercase tracking-wider w-1/4">Template</th>
                <th className="text-left px-6 py-3.5 font-bold text-slate-500 text-[11px] uppercase tracking-wider w-1/2">Content Preview</th>
                <th className="text-left px-6 py-3.5 font-bold text-slate-500 text-[11px] uppercase tracking-wider">Created</th>
                <th className="text-left px-6 py-3.5 font-bold text-slate-500 text-[11px] uppercase tracking-wider">Updated</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan={4} className="py-24 text-center">
                  <div className="flex flex-col items-center justify-center text-slate-400">
                    <div className="bg-slate-50 p-4 rounded-full mb-4">
                      <LayoutTemplate size={32} className="text-slate-300" />
                    </div>
                    <h3 className="text-[15px] font-bold text-slate-900 mb-1">No email templates yet</h3>
                    <p className="text-[13px] text-slate-500 mb-5">Create your first email template to use in Gmail.</p>
                    <button className="flex items-center gap-2 bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-[13px] font-bold shadow-sm hover:bg-slate-50 transition-colors">
                      <MailPlus size={16} /> New Template
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div className="px-6 py-3 border-t border-slate-100 flex items-center justify-between text-[12px] text-slate-500 bg-slate-50/50">
            <div className="flex items-center gap-4">
              <span>No entries to show</span>
              <div className="flex items-center gap-2">
                <span>Rows per page</span>
                <select className="border border-slate-200 rounded px-2 py-1 bg-white focus:outline-none">
                  <option>20</option>
                  <option>50</option>
                  <option>100</option>
                </select>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button disabled className="px-2 py-1 rounded opacity-40">«</button>
              <button disabled className="px-2 py-1 rounded opacity-40">‹</button>
              <span className="px-3">Page 0 of 0</span>
              <button disabled className="px-2 py-1 rounded opacity-40">›</button>
              <button disabled className="px-2 py-1 rounded opacity-40">»</button>
            </div>
          </div>
        </div>

      </div>
    </DashboardLayout>
  );
}
