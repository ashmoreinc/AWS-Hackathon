"use client";

import { off } from "process";
import { useState } from "react";

export default function Home() {
  const [offers, setOffers] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const onUserChange = () => {
    const service = (document.getElementById('service-select') as HTMLSelectElement).value;
    const hour = parseInt((document.getElementById('hour-input') as HTMLInputElement).value);

    setIsLoading(true);
    // Fetch offers based on user input
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/offers/recommend`,  {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        "user_id": "USER001",
        "connection_type": service, 
      }),
    })
      .then(response => response.json())
      .then(data => {
        setOffers(data?.recommended_offers || []);
        setIsLoading(false);
      });
  }

  return (
    <div>
      <main className="flex flex-col">
        <h1 className="font-bold mx-auto">AWS Hackathon Demo</h1>
        <div className="mx-auto w-full grid grid-cols-2 gap-4">
          <div className="p-4 rounded-lg shadow-md">
            <h1>Your offers</h1>
            {isLoading && <p>Loading offers...</p>}
            {offers.length === 0 && <p>No offers available. Please select your network type and hour.</p>}
            {offers.map((offer: unknown, index: number) => {
              return (
                <div key={index}>
                  <h1>{(offer as { offer_name?: string }).offer_name || "No name"}</h1>
                </div>
              )
            })}
          </div>
          <div className="flex flex-col items-center bg-gray-800 white bg-opacity-10 p-4 rounded-lg shadow-md">
            <h1>Who are you?</h1>
            <div>
              <label htmlFor="service-select">Choose a your network type:</label>
              <select id="service-select" onChange={onUserChange}>
                <option value="wifi">WiFi</option>
                <option value="mobile">Mobile Network</option>
              </select>
            </div>
            <div>
              <label htmlFor="hour-input">What hour is it?</label>
              <input className="w-24" name="Hour" id="hour-input" type="number" min="0" max="23" onChange={onUserChange}/>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
