from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime

class User:
    def __init__(self, db):
        self.collection = db["users"]

    def create_user(self, name, email, password, phone, age, role, verified=False):
        """Create a new user record in the database"""
        user_data = {
            "name": name,
            "email": email,
            "password": password,  # Note: Password should be hashed before storing
            "phone": phone,
            "age": int(age),
            "role": role,
            "verified": verified,
            "created_at": datetime.utcnow()
        }
        return self.collection.insert_one(user_data).inserted_id

    def find_by_email(self, email):
        """Find a user by their email address"""
        return self.collection.find_one({"email": email})

    def find_by_id(self, user_id):
        """Find a user by their ID"""
        return self.collection.find_one({"_id": ObjectId(user_id)})
    
    def verify_user(self, email):
        """Mark a user as verified"""
        return self.collection.update_one(
            {"email": email},
            {"$set": {"verified": True}}
        )
    
    def update_password(self, email, hashed_password):
        """Update a user's password"""
        return self.collection.update_one(
            {"email": email},
            {"$set": {"password": hashed_password}}
        )

class Campaign:
    def __init__(self, db):
        self.collection = db["campaigns"]

    def create_campaign(self, title, description, funding_goal, deadline, ngo_id, category="General"):
        """Create a new campaign by an NGO"""
        campaign_data = {
            "title": title,
            "description": description,
            "funding_goal": float(funding_goal),
            "current_funding": 0,
            "deadline": deadline,
            "ngo_id": ObjectId(ngo_id),
            "category": category,
            "status": "pending_approval",  # Initial status requires admin approval
            "donations": [],               # List to track donations
            "created_at": datetime.utcnow()
        }
        return self.collection.insert_one(campaign_data).inserted_id

    def find_all_approved_campaigns(self):
        """Find all campaigns with approved status"""
        return list(self.collection.find({"status": "approved"}))
    
    def find_active_campaigns(self):
        """Find all approved campaigns that haven't reached their funding goal"""
        return list(self.collection.find({
            "status": "approved",
            "$expr": {"$lt": ["$current_funding", "$funding_goal"]}
        }).sort("deadline", 1))

    def find_by_id(self, campaign_id):
        """Find a campaign by its ID"""
        return self.collection.find_one({"_id": ObjectId(campaign_id)})
    
    def find_by_ngo(self, ngo_id):
        """Find all campaigns created by a specific NGO"""
        return list(self.collection.find({"ngo_id": ObjectId(ngo_id)}))

    def approve_campaign(self, campaign_id):
        """Approve a campaign (admin function)"""
        return self.collection.update_one(
            {"_id": ObjectId(campaign_id)},
            {"$set": {"status": "approved"}}
        )
    
    def reject_campaign(self, campaign_id):
        """Reject a campaign (admin function)"""
        return self.collection.update_one(
            {"_id": ObjectId(campaign_id)},
            {"$set": {"status": "rejected"}}
        )

    def update_campaign_status(self, campaign_id):
        """Update campaign status based on funding goal achievement"""
        campaign = self.find_by_id(campaign_id)
        if campaign and campaign["current_funding"] >= campaign["funding_goal"]:
            return self.collection.update_one(
                {"_id": ObjectId(campaign_id)},
                {"$set": {"status": "funded"}}
            )
        return None

class Donor:
    def __init__(self, db):
        self.collection = db["campaigns"]  # Donations are stored within campaigns

    def donate_to_campaign(self, campaign_id, donor_id, amount, transaction_id=None):
        """Record a donation to a campaign"""
        campaign = self.collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            return False
        
        # Calculate new funding amount
        new_funding = campaign.get("current_funding", 0) + float(amount)
        
        # Create donation record
        donation = {
            "donor_id": ObjectId(donor_id),
            "amount": float(amount),
            "date": datetime.utcnow(),
            "transaction_id": transaction_id
        }
        
        # Update campaign with new donation and funding amount
        update_result = self.collection.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$set": {"current_funding": new_funding},
                "$push": {"donations": donation}
            }
        )
        
        if update_result.modified_count > 0:
            # Check if funding goal has been reached and update status if needed
            if new_funding >= campaign["funding_goal"]:
                self.collection.update_one(
                    {"_id": ObjectId(campaign_id)},
                    {"$set": {"status": "funded"}}
                )
            return True
        
        return False
    
    def get_donor_campaigns(self, donor_id):
        """Get all campaigns a donor has contributed to"""
        return list(self.collection.find({"donations.donor_id": ObjectId(donor_id)}))
    
    def get_total_donations(self, donor_id):
        """Calculate total amount donated by a donor"""
        campaigns = self.get_donor_campaigns(donor_id)
        total = 0
        
        for campaign in campaigns:
            for donation in campaign.get("donations", []):
                if str(donation["donor_id"]) == str(donor_id):
                    total += donation["amount"]
        
        return total

