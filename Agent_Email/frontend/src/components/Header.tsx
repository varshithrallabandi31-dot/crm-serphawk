"use client";

import { Search, Bell, ChevronDown } from 'lucide-react';
import { useState } from 'react';

type Role = 'Admin' | 'Employee' | 'Client';

interface HeaderProps {
  currentRole: Role;
  setRole: (role: Role) => void;
}

export function Header({ currentRole, setRole }: HeaderProps) {
  const [isOpen, setIsOpen] = useState(false);

  const getProfile = () => {
    switch (currentRole) {
      case 'Admin': return { name: 'John Admin', role: 'Admin', img: 'https://ui-avatars.com/api/?name=John+Admin&background=random' };
      case 'Employee': return { name: 'Sarah Employee', role: 'Employee', img: 'https://ui-avatars.com/api/?name=Sarah+Emp&background=random' };
      case 'Client': return { name: 'Mike Client', role: 'Client', img: 'https://ui-avatars.com/api/?name=Mike+Client&background=random' };
    }
  };

  const profile = getProfile();

  return (
    <header className="h-20 bg-white border-b flex items-center justify-between px-8 fixed top-0 right-0 left-64 z-10">
      <div className="relative w-96">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input 
          type="text" 
          placeholder="Search clients, emails, documents..." 
          className="w-full pl-10 pr-4 py-2 bg-gray-50 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100 text-sm"
        />
      </div>

      <div className="flex items-center gap-6">
        {/* Role Switcher for Demo */}
        <div className="relative">
          <button 
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-2 text-sm text-gray-600 border px-3 py-1.5 rounded-md hover:bg-gray-50"
          >
            View as {currentRole}
            <ChevronDown className="w-4 h-4" />
          </button>
          
          {isOpen && (
            <div className="absolute right-0 mt-2 w-40 bg-white border rounded-lg shadow-lg py-1 z-20">
              {['Admin', 'Employee', 'Client'].map((role) => (
                <button
                  key={role}
                  onClick={() => { setRole(role as Role); setIsOpen(false); }}
                  className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50"
                >
                  {role}
                </button>
              ))}
            </div>
          )}
        </div>

        <button className="relative text-gray-500 hover:text-gray-700">
          <Bell className="w-5 h-5" />
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white"></span>
        </button>

        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <div className="text-sm font-semibold text-gray-900">{profile.name}</div>
            <div className="text-xs text-gray-500">{profile.role}</div>
          </div>
          <img 
            src={profile.img} 
            alt="Profile" 
            className="w-10 h-10 rounded-full border border-gray-200"
          />
        </div>
      </div>
    </header>
  );
}
