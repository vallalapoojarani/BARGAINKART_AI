# BARGAINKART 🛒✨
### AI-Powered Price Negotiation, Product Authenticity and Price Transparency E-Commerce System
> **Tagline:** *"Compare. Verify. Bargain. Save."*  
> **Project Type:** Final-Year CSE / AIML Academic Capstone & Production Architecture

---

## 📖 Executive Summary
**BARGAINKART** is a production-grade full-stack e-commerce web application engineered to solve three major pain points in online consumer commerce:
1. **Counterfeit & Seller Fraud Risk:** Buyers struggle to identify fake listings, unverified resellers, and manipulated reviews.
2. **Opaque Pricing Disparities:** The same product is listed at wildly disparate prices across different platforms and vendors without transparency.
3. **Inflexible Pricing & Margin Inefficiency:** Retail prices remain rigid despite vendor inventory pressure, stock velocity needs, and customer willingness to pay.

BARGAINKART introduces an explainable **Multi-Factor AI Authenticity Engine**, a cross-marketplace **Price Transparency Matrix**, and an automated **Multi-Round AI Price Negotiator** that acts as an intelligent bargaining agent between consumer and vendor inventory.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3 (Modern Glassmorphic Design Tokens, Responsive Grid/Flexbox), JavaScript (ES6+), Chart.js 4.4, FontAwesome 6.5 |
| **Backend** | Python 3.10+, Flask 3.1, Flask-Login, Flask-SQLAlchemy 3.1, Werkzeug, PyMongo 4.6+ |
| **Databases** | **Dual Database Engine:**<br>• **Relational:** SQLite (default zero-config) / PostgreSQL production ready<br>• **Document Store:** MongoDB (PyMongo sync, audit logging, price intelligence with graceful fallback) |
| **AI / Machine Learning** | Scikit-learn (RandomForest, IsolationForest, TF-IDF Vectorizer, Cosine Similarity), NumPy, NLP heuristics, Game-Theoretic Negotiation Engine (ZOPA & Concession Curves) |
| **Security** | Salted password hashing (Scrypt / PBKDF2), Session authentication, Cryptographic Deal Tokens (`BK-DEAL-...`), CSRF & SQL injection protections, .env isolation |

---

## 🚀 Key Modules & System Architecture

