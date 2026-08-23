'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Mail, Calendar, LayoutTemplate, Settings } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const NAV_ITEMS = [
  { label: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Tracked Emails', href: '/dashboard/emails', icon: Mail },
  { label: 'Send Calendar', href: '/dashboard/calendar', icon: Calendar },
  { label: 'Email Templates', href: '/dashboard/templates', icon: LayoutTemplate },
  { label: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 bg-[#f8f9fa] border-r border-slate-200 flex flex-col flex-shrink-0 pt-6 px-4">
      <nav className="flex-1 space-y-1">
        {NAV_ITEMS.map(({ label, href, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={label}
              href={href}
              className={twMerge(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all duration-200",
                active 
                  ? "bg-[#111827] text-white shadow-md" 
                  : "text-slate-600 hover:bg-slate-200/50 hover:text-slate-900"
              )}
            >
              <Icon size={16} className={clsx(active ? "text-white" : "text-slate-500")} />
              {label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
