"use client";
import Header from "@/components/layout/Header";
import ChatInterface from "@/components/dashboard/ChatInterface";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sprout } from "lucide-react";

export default function ChatPage() {
  return (
    <div className="flex flex-col h-screen">
      <Header title="Ask FarmerAI" />
      <div className="flex-1 p-6 overflow-hidden">
        <Card className="h-full flex flex-col overflow-hidden">
          <CardHeader className="pb-3 border-b">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Sprout className="h-4 w-4 text-green-500" />
              AI Farm Advisor
              <span className="text-xs font-normal text-muted-foreground ml-1">
                — powered by Claude (Anthropic)
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 p-0 overflow-hidden">
            <ChatInterface />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
