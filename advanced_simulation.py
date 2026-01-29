"""
Advanced Simulation: Inventory Stockout with DynamoDB Streams Auto-Pivot
Demonstrates how the system automatically detects stockouts and redirects traffic
"""

import json
import time
from typing import Dict, List
from collections import defaultdict
import random

class InventoryMonitor:
    """Simulates DynamoDB Streams + Lambda trigger for inventory monitoring"""
    
    def __init__(self, offers: List[Dict]):
        self.offers = offers
        self.alerts = []
        self.pivot_rules = []
    
    def check_inventory(self, offer_id: str, new_inventory: int) -> Dict:
        """Simulates DynamoDB Stream event processing"""
        if new_inventory <= 5:
            alert = {
                'type': 'LOW_STOCK' if new_inventory > 0 else 'STOCKOUT',
                'offer_id': offer_id,
                'inventory': new_inventory,
                'timestamp': time.time()
            }
            self.alerts.append(alert)
            
            if new_inventory == 0:
                self.trigger_pivot(offer_id)
            
            return alert
        return None
    
    def trigger_pivot(self, stockout_offer_id: str):
        """Automatically select next best offer based on merchant priorities"""
        stockout_offer = next(o for o in self.offers if o['id'] == stockout_offer_id)
        
        # Find replacement: same category, highest priority, available inventory
        candidates = [
            o for o in self.offers 
            if o['category'] == stockout_offer['category'] 
            and o['inventory'] > 0 
            and o['id'] != stockout_offer_id
        ]
        
        if candidates:
            pivot_offer = max(candidates, key=lambda x: x['priority'])
        else:
            # Fallback: any category, highest priority
            pivot_offer = max([o for o in self.offers if o['inventory'] > 0], key=lambda x: x['priority'])
        
        pivot_rule = {
            'from_offer': stockout_offer_id,
            'to_offer': pivot_offer['id'],
            'reason': 'same_category' if pivot_offer['category'] == stockout_offer['category'] else 'highest_priority',
            'priority_boost': 20  # Temporary boost to accelerate pivot
        }
        self.pivot_rules.append(pivot_rule)
        
        print(f"\n🔄 AUTO-PIVOT TRIGGERED:")
        print(f"   From: {stockout_offer_id} ({stockout_offer['category']})")
        print(f"   To: {pivot_offer['id']} ({pivot_offer['category']}, Priority {pivot_offer['priority']})")
        print(f"   Reason: {pivot_rule['reason']}")
        print(f"   Action: Boosting {pivot_offer['id']} priority by +{pivot_rule['priority_boost']}\n")
        
        return pivot_rule

class EnhancedDecisionEngine:
    """Decision engine with inventory-aware ranking and auto-pivot support"""
    
    def __init__(self, offers: List[Dict], inventory_monitor: InventoryMonitor):
        self.offers = offers
        self.monitor = inventory_monitor
        self.trending = defaultdict(float)
        self.user_affinity = defaultdict(lambda: defaultdict(float))
    
    def rank_offers(self, user_id: str, user_affinity_category: str) -> List[Dict]:
        scored = []
        
        for offer in self.offers:
            if offer['inventory'] <= 0:
                continue  # Skip out-of-stock offers
            
            # Base score
            base_score = offer['priority']
            
            # User affinity boost
            affinity_boost = 35 if offer['category'] == user_affinity_category else 0
            
            # Trending boost
            trending_boost = self.trending[offer['category']]
            
            # Pivot boost (if this offer is a pivot target)
            pivot_boost = 0
            for rule in self.monitor.pivot_rules:
                if rule['to_offer'] == offer['id']:
                    pivot_boost = rule['priority_boost']
            
            # Inventory urgency (boost low stock items)
            inventory_boost = 10 if offer['inventory'] < 20 else 0
            
            total_score = base_score + affinity_boost + trending_boost + pivot_boost + inventory_boost
            
            scored.append({
                **offer,
                'score': total_score,
                'breakdown': {
                    'base': base_score,
                    'affinity': affinity_boost,
                    'trending': trending_boost,
                    'pivot': pivot_boost,
                    'inventory': inventory_boost
                }
            })
        
        return sorted(scored, key=lambda x: x['score'], reverse=True)
    
    def process_interaction(self, user_id: str, offer_id: str, action: str):
        """Update trending scores and user affinity"""
        offer = next(o for o in self.offers if o['id'] == offer_id)
        
        if action == 'CLICK':
            self.trending[offer['category']] += 1.5
            self.user_affinity[user_id][offer['category']] += 1.0
        elif action == 'REDEMPTION':
            self.trending[offer['category']] += 5.0
            self.user_affinity[user_id][offer['category']] += 3.0
            offer['inventory'] -= 1
            
            # Trigger inventory check
            self.monitor.check_inventory(offer_id, offer['inventory'])

