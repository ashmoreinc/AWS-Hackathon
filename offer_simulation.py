import random
import time
from collections import defaultdict
from typing import Dict, List

class OfferManagementSimulator:
    def __init__(self):
        self.offers = [
            {"id": "OFF001", "category": "electronics", "priority": 95, "inventory": 50, "discount": 25},
            {"id": "OFF002", "category": "fashion", "priority": 88, "inventory": 200, "discount": 40},
            {"id": "OFF003", "category": "food", "priority": 70, "inventory": 500, "discount": 15},
            {"id": "OFF004", "category": "electronics", "priority": 82, "inventory": 30, "discount": 30},
            {"id": "OFF005", "category": "sports", "priority": 75, "inventory": 120, "discount": 35},
        ]
        self.trending_scores = defaultdict(float)
        self.offer_clicks = defaultdict(int)
        self.users = [{"id": f"USER{i:03d}", "affinity": random.choice(["electronics", "fashion", "food", "sports"])} for i in range(100)]
        self.stockout_triggered = False
        
    def calculate_offer_score(self, offer: Dict, user: Dict, trending_boost: float = 0) -> float:
        base_score = offer['priority']
        affinity_boost = 30 if offer['category'] == user['affinity'] else 0
        inventory_penalty = -50 if offer['inventory'] <= 0 else 0
        return base_score + affinity_boost + trending_boost + inventory_penalty
    
    def rank_offers(self, user: Dict) -> List[Dict]:
        scored = []
        for offer in self.offers:
            trending_boost = self.trending_scores[offer['category']]
            score = self.calculate_offer_score(offer, user, trending_boost)
            scored.append({**offer, 'score': score})
        return sorted(scored, key=lambda x: x['score'], reverse=True)
    
    def user_interaction(self, user: Dict, iteration: int):
        ranked = self.rank_offers(user)
        top_offer = ranked[0]
        
        if top_offer['inventory'] > 0:
            self.offer_clicks[top_offer['id']] += 1
            self.trending_scores[top_offer['category']] += 2.0
            
            # 30% chance of redemption
            if random.random() < 0.3:
                for offer in self.offers:
                    if offer['id'] == top_offer['id']:
                        offer['inventory'] -= 1
                        return top_offer['id'], 'REDEEMED', top_offer['inventory']
            
            return top_offer['id'], 'CLICKED', top_offer['inventory']
        else:
            return top_offer['id'], 'STOCKOUT_SKIPPED', 0
    
    def trigger_stockout(self):
        most_popular = max(self.offer_clicks.items(), key=lambda x: x[1])[0]
        for offer in self.offers:
            if offer['id'] == most_popular:
                print(f"\n🚨 STOCKOUT EVENT: {offer['id']} ({offer['category']}) - Inventory set to 0")
                print(f"   Previous inventory: {offer['inventory']}, Clicks: {self.offer_clicks[most_popular]}")
                offer['inventory'] = 0
                self.stockout_triggered = True
                return most_popular
    
    def run_simulation(self):
        print("=" * 80)
        print("REAL-TIME OFFER MANAGEMENT SIMULATION")
        print("=" * 80)
        print(f"Users: {len(self.users)} | Offers: {len(self.offers)} | Interactions: 200\n")
        
        interactions_log = []
        
        for i in range(200):
            user = random.choice(self.users)
            offer_id, action, inventory = self.user_interaction(user, i)
            interactions_log.append((i, user['id'], offer_id, action, inventory))
            
            # Trigger stockout at iteration 100
            if i == 100 and not self.stockout_triggered:
                stockout_offer = self.trigger_stockout()
                print(f"\n📊 Trending scores before stockout: {dict(self.trending_scores)}")
                print(f"📊 Offer clicks: {dict(self.offer_clicks)}\n")
            
            # Decay trending scores
            if i % 20 == 0:
                for cat in self.trending_scores:
                    self.trending_scores[cat] *= 0.9
        
        # Analysis
        print("\n" + "=" * 80)
        print("SIMULATION RESULTS")
        print("=" * 80)
        
        # Pre-stockout analysis (iterations 0-100)
        pre_stockout = [log for log in interactions_log if log[0] < 100]
        pre_offer_dist = defaultdict(int)
        for log in pre_stockout:
            pre_offer_dist[log[2]] += 1
        
        print("\n📈 PRE-STOCKOUT (Iterations 0-100):")
        for offer_id, count in sorted(pre_offer_dist.items(), key=lambda x: x[1], reverse=True):
            offer = next(o for o in self.offers if o['id'] == offer_id)
            print(f"   {offer_id} ({offer['category']}, Priority {offer['priority']}): {count} interactions")
        
        # Post-stockout analysis (iterations 101-200)
        post_stockout = [log for log in interactions_log if log[0] >= 101]
        post_offer_dist = defaultdict(int)
        for log in post_stockout:
            post_offer_dist[log[2]] += 1
        
        print("\n📉 POST-STOCKOUT (Iterations 101-200):")
        for offer_id, count in sorted(post_offer_dist.items(), key=lambda x: x[1], reverse=True):
            offer = next(o for o in self.offers if o['id'] == offer_id)
            status = "⚠️ OUT OF STOCK" if offer['inventory'] == 0 else f"✓ {offer['inventory']} left"
            print(f"   {offer_id} ({offer['category']}, Priority {offer['priority']}): {count} interactions [{status}]")
        
        # Pivot analysis
        print("\n🔄 AUTOMATIC PIVOT ANALYSIS:")
        stockout_offer_id = next(o['id'] for o in self.offers if o['inventory'] == 0)
        pre_count = pre_offer_dist[stockout_offer_id]
        post_count = post_offer_dist.get(stockout_offer_id, 0)
        
        print(f"   Stockout Offer: {stockout_offer_id}")
        print(f"   Pre-stockout interactions: {pre_count}")
        print(f"   Post-stockout interactions: {post_count}")
        print(f"   Traffic redirected: {pre_count - post_count} interactions")
        
        # Find pivot winner
        pivot_candidates = {k: v for k, v in post_offer_dist.items() if k != stockout_offer_id}
        if pivot_candidates:
            pivot_winner = max(pivot_candidates.items(), key=lambda x: x[1])
            pivot_offer = next(o for o in self.offers if o['id'] == pivot_winner[0])
            print(f"\n✅ PIVOT WINNER: {pivot_winner[0]} ({pivot_offer['category']}, Priority {pivot_offer['priority']})")
            print(f"   Captured {pivot_winner[1]} interactions post-stockout")
            print(f"   Reason: {'Same category affinity' if pivot_offer['category'] == next(o for o in self.offers if o['id'] == stockout_offer_id)['category'] else 'Highest merchant priority'}")
        
        # Final inventory status
        print("\n📦 FINAL INVENTORY STATUS:")
        for offer in sorted(self.offers, key=lambda x: x['priority'], reverse=True):
            status = "🔴 DEPLETED" if offer['inventory'] == 0 else f"🟢 {offer['inventory']} units"
            print(f"   {offer['id']} ({offer['category']}, Priority {offer['priority']}): {status}")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    sim = OfferManagementSimulator()
    sim.run_simulation()
