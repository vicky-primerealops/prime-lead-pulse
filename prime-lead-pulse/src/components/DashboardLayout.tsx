import { ReactNode } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';

export default function DashboardLayout({ children, userEmail, onLogout }: { children: ReactNode, userEmail: string, onLogout: () => void }) {
  return (
    <div className="flex flex-col h-screen bg-[#f8f9fa] font-sans text-slate-900">
      <Header userEmail={userEmail} onLogout={onLogout} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
