"use client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sprout, TrendingUp, Clock } from "lucide-react";

interface Crop {
  name: string;
  confidence: number;
  expected_yield_kg: number;
  reason: string;
}

interface CropData {
  recommended_crops: Crop[];
  avoid_crops: string[];
  best_sowing_window: string;
}

const CONFIDENCE_COLOR = (c: number) => {
  if (c >= 0.85) return "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300";
  if (c >= 0.65) return "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300";
  return "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300";
};

export default function CropCards({ data }: { data?: CropData }) {
  if (!data) {
    return (
      <Card className="animate-pulse">
        <CardHeader><div className="h-5 bg-muted rounded w-40" /></CardHeader>
        <CardContent><div className="h-32 bg-muted rounded" /></CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-green-200 dark:border-green-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Sprout className="h-4 w-4 text-green-500" />
          Crop Recommendations
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {data.recommended_crops.map((crop, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg border ${
              i === 0
                ? "border-green-300 dark:border-green-700 bg-green-50 dark:bg-green-950"
                : "border-border bg-muted/30"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                {i === 0 && (
                  <span className="text-xs font-semibold text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900 px-2 py-0.5 rounded-full">
                    Top Pick
                  </span>
                )}
                <span className="font-semibold text-sm">{crop.name}</span>
              </div>
              <Badge className={CONFIDENCE_COLOR(crop.confidence)}>
                {Math.round(crop.confidence * 100)}% match
              </Badge>
            </div>

            <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
              <span className="flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                ~{crop.expected_yield_kg.toLocaleString()} kg/acre
              </span>
            </div>

            <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
              {crop.reason}
            </p>
          </div>
        ))}

        <div className="flex items-center gap-2 text-xs text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-950 px-3 py-2 rounded-lg">
          <Clock className="h-3 w-3 shrink-0" />
          {data.best_sowing_window}
        </div>

        {data.avoid_crops.length > 0 && (
          <div className="text-xs text-muted-foreground">
            <span className="font-medium text-red-600 dark:text-red-400">Avoid: </span>
            {data.avoid_crops.join(", ")}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
