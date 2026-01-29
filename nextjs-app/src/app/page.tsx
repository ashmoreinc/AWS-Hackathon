"use client";

export default function Home() {

  return (
    <div>
      <main className="flex flex-col">
        <h1 className="font-bold mx-auto">AWS Hackathon Demo</h1>
        <div className="mx-auto w-full grid grid-cols-2 gap-4">
          <div className="p-4 rounded-lg shadow-md">
            <h1>Your offers</h1>
          </div>
          <div className="flex flex-col items-center bg-gray-800 white bg-opacity-10 p-4 rounded-lg shadow-md">
            <h1>Who are you?</h1>
            <div>
              <label htmlFor="service-select">Choose a your network type:</label>
              <select id="service-select">
                <option value="wifi">WiFi</option>
                <option value="mobile-data">Mobile Network</option>
              </select>
            </div>
            <div>
              <label htmlFor="hour-input">What hour is it?</label>
              <input className="w-24" name="Hour" id="hour-input" type="number" min="0" max="23" />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