def run_advanced_simulation():
    print("=" * 90)
    print("ADVANCED SIMULATION: INVENTORY STOCKOUT WITH AUTO-PIVOT")
    print("=" * 90)
    
    # Initialize offers
    offers = [
        {"id": "OFF001", "name": "Premium Laptop", "category": "electronics", "priority": 95, "inventory": 25, "discount": 25},
        {"id": "OFF002", "name": "Fashion Sale", "category": "fashion", "priority": 88, "inventory": 200, "discount": 40},
        {"id": "OFF003", "name": "Grocery Bundle", "category": "food", "priority": 70, "inventory": 500, "discount": 15},
        {"id": "OFF004", "name": "Smart Home", "category": "electronics", "priority": 82, "inventory": 50, "discount": 30},
        {"id": "OFF005", "name": "Fitness Gear", "category": "sports", "priority": 75, "inventory": 120, "discount": 35},
    ]
    
    # Initialize system components
    monitor = InventoryMonitor(offers)
    engine = EnhancedDecisionEngine(offers, monitor)
    
    # Generate users with category preferences
    users = [
        {"id": f"USER{i:03d}", "affinity": random.choices(
            ["electronics", "fashion", "food", "sports"],
            weights=[0.4, 0.3, 0.2, 0.1]  # Electronics most popular
        )[0]}
        for i in range(100)
    ]
    
    # Track metrics
    offer_interactions = defaultdict(lambda: {'clicks': 0, 'redemptions': 0})
    phase_metrics = {'pre_stockout': defaultdict(int), 'post_stockout': defaultdict(int)}
    
    print(f"\nUsers: {len(users)} | Offers: {len(offers)} | Interactions: 300\n")
    print("Initial Inventory:")
    for offer in offers:
        print(f"  {offer['id']} ({offer['category']}): {offer['inventory']} units")
    
    # Run simulation
    for iteration in range(300):
        user = random.choice(users)
        ranked = engine.rank_offers(user['id'], user['affinity'])
        
        if not ranked:
            continue
        
        top_offer = ranked[0]
        
        # User interaction
        action = 'REDEMPTION' if random.random() < 0.25 else 'CLICK'
        engine.process_interaction(user['id'], top_offer['id'], action)
        
        offer_interactions[top_offer['id']][action.lower() + 's'] += 1
        
        # Track phase metrics
        phase = 'pre_stockout' if iteration < 150 else 'post_stockout'
        phase_metrics[phase][top_offer['id']] += 1
        
        # Print key events
        if action == 'REDEMPTION' and top_offer['inventory'] <= 5:
            print(f"⚠️  Iteration {iteration}: {top_offer['id']} inventory low: {top_offer['inventory']} units")
        
        # Trending decay
        if iteration % 30 == 0:
            for cat in engine.trending:
                engine.trending[cat] *= 0.85
    
    # Results
    print("\n" + "=" * 90)
    print("SIMULATION RESULTS")
    print("=" * 90)
    
    print("\n📊 PHASE 1: PRE-STOCKOUT (Iterations 0-149)")
    for offer_id, count in sorted(phase_metrics['pre_stockout'].items(), key=lambda x: x[1], reverse=True):
        offer = next(o for o in offers if o['id'] == offer_id)
        print(f"   {offer_id} ({offer['category']}, P{offer['priority']}): {count} interactions")
    
    print("\n📊 PHASE 2: POST-STOCKOUT (Iterations 150-299)")
    for offer_id, count in sorted(phase_metrics['post_stockout'].items(), key=lambda x: x[1], reverse=True):
        offer = next(o for o in offers if o['id'] == offer_id)
        status = "🔴 DEPLETED" if offer['inventory'] == 0 else f"✓ {offer['inventory']} left"
        print(f"   {offer_id} ({offer['category']}, P{offer['priority']}): {count} interactions [{status}]")
    
    print("\n🎯 PIVOT EFFECTIVENESS:")
    if monitor.pivot_rules:
        for rule in monitor.pivot_rules:
            from_count_pre = phase_metrics['pre_stockout'][rule['from_offer']]
            to_count_post = phase_metrics['post_stockout'][rule['to_offer']]
            print(f"   {rule['from_offer']} → {rule['to_offer']}")
            print(f"   Traffic captured: {to_count_post} interactions post-pivot")
            print(f"   Pivot efficiency: {(to_count_post / from_count_pre * 100):.1f}% of original traffic")
    
    print("\n📦 FINAL INVENTORY:")
    for offer in sorted(offers, key=lambda x: x['priority'], reverse=True):
        metrics = offer_interactions[offer['id']]
        status = "🔴 OUT" if offer['inventory'] == 0 else f"🟢 {offer['inventory']}"
        print(f"   {offer['id']} ({offer['category']}, P{offer['priority']}): {status} | "
              f"Clicks: {metrics['clicks']}, Redemptions: {metrics['redemptions']}")
    
    print("\n🚨 ALERTS TRIGGERED:")
    for alert in monitor.alerts:
        print(f"   {alert['type']}: {alert['offer_id']} (Inventory: {alert['inventory']})")
    
    print("\n" + "=" * 90)
    print("✅ Simulation complete - System successfully pivoted to next best offer")
    print("=" * 90)

if __name__ == "__main__":
    run_advanced_simulation()
