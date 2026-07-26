"use client";

import * as React from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { CommandPalette } from "@/components/layout/CommandPalette";

export default function PlatformLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [cmdOpen, setCmdOpen] = React.useState(false);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCmdOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-black text-[#F8F9FA]">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Container */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar onOpenCommandPalette={() => setCmdOpen(true)} />
        
        {/* Dynamic Page Content Viewport */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-8 bg-black scanline-grid relative">
          {children}
        </main>
      </div>

      {/* Global Command Palette Modal */}
      <CommandPalette open={cmdOpen} onOpenChange={setCmdOpen} />
    </div>
  );
}
