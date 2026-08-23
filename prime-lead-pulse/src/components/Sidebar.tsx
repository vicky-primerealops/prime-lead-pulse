'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Mail, LogOut, Activity } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Tracked Emails', href: '/dashboard/emails', icon: Mail },
];

export default function Sidebar({ userEmail, onLogout }: { userEmail: string; onLogout: () => void }) {
  const pathname = usePathname();

  return (
    <div className="w-56 min-h-screen bg-gray-900 text-white flex flex-col flex-shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-700 flex items-center gap-2">
        <Activity className="text-indigo-400" size={20} />
        <span className="font-bold text-sm">Prime Lead Pulse</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3">
        {NAV_ITEMS.map(({ label, href, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm mb-1 transition-colors ${active ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* User + Logout */}
      <div className="px-4 py-4 border-t border-gray-700">
        <p className="text-xs text-gray-400 truncate mb-2">{userEmail}</p>
        <button
          onClick={onLogout}
          className="flex items-center gap-2 text-xs text-gray-400 hover:text-white transition-colors"
        >
          <LogOut size={14} />
          Log Out
        </button>
      </div>
    </div>
  );
}
