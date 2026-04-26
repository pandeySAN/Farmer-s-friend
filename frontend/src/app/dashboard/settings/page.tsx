"use client";
import { useEffect, useState } from "react";
import Header from "@/components/layout/Header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem,
  SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { authAPI } from "@/lib/api";
import toast from "react-hot-toast";
import { Loader2, Save, Settings } from "lucide-react";

const INDIAN_STATES = [
  "Andhra Pradesh","Assam","Bihar","Chhattisgarh","Gujarat",
  "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala",
  "Madhya Pradesh","Maharashtra","Odisha","Punjab","Rajasthan",
  "Tamil Nadu","Telangana","Uttar Pradesh","Uttarakhand","West Bengal",
];

export default function SettingsPage() {
  const [loading,  setLoading]  = useState(false);
  const [fetching, setFetching] = useState(true);
  const [form, setForm] = useState({
    name: "", district: "", state: "",
    land_area_acres: "", soil_type: "", irrigation: "", language: "hi",
    latitude: "", longitude: "",
  });

  useEffect(() => {
    authAPI.getMe()
      .then(({ data }) => setForm({
        name:            data.name           || "",
        district:        data.district       || "",
        state:           data.state          || "",
        land_area_acres: data.land_area_acres?.toString() || "",
        soil_type:       data.soil_type      || "",
        irrigation:      data.irrigation     || "",
        language:        data.language       || "hi",
        latitude:        data.latitude?.toString()  || "",
        longitude:       data.longitude?.toString() || "",
      }))
      .finally(() => setFetching(false));
  }, []);

  const handleSave = async () => {
    setLoading(true);
    try {
      await authAPI.updateMe({
        name:            form.name,
        district:        form.district,
        state:           form.state,
        land_area_acres: form.land_area_acres ? parseFloat(form.land_area_acres) : undefined,
        soil_type:       form.soil_type   || undefined,
        irrigation:      form.irrigation  || undefined,
        language:        form.language,
        latitude:        form.latitude  ? parseFloat(form.latitude)  : undefined,
        longitude:       form.longitude ? parseFloat(form.longitude) : undefined,
      });
      localStorage.setItem("farmer_name", form.name);
      toast.success("Profile updated successfully!");
    } catch {
      toast.error("Failed to save. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return (
      <div className="flex flex-col h-screen">
        <Header title="Settings" />
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-green-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      <Header title="Settings" />
      <div className="flex-1 p-6 overflow-y-auto max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-green-500" />
              Farm Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            {/* Personal */}
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 space-y-2">
                <Label>Full Name</Label>
                <Input value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>

              <div className="space-y-2">
                <Label>State</Label>
                <Select value={form.state} onValueChange={(v) => setForm({ ...form, state: v })}>
                  <SelectTrigger><SelectValue placeholder="Select state" /></SelectTrigger>
                  <SelectContent>
                    {INDIAN_STATES.map((s) => (
                      <SelectItem key={s} value={s}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>District</Label>
                <Input value={form.district}
                  onChange={(e) => setForm({ ...form, district: e.target.value })}
                  placeholder="e.g. Lucknow" />
              </div>
            </div>

            {/* Farm details */}
            <div className="grid grid-cols-2 gap-4 pt-2 border-t">
              <div className="space-y-2">
                <Label>Land Area (acres)</Label>
                <Input type="number" value={form.land_area_acres}
                  onChange={(e) => setForm({ ...form, land_area_acres: e.target.value })}
                  placeholder="e.g. 3.5" />
              </div>

              <div className="space-y-2">
                <Label>Soil Type</Label>
                <Select value={form.soil_type} onValueChange={(v) => setForm({ ...form, soil_type: v })}>
                  <SelectTrigger><SelectValue placeholder="Select soil" /></SelectTrigger>
                  <SelectContent>
                    {["alluvial","black","red","laterite","sandy","clay"].map((s) => (
                      <SelectItem key={s} value={s} className="capitalize">{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Irrigation Type</Label>
                <Select value={form.irrigation} onValueChange={(v) => setForm({ ...form, irrigation: v })}>
                  <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
                  <SelectContent>
                    {["drip","flood","sprinkler","none"].map((s) => (
                      <SelectItem key={s} value={s} className="capitalize">{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Language</Label>
                <Select value={form.language} onValueChange={(v) => setForm({ ...form, language: v })}>
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
            </div>

            {/* GPS */}
            <div className="grid grid-cols-2 gap-4 pt-2 border-t">
              <div className="space-y-2">
                <Label>Latitude <span className="text-xs text-muted-foreground">(optional)</span></Label>
                <Input type="number" step="0.0001" value={form.latitude}
                  onChange={(e) => setForm({ ...form, latitude: e.target.value })}
                  placeholder="e.g. 26.85" />
              </div>
              <div className="space-y-2">
                <Label>Longitude <span className="text-xs text-muted-foreground">(optional)</span></Label>
                <Input type="number" step="0.0001" value={form.longitude}
                  onChange={(e) => setForm({ ...form, longitude: e.target.value })}
                  placeholder="e.g. 80.91" />
              </div>
              <p className="col-span-2 text-xs text-muted-foreground">
                GPS coordinates improve weather accuracy. Find yours at maps.google.com → right-click your location.
              </p>
            </div>

            <Button
              onClick={handleSave}
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700"
            >
              {loading
                ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</>
                : <><Save className="mr-2 h-4 w-4" /> Save Profile</>}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
