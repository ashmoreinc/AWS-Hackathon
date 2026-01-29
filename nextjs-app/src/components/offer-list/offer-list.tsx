"use client"

import { z } from "zod";
import Image from "next/image";
import { useState } from "react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";

// Reuse your existing Zod schema and Offer type (export if needed)
export const OfferSchema = z.object({
  id: z.string(),
  name: z.string(),
  image: z.string(),
  boost: z.boolean(),
  commission: z.number().min(0).max(5),
  expiry: z.string(),
  offerType: z.string(),
  tags: z.array(z.string()),
  redemptionType: z.string(),
  final_score: z.number().optional(),
});
export type Offer = z.infer<typeof OfferSchema>;

export function timeUntilExpiry(expiryISO: string): string {
  const now = new Date();
  const expiry = new Date(expiryISO);
  const diffMs = expiry.getTime() - now.getTime();
  if (diffMs <= 0) return "Expired";

  const prefix = "Expires in ";
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMinutes < 60)
    return `${prefix} in ${diffMinutes} minute${diffMinutes === 1 ? "" : "s"}`;
  if (diffHours < 24)
    return `${prefix} in ${diffHours} hour${diffHours === 1 ? "" : "s"}`;
  return `${prefix} in ${diffDays} day${diffDays === 1 ? "" : "s"}`;
}

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

function OfferCard({
  offer,
  showDebugInfo,
  onClick,
}: {
  offer: Offer;
  showDebugInfo: boolean;
  onClick: (offer: Offer) => void;
}) {
  return (
    <Card
      onClick={() => onClick(offer)}
      className="h-full w-full cursor-pointer flex flex-col rounded-2xl border bg-background shadow-sm transition hover:shadow-md hover:ring-1 hover:ring-muted p-0"
    >
      <OfferImage src={offer.image} alt={offer.name} />
      <CardContent className="flex flex-1 flex-col gap-3 p-4">
        <div className="space-y-1">
          <h2 className="text-base font-semibold leading-tight mb-2">
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
        {showDebugInfo ? (
          <div className="space-y-1 text-sm text-muted-foreground">
            <p>Debug info</p>
            <p>Offer Final Score: {offer.final_score}</p>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function OfferDrawer({
  offer,
  open,
  onOpenChange,
}: {
  offer: Offer | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  if (!offer) return null;
  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent className="max-h-[90vh]">
        <div className="mx-auto w-full max-w-4xl p-6">
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="relative aspect-[4/3] w-full overflow-hidden rounded-xl">
              <Image
                src={offer.image}
                alt={offer.name}
                fill
                className="object-cover"
              />
            </div>

            <div className="space-y-4 text-sm">
              <DrawerHeader className="px-0">
                <DrawerTitle className="text-4xl text-start">
                  {offer.name}
                </DrawerTitle>
              </DrawerHeader>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">{offer.offerType}</Badge>
                <Badge variant="secondary">{offer.redemptionType}</Badge>
                {offer.boost && (
                  <Badge className="bg-green-500/15 text-green-700">
                    Boosted
                  </Badge>
                )}
              </div>

              <div className="space-y-1">
                <p>
                  <span className="font-medium">Commission:</span>{" "}
                  {offer.commission}%
                </p>
                <p>
                  <span className="font-medium">Expires:</span>{" "}
                  {new Date(offer.expiry).toLocaleString()}
                </p>
                <p className="text-muted-foreground">
                  {timeUntilExpiry(offer.expiry)}
                </p>
              </div>

              {offer.tags.length > 0 ? (
                <div>
                  <p className="font-medium mb-1">Tags</p>
                  <div className="flex flex-wrap gap-1">
                    {offer.tags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  );
}

export type OffersListProps = {
  offers: Offer[];
  showDebugInfo: boolean;
};

export function OffersList({ offers, showDebugInfo }: OffersListProps) {
  const [selectedOffer, setSelectedOffer] = useState<Offer | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div>
      <Carousel className="relative -mx-2">
        <CarouselContent className="p-4 items-stretch">
          {offers.map((offer) => (
            <CarouselItem
              key={offer.id}
              className="md:basis-1/2 lg:basis-1/3 flex items-stretch"
            >
              <OfferCard
                offer={offer}
                showDebugInfo={showDebugInfo}
                onClick={(offer) => {
                  setSelectedOffer(offer);
                  setDrawerOpen(true);
                }}
              />
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>

      <OfferDrawer
        offer={selectedOffer}
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
      />
    </div>
  );
}
