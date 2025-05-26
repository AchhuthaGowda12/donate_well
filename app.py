# from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
# from flask_pymongo import PyMongo
# from werkzeug.security import generate_password_hash, check_password_hash
# from itsdangerous import URLSafeTimedSerializer, SignatureExpired
# from bson.objectid import ObjectId
# import os
# import datetime
# import stripe
# import smtplib
# import random
# import string
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from datetime import datetime, timedelta
# from dotenv import load_dotenv



# import base64



# # Load environment variables
# load_dotenv()

# stripe.api_key = os.environ.get("stripe_key")

# app = Flask(__name__)
# app.secret_key = os.environ.get('SECRET_KEY', 'mysecretkey')

# # MongoDB Configuration
# app.config["MONGO_URI"] = os.getenv("MONGO_URI")
# mongo = PyMongo(app)


# # Email configuration
# smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
# smtp_port = int(os.environ.get('SMTP_PORT', '587'))
# smtp_username = os.environ.get('SMTP_USERNAME')
# smtp_password = os.environ.get('SMTP_PASSWORD')

# # URL safe serializer for generating tokens
# serializer = URLSafeTimedSerializer(app.secret_key)


# if mongo.db is None:
#     print("MongoDB connection not established!")
# else:
#     print("MongoDB connection established!")


# # Email sending functions
# def send_email(to_email, subject, body):
#     """Generic function to send emails"""
#     if not all([smtp_username, smtp_password]):
#         print("Error: SMTP credentials not properly configured")
#         return False

#     msg = MIMEMultipart()
#     msg['From'] = smtp_username
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'html'))

#     try:
#         server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
#         server.ehlo()
#         server.starttls()
#         server.ehlo()
#         server.login(smtp_username, smtp_password)
#         server.send_message(msg)
#         server.quit()
#         return True
#     except Exception as e:
#         print(f"Error sending email: {str(e)}")
#         return False


# def send_verification_email(email, name):
#     """Send email verification token to user"""
#     # Generate token
#     token = serializer.dumps(email, salt='email-verification')
    
#     # Build verification URL
#     verify_url = url_for('verify_email', token=token, _external=True)
    
#     # Email content
#     subject = "Please Verify Your Email"
#     body = f"""
#     <html>
#     <body>
#         <h2>Welcome to our donation platform, {name}!</h2>
#         <p>Thank you for registering. Please click the link below to verify your email address:</p>
#         <p><a href="{verify_url}">Verify Email</a></p>
#         <p>This link will expire in 24 hours.</p>
#         <p>If you did not create an account, please ignore this email.</p>
#     </body>
#     </html>
#     """
    
#     return send_email(email, subject, body)


# def send_welcome_email(email, name):
#     """Send welcome email after successful verification"""
#     subject = "Welcome to Our Donation Platform!"
#     body = f"""
#     <html>
#     <body>
#         <h2>Welcome aboard, {name}!</h2>
#         <p>Your email has been successfully verified.</p>
#         <p>You can now log in and start using our platform to connect with NGOs or make donations.</p>
#         <p>If you have any questions, feel free to contact our support team.</p>
#     </body>
#     </html>
#     """
    
#     return send_email(email, subject, body)


# def send_password_reset_email(email):
#     """Send password reset token to user"""
#     # Generate OTP
#     otp = ''.join(random.choices(string.digits, k=6))
    
#     # Store OTP in database with expiry
#     expires_at = datetime.utcnow() + timedelta(minutes=30)
#     mongo.db.password_reset_tokens.insert_one({
#         "email": email,
#         "otp": otp,
#         "expires_at": expires_at,
#         "used": False
#     })
    
#     # Email content
#     subject = "Password Reset Request"
#     body = f"""
#     <html>
#     <body>
#         <h2>Password Reset</h2>
#         <p>You requested a password reset. Here is your one-time passcode:</p>
#         <h3>{otp}</h3>
#         <p>This code will expire in 30 minutes.</p>
#         <p>If you did not request this, please ignore this email.</p>
#     </body>
#     </html>
#     """
    
#     return send_email(email, subject, body)


# @app.route("/")
# def homepage():
#     name = session.get("name", None)
#     return render_template("homepage.html", name=name)


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         name = request.form.get("name")
#         email = request.form.get("email")
#         phone = request.form.get("phone")
#         password = request.form.get("password")
#         confirm_password = request.form.get("confirmPassword")
#         age = request.form.get("age")
#         role = request.form.get("role")
        
#         if not all([name, email, phone, password, confirm_password, age, role]):
#             flash("Please fill in all fields.", "error")
#             return redirect(url_for("register"))

#         if password != confirm_password:
#             flash("Passwords do not match.", "error")
#             return redirect(url_for("register"))

#         if mongo.db.users.find_one({"email": email}):
#             flash("Email already registered. Please login.", "error")
#             return redirect(url_for("login"))
        
#         hashed_password = generate_password_hash(password)
        
#         # Insert user with verified status set to False
#         user_id = mongo.db.users.insert_one({
#             "name": name,
#             "email": email,
#             "password": hashed_password,
#             "phone": phone,
#             "age": int(age),
#             "role": role,
#             "verified": False,
#             "created_at": datetime.utcnow()
#         }).inserted_id
        
#         # Send verification email
#         if send_verification_email(email, name):
#             flash("Registration successful! Please check your email to verify your account.", "success")
#         else:
#             flash("Registration successful but we couldn't send verification email. Please contact support.", "warning")
        
