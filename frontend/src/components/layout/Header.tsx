"use client";
import { useEffect, useState } from "react";
import { Bell, Sun, Moon, Menu } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { getFarmerName } from "@/lib/utils";

export default function Header({ title }: { title?: string }) {
  const { theme, setTheme } = useTheme();
  const [name, setName] = useState("");

  useEffect(() => {
    setName(getFarmerName());
  }, []);

  return (
    <header className="h-16 border-b border-border bg-white dark:bg-zinc-900 flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-semibold text-foreground">
          {title || "Dashboard"}
        </h1>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost" size="icon"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="text-muted-foreground"
        >
          {theme === "dark"
            ? <Sun className="h-4 w-4" />
            : <Moon className="h-4 w-4" />}
        </Button>

        <Button variant="ghost" size="icon" className="text-muted-foreground relative">
          <Bell className="h-4 w-4" />
          <span className="absolute top-2 right-2 w-1.5 h-1.5 bg-green-500 rounded-full" />
        </Button>

        <div className="flex items-center gap-2 ml-2">
          <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center text-green-700 dark:text-green-300 font-semibold text-sm">
            {name.charAt(0).toUpperCase() || "F"}
          </div>
          <span className="text-sm font-medium hidden sm:block">{name}</span>
        </div>
      </div>
    </header>
  );
}