```
BARGAINKART/
├── app.py                     # Flask application factory, error handlers & context
├── config.py                  # Environment-aware configuration (SQLite / PostgreSQL)
├── run.py                     # Root execution runner with automatic seeding
├── requirements.txt           # Production dependencies
├── .env.example               # Environment variables template
│
├── models/                    # Relational ORM models
│   ├── __init__.py            # SQLAlchemy & LoginManager initialization
│   └── models.py              # User, Seller, Product, Order, Tracking, Negotiation, etc.
│
├── routes/                    # REST API & Frontend View Controllers
│   ├── __init__.py            # Blueprint registration
│   ├── auth.py                # Login, Register, Logout, Profile, Forgot Password
│   ├── products.py            # Catalog filtering, details, category browser
│   ├── verify.py              # AI Authenticity Studio & verification API
│   ├── compare.py             # Price transparency & multi-seller comparison
│   ├── negotiate.py           # Multi-round bargaining studio & deal applier
│   ├── cart.py                # Cart calculations, negotiated price lock, wishlist
│   ├── orders.py              # Simulated checkout, order management & tracking
│   ├── dashboard.py           # User Analytics Dashboard & Chart.js data feed
│   ├── admin.py               # Administrative control console & status updates
│   └── ai_assistant.py        # Conversational floating AI agent
│
├── services/                  # Business logic & orchestration layer
│   ├── __init__.py
│   ├── pricing_service.py     # Cross-seller price matrices & spread calculations
│   ├── negotiation_service.py # Multi-turn bargaining state machine
│   └── authenticity_service.py# AI audit coordination & audit logging
│
├── ai/                        # Pure AI/ML mathematical models
│   ├── __init__.py            # High-performance singleton model instances
│   ├── authenticity_model.py  # Explainable multi-factor authenticity scoring
│   ├── price_prediction.py    # RandomForest price regression & fair market range
│   ├── negotiation_model.py   # Multi-round dynamic concession bargaining agent
│   ├── recommendation.py      # TF-IDF & Cosine Similarity product recommender
│   └── fraud_detection.py     # Isolation Forest seller anomaly detector
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Core layout with sidebar, header & floating AI widget
│   ├── index.html             # High-conversion landing page
│   ├── login.html             # Login with 1-click demo buttons
│   ├── register.html          # User registration
│   ├── forgot_password.html   # Password recovery UI
│   ├── products.html          # Product catalog with 6-action cards
│   ├── product_detail.html    # Details with prominent AI PRODUCT ANALYSIS
│   ├── categories.html        # Category visual gallery
│   ├── negotiate.html         # Interactive AI bargaining studio
│   ├── verify.html            # AI Authenticity Studio
│   ├── compare.html           # Price Transparency Hub
│   ├── cart.html              # Itemized cart with negotiated discounts
│   ├── wishlist.html          # Wishlist with price drop alerts
│   ├── checkout.html          # Realistic simulated checkout
│   ├── orders.html            # Order management history
│   ├── tracking.html          # 7-stage visual milestone stepper
│   ├── dashboard_home.html    # Home overview dashboard
│   ├── user_analytics.html    # Analytics dashboard (6 KPIs + 8 Chart.js charts)
│   ├── admin_dashboard.html   # Complete admin management console
│   └── profile.html           # User profile & settings
│
├── static/                    # Frontend assets
│   ├── css/styles.css         # Complete responsive design system
│   └── js/
│       ├── main.js            # Sidebar toggle, cart/wishlist AJAX handlers
│       ├── assistant.js       # Floating AI chat drawer & chip triggers
│       └── charts.js          # Chart.js visualization initializers
│
├── database/                  # Database storage & initialization
│   ├── bargainkart.db         # Pre-seeded SQLite database
│   └── seed.py                # Comprehensive demo database generator
│
├── datasets/                  # Sample academic demonstration datasets
│   ├── products_dataset.json  # Rich hardware catalogs & datasheets
│   ├── historical_prices.csv  # 6-month historical transaction records
│   └── reviews_sentiment.csv  # NLP sentiment & fake review sample data
│
└── tests/                     # Automated testing suite
    ├── test_ai_models.py      # AI/ML unit test suite
    └── test_app.py            # Flask route & API integration test suite
```

---

## 🧠 AI / Machine Learning Methodology

### 1. Explainable Authenticity Scoring (`ai/authenticity_model.py`)
Rather than relying on unexplainable black-box models, the authenticity engine evaluates 5 distinct feature vectors:
$$\text{Confidence Score} = \sum_{i=1}^5 w_i \cdot S_i$$
- **Seller Consistency ($w_1 = 0.25$):** Evaluates account age in days, merchant rating ($0-5$), verified credentials badge, and dispute rate penalty.
- **Price Normalcy ($w_2 = 0.25$):** Measures statistical distance of the listing price against median benchmark competitor prices. Abnormal discounts ($>45\%$) trigger counterfeit risk penalties.
- **Specification Integrity ($w_3 = 0.20$):** Verifies the presence of key hardware attributes (processor, GPU, memory, resolution, warranty) against category minimums.
- **Review Signals NLP ($w_4 = 0.15$):** Scans customer reviews for synthetic review phrasing (*"100% genuine guaranteed"*, *"best replica"*, *"contact on whatsapp"*) and calculates verified-buyer ratios.
- **Image Presentation ($w_5 = 0.15$):** Checks for high-resolution catalog imagery and lack of scam watermarks.

**Risk Classification:**
- **$\ge 82\%$:** LOW RISK (*"Likely Authentic"*)
- **$65\% - 81\%$:** MEDIUM RISK (*"Moderate Caution / Verify Listing"*)
- **$< 65\%$:** HIGH RISK (*"Potentially Suspicious Listing"*)

> *Ethical AI Notice:* The system transparently informs users that AI confidence metrics represent statistical risk assessments rather than legal warranties.

### 2. Fair Market Price Estimation (`ai/price_prediction.py`)
- Employs a **RandomForestRegressor** trained on product base price, category encodings, brand tier weights, real-time demand indices, and competitor price variance.
- Outputs a **Predicted Market Price** and a bounded **Market Range** (e.g. ₹47,000 – ₹49,000 for a ₹50,000 item) along with timing advice (*"Buy Now"*, *"Fair Market"*, *"Negotiate with AI"*).