#         return redirect(url_for("login"))

#     return render_template("register.html")


# @app.route("/verify-email/<token>")
# def verify_email(token):
#     try:
#         # Verify token with 24-hour expiry
#         email = serializer.loads(token, salt='email-verification', max_age=86400)
        
#         # Update user verification status
#         result = mongo.db.users.update_one(
#             {"email": email, "verified": False},
#             {"$set": {"verified": True}}
#         )
        
#         if result.modified_count > 0:
#             # Get user info for welcome email
#             user = mongo.db.users.find_one({"email": email})
#             if user:
#                 send_welcome_email(email, user["name"])
            
#             flash("Email verification successful! You can now log in.", "success")
#         else:
#             flash("Email already verified or not found.", "info")
        
#         return redirect(url_for("login"))
        
#     except SignatureExpired:
#         flash("The verification link has expired. Please request a new one.", "error")
#         return redirect(url_for("resend_verification"))
#     except:
#         flash("Invalid verification link.", "error")
#         return redirect(url_for("register"))


# @app.route("/resend-verification", methods=["GET", "POST"])
# def resend_verification():
#     if request.method == "POST":
#         email = request.form.get("email")
        
#         user = mongo.db.users.find_one({"email": email})
#         if not user:
#             flash("Email not found.", "error")
#             return redirect(url_for("resend_verification"))
            
#         if user.get("verified", False):
#             flash("This email is already verified.", "info")
#             return redirect(url_for("login"))
            
#         if send_verification_email(email, user["name"]):
#             flash("Verification email sent! Please check your inbox.", "success")
#             return redirect(url_for("login"))
#         else:
#             flash("Failed to send verification email. Please try again later.", "error")
            
#     return render_template("resend_verification.html")


# @app.route("/startup-dashboard")
# def startup_dashboard():
#     # Redirect to the new dashboard name
#     return redirect(url_for("ngo_dashboard"))


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")
#         role = request.form.get("role")
        
#         user = mongo.db.users.find_one({"email": email})
#         if not user or not check_password_hash(user["password"], password):
#             flash("Invalid email or password.", "error")
#             return redirect(url_for("login"))
        
#         if not user.get("verified", False):
#             flash("Please verify your email before logging in.", "error")
#             return redirect(url_for("login"))

#         session["user_id"] = str(user["_id"])
#         session["role"] = user["role"]
#         session["name"] = user["name"]

#         # Redirect based on user role
#         if role == "admin":
#             return redirect(url_for("admin_panel"))
#         elif role == "donor":
#             return redirect(url_for("donor_dashboard"))
#         elif role == "ngo":
#             return redirect(url_for("ngo_dashboard"))
#         else:
#             return redirect(url_for("homepage"))
            
#     return render_template("login.html")


# @app.route("/forgot-password", methods=["GET", "POST"])
# def forgot_password():
#     if request.method == "POST":
#         email = request.form.get("email")
        
#         user = mongo.db.users.find_one({"email": email})
#         if not user:
#             # Security: still show success message even if email not found
#             flash("If your email exists in our system, you will receive a password reset link.", "info")
#             return redirect(url_for("login"))
        
#         if send_password_reset_email(email):
#             flash("Password reset instructions sent to your email.", "success")
#             return redirect(url_for("reset_password"))
#         else:
#             flash("Failed to send reset email. Please try again later.", "error")
    
#     return render_template("forgot_password.html")


# @app.route("/reset-password", methods=["GET", "POST"])
# def reset_password():
#     if request.method == "POST":
#         email = request.form.get("email")
#         otp = request.form.get("otp")
#         new_password = request.form.get("new_password")
#         confirm_password = request.form.get("confirm_password")
        
#         if new_password != confirm_password:
#             flash("Passwords don't match.", "error")
#             return redirect(url_for("reset_password"))
            
#         # Verify OTP
#         token = mongo.db.password_reset_tokens.find_one({
#             "email": email,
#             "otp": otp,
#             "expires_at": {"$gt": datetime.utcnow()},
#             "used": False
#         })
        
#         if not token:
#             flash("Invalid or expired OTP.", "error")
#             return redirect(url_for("reset_password"))
            
#         # Update password
#         hashed_password = generate_password_hash(new_password)
#         mongo.db.users.update_one(
#             {"email": email},
#             {"$set": {"password": hashed_password}}
#         )
        
#         # Mark token as used
#         mongo.db.password_reset_tokens.update_one(
#             {"_id": token["_id"]},
#             {"$set": {"used": True}}
#         )
        
#         flash("Password reset successful! You can now log in with your new password.", "success")
#         return redirect(url_for("login"))
        
#     return render_template("reset_password.html")


# # Dashboard route for NGOs (previously startups)
# @app.route("/ngo-dashboard")
# def ngo_dashboard():
#     if "role" in session and session["role"] == "ngo":
#         user_id = session["user_id"]
        
#         # Aggregation pipeline to get campaigns with donor details
#         pipeline = [
#             {
#                 "$match": {"ngo_id": ObjectId(user_id)}
#             },
#             {
#                 "$lookup": {
#                     "from": "users",
#                     "localField": "donations.donor_id",
#                     "foreignField": "_id",
#                     "as": "donor_details"
#                 }
#             }
#         ]
        
#         try:
#             campaigns = list(mongo.db.campaigns.aggregate(pipeline))
            
#             # Process each campaign to add donor names
#             for campaign in campaigns:
#                 # Create a map of donor IDs to names
#                 donor_map = {str(donor['_id']): donor['name'] 
#                               for donor in campaign.get('donor_details', [])}
                
