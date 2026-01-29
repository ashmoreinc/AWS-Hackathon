import { z } from "zod";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { Card, CardContent } from "@/components/ui/card";
import { mockOffers } from "./mock-data";

// Zod schema
const OfferSchema = z.object({
  id: z.string(),
  name: z.string(),
  image: z.string(),
  boost: z.boolean(),
  commission: z.number().min(0).max(5),
  expiry: z.string(),
  offerType: z.string(),
  tags: z.array(z.string()),
  redemptionType: z.string(),
});

export function timeUntilExpiry(expiryISO: string): string {
  const now = new Date();
  const expiry = new Date(expiryISO);

  const diffMs = expiry.getTime() - now.getTime();

  if (diffMs <= 0) {
    return "Expired";
  }

  const prefix = "Expires in ";
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMinutes < 60) {
    return `${prefix} in ${diffMinutes} minute${diffMinutes === 1 ? "" : "s"}`;
  }

  if (diffHours < 24) {
    return `${prefix} in ${diffHours} hour${diffHours === 1 ? "" : "s"}`;
  }

  return `${prefix} in ${diffDays} day${diffDays === 1 ? "" : "s"}`;
}
// Mock data
const offers = mockOffers.map((offer) => OfferSchema.parse(offer));

export default function OffersPage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-semibold mb-6">Featured Offers</h1>

      <Carousel className="relative">
        <CarouselContent className="p-4 items-stretch">
          {offers.map((offer) => (
            <CarouselItem
              key={offer.id}
              className="md:basis-1/2 lg:basis-1/3 flex items-stretch"
            >
              <Card className="rounded-2xl shadow-md overflow-hidden h-full flex flex-col w-full">
                <img
                  src={offer.image}
                  alt={offer.name}
                  className="h-40 w-full object-cover"
                />
                <CardContent className="p-4 space-y-2 flex flex-col flex-1">
                  <h2 className="text-lg font-medium">{offer.name}</h2>
                  <p className="text-sm text-muted-foreground">
                    {offer.offerType} • {offer.redemptionType}
                  </p>
                  <div className="flex items-center justify-between text-sm">
                    <span>Boost: {offer.boost}×</span>
                    <span>Commission: {offer.commission}%</span>
                  </div>
                  <div className="mt-auto space-y-2">
                    <p className="text-xs text-muted-foreground">
                      {timeUntilExpiry(offer.expiry)}
                    </p>
                    <div className="flex flex-wrap gap-1 pt-1">
                      {offer.tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-xs bg-secondary px-2 py-0.5 rounded-full"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  );
}
