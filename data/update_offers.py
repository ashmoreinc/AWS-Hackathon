import json

# Read offers
with open('offers.json', 'r') as f:
    offers = json.load(f)

# Remove all "local" offerType offers
offers = [offer for offer in offers if offer.get('offerType') != 'local']

# Add "lunch" attribute to all remaining offers
for offer in offers:
    offer['lunch'] = (offer['id'] == '189f3060626368d0a716f0e795d8f2c7')

# Write back
with open('offers.json', 'w') as f:
    json.dump(offers, f, indent=2)

print(f"✅ Removed local offers. Remaining: {len(offers)}")
print(f"✅ Added 'lunch' attribute to all offers")
print(f"✅ Lunch offer: {sum(1 for o in offers if o.get('lunch'))}")