#                 # Add donor names to donations
#                 if 'donations' in campaign:
#                     for donation in campaign['donations']:
#                         donor_id = str(donation['donor_id'])
#                         donation['donor_name'] = donor_map.get(donor_id, 'Anonymous Donor')
#                         # Format amount to 2 decimal places
#                         donation['amount'] = float(donation['amount'])

                
#                 #image part added
#                 if 'image' in campaign and isinstance(campaign['image'], bytes):
#                     campaign['image'] = f"data:image/png;base64,{base64.b64encode(campaign['image']).decode('utf-8')}"
            
#             return render_template("ngo_dashboard.html", name=session["name"], campaigns=campaigns)
            
#         except Exception as e:
#             print(f"Error fetching campaigns: {e}")
#             return render_template("ngo_dashboard.html", name=session["name"], campaigns=[])
            
#     return redirect("/login")

# from bson import Binary
# from werkzeug.utils import secure_filename

# @app.route("/create-campaign", methods=["GET", "POST"])
# def create_campaign():
#     if request.method == "POST":
#         title = request.form.get("title")
#         description = request.form.get("description")
#         funding_goal = float(request.form.get("funding_goal"))
#         deadline = request.form.get("deadline")
#         category = request.form.get("category", "General")
#         user_id = session["user_id"]
#         image = request.files["image"]

#         if image:
#             image_data = Binary(image.read())
#             image_filename = secure_filename(image.filename)
#         else:
#             image_data = None
#             image_filename = None

#         # Campaign document with image
#         campaign = {
#             "title": title,
#             "description": description,
#             "funding_goal": funding_goal,
#             "current_funding": 0,
#             "deadline": deadline,
#             "ngo_id": ObjectId(user_id),
#             "category": category,
#             "status": "pending_approval",
#             "donations": [],
#             "created_at": datetime.utcnow(),
#             "image": image_data,
#             "image_name": image_filename
#         }

#         mongo.db.campaigns.insert_one(campaign)

#         flash("Campaign created successfully! It will be live after admin approval.", "success")
#         return redirect("/ngo-dashboard")

#     return render_template("create_campaign.html")



# @app.route("/donor-dashboard")
# def donor_dashboard():
#     if "role" in session and session["role"] == "donor":
#         user_id = session["user_id"]
        
#         # Fetch campaigns the user has donated to
#         user_donations = []
#         donations = mongo.db.campaigns.find({"donations.donor_id": ObjectId(user_id)})
        
#         total_donated = 0
#         for campaign in donations:
#             for donation in campaign["donations"]:
#                 if str(donation["donor_id"]) == user_id:
#                     # Add donation date and transaction ID
#                     user_donations.append({
#                         "campaign_title": campaign["title"],
#                         "campaign_description": campaign["description"],
#                         "amount": donation["amount"],
#                         "status": campaign["status"],
#                         "deadline": campaign["deadline"],
#                         "donation_date": donation.get("date"),
#                         "transaction_id": donation.get("transaction_id"),
#                         "campaign_id": str(campaign["_id"])  # Add campaign ID for tracking
#                     })
#                     total_donated += donation["amount"]
        
#         # Fetch only approved and not fully funded campaigns
#         campaigns = list(mongo.db.campaigns.find({
#             "status": "approved",
#             "$expr": {
#                 "$lt": ["$current_funding", "$funding_goal"]
#             }
#         }).sort("deadline", 1))  # Sort by deadline ascending
        
#         for campaign in campaigns:
#             try:
#                 # Calculate current funding if not already set
#                 if "current_funding" not in campaign:
#                     current_funding = sum(don["amount"] for don in campaign.get("donations", []))
#                     # Update the campaign document with current funding
#                     mongo.db.campaigns.update_one(
#                         {"_id": campaign["_id"]},
#                         {"$set": {"current_funding": current_funding}}
#                     )
#                     campaign["current_funding"] = current_funding
                
#                 # Calculate remaining funding
#                 campaign["remaining_funding"] = campaign["funding_goal"] - campaign["current_funding"]
                
#                 # Calculate funding progress percentage
#                 campaign["funding_progress"] = (campaign["current_funding"] / campaign["funding_goal"]) * 100
                
#                 # Add time remaining calculation
#                 if isinstance(campaign["deadline"], str):
#                     deadline = datetime.strptime(campaign["deadline"], "%Y-%m-%d")
#                 else:
#                     deadline = campaign["deadline"]
#                 campaign["days_remaining"] = (deadline - datetime.now()).days
                
#                 # Remove campaigns that are fully funded
#                 if campaign["remaining_funding"] <= 0:
#                     campaigns.remove(campaign)

                


#                 #image part added
#                 if 'image' in campaign and isinstance(campaign['image'], bytes):
#                     campaign['image'] = f"data:image/png;base64,{base64.b64encode(campaign['image']).decode('utf-8')}"




                    
#             except Exception as e:
#                 app.logger.error(f"Error processing campaign {campaign.get('_id')}: {str(e)}")
#                 continue
        
#         return render_template(
#             "donor_dashboard.html",
#             name=session["name"],
#             campaigns=campaigns,
#             user_donations=user_donations,
#             total_donated=total_donated
#         )
#     return redirect("/login")


# @app.route('/logout')
# def logout():
#     # Clear the session data
#     session.clear()
#     # Redirect the user to the login page (or homepage)
#     return redirect(url_for('homepage'))


