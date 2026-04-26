"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem,
  SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
  Card, CardContent, CardDescription,
  CardFooter, CardHeader, CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { authAPI } from "@/lib/api";
import toast from "react-hot-toast";
import { Loader2, Sprout } from "lucide-react";

const INDIAN_STATES = [
  "Andhra Pradesh","Assam","Bihar","Chhattisgarh","Gujarat",
  "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala",
  "Madhya Pradesh","Maharashtra","Odisha","Punjab","Rajasthan",
  "Tamil Nadu","Telangana","Uttar Pradesh","Uttarakhand","West Bengal",
];

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    name: "", email: "", password: "", phone: "",
    state: "", district: "", language: "hi",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await authAPI.register(form);
      localStorage.setItem("farmer_token", data.access_token);
      localStorage.setItem("farmer_name",  data.name);
      localStorage.setItem("farmer_id",    data.farmer_id);
      toast.success("Account created! Welcome to FarmerAI 🌾");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-950 dark:to-emerald-950 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="text-center space-y-2">
          <div className="flex justify-center">
            <div className="bg-green-100 dark:bg-green-900 p-3 rounded-full">
              <Sprout className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <CardTitle className="text-2xl font-semibold">Create your farm account</CardTitle>
          <CardDescription>
            Step {step} of 2 —{" "}
            <Badge variant="outline" className="ml-1">
              {step === 1 ? "Basic details" : "Location"}
            </Badge>
          </CardDescription>
        </CardHeader>

        <form onSubmit={step === 1 ? (e) => { e.preventDefault(); setStep(2); } : handleSubmit}>
          <CardContent className="space-y-4">
            {step === 1 && (
              <>
                <div className="space-y-2">
                  <Label>Full name</Label>
                  <Input placeholder="Ramesh Kumar" value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input type="email" placeholder="you@example.com" value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })} required />
                </div>
                <div className="space-y-2">
                  <Label>Password</Label>
                  <Input type="password" placeholder="Min. 8 characters" value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })} required />
                </div>
                <div className="space-y-2">
                  <Label>
                    Mobile number{" "}
                    <span className="text-muted-foreground text-xs">(optional)</span>
                  </Label>
                  <Input placeholder="+91 98765 43210" value={form.phone}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                </div>
              </>
            )}

            {step === 2 && (
              <>
                <div className="space-y-2">
                  <Label>State</Label>
                  <Select onValueChange={(v) => setForm({ ...form, state: v })}>
                    <SelectTrigger><SelectValue placeholder="Select your state" /></SelectTrigger>
                    <SelectContent>
                      {INDIAN_STATES.map((s) => (
                        <SelectItem key={s} value={s}>{s}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>District</Label>
                  <Input placeholder="e.g. Lucknow" value={form.district}
                    onChange={(e) => setForm({ ...form, district: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label>Preferred language</Label>
                  <Select defaultValue="hi" onValueChange={(v) => setForm({ ...form, language: v })}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hi">हिन्दी (Hindi)</SelectItem>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="pa">ਪੰਜਾਬੀ (Punjabi)</SelectItem>
                      <SelectItem value="mr">मराठी (Marathi)</SelectItem>
                      <SelectItem value="ta">தமிழ் (Tamil)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}
          </CardContent>

          <CardFooter className="flex flex-col gap-3">
            <div className="flex w-full gap-2">
              {step === 2 && (
                <Button type="button" variant="outline" className="flex-1"
                  onClick={() => setStep(1)}>
                  Back
                </Button>
              )}
              <Button
                type="submit"
                className="flex-1 bg-green-600 hover:bg-green-700"
                disabled={loading}
              >
                {loading ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating...</>
                ) : step === 1 ? "Next →" : "Create account"}
              </Button>
            </div>
            <p className="text-sm text-muted-foreground text-center">
              Already have an account?{" "}
              <Link href="/login" className="text-green-600 hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
