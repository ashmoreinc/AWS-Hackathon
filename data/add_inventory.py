import json
import random

# Read offers
with open('offers.json', 'r') as f:
    offers = json.load(f)

# Add random inventory_count to each offer
for offer in offers:
    # Random inventory between 0 and 150
    # 10% chance of 0 (out of stock)
    # 20% chance of 1-10 (low stock - high scarcity score)
    # 70% chance of 11-150 (normal stock)
    rand = random.random()
    if rand < 0.1:
        offer['inventory_count'] = 0
    elif rand < 0.3:
        offer['inventory_count'] = random.randint(1, 10)
    else:
        offer['inventory_count'] = random.randint(11, 150)

# Write back
with open('offers.json', 'w') as f:
    json.dump(offers, f, indent=2)

print(f"✅ Added inventory_count to {len(offers)} offers")
print(f"   - Out of stock: {sum(1 for o in offers if o['inventory_count'] == 0)}")
print(f"   - Low stock (1-10): {sum(1 for o in offers if 1 <= o['inventory_count'] <= 10)}")
print(f"   - Normal stock (11+): {sum(1 for o in offers if o['inventory_count'] > 10)}")
