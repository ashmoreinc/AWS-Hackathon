import { z } from "zod";
import Image from "next/image";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { Card, CardContent } from "@/components/ui/card";
import { mockOffers } from "./mock-data";
import { Badge } from "@/components/ui/badge";

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

type Offer = z.infer<typeof OfferSchema>;

function OfferImage({ src, alt }: { src: string; alt: string }) {
  return (
    <div className="relative w-full h-44 rounded-t-2xl overflow-hidden">
      <Image
        src={src}
        alt={alt}
        fill
        className="object-cover"
        sizes="(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw"
      />
    </div>
  );
}

function OfferCard({ offer }: { offer: Offer }) {
  return (
    <Card className="h-full w-full flex flex-col rounded-2xl border bg-background shadow-sm transition hover:shadow-md">
      <OfferImage src={offer.image} alt={offer.name} />

      <CardContent className="flex flex-1 flex-col gap-3 p-4">
        <div className="space-y-1">
          <h2 className="text-base font-semibold leading-tight">
            {offer.name}
          </h2>

          <div className="flex flex-wrap gap-1 text-xs">
            <Badge variant="secondary">{offer.offerType}</Badge>
            <Badge variant="secondary">{offer.redemptionType}</Badge>
            {offer.boost && (
              <Badge className="bg-green-500/15 text-green-700">Boosted</Badge>
            )}
          </div>
        </div>

        <div className="mt-auto space-y-2">
          <p className="text-xs text-muted-foreground">
            {timeUntilExpiry(offer.expiry)}
          </p>

          <div className="flex flex-wrap gap-1">
            {offer.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-muted px-2 py-0.5 text-[11px] text-muted-foreground"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function OffersPage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-semibold mb-6">Featured Offers</h1>

      <Carousel className="relative -mx-2">
        <CarouselContent className="p-4 items-stretch">
          {offers.map((offer) => (
            <CarouselItem
              key={offer.id}
              className="md:basis-1/2 lg:basis-1/3 flex items-stretch"
            >
              <OfferCard offer={offer} />
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  );
}