# #Admin Panel Route
# @app.route("/admin", methods=["GET", "POST"])
# def admin_panel():
#     if "role" in session and session["role"] == "admin":
#         # Fetch all users and campaigns
#         users = list(mongo.db.users.find({}, {"password": 0}))  # Exclude passwords for security
#         campaigns = list(mongo.db.campaigns.find())

#         if request.method == "POST":
#             # Approve or Reject a campaign
#             campaign_id = request.form.get("campaign_id")
#             action = request.form.get("action")

#             if campaign_id:
#                 if action == "approve":
#                     mongo.db.campaigns.update_one(
#                         {"_id": ObjectId(campaign_id)},
#                         {"$set": {"status": "approved"}}
#                     )
#                     flash("Campaign approved successfully", "success")
#                 elif action == "reject":
#                     mongo.db.campaigns.update_one(
#                         {"_id": ObjectId(campaign_id)},
#                         {"$set": {"status": "rejected"}}
#                     )
#                     flash("Campaign rejected", "info")

#             # Redirect to the admin page after the action
#             return redirect(url_for("admin_panel"))

#         return render_template("admin_dashboard.html", users=users, campaigns=campaigns)

#     return redirect("/login")


# @app.route("/donate/<campaign_id>", methods=["POST"])
# def donate(campaign_id):
#     if "role" not in session or session["role"] != "donor":
#         return jsonify({"error": "Please login as a donor"}), 401
        
#     try:
#         # Get the donation amount from the form
#         amount = float(request.form.get("donation"))
        
#         # Fetch campaign details
#         campaign = mongo.db.campaigns.find_one({"_id": ObjectId(campaign_id)})
#         if not campaign:
#             return jsonify({"error": "Campaign not found"}), 404
            
#         # Validate campaign status
#         if campaign.get("status") != "approved":
#             return jsonify({"error": "Campaign is not approved for donations"}), 400
            
#         # Store donation details in session
#         session['pending_donation'] = {
#             'amount': amount,
#             'campaign_id': str(campaign["_id"])
#         }
            
#         # Return success response with redirect URL
#         return jsonify({
#             "success": True,
#             "redirect": url_for('payment', 
#                               campaign_id=campaign_id, 
#                               amount=amount)
#         })
        
#     except ValueError:
#         return jsonify({"error": "Invalid donation amount"}), 400
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/payment/<campaign_id>')
# def payment(campaign_id):
#     if "role" not in session or session["role"] != "donor":
#         return redirect(url_for("login"))
        
#     try:
#         # Get pending donation from session
#         pending_donation = session.get('pending_donation')
#         if not pending_donation or pending_donation['campaign_id'] != campaign_id:
#             return redirect(url_for('donor_dashboard'))
            
#         # Fetch campaign details from database
#         campaign = mongo.db.campaigns.find_one({"_id": ObjectId(campaign_id)})
#         if not campaign:
#             return redirect(url_for('donor_dashboard'))
            
#         return render_template(
#             "payment.html",
#             campaign=campaign,
#             amount=pending_donation['amount'],
#             name=session.get("name")
#         )
        
#     except Exception as e:
#         print(f"Error in payment route: {str(e)}")
#         return redirect(url_for('donor_dashboard'))


# @app.route("/create-payment-intent/<campaign_id>", methods=["POST"])
# def create_payment_intent(campaign_id):
#     if "role" not in session or session["role"] != "donor":
#         return jsonify({"error": "Unauthorized"}), 401
        
#     try:
#         # Get donation details from session
#         pending_donation = session.get('pending_donation')
#         if not pending_donation or pending_donation['campaign_id'] != campaign_id:
#             return jsonify({"error": "Invalid donation session - please try donating again"}), 400
            
#         amount = pending_donation['amount']
        
#         print(f"Creating payment intent for campaign {campaign_id}, amount: {amount}")  # Debug log
        
#         # Create Stripe PaymentIntent
#         intent = stripe.PaymentIntent.create(
#             amount=int(amount * 100),  # Convert to cents
#             currency="usd",
#             automatic_payment_methods={
#                 "enabled": True
#             },
#             metadata={
#                 "campaign_id": campaign_id,
#                 "donor_id": session["user_id"]
#             }
#         )
        
#         print(f"Payment intent created successfully: {intent.id}")  # Debug log
        
#         return jsonify({
#             "clientSecret": intent.client_secret
#         })
        
#     except Exception as e:
#         print(f"Error creating payment intent: {str(e)}")  # Debug log
#         return jsonify({"error": f"Payment initialization failed: {str(e)}"}), 400


# @app.route("/confirm-donation/<campaign_id>")
# def confirm_donation(campaign_id):
#     if "role" not in session or session["role"] != "donor":
#         return redirect(url_for('login'))
        
#     try:
#         payment_intent_id = request.args.get('payment_intent')
#         payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
#         if payment_intent.status == "succeeded":
#             # Get donation details from pending donation in session
#             pending_donation = session.get('pending_donation')
#             if not pending_donation or pending_donation['campaign_id'] != campaign_id:
#                 flash("Invalid donation session", "error")
#                 return redirect(url_for('donor_dashboard'))
            
#             amount = pending_donation['amount']
            
#             # Update campaign with new donation
#             now = datetime.utcnow()
#             donation_data = {
#                 "donor_id": ObjectId(session["user_id"]),
#                 "amount": amount,
#                 "date": now,
#                 "transaction_id": payment_intent_id
#             }
            
