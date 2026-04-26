"use client";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CloudSun, Droplets, Thermometer, Wind, AlertTriangle } from "lucide-react";

interface WeatherData {
  temperature_celsius: number;
  humidity_percent: number;
  rainfall_mm_month: number;
  season: string;
  risk_alerts: string[];
  suitable_for_sowing: boolean;
}

const SEASON_COLORS: Record<string, string> = {
  kharif: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  rabi:   "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  zaid:   "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
};

export default function WeatherWidget({ data }: { data?: WeatherData }) {
  if (!data) {
    return (
      <Card className="animate-pulse">
        <CardHeader><div className="h-5 bg-muted rounded w-32" /></CardHeader>
        <CardContent><div className="h-24 bg-muted rounded" /></CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-blue-200 dark:border-blue-800">
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <CloudSun className="h-4 w-4 text-blue-500" />
          Current Weather
        </CardTitle>
        <Badge className={SEASON_COLORS[data.season] || "bg-muted text-muted-foreground"}>
          {data.season}
        </Badge>
      </CardHeader>

      <CardContent className="space-y-3">
        <div className="grid grid-cols-3 gap-3">
          <div className="flex flex-col items-center p-3 bg-orange-50 dark:bg-orange-950 rounded-lg">
            <Thermometer className="h-4 w-4 text-orange-500 mb-1" />
            <span className="text-xl font-bold text-orange-600">{data.temperature_celsius}°</span>
            <span className="text-xs text-muted-foreground">Temp (°C)</span>
          </div>
          <div className="flex flex-col items-center p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
            <Droplets className="h-4 w-4 text-blue-500 mb-1" />
            <span className="text-xl font-bold text-blue-600">{data.humidity_percent}%</span>
            <span className="text-xs text-muted-foreground">Humidity</span>
          </div>
          <div className="flex flex-col items-center p-3 bg-cyan-50 dark:bg-cyan-950 rounded-lg">
            <Wind className="h-4 w-4 text-cyan-500 mb-1" />
            <span className="text-xl font-bold text-cyan-600">{data.rainfall_mm_month}</span>
            <span className="text-xs text-muted-foreground">Rain (mm)</span>
          </div>
        </div>

        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${
          data.suitable_for_sowing
            ? "bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300"
            : "bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300"
        }`}>
          <div className={`w-2 h-2 rounded-full ${data.suitable_for_sowing ? "bg-green-500" : "bg-red-500"}`} />
          {data.suitable_for_sowing ? "Good conditions for sowing" : "Not ideal for sowing now"}
        </div>

        {data.risk_alerts.length > 0 && (
          <div className="space-y-1">
            {data.risk_alerts.map((alert, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950 px-3 py-2 rounded-lg">
                <AlertTriangle className="h-3 w-3 mt-0.5 shrink-0" />
                {alert}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
