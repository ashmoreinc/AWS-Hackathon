"use client";

import { useEffect, useState } from "react";
import { Offer, OffersList } from "@/components/offer-list/offer-list";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { mockOffers } from "./mock-data";

export default function Home() {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [useMockData, setUseMockData] = useState(false);
  const [showDebugInfo, setShowDebugInfo] = useState(false);

  const fetchOffers = (service: string) => {
    setIsLoading(true);
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/offers/recommend`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: "USER001",
        connection_type: service,
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
      const service = serviceSelect?.value || "wifi";
      fetchOffers(service);
    }
  }, [useMockData]);

  const onUserChange = () => {
    if (useMockData) return; // Skip fetch if using mock data
    const service = (
      document.getElementById("service-select") as HTMLSelectElement
    ).value;
    fetchOffers(service);
  };

  return (
    <main className="flex flex-col max-w-7xl mx-auto p-6 space-y-8">
      <h1 className="text-5xl font-bold">AWS Hackathon Demo - Team Rotom</h1>

      {/* User Input Section */}
      <section className="p-6 rounded-lg shadow-md bg-gray-50 w-2/5">
        <h2 className="text-xl font-semibold mb-4">User configuration</h2>

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
        <div className="flex flex-col space-y-4">
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
