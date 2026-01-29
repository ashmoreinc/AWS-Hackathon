"use client";

import { useEffect, useState } from "react";
import { Offer, OffersList } from "@/components/offer-list/offer-list";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { mockOffers } from "./mock-data";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogClose,
} from "@/components/ui/dialog";

function UserIdPills({
  userIds,
  selectedUserId,
  onChange,
}: {
  userIds: string[];
  selectedUserId: string | null;
  onChange: (userId: string) => void;
}) {
  return (
    <div className="mb-4">
      <label className="mb-2 block font-medium">Select User ID</label>
      <div className="flex flex-wrap gap-2">
        {userIds.map((userId) => {
          const isSelected = userId === selectedUserId;
          return (
            <Badge
              key={userId}
              onClick={() => onChange(userId)}
              className={`cursor-pointer select-none ${
                isSelected
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              {userId}
            </Badge>
          );
        })}
      </div>
    </div>
  );
}

export default function Home() {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [useMockData, setUseMockData] = useState(false);
  const [showDebugInfo, setShowDebugInfo] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(
    "USER001",
  );
  const mockUserIds = ["USER001", "USER002", "USER003"];

  const fetchOffers = (service: string, time?: string) => {
    setIsLoading(true);

    console.log(time ? { current_time: time + ":00" } : {});
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/offers/recommend`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: selectedUserId,
        connection_type: service,
        ...(time ? { current_time: time + ":00" } : {}),
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        setOffers(data?.offers || []);
        setIsLoading(false);
      })
      .catch(() => {
        setOffers([]);
        setIsLoading(false);
      });
  };

  // inside Home component, add this effect:
  useEffect(() => {
    if (useMockData) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setOffers(mockOffers);
      setIsLoading(false);
    } else {
      // refetch using the current selected network
      const serviceSelect = document.getElementById(
        "service-select",
      ) as HTMLSelectElement | null;
      const timeSelect = document.getElementById(
        "hour-input",
      ) as HTMLInputElement | null;
      const time = timeSelect?.value || undefined;
      const service = serviceSelect?.value || "wifi";
      fetchOffers(service, time);
    }
  }, [useMockData, selectedUserId]);

  const onUserChange = () => {
    if (useMockData) return; // Skip fetch if using mock data
    const service = (
      document.getElementById("service-select") as HTMLSelectElement
    ).value;

    const timeSelect = document.getElementById(
      "hour-input",
    ) as HTMLInputElement | null;

    fetchOffers(service, timeSelect?.value || undefined);
  };

  return (
    <main className="flex flex-col max-w-7xl mx-auto p-6 space-y-8 mb-16">
      <h1 className="text-5xl font-bold">AWS Hackathon Demo - Team Rotom</h1>

      <section className="absolute top-6 right-6 hidden md:block">
        <Dialog>
          <DialogTrigger asChild>
            <img
              src="/VisitMeImage.png"
              className="h-48 cursor-pointer rounded-md shadow-md"
              alt="Visit Me"
            />
          </DialogTrigger>

          <DialogContent className="p-8">
            <img
              src="/VisitMeImage.png"
              className="h-full cursor-pointer rounded-md shadow-md p-8"
              alt="Visit Me"
            />
          </DialogContent>
        </Dialog>
      </section>

      {/* User Input Section */}
      <section className="p-6 rounded-lg shadow-md bg-gray-50">
        <h2 className="text-xl font-semibold mb-4">User configuration</h2>

        <div className="flex flex-col md:flex-row md:gap-5">
          <div className="flex space-x-2 mb-4">
            <Switch
              id="use-mock-toggle"
              checked={useMockData}
              onCheckedChange={setUseMockData}
            />
            <Label
              htmlFor="use-mock-toggle"
              className="cursor-pointer select-none"
            >
              Use Mock Data
            </Label>
          </div>
          <div className="flex space-x-2 mb-4">
            <Switch
              id="show-debug-toggle"
              checked={showDebugInfo}
              onCheckedChange={setShowDebugInfo}
            />
            <Label
              htmlFor="show-debug-toggle"
              className="cursor-pointer select-none"
            >
              Show Debug Info
            </Label>
          </div>
        </div>
        <div className="flex flex-col space-y-4">
          <UserIdPills
            userIds={mockUserIds}
            selectedUserId={selectedUserId}
            onChange={setSelectedUserId}
          />
        </div>
        <div className="flex flex-col md:flex-row gap-5">
          <div>
            <Label htmlFor="service-select" className="mb-1 block font-medium">
              Choose your network type:
            </Label>
            <select
              id="service-select"
              className="w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              onChange={onUserChange}
              defaultValue="wifi"
            >
              <option value="wifi">WiFi</option>
              <option value="mobile">Mobile Network</option>
            </select>
          </div>

          <div>
            <Label htmlFor="hour-input" className="mb-1 block font-medium">
              What hour is it? (0–23)
            </Label>
            <input
              id="hour-input"
              type="number"
              min={0}
              max={23}
              className="w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              onChange={onUserChange}
              placeholder="Enter hour"
            />
          </div>
        </div>
      </section>

      <div className="gap-8 mx-2">
        {/* Offers Section */}
        <section className="">
          <h2 className="text-xl font-semibold mb-4">Your Offers</h2>

          {isLoading && (
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <Spinner size="lg" />
              <p className="text-muted-foreground">Loading offers...</p>
            </div>
          )}

          {!isLoading && offers.length === 0 && (
            <p className="text-center text-muted-foreground">
              No offers available. Please select your network type.
            </p>
          )}

          {!isLoading && offers.length > 0 && (
            <OffersList offers={offers} showDebugInfo={showDebugInfo} />
          )}
        </section>
      </div>
    </main>
  );
}
