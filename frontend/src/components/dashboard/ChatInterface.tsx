"use client";
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Loader2, Sprout, User, AlertTriangle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";
import { formatCurrency } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  status?: string;
  data?: any;
}

const QUICK_QUESTIONS = [
  "इस मौसम में क्या उगाऊं?",
  "मेरी मिट्टी के लिए कौन सी फसल सबसे अच्छी है?",
  "What crop gives best profit right now?",
  "गेहूं या सरसों — कौन सा ज़्यादा फायदेमंद है?",
];

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id:   "welcome",
      role: "assistant",
      text: "नमस्ते! 🌾 मैं आपका FarmerAI सहायक हूं। आप मुझसे फसल, मौसम, बाज़ार भाव या खेती से जुड़ा कोई भी सवाल पूछ सकते हैं।\n\nHello! I'm your FarmerAI assistant. Ask me anything about crops, weather, market prices, or farming.",
    },
  ]);
  const [input,   setInput]   = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (query?: string) => {
    const text = query || input.trim();
    if (!text || loading) return;
    setInput("");
    setLoading(true);

    const userMsg: Message    = { id: Date.now().toString(), role: "user", text };
    const assistantId = Date.now().toString() + "_ai";
    const assistantMsg: Message = {
      id: assistantId, role: "assistant", text: "", status: "🌦️ Fetching weather data...",
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);

    try {
      const token = localStorage.getItem("farmer_token");
      const resp  = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/ask/stream`,
        {
          method:  "POST",
          headers: {
            "Content-Type":  "application/json",
            "Authorization": `Bearer ${token}`,
          },
          body: JSON.stringify({ query: text }),
        }
      );

      if (!resp.ok) throw new Error("Request failed");

      const reader  = resp.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const lines = decoder.decode(value).split("\n");
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const event = JSON.parse(line.slice(6));

            if (event.type === "status") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, status: event.message } : m
                )
              );
            } else if (event.type === "token") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, text: m.text + event.text, status: undefined }
                    : m
                )
              );
            } else if (event.type === "done") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, data: event.state, status: undefined } : m
                )
              );
            }
          } catch {}
        }
      }
    } catch {
      toast.error("Could not reach the server. Please try again.");
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, text: "Sorry, something went wrong. Please try again.", status: undefined }
            : m
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-1">
        <div className="space-y-4 p-4">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
              >
                {/* Avatar */}
                <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  msg.role === "assistant"
                    ? "bg-green-100 dark:bg-green-900"
                    : "bg-blue-100 dark:bg-blue-900"
                }`}>
                  {msg.role === "assistant"
                    ? <Sprout className="h-4 w-4 text-green-600" />
                    : <User   className="h-4 w-4 text-blue-600"  />}
                </div>

                {/* Bubble + data cards */}
                <div className={`max-w-[80%] space-y-2 flex flex-col ${
                  msg.role === "user" ? "items-end" : "items-start"
                }`}>
                  <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-green-600 text-white rounded-tr-none"
                      : "bg-muted rounded-tl-none"
                  }`}>
                    {msg.status && (
                      <div className="flex items-center gap-2 text-xs opacity-70 mb-2">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        {msg.status}
                      </div>
                    )}
                    {msg.text || (msg.status ? "" : "...")}
                  </div>

                  {/* Structured data cards */}
                  {msg.data && (
                    <div className="grid grid-cols-2 gap-2 w-full">
                      {msg.data.crops?.recommended_crops?.slice(0, 2).map((c: any, i: number) => (
                        <Card key={i} className="border-green-200 dark:border-green-800">
                          <CardContent className="p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-semibold text-green-700 dark:text-green-400">
                                {c.name}
                              </span>
                              <Badge variant="outline" className="text-xs">
                                {Math.round(c.confidence * 100)}%
                              </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              ~{c.expected_yield_kg?.toLocaleString()} kg/acre
                            </p>
                          </CardContent>
                        </Card>
                      ))}

                      {msg.data.resources && (
                        <Card className="col-span-2 border-amber-200 dark:border-amber-800">
                          <CardContent className="p-3 flex justify-between">
                            <div className="text-center">
                              <p className="text-xs text-muted-foreground">Est. Cost</p>
                              <p className="text-sm font-semibold text-red-600">
                                {formatCurrency(msg.data.resources.estimated_cost_inr)}
                              </p>
                            </div>
                            <div className="text-center">
                              <p className="text-xs text-muted-foreground">Est. Profit</p>
                              <p className="text-sm font-semibold text-green-600">
                                {formatCurrency(msg.data.resources.expected_profit_inr)}
                              </p>
                            </div>
                            <div className="text-center">
                              <p className="text-xs text-muted-foreground">Season</p>
                              <p className="text-sm font-semibold capitalize">
                                {msg.data.weather?.season}
                              </p>
                            </div>
                          </CardContent>
                        </Card>
                      )}

                      {msg.data.weather?.risk_alerts?.length > 0 && (
                        <Card className="col-span-2 border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-950">
                          <CardContent className="p-3 space-y-1">
                            {msg.data.weather.risk_alerts.slice(0, 2).map((alert: string, i: number) => (
                              <div key={i} className="flex items-start gap-2 text-xs text-amber-700 dark:text-amber-300">
                                <AlertTriangle className="h-3 w-3 mt-0.5 shrink-0" />
                                {alert}
                              </div>
                            ))}
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Quick questions */}
      {messages.length <= 1 && (
        <div className="px-4 pb-3 flex flex-wrap gap-2">
          {QUICK_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              className="text-xs bg-green-50 dark:bg-green-950 hover:bg-green-100 dark:hover:bg-green-900 text-green-700 dark:text-green-300 rounded-full px-3 py-1.5 border border-green-200 dark:border-green-800 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input bar */}
      <div className="p-4 border-t flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
          placeholder="अपना सवाल लिखें / Type your question..."
          disabled={loading}
          className="flex-1"
        />
        <Button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="bg-green-600 hover:bg-green-700 shrink-0"
        >
          {loading
            ? <Loader2 className="h-4 w-4 animate-spin" />
            : <Send className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  );
}
