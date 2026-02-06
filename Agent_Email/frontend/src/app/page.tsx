"use client";

import { useRole } from "@/context/RoleContext";
import { Users, MessageSquare, Send, FileText, ShoppingCart, Ticket, Activity } from "lucide-react";

export default function Dashboard() {
  const { role } = useRole();

  const Widget = ({ title, value, change, icon: Icon, color }: any) => (
    <div className="bg-white p-6 rounded-xl border shadow-sm">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <h3 className="text-2xl font-bold mt-2 text-gray-900">{value}</h3>
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6 text-gray-700" />
        </div>
      </div>
      <div className="mt-4 flex items-center text-sm">
        <span className={change.startsWith('+') ? "text-green-600 font-medium" : "text-red-600 font-medium"}>
          {change}
        </span>
        <span className="text-gray-400 ml-2">from last month</span>
      </div>
    </div>
  );

  const AdminWidgets = () => (
    <>
      <Widget title="Total Clients" value="1,248" change="+12%" icon={Users} color="bg-blue-100" />
      <Widget title="Active Conversations" value="86" change="+5%" icon={MessageSquare} color="bg-green-100" />
      <Widget title="Emails Sent Today" value="342" change="-2%" icon={Send} color="bg-purple-100" />
      <Widget title="Docs Processed" value="156" change="+8%" icon={FileText} color="bg-orange-100" />
    </>
  );

  const ClientWidgets = () => (
    <>
      <Widget title="Active Tickets" value="3" change="" icon={Ticket} color="bg-orange-100" />
      <Widget title="Total Orders" value="12" change="" icon={ShoppingCart} color="bg-blue-100" />
      <Widget title="Documents" value="5" change="" icon={FileText} color="bg-purple-100" />
      <Widget title="Messages" value="2" change="" icon={MessageSquare} color="bg-green-100" />
    </>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">Welcome back to SERP Hawk CRM, here is what's happening today.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {role === 'Client' ? <ClientWidgets /> : <AdminWidgets />}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border p-6 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-bold text-lg flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-blue-600" />
              Recent Conversations
            </h2>
            <button className="text-sm text-blue-600 font-medium hover:underline">View All</button>
          </div>
          
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer">
                <div className="flex justify-between mb-2">
                  <div className="font-semibold text-gray-900">Sarah Wilson <span className="text-gray-400 font-normal ml-2">to Support Team</span></div>
                  <div className="text-xs text-gray-400">10:30 AM</div>
                </div>
                <div className="font-medium text-gray-800 text-sm mb-1">Enterprise Plan Inquiry</div>
                <p className="text-sm text-gray-500 line-clamp-1">Hello, I would like to discuss upgrading our current plan to the enterprise tier...</p>
                <div className="mt-3">
                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-md">OPENED</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="font-bold text-lg mb-6 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            Real-Time Remarks
          </h2>
          <div className="relative border-l-2 border-blue-100 pl-6 space-y-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="relative">
                <div className="absolute -left-[31px] top-0 w-3 h-3 rounded-full bg-blue-500 ring-4 ring-white"></div>
                <div className="flex justify-between mb-1">
                  <span className="font-semibold text-sm">John Admin</span>
                  <span className="text-xs text-gray-400">10 mins ago</span>
                </div>
                <p className="text-sm text-gray-600">Client Acme Corp requested a demo for the new OCR feature.</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
