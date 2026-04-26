"use client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus, IndianRupee } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface PriceForecast {
  crop: string;
  current_price_inr: number;
  predicted_price_inr: number;
  trend: string;
  best_selling_month: string;
  advice: string;
  source: string;
}

interface MarketData {
  price_forecasts: PriceForecast[];
  best_selling_month: string;
  market_risk: string;
}

const RISK_COLORS: Record<string, string> = {
  low:    "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  high:   "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

const TrendIcon = ({ trend }: { trend: string }) => {
  if (trend === "rising")  return <TrendingUp   className="h-3 w-3 text-green-500" />;
  if (trend === "falling") return <TrendingDown className="h-3 w-3 text-red-500"   />;
  return <Minus className="h-3 w-3 text-muted-foreground" />;
};

const BAR_COLORS = ["#16a34a", "#0284c7", "#d97706"];

export default function MarketChart({ data }: { data?: MarketData }) {
  if (!data) {
    return (
      <Card className="animate-pulse">
        <CardHeader><div className="h-5 bg-muted rounded w-36" /></CardHeader>
        <CardContent><div className="h-40 bg-muted rounded" /></CardContent>
      </Card>
    );
  }

  const chartData = data.price_forecasts.map((p) => ({
    name: p.crop.split(" ")[0],
    current:   p.current_price_inr,
    predicted: p.predicted_price_inr,
  }));

  return (
    <Card className="border-amber-200 dark:border-amber-800">
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <IndianRupee className="h-4 w-4 text-amber-500" />
          Market Prices (₹/quintal)
        </CardTitle>
        <Badge className={RISK_COLORS[data.market_risk] || ""}>
          {data.market_risk} risk
        </Badge>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Chart */}
        <ResponsiveContainer width="100%" height={120}>
          <BarChart data={chartData} barSize={16} barGap={4}>
            <XAxis dataKey="name" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis hide />
            <Tooltip
              formatter={(val: number) => [`₹${val.toLocaleString()}`, ""]}
              contentStyle={{ fontSize: 12, borderRadius: 8 }}
            />
            <Bar dataKey="current" name="Current" radius={[4,4,0,0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} opacity={0.6} />
              ))}
            </Bar>
            <Bar dataKey="predicted" name="Predicted" radius={[4,4,0,0]}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        {/* Price rows */}
        <div className="space-y-2">
          {data.price_forecasts.map((p, i) => (
            <div key={i} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <TrendIcon trend={p.trend} />
                <span className="font-medium">{p.crop}</span>
                <span className="text-xs text-muted-foreground">Best: {p.best_selling_month}</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-muted-foreground">₹{p.current_price_inr.toLocaleString()}</span>
                <span>→</span>
                <span className="font-semibold text-green-600">₹{p.predicted_price_inr.toLocaleString()}</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