#             # Update campaign document
#             result = mongo.db.campaigns.update_one(
#                 {"_id": ObjectId(campaign_id)},
#                 {
#                     "$push": {"donations": donation_data},
#                     "$inc": {"current_funding": amount}
#                 }
#             )
            
#             if result.modified_count == 1:
#                 session.pop('pending_donation', None)
#                 flash("Donation successful! Thank you for your contribution.", "success")
#             else:
#                 # If donation fails, initiate refund
#                 stripe.Refund.create(payment_intent=payment_intent_id)
#                 flash("Donation failed, payment refunded", "error")
                
#         else:
#             flash("Payment failed or was cancelled", "error")
            
#         return redirect(url_for('donor_dashboard'))
            
#     except Exception as e:
#         print(f"Error in confirm_donation: {str(e)}")  # Add logging
#         flash(f"An error occurred during payment processing", "error")
#         return redirect(url_for('donor_dashboard'))


# if __name__ == "__main__":
#     app.run(debug=True)


# # # Route to create a campaign (NGO)
# # @app.route("/create-campaign", methods=["GET", "POST"])
# # def create_campaign():
# #     if request.method == "POST":
# #         title = request.form.get("title")
# #         description = request.form.get("description")
# #         funding_goal = float(request.form.get("funding_goal"))
# #         deadline = request.form.get("deadline")
# #         category = request.form.get("category", "General")  # New field for campaign category
# #         user_id = session["user_id"]

# #         # Insert campaign into database
# #         campaign = {
# #             "title": title,
# #             "description": description,
# #             "funding_goal": funding_goal,
# #             "current_funding": 0,
# #             "deadline": deadline,
# #             "ngo_id": ObjectId(user_id),
# #             "category": category,             # Category of campaign
# #             "status": "pending_approval",     # Initial status requires admin approval
# #             "donations": [],                  # List to track donations
# #             "created_at": datetime.utcnow()
# #         }
# #         mongo.db.campaigns.insert_one(campaign)
# #         flash("Campaign created successfully! It will be live after admin approval.", "success")
# #         return redirect("/ngo-dashboard")
# #     return render_template("create_campaign.html")

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from bson.objectid import ObjectId
import os
import datetime
import stripe
import random
import string
from datetime import datetime, timedelta
from dotenv import load_dotenv
import base64

# SendGrid imports
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load environment variables
load_dotenv()

stripe.api_key = os.environ.get("stripe_key")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mysecretkey')

# MongoDB Configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# SendGrid configuration
sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
from_email = os.environ.get('FROM_EMAIL', 'donatetongo3@gmail.com')

# Initialize SendGrid client
sg = SendGridAPIClient(api_key=sendgrid_api_key) if sendgrid_api_key else None

# URL safe serializer for generating tokens
serializer = URLSafeTimedSerializer(app.secret_key)

if mongo.db is None:
    print("MongoDB connection not established!")
else:
    print("MongoDB connection established!")

if not sg:
    print("Warning: SendGrid not configured properly!")
else:
    print("SendGrid configured successfully!")

# Email sending functions
def send_email(to_email, subject, html_content):
    """Generic function to send emails using SendGrid"""
    if not sg:
        print("Error: SendGrid not properly configured")
        return False

    try:
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        response = sg.send(message)
        
        # SendGrid returns 2xx status codes for success
        if response.status_code in [200, 201, 202]:
            print(f"Email sent successfully to {to_email}")
            return True
        else:
            print(f"SendGrid error: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error sending email via SendGrid: {str(e)}")
        return False

def send_verification_email(email, name):
    """Send email verification token to user"""
    # Generate token
    token = serializer.dumps(email, salt='email-verification')
    
    # Build verification URL
    verify_url = url_for('verify_email', token=token, _external=True)
    
    # Email content
    subject = "Please Verify Your Email"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50;">Welcome to our donation platform, {name}!</h2>
            <p>Thank you for registering. Please click the button below to verify your email address:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}" 
                   style="background-color: #3498db; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Verify Email
                </a>
            </div>
            <p><strong>This link will expire in 24 hours.</strong></p>
            <p style="color: #7f8c8d; font-size: 14px;">
                If you did not create an account, please ignore this email.
            </p>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="color: #95a5a6; font-size: 12px;">
                This email was sent from our donation platform. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)

def send_welcome_email(email, name):
    """Send welcome email after successful verification"""
    subject = "Welcome to Our Donation Platform!"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #27ae60;">Welcome aboard, {name}! 🎉</h2>
            <p>Your email has been successfully verified.</p>
            <p>You can now log in and start using our platform to:</p>
            <ul style="color: #2c3e50;">
                <li>Connect with NGOs and charitable organizations</li>
                <li>Make secure donations to causes you care about</li>
                <li>Track your donation history and impact</li>
            </ul>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{url_for('login', _external=True)}" 
                   style="background-color: #27ae60; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Start Donating
                </a>
            </div>
            <p>If you have any questions, feel free to contact our support team.</p>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="color: #95a5a6; font-size: 12px;">
                Thank you for joining our mission to make a difference!
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)

