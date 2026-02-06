"use client";

import "./globals.css";
import { Inter } from "next/font/google";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { RoleProvider, useRole } from "@/context/RoleContext";

const inter = Inter({ subsets: ["latin"] });

function AppContent({ children }: { children: React.ReactNode }) {
  const { role, setRole } = useRole();

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar role={role} />
      <div className="flex-1 flex flex-col ml-64">
        <Header currentRole={role} setRole={setRole} />
        <main className="flex-1 overflow-y-auto mt-20 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} bg-gray-50`}>
        <RoleProvider>
          <AppContent>{children}</AppContent>
        </RoleProvider>
      </body>
    </html>
  );
}
