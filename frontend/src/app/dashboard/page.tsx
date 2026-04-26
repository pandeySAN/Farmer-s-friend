"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/layout/Header";
import WeatherWidget from "@/components/dashboard/WeatherWidget";
import CropCards from "@/components/dashboard/CropCards";
import MarketChart from "@/components/dashboard/MarketChart";
import ChatInterface from "@/components/dashboard/ChatInterface";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { authAPI } from "@/lib/api";
import { formatCurrency, getFarmerName } from "@/lib/utils";
import { Sprout, IndianRupee, Tractor, MapPin } from "lucide-react";

export default function DashboardPage() {
  const router  = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("farmer_token");
    if (!token) { router.replace("/login"); return; }

    authAPI.getMe()
      .then(({ data }) => setProfile(data))
      .catch(() => router.replace("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-green-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground text-sm">Loading your farm data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <Header title="Dashboard" />

      <div className="flex-1 p-6 overflow-y-auto">
        {/* Welcome banner */}
        <div className="mb-6 p-5 rounded-xl bg-gradient-to-r from-green-600 to-emerald-500 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">
                नमस्ते, {profile?.name || getFarmerName()} 🌾
              </h2>
              <p className="text-green-100 text-sm mt-1 flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {[profile?.district, profile?.state].filter(Boolean).join(", ") || "Location not set"}
              </p>
            </div>
            <Sprout className="h-12 w-12 text-green-200 opacity-60" />
          </div>

          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="bg-white/20 rounded-lg p-3">
              <p className="text-xs text-green-100">Farm Size</p>
              <p className="text-lg font-bold">
                {profile?.land_area_acres ? `${profile.land_area_acres} acres` : "—"}
              </p>
            </div>
            <div className="bg-white/20 rounded-lg p-3">
              <p className="text-xs text-green-100">Soil Type</p>
              <p className="text-lg font-bold capitalize">{profile?.soil_type || "—"}</p>
            </div>
            <div className="bg-white/20 rounded-lg p-3">
              <p className="text-xs text-green-100">Irrigation</p>
              <p className="text-lg font-bold capitalize">{profile?.irrigation || "—"}</p>
            </div>
          </div>
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column — widgets */}
          <div className="lg:col-span-1 space-y-6">
            <WeatherWidget data={undefined} />
            <CropCards data={undefined} />
            <MarketChart data={undefined} />
          </div>

          {/* Right column — chat */}
          <div className="lg:col-span-2">
            <Card className="h-[700px] flex flex-col overflow-hidden border-green-200 dark:border-green-800">
              <CardHeader className="pb-3 border-b">
                <CardTitle className="text-base font-semibold flex items-center gap-2">
                  <Sprout className="h-4 w-4 text-green-500" />
                  Ask FarmerAI
                  <span className="text-xs font-normal text-muted-foreground ml-1">
                    — powered by Claude
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 p-0 overflow-hidden">
                <ChatInterface />
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
