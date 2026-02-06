"use client";

import {
  LayoutDashboard,
  Users,
  FileText,
  Bot,
  MessageSquare,
  Mail,
  FileScan,
  StickyNote,
  Activity,
  Settings,
  LogOut
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

type Role = 'Admin' | 'Employee' | 'Client';

interface SidebarProps {
  role: Role;
}

export function Sidebar({ role }: SidebarProps) {
  const pathname = usePathname();

  const allItems = [
    { name: 'Dashboard', icon: LayoutDashboard, href: '/', roles: ['Admin', 'Employee', 'Client'] },
    { name: 'Clients', icon: Users, href: '/clients', roles: ['Admin', 'Employee'] },
    { name: 'AllyTech Enquiries', icon: FileText, href: '/enquiries', roles: ['Admin', 'Employee'] },
    { name: 'Email Agent', icon: Bot, href: '/email-agent', roles: ['Admin', 'Employee'] },
    { name: 'Conversations', icon: MessageSquare, href: '/conversations', roles: ['Admin', 'Employee', 'Client'] },
    { name: 'Emails', icon: Mail, href: '/emails', roles: ['Admin', 'Employee'] },
    { name: 'Documents (OCR)', icon: FileScan, href: '/documents', roles: ['Admin', 'Employee'] },
    { name: 'Remarks', icon: StickyNote, href: '/remarks', roles: ['Admin', 'Employee'] },
    { name: 'Activity Logs', icon: Activity, href: '/logs', roles: ['Admin'] },
    { name: 'Settings', icon: Settings, href: '/settings', roles: ['Admin', 'Employee', 'Client'] },
  ];

  const filteredItems = allItems.filter(item => item.roles.includes(role));

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-screen flex flex-col fixed left-0 top-0 text-gray-800">
      <div className="p-6 border-b border-gray-100 flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold shadow-sm">
          SH
        </div>
        <span className="font-bold text-xl tracking-tight text-gray-900">SERP Hawk</span>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {filteredItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-blue-50 text-blue-600 shadow-sm"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <item.icon className={cn("w-5 h-5", isActive ? "text-blue-600" : "text-gray-400 group-hover:text-gray-600")} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-100">
        <button className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg w-full transition-colors">
          <LogOut className="w-5 h-5" />
          Logout
        </button>
      </div>
    </div>
  );
}