### 3. Multi-Round Dynamic Negotiation (`ai/negotiation_model.py`)
- Uses a multi-turn concession curve across 3 rounds.
- Calculates the vendor's reserve floor:
$$\text{Floor Price} = \text{Base Price} \times \text{Dynamic Margin}$$
(adjusted dynamically for high inventory stock or sluggish demand).
- Concession factor increases per round ($35\% \rightarrow 70\% \rightarrow 95\%$), offering an engaging, human-like bargaining conversation.
- Flags absurd lowball offers below vendor wholesale cost and invites realistic counter-offers.

### 4. Recommendation & Fraud Detection (`ai/recommendation.py` & `ai/fraud_detection.py`)
- **TF-IDF + Cosine Similarity:** Computes semantic similarity between specifications and product titles to suggest *"Similar Products"* and *"Better Value Alternatives"*.
- **Isolation Forest:** Unsupervised anomaly detection identifying irregular seller behavior, synthetic review clustering, and artificial price markup tricks.

---

## ⚡ Quick Start & Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed.

### Step 1: Clone or Extract the Project
```bash
cd BARGAINKART
```

### Step 2: Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python run.py
```
*Note: The application will automatically verify and seed the SQLite database with 14 products, 6 sellers, orders, reviews, and test accounts on first launch.*

Access the application in your browser:
**`http://127.0.0.1:5000`**

---

## 🔑 Default Demo Accounts

For college presentation and grading evaluation, use these pre-configured accounts:

| Role | Email | Password | Privileges |
|---|---|---|---|
| **Regular Shopper** | `demo@bargainkart.com` | `Demo@123` | Browsing, AI Verification, Negotiator, Cart, Simulated Checkout, Tracking, User Analytics |
| **Platform Administrator** | `admin@bargainkart.com` | `Admin@123` | Full access + Admin Dashboard, Live Order Status Control, Seller Directory, AI Audit Logs |

*(Quick-fill buttons are provided on the login page for instant 1-click demonstration!)*

---

## 📡 REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authenticate user via JSON |
| `POST` | `/api/auth/register` | Register new customer account |
| `GET` | `/api/products` | Query products catalog with filters |
| `GET` | `/api/products/<id>` | Retrieve full product specifications & seller data |
| `GET` | `/api/products/<id>/verify` | Execute live AI Authenticity Assessment |
| `GET` | `/api/products/<id>/prices` | Get multi-seller price transparency matrix |
| `POST` | `/api/products/<id>/negotiate` | Submit offer to AI bargaining agent |
| `POST` | `/api/negotiate/apply-deal` | Lock agreed negotiated price into user cart |
| `GET` | `/api/cart` | View cart items and savings calculations |
| `POST` | `/api/cart/add` | Add product (standard or negotiated) to cart |
| `POST` | `/api/checkout/place-order` | Execute simulated checkout & spawn 7-stage tracking |
| `GET` | `/api/orders` | Retrieve customer order history |
| `GET` | `/api/orders/<id>/tracking` | Retrieve order fulfillment timeline |
| `GET` | `/api/dashboard/stats` | JSON feed for 8 Chart.js user analytics charts |
| `POST` | `/api/admin/order/<id>/status` | Update order status live (Admin) |
| `POST` | `/api/ai/assistant` | Conversational NLP query interface |

---

## 🧪 Automated Testing

Run the automated test suite to verify 100% code functionality:

```bash
# Run AI/ML unit tests
python -m unittest tests/test_ai_models.py

# Run Flask integration & API route tests
python -m unittest tests/test_app.py
```

---

## 🔮 Future Enhancements
1. **Computer Vision Siamese Network:** Deep convolutional neural network comparing live camera uploads against verified manufacturer CAD renders.
2. **Blockchain Decentralized Proof-of-Origin:** Minting tamper-proof ERC-721 product passports for luxury electronics.
3. **Voice AI Assistant:** WebSpeech API integration for hands-free voice bargaining.
4. **Reinforcement Learning from Human Feedback (RLHF):** PPO agent trained on negotiation dialogue transcripts to optimize conversion rates while preserving seller margin.

---

## 🎓 Academic Submission Statement
*Developed as a Final-Year CSE / AIML Capstone Project demonstrating full-stack engineering, production Flask REST APIs, explainable machine learning models, and modern user experience design.*
#   B A R G A I N K A R T _ A I  
 #   B A R G A I N K A R T _ A I  
 