def send_password_reset_email(email):
    """Send password reset token to user"""
    # Generate OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    # Store OTP in database with expiry
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    mongo.db.password_reset_tokens.insert_one({
        "email": email,
        "otp": otp,
        "expires_at": expires_at,
        "used": False
    })
    
    # Email content
    subject = "Password Reset Request"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #e74c3c;">Password Reset Request</h2>
            <p>You requested a password reset. Here is your one-time passcode:</p>
            <div style="text-align: center; margin: 30px 0;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; 
                           border-left: 4px solid #e74c3c;">
                    <h3 style="font-size: 32px; margin: 0; color: #2c3e50; letter-spacing: 5px;">
                        {otp}
                    </h3>
                </div>
            </div>
            <p><strong>This code will expire in 30 minutes.</strong></p>
            <p style="color: #e74c3c; font-weight: bold;">
                If you did not request this password reset, please ignore this email and 
                consider changing your password as a security precaution.
            </p>
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="color: #95a5a6; font-size: 12px;">
                For security reasons, this code can only be used once.
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html_content)

# Keep all your existing routes unchanged
@app.route("/")
def homepage():
    name = session.get("name", None)
    return render_template("homepage.html", name=name)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")
        age = request.form.get("age")
        role = request.form.get("role")
        
        if not all([name, email, phone, password, confirm_password, age, role]):
            flash("Please fill in all fields.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        if mongo.db.users.find_one({"email": email}):
            flash("Email already registered. Please login.", "error")
            return redirect(url_for("login"))
        
        hashed_password = generate_password_hash(password)
        
        # Insert user with verified status set to False
        user_id = mongo.db.users.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password,
            "phone": phone,
            "age": int(age),
            "role": role,
            "verified": False,
            "created_at": datetime.utcnow()
        }).inserted_id
        
        # Send verification email
        if send_verification_email(email, name):
            flash("Registration successful! Please check your email to verify your account.", "success")
        else:
            flash("Registration successful but we couldn't send verification email. Please contact support.", "warning")
        
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/verify-email/<token>")
def verify_email(token):
    try:
        # Verify token with 24-hour expiry
        email = serializer.loads(token, salt='email-verification', max_age=86400)
        
        # Update user verification status
        result = mongo.db.users.update_one(
            {"email": email, "verified": False},
            {"$set": {"verified": True}}
        )
        
        if result.modified_count > 0:
            # Get user info for welcome email
            user = mongo.db.users.find_one({"email": email})
            if user:
                send_welcome_email(email, user["name"])
            
            flash("Email verification successful! You can now log in.", "success")
        else:
            flash("Email already verified or not found.", "info")
        
        return redirect(url_for("login"))
        
    except SignatureExpired:
        flash("The verification link has expired. Please request a new one.", "error")
        return redirect(url_for("resend_verification"))
    except:
        flash("Invalid verification link.", "error")
        return redirect(url_for("register"))

@app.route("/resend-verification", methods=["GET", "POST"])
def resend_verification():
    if request.method == "POST":
        email = request.form.get("email")
        
        user = mongo.db.users.find_one({"email": email})
        if not user:
            flash("Email not found.", "error")
            return redirect(url_for("resend_verification"))
            
        if user.get("verified", False):
            flash("This email is already verified.", "info")
            return redirect(url_for("login"))
            
        if send_verification_email(email, user["name"]):
            flash("Verification email sent! Please check your inbox.", "success")
            return redirect(url_for("login"))
        else:
            flash("Failed to send verification email. Please try again later.", "error")
            
    return render_template("resend_verification.html")

