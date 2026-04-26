"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sprout, LayoutDashboard, MessageSquare,
  History, Settings, LogOut, TrendingUp, CloudSun,
} from "lucide-react";
import { cn, logout, getFarmerName } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const navItems = [
  { label: "Dashboard",  href: "/dashboard",         icon: LayoutDashboard },
  { label: "Ask AI",     href: "/dashboard/chat",    icon: MessageSquare   },
  { label: "Market",     href: "/dashboard/market",  icon: TrendingUp      },
  { label: "Weather",    href: "/dashboard/weather", icon: CloudSun        },
  { label: "History",    href: "/dashboard/history", icon: History         },
  { label: "Settings",   href: "/dashboard/settings",icon: Settings        },
];

export default function Sidebar() {
  const pathname = usePathname();
  const name = getFarmerName();

  return (
    <aside className="hidden md:flex flex-col w-64 bg-white dark:bg-zinc-900 border-r border-border h-screen sticky top-0">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-border">
        <div className="bg-green-100 dark:bg-green-900 p-2 rounded-lg">
          <Sprout className="h-5 w-5 text-green-600 dark:text-green-400" />
        </div>
        <span className="font-bold text-lg text-green-700 dark:text-green-400">FarmerAI</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ label, href, icon: Icon }) => (
          <Link key={href} href={href}>
            <div className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
              pathname === href
                ? "bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-400"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}>
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </div>
          </Link>
        ))}
      </nav>

      {/* User + logout */}
      <div className="px-4 py-4 border-t border-border">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center text-green-700 dark:text-green-300 font-semibold text-sm">
            {name.charAt(0).toUpperCase()}
          </div>
          <span className="text-sm font-medium truncate">{name}</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start text-muted-foreground hover:text-destructive"
          onClick={logout}
        >
          <LogOut className="h-4 w-4 mr-2" />
          Sign out
        </Button>
      </div>
    </aside>
  );
}
