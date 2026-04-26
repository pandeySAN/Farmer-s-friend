"use client";
import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { chatAPI } from "@/lib/api";
import { History, MessageSquare, ChevronDown, ChevronUp } from "lucide-react";
import { format } from "date-fns";

interface HistoryItem {
  id: string;
  query: string;
  response: string;
  date: string;
}

export default function HistoryPage() {
  const [items,    setItems]    = useState<HistoryItem[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    chatAPI.getHistory()
      .then(({ data }) => setItems(data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col h-screen">
      <Header title="Chat History" />
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-3xl space-y-3">
          {loading && (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-20 bg-muted rounded-xl animate-pulse" />
              ))}
            </div>
          )}

          {!loading && items.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-muted-foreground gap-3">
              <MessageSquare className="h-10 w-10 opacity-40" />
              <p className="text-sm">No conversations yet. Ask FarmerAI your first question!</p>
            </div>
          )}

          {items.map((item) => (
            <Card key={item.id} className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => setExpanded(expanded === item.id ? null : item.id)}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2">
                    <MessageSquare className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                    <p className="text-sm font-medium line-clamp-2">{item.query}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-xs text-muted-foreground">
                      {format(new Date(item.date), "dd MMM, h:mm a")}
                    </span>
                    {expanded === item.id
                      ? <ChevronUp className="h-4 w-4 text-muted-foreground" />
                      : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
                  </div>
                </div>
              </CardHeader>

              {expanded === item.id && (
                <CardContent>
                  <div className="bg-muted rounded-lg p-4 text-sm whitespace-pre-wrap leading-relaxed">
                    {item.response}
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