class CampaignAnalytics:
    def __init__(self, db):
        self.collection = db["campaigns"]
        self.users = db["users"]

    def get_campaign_metrics(self, campaign_id):
        """Get metrics for a specific campaign"""
        campaign = self.collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            return None
            
        donations = campaign.get("donations", [])
        total_raised = sum(donation["amount"] for donation in donations)
        donor_count = len(set(str(donation["donor_id"]) for donation in donations))
        
        # Calculate deadline if it exists
        days_remaining = 0
        if "deadline" in campaign:
            if isinstance(campaign["deadline"], str):
                deadline = datetime.strptime(campaign["deadline"], "%Y-%m-%d")
            else:
                deadline = campaign["deadline"]
            days_remaining = (deadline - datetime.utcnow()).days
        
        metrics = {
            "total_raised": total_raised,
            "goal_progress": (total_raised / campaign["funding_goal"]) * 100 if campaign["funding_goal"] > 0 else 0,
            "donor_count": donor_count,
            "days_remaining": days_remaining
        }
        return metrics

    def get_donation_timeline(self, campaign_id):
        """Get donation timeline for a campaign"""
        campaign = self.collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            return []
            
        donations = campaign.get("donations", [])
        
        # Group donations by day
        timeline = {}
        for donation in donations:
            date_str = donation["date"].strftime("%Y-%m-%d")
            if date_str not in timeline:
                timeline[date_str] = 0
            timeline[date_str] += donation["amount"]
            
        # Convert to sorted list
        result = [{"date": date, "amount": amount} for date, amount in timeline.items()]
        result.sort(key=lambda x: x["date"])
        
        return result

    def get_donor_demographics(self, campaign_id):
        """Get demographics of donors for a campaign"""
        campaign = self.collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            return []
            
        donor_ids = set(str(donation["donor_id"]) for donation in campaign.get("donations", []))
        
        # Get age groups
        age_groups = {}
        for donor_id in donor_ids:
            user = self.users.find_one({"_id": ObjectId(donor_id)})
            if user and "age" in user:
                age_group = (user["age"] // 10) * 10  # Group by decade
                age_group_str = f"{age_group}-{age_group+9}"
                if age_group_str not in age_groups:
                    age_groups[age_group_str] = 0
                age_groups[age_group_str] += 1
                
        # Convert to sorted list
        result = [{"age_group": age_group, "count": count} for age_group, count in age_groups.items()]
        result.sort(key=lambda x: int(x["age_group"].split("-")[0]))
        
        return result

    def get_donation_distribution(self, campaign_id):
        """Get distribution of donation amounts for a campaign"""
        campaign = self.collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            return []
            
        donations = campaign.get("donations", [])
        
        # Define donation ranges
        ranges = [
            {"min": 0, "max": 50, "label": "$0-$50"},
            {"min": 50, "max": 100, "label": "$50-$100"},
            {"min": 100, "max": 250, "label": "$100-$250"},
            {"min": 250, "max": 500, "label": "$250-$500"},
            {"min": 500, "max": 1000, "label": "$500-$1000"},
            {"min": 1000, "max": float('inf'), "label": "$1000+"}
        ]
        
        # Count donations in each range
        distribution = {r["label"]: {"count": 0, "total": 0} for r in ranges}
        for donation in donations:
            amount = donation["amount"]
            for r in ranges:
                if r["min"] <= amount < r["max"] or (r["max"] == float('inf') and amount >= r["min"]):
                    distribution[r["label"]]["count"] += 1
                    distribution[r["label"]]["total"] += amount
                    break
                    
        # Convert to list
        result = [{"range": label, "count": data["count"], "total": data["total"]} 
                  for label, data in distribution.items()]
        
        return result