@app.route("/startup-dashboard")
def startup_dashboard():
    # Redirect to the new dashboard name
    return redirect(url_for("ngo_dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        
        user = mongo.db.users.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))
        
        if not user.get("verified", False):
            flash("Please verify your email before logging in.", "error")
            return redirect(url_for("login"))

        session["user_id"] = str(user["_id"])
        session["role"] = user["role"]
        session["name"] = user["name"]

        # Redirect based on user role
        if role == "admin":
            return redirect(url_for("admin_panel"))
        elif role == "donor":
            return redirect(url_for("donor_dashboard"))
        elif role == "ngo":
            return redirect(url_for("ngo_dashboard"))
        else:
            return redirect(url_for("homepage"))
            
    return render_template("login.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        
        user = mongo.db.users.find_one({"email": email})
        if not user:
            # Security: still show success message even if email not found
            flash("If your email exists in our system, you will receive a password reset link.", "info")
            return redirect(url_for("login"))
        
        if send_password_reset_email(email):
            flash("Password reset instructions sent to your email.", "success")
            return redirect(url_for("reset_password"))
        else:
            flash("Failed to send reset email. Please try again later.", "error")
    
    return render_template("forgot_password.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        otp = request.form.get("otp")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        if new_password != confirm_password:
            flash("Passwords don't match.", "error")
            return redirect(url_for("reset_password"))
            
        # Verify OTP
        token = mongo.db.password_reset_tokens.find_one({
            "email": email,
            "otp": otp,
            "expires_at": {"$gt": datetime.utcnow()},
            "used": False
        })
        
        if not token:
            flash("Invalid or expired OTP.", "error")
            return redirect(url_for("reset_password"))
            
        # Update password
        hashed_password = generate_password_hash(new_password)
        mongo.db.users.update_one(
            {"email": email},
            {"$set": {"password": hashed_password}}
        )
        
        # Mark token as used
        mongo.db.password_reset_tokens.update_one(
            {"_id": token["_id"]},
            {"$set": {"used": True}}
        )
        
        flash("Password reset successful! You can now log in with your new password.", "success")
        return redirect(url_for("login"))
        
    return render_template("reset_password.html")

# Dashboard route for NGOs (previously startups)
@app.route("/ngo-dashboard")
def ngo_dashboard():
    if "role" in session and session["role"] == "ngo":
        user_id = session["user_id"]
        
        # Aggregation pipeline to get campaigns with donor details
        pipeline = [
            {
                "$match": {"ngo_id": ObjectId(user_id)}
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "donations.donor_id",
                    "foreignField": "_id",
                    "as": "donor_details"
                }
            }
        ]
        
        try:
            campaigns = list(mongo.db.campaigns.aggregate(pipeline))
            
            # Process each campaign to add donor names
            for campaign in campaigns:
                # Create a map of donor IDs to names
                donor_map = {str(donor['_id']): donor['name'] 
                              for donor in campaign.get('donor_details', [])}
                
                # Add donor names to donations
                if 'donations' in campaign:
                    for donation in campaign['donations']:
                        donor_id = str(donation['donor_id'])
                        donation['donor_name'] = donor_map.get(donor_id, 'Anonymous Donor')
                        # Format amount to 2 decimal places
                        donation['amount'] = float(donation['amount'])

                
                #image part added
                if 'image' in campaign and isinstance(campaign['image'], bytes):
                    campaign['image'] = f"data:image/png;base64,{base64.b64encode(campaign['image']).decode('utf-8')}"
            
            return render_template("ngo_dashboard.html", name=session["name"], campaigns=campaigns)
            
        except Exception as e:
            print(f"Error fetching campaigns: {e}")
            return render_template("ngo_dashboard.html", name=session["name"], campaigns=[])
            
    return redirect("/login")

from bson import Binary
from werkzeug.utils import secure_filename

@app.route("/create-campaign", methods=["GET", "POST"])
def create_campaign():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        funding_goal = float(request.form.get("funding_goal"))
        deadline = request.form.get("deadline")
        category = request.form.get("category", "General")
        user_id = session["user_id"]
        image = request.files["image"]

        if image:
            image_data = Binary(image.read())
            image_filename = secure_filename(image.filename)
        else:
            image_data = None
            image_filename = None

        # Campaign document with image
        campaign = {
            "title": title,
            "description": description,
            "funding_goal": funding_goal,
            "current_funding": 0,
            "deadline": deadline,
            "ngo_id": ObjectId(user_id),
            "category": category,
            "status": "pending_approval",
            "donations": [],
            "created_at": datetime.utcnow(),
            "image": image_data,
            "image_name": image_filename
        }

        mongo.db.campaigns.insert_one(campaign)

        flash("Campaign created successfully! It will be live after admin approval.", "success")
        return redirect("/ngo-dashboard")

    return render_template("create_campaign.html")

@app.route("/donor-dashboard")
def donor_dashboard():
    if "role" in session and session["role"] == "donor":
        user_id = session["user_id"]
        
        # Fetch campaigns the user has donated to
        user_donations = []
        donations = mongo.db.campaigns.find({"donations.donor_id": ObjectId(user_id)})
        
        total_donated = 0
        for campaign in donations:
            for donation in campaign["donations"]:
                if str(donation["donor_id"]) == user_id:
                    # Add donation date and transaction ID
                    user_donations.append({
                        "campaign_title": campaign["title"],
                        "campaign_description": campaign["description"],
                        "amount": donation["amount"],
                        "status": campaign["status"],
                        "deadline": campaign["deadline"],
                        "donation_date": donation.get("date"),
                        "transaction_id": donation.get("transaction_id"),
                        "campaign_id": str(campaign["_id"])  # Add campaign ID for tracking
                    })
                    total_donated += donation["amount"]
        
        # Fetch only approved and not fully funded campaigns
        campaigns = list(mongo.db.campaigns.find({
            "status": "approved",
            "$expr": {
                "$lt": ["$current_funding", "$funding_goal"]
            }
        }).sort("deadline", 1))  # Sort by deadline ascending
        
        for campaign in campaigns:
            try:
                # Calculate current funding if not already set
                if "current_funding" not in campaign:
                    current_funding = sum(don["amount"] for don in campaign.get("donations", []))
                    # Update the campaign document with current funding
                    mongo.db.campaigns.update_one(
                        {"_id": campaign["_id"]},
                        {"$set": {"current_funding": current_funding}}
                    )
                    campaign["current_funding"] = current_funding
                
                # Calculate remaining funding
                campaign["remaining_funding"] = campaign["funding_goal"] - campaign["current_funding"]
                
                # Calculate funding progress percentage
                campaign["funding_progress"] = (campaign["current_funding"] / campaign["funding_goal"]) * 100
                
                # Add time remaining calculation
                if isinstance(campaign["deadline"], str):
                    deadline = datetime.strptime(campaign["deadline"], "%Y-%m-%d")
                else:
                    deadline = campaign["deadline"]
                campaign["days_remaining"] = (deadline - datetime.now()).days
                
                # Remove campaigns that are fully funded
                if campaign["remaining_funding"] <= 0:
                    campaigns.remove(campaign)

                #image part added
                if 'image' in campaign and isinstance(campaign['image'], bytes):
                    campaign['image'] = f"data:image/png;base64,{base64.b64encode(campaign['image']).decode('utf-8')}"
                    
            except Exception as e:
                app.logger.error(f"Error processing campaign {campaign.get('_id')}: {str(e)}")
                continue
        
        return render_template(
            "donor_dashboard.html",
            name=session["name"],
            campaigns=campaigns,
            user_donations=user_donations,
            total_donated=total_donated
        )
    return redirect("/login")

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the login page (or homepage)
    return redirect(url_for('homepage'))

#Admin Panel Route
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if "role" in session and session["role"] == "admin":
        # Fetch all users and campaigns
        users = list(mongo.db.users.find({}, {"password": 0}))  # Exclude passwords for security
        campaigns = list(mongo.db.campaigns.find())

        if request.method == "POST":
            # Approve or Reject a campaign
            campaign_id = request.form.get("campaign_id")
            action = request.form.get("action")

            if campaign_id:
                if action == "approve":
                    mongo.db.campaigns.update_one(
                        {"_id": ObjectId(campaign_id)},
                        {"$set": {"status": "approved"}}
                    )
                    flash("Campaign approved successfully", "success")
                elif action == "reject":
                    mongo.db.campaigns.update_one(
                        {"_id": ObjectId(campaign_id)},
                        {"$set": {"status": "rejected"}}
                    )
                    flash("Campaign rejected", "info")

            # Redirect to the admin page after the action
            return redirect(url_for("admin_panel"))

        return render_template("admin_dashboard.html", users=users, campaigns=campaigns)

    return redirect("/login")

@app.route("/donate/<campaign_id>", methods=["POST"])
def donate(campaign_id):
    if "role" not in session or session["role"] != "donor":
        return jsonify({"error": "Please login as a donor"}), 401
        
    try:
        # Get the donation amount from the form
        amount = float(request.form.get("donation"))
        
        # Fetch campaign details
        campaign = mongo.db.campaigns.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            return jsonify({"error": "Campaign not found"}), 404
            
        # Validate campaign status
        if campaign.get("status") != "approved":
            return jsonify({"error": "Campaign is not approved for donations"}), 400
            
        # Store donation details in session
        session['pending_donation'] = {
            'amount': amount,
            'campaign_id': str(campaign["_id"])
        }
            
        # Return success response with redirect URL
        return jsonify({
            "success": True,
            "redirect": url_for('payment', 
                              campaign_id=campaign_id, 
                              amount=amount)
        })
        
    except ValueError:
        return jsonify({"error": "Invalid donation amount"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/payment/<campaign_id>')
def payment(campaign_id):
    if "role" not in session or session["role"] != "donor":
        return redirect(url_for("login"))
        
    try:
        # Get pending donation from session
        pending_donation = session.get('pending_donation')
        if not pending_donation or pending_donation['campaign_id'] != campaign_id:
            return redirect(url_for('donor_dashboard'))
            
        # Fetch campaign details from database
        campaign = mongo.db.campaigns.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            return redirect(url_for('donor_dashboard'))
            
        return render_template(
            "payment.html",
            campaign=campaign,
            amount=pending_donation['amount'],
            name=session.get("name")
        )
        
    except Exception as e:
        print(f"Error in payment route: {str(e)}")
        return redirect(url_for('donor_dashboard'))

@app.route("/create-payment-intent/<campaign_id>", methods=["POST"])
def create_payment_intent(campaign_id):
    if "role" not in session or session["role"] != "donor":
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        # Get donation details from session
        pending_donation = session.get('pending_donation')
        if not pending_donation or pending_donation['campaign_id'] != campaign_id:
            return jsonify({"error": "Invalid donation session - please try donating again"}), 400
            
        amount = pending_donation['amount']
        
        print(f"Creating payment intent for campaign {campaign_id}, amount: {amount}")  # Debug log
        
        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            automatic_payment_methods={
                "enabled": True
            },
            metadata={
                "campaign_id": campaign_id,
                "donor_id": session["user_id"]
            }
        )
        
        print(f"Payment intent created successfully: {intent.id}")  # Debug log
        
        return jsonify({
            "clientSecret": intent.client_secret
        })
        
    except Exception as e:
        print(f"Error creating payment intent: {str(e)}")  # Debug log
        return jsonify({"error": f"Payment initialization failed: {str(e)}"}), 400

@app.route("/confirm-donation/<campaign_id>")
def confirm_donation(campaign_id):
    if "role" not in session or session["role"] != "donor":
        return redirect(url_for('login'))
        
    try:
        payment_intent_id = request.args.get('payment_intent')
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if payment_intent.status == "succeeded":
            # Get donation details from pending donation in session
            pending_donation = session.get('pending_donation')
            if not pending_donation or pending_donation['campaign_id'] != campaign_id:
                flash("Invalid donation session", "error")
                return redirect(url_for('donor_dashboard'))
            
            amount = pending_donation['amount']
            
            # Update campaign with new donation
            now = datetime.utcnow()
            donation_data = {
                "donor_id": ObjectId(session["user_id"]),
                "amount": amount,
                "date": now,
                "transaction_id": payment_intent_id
            }
            
            # Update campaign document
            result = mongo.db.campaigns.update_one(
                {"_id": ObjectId(campaign_id)},
                {
                    "$push": {"donations": donation_data},
                    "$inc": {"current_funding": amount}
                }
            )
            
            if result.modified_count == 1:
                session.pop('pending_donation', None)
                flash("Donation successful! Thank you for your contribution.", "success")
            else:
                # If donation fails, initiate refund
                stripe.Refund.create(payment_intent=payment_intent_id)
                flash("Donation failed, payment refunded", "error")
                
        else:
            flash("Payment failed or was cancelled", "error")
            
        return redirect(url_for('donor_dashboard'))
            
    except Exception as e:
        print(f"Error in confirm_donation: {str(e)}")  # Add logging
        flash(f"An error occurred during payment processing", "error")
        return redirect(url_for('donor_dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
