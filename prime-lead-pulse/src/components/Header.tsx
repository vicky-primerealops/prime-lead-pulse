import { Mailbox, LogOut } from 'lucide-react';

export default function Header({ userEmail, onLogout }: { userEmail: string, onLogout: () => void }) {
  // Extract a name from the email
  const name = userEmail.split('@')[0].replace(/[^a-zA-Z]/g, ' ');
  const displayName = name.charAt(0).toUpperCase() + name.slice(1);

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 z-10 relative shadow-sm">
      <div className="flex items-center gap-2">
        <div className="bg-slate-900 text-white p-1.5 rounded-md">
          <Mailbox size={20} className="stroke-[2.5]" />
        </div>
        <span className="font-bold text-lg tracking-tight text-slate-900">Prime Lead Pulse</span>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
            {displayName.charAt(0).toUpperCase()}
          </div>
          <span className="text-sm font-medium text-slate-700">{displayName}</span>
        </div>
        <button 
          onClick={onLogout}
          className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
          title="Log Out"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
