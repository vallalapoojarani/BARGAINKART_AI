import os
import sys
import json
import random
from datetime import datetime, timezone, timedelta, date

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.models import (
    User, Seller, Product, ProductSellerPrice, PriceHistory,
    Review, Order, OrderItem, TrackingEvent, Negotiation, AuthenticityCheck, Wishlist, CartItem, Coupon
)

app = create_app()

def build_500_products():
    """Generates 500 rich, diverse, realistic e-commerce products across 6 core categories."""
    products = []
    
    # Unsplash curated image collections for maximum visual appeal
    images = {
        'Kitchen & Dining': [
            'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1593618998160-e34014e67546?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1585515320310-259814833e62?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1583778176476-4a8b02a64c01?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1610557892470-55d9e80c0bce?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1628088062854-d1870b4553da?auto=format&fit=crop&w=800&q=80'
        ],
        'Kids Fashion & Toys': [
            'https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1518831959646-742c3a14ebf7?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1566492031773-4f4e44671857?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1508873696983-2df5293cb32f?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1560859251-d563a49c5e4a?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1533512930330-4ac257c86793?auto=format&fit=crop&w=800&q=80'
        ],
        'Mens Fashion & Wear': [
            'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80'
        ],
        'Womens Fashion & Ethnic': [
            'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80'
        ],
        'Electronics & Gadgets': [
            'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80'
        ],
        'Home Decor & Space Furnishings': [
            'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1534349762230-e0cadf78f5da?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1540932239986-30128078f3c5?auto=format&fit=crop&w=800&q=80'
        ]
    }

    # Archetypes per category to generate realistic items with variation
    kitchen_items = [
        ("Kitchen Pro Multi-Blade Peeler & Slicer Set", "KitchenPro", 200.0, "Essential kitchen duo with dual stainless-steel julienne and serrated swivel peelers.", {"Blade Material": "304 Food-Grade Stainless Steel", "Grip": "Ergonomic Non-Slip Silicone", "Dishwasher Safe": "Yes"}),
        ("Kitchen Pro Stainless Steel Chef Knife (Ergonomic Grip)", "KitchenPro", 300.0, "Precision forged high-carbon 8-inch chef knife with ultra-sharp edge and ergonomic slip-resistant balance handle.", {"Blade Length": "8 Inch", "Material": "High-Carbon Steel", "Warranty": "2 Years"}),
        ("Prestige Iris 750W Mixer Grinder (3 Stainless Jars + Juicer)", "Prestige", 3499.0, "Heavy-duty 750-watt copper motor for grinding tough spices and idli batter.", {"Power": "750 Watts", "Jars": "4 Units (Wet, Dry, Chutney, Juicer)", "Speed": "3 Speeds + Incher"}),
        ("Pigeon Stainless Steel 5L Outer Lid Pressure Cooker", "Pigeon", 1299.0, "Durable virgin aluminum and steel thermal induction base pressure cooker.", {"Capacity": "5 Litres", "Base": "Induction & Gas Compatible", "Safety": "Gasket Release System"}),
        ("Philips Digital Air Fryer with Rapid Air Technology", "Philips", 6499.0, "Bake, fry, and grill with 90% less oil using patented starfish bottom airflow.", {"Capacity": "4.1 Litres", "Power": "1400 Watts", "Presets": "7 Touch Screen Programs"}),
        ("Hawkins Futura Hard Anodized 3.5L Deep Kadai", "Hawkins", 1650.0, "Non-toxic, high-conduction hard-anodized deep kadai with stay-cool rosewood handles.", {"Diameter": "28 cm", "Thickness": "3.25 mm", "Coating": "Hard Anodized"}),
        ("Wonderchef Royal Velvet Non-Stick Cookware Set (3 Pcs)", "Wonderchef", 2299.0, "Virgin aluminum cookware with PFOA-free durable marble non-stick coating.", {"Contents": "Kadhai with Lid, Fry Pan, Dosa Tawa", "Compatibility": "Gas & Induction", "Warranty": "2 Years"}),
        ("Milton Thermosteel 1000ml Vacuum Insulated Flask", "Milton", 890.0, "24-hour hot & cold temperature retention with 304 food-grade stainless steel inside.", {"Capacity": "1000 ml", "Insulation": "Double-Wall Vacuum", "Leakproof": "Yes"}),
        ("Cello Modustack Airtight Kitchen Storage Jars (Set of 6)", "Cello", 649.0, "Stackable BPA-free crystal-clear modular jars with silicone freshness seal.", {"Volume": "1000 ml each", "Material": "BPA-Free PET", "Features": "Modular Stackable"}),
        ("Bajaj Splendora 3-Litre 3000W Instant Water Geyser", "Bajaj", 2799.0, "Instant high-speed kitchen heating with copper heating element and ABS outer body.", {"Capacity": "3 Litres", "Wattage": "3000 W", "Pressure Rating": "6.5 Bar"}),
        ("Kent Ultra Storage 8L UV + UF Water Purifier", "Kent", 8499.0, "Double purification via UV and Hollow Fiber UF membrane for sweet purified municipal water.", {"Capacity": "8 Litres Storage", "Flow Rate": "60 L/hr", "Mounting": "Wall Mount"})
    ]

    kids_items = [
        ("Little Star Cotton Floral Festive Frock (Girls 2-8Y)", "LittleStar", 599.0, "Breathable pure combed cotton frock with floral motifs and satin tie-back sash.", {"Material": "100% Cotton", "Occasion": "Festive & Casual", "Closure": "Back Zipper"}),
        ("Traditional Silk Pattu Pavada Langa Set for Girls", "Shivangi", 1499.0, "Authentic South Indian festive zari border jacquard silk pavada with stitched blouse.", {"Fabric": "Art Silk with Gold Zari", "Festival": "Bathukamma & Diwali", "Lining": "Pure Cotton Inner"}),
        ("Boys Cotton Kurta Pajama with Embroidered Waistcoat", "Klap", 1199.0, "Regal 3-piece ethnic set with mandarin collar kurta and matching churidar pants.", {"Fabric": "Chanderi Cotton Blend", "Fit": "Regular Tailored", "Dry Clean": "Gentle Machine Wash"}),
        ("Kids Denim Adjustable Suspender Dungarees with T-Shirt", "Hopscotch", 849.0, "Durable stretch-washed denim dungarees paired with a soft striped cotton tee.", {"Fabric": "Cotton Denim & Knit Tee", "Straps": "Adjustable Metal Buckles", "Pockets": "4 Functional"}),
        ("Smartivity Mega STEM Robotic Crane DIY Science Kit", "Smartivity", 799.0, "Hands-on wooden mechanical engineering kit teaching hydraulics and rack-pinion gears.", {"Age Group": "6 to 12 Years", "Components": "140 Laser-Cut Wood Pieces", "Screen Free": "Yes"}),
        ("Hot Wheels 10-Car Collector Gift Pack", "Mattel", 1150.0, "Authentic die-cast 1:64 scale sports cars with detailed decos and aerodynamic wheels.", {"Material": "Die-Cast Metal & ABS", "Scale": "1:64", "Recommended Age": "3+ Years"}),
        ("Toysthree 360° Stunt Remote Control Off-Road Car", "Toysthree", 899.0, "High-speed 4WD RC vehicle with tumbling flips and vibrant LED chassis illumination.", {"Battery": "Rechargeable Li-Ion", "Range": "35 Meters", "Control": "2.4GHz Anti-Interference"}),
        ("Kids Ergonomic Orthopedic School Backpack (Waterproof)", "Safari", 1099.0, "Multi-compartment backpack with padded air-mesh spine support and reflective safety strips.", {"Capacity": "28 Litres", "Pockets": "3 Large + 2 Bottle Mesh", "Waterproof": "Rain Cover Included"})
    ]

    mens_items = [
        ("Louis Philippe Men's Formal Premium Cotton Shirt", "Louis Philippe", 1899.0, "Crafted from Egyptian Giza cotton with wrinkle-resistant finish and spread collar.", {"Fabric": "100% Giza Cotton", "Fit": "Slim Fit", "Weave": "Twill"}),
        ("Levi's 511 Slim Fit Stretch Denim Jeans", "Levi's", 2799.0, "Iconic mid-rise slim-fit jeans with built-in Levi's Flex stretch technology.", {"Fit": "Slim Through Seat & Thigh", "Leg": "Slim Leg 14.5\" Opening", "Stretch": "2% Elastane"}),
        ("Manyavar Men's Jacquard Silk Kurta & Churidar Set", "Manyavar", 3499.0, "Designer ethnic attire tailored with royal mandarin collar and subtle zari weave.", {"Fabric": "Silk Blend Jacquard", "Color": "Mustard Festive Gold", "Festival": "Diwali & Wedding"}),
        ("Allen Solly Men's Casual Cotton Chinos Trousers", "Allen Solly", 1599.0, "Flat-front cotton twill chinos offering sharp smart-casual versatility.", {"Rise": "Mid Rise", "Closure": "Button & Zip Fly", "Pockets": "4 Welt Pockets"}),
        ("Puma Smash v2 Classic Leather Sneakers", "Puma", 2499.0, "Timeless tennis-inspired silhouette with cushioned SoftFoam+ comfort sockliner.", {"Upper": "Genuine Suede & Leather", "Sole": "Durable Textured Rubber", "Arch Support": "Neutral"}),
        ("Woodland Leather Casual Bi-Fold Wallet & Reversible Belt Combo", "Woodland", 1299.0, "Handcrafted genuine full-grain leather accessories set with solid brass buckle.", {"Material": "100% Full-Grain Leather", "Card Slots": "8 Cards + Currency", "RFID Blocking": "Yes"}),
        ("Jack & Jones Graphic Cotton Regular Fit Hoodie", "Jack & Jones", 1799.0, "Warm brushed-fleece hoodie with ribbed cuffs, kangaroo pocket, and drawstring hood.", {"Fabric": "80% Cotton, 20% Polyester", "GSM": "320 Heavyweight", "Care": "Machine Wash Warm"}),
        ("Raymond Pure Linen Casual Breathable Shirt", "Raymond", 2199.0, "Pure French flax linen offering all-day coolness and sophisticated textured drape.", {"Fabric": "100% French Linen", "Sleeve": "Full with Roll-Up Tabs", "Collar": "Semi-Spread"})
    ]

    womens_items = [
        ("Kanjeevaram Soft Silk Traditional Saree with Blouse Piece", "Kanchipuram Silks", 3899.0, "Rich South Indian wedding saree woven with elaborate floral zari pallu and temple border.", {"Fabric": "Kanjeevaram Art Silk", "Length": "6.3 Meters with Blouse", "Occasion": "Bathukamma, Diwali & Weddings"}),
        ("BIBA Women's Printed Anarkali Kurta with Dupatta Set", "BIBA", 2999.0, "Flowing tiered Anarkali suit featuring gold foil hand-block prints and gotta patti accents.", {"Fabric": "100% Pure Rayon", "Neckline": "Sweetheart Neck", "Sleeve": "Three-Quarter"}),
        ("W for Woman Festive Geometric Kurti & Flared Palazzo Set", "W", 1999.0, "Contemporary ethnic coordinates crafted with breathable viscose cotton blend.", {"Set Contents": "Straight Kurti + Flared Palazzo", "Pockets": "Side Pocket in Palazzo", "Fit": "Regular Fit"}),
        ("Zaveri Pearls 24K Gold Plated Kundan Choker Necklace Set", "Zaveri Pearls", 899.0, "Traditional handcrafted Kundan necklace paired with matching jhumka earrings and maang tikka.", {"Plating": "24K Gold Micron", "Stones": "Austrian Pearls & Kundan", "Adjustable": "Dori Tie"}),
        ("Lavie Women's Monogram Structured Satchel Handbag", "Lavie", 1699.0, "Elegantly embossed faux-leather handbag with dual compartments and detachable shoulder strap.", {"Material": "Premium Vegan PU Leather", "Compartments": "2 Main + 3 Utility Pockets", "Hardware": "Gold-Tone Metal"}),
        ("FabIndia Handloom Chanderi Cotton Saree (Pastel Elegance)", "FabIndia", 3290.0, "Lightweight handspun Chanderi saree with sheer texture and shimmering zari borders.", {"Craft": "Handloom Chanderi", "Care": "Dry Clean Recommended", "Origin": "Madhya Pradesh, India"}),
        ("Vero Moda Double-Breasted Tailored Formal Blazer", "Vero Moda", 2899.0, "Sharp structured power blazer with notched lapels and flap front pockets.", {"Fit": "Tailored Regular", "Lining": "Full Polyester Satin", "Shoulder": "Padded Structure"}),
        ("Global Desi Boho Embroidered Tiered Maxi Dress", "Global Desi", 1799.0, "Free-spirited bohemian dress with tassel necktie and mirror-work bodice.", {"Fabric": "100% Viscose Georgette", "Silhouette": "Tiered Flared Maxi", "Length": "Ankle Length"})
    ]

    tech_items = [
        ("Apple MacBook Pro 16\" (M3 Max, 36GB, 1TB SSD)", "Apple", 349900.0, "The ultimate professional workstation powered by Apple Silicon M3 Max. Features Liquid Retina XDR display, 22-hour battery life.", {"Processor": "Apple M3 Max 16-Core", "RAM": "36GB Unified", "Display": "16.2\" Liquid Retina XDR"}),
        ("Dell XPS 15 OLED (Intel Core i9, 32GB, RTX 4070)", "Dell", 214990.0, "Premium ultraportable creator laptop featuring a stunning 3.5K OLED InfinityEdge touch screen.", {"CPU": "Intel i9-13900H", "GPU": "NVIDIA RTX 4070 8GB", "Storage": "1TB PCIe Gen4 SSD"}),
        ("Apple iPhone 15 Pro Max (256GB, Natural Titanium)", "Apple", 148900.0, "Forged in aerospace-grade titanium with the groundbreaking A17 Pro chip and 5x telephoto camera.", {"Chip": "A17 Pro (3nm)", "Screen": "6.7\" Super Retina XDR 120Hz", "Camera": "48MP Triple Lens"}),
        ("Samsung Galaxy S24 Ultra 5G (12GB RAM, 256GB)", "Samsung", 129999.0, "Galaxy AI powerhouse with titanium armor frame, built-in S-Pen, and 200MP Quad Tele camera.", {"Processor": "Snapdragon 8 Gen 3 for Galaxy", "Display": "6.8\" Dynamic AMOLED 2X", "Battery": "5000 mAh 45W"}),
        ("Sony WH-1000XM5 Wireless Active Noise Cancelling Headphones", "Sony", 28990.0, "Industry-leading noise cancellation powered by dual QN1 processors with 30-hour battery.", {"ANC": "Auto NC Optimizer", "Battery": "30 Hours Quick Charge", "Driver": "30mm Precision Engineered"}),
        ("OnePlus 12 5G (16GB RAM, 512GB Storage, Silky Black)", "OnePlus", 64999.0, "Flagship powerhouse powered by Snapdragon 8 Gen 3 with 4th Gen Hasselblad Camera System.", {"RAM": "16GB LPDDR5X", "Charging": "100W SUPERVOOC", "Display": "6.82\" 2K 120Hz ProXDR"}),
        ("Apple Watch Ultra 2 (GPS + Cellular, 49mm Titanium)", "Apple", 89900.0, "Most rugged Apple Watch ever built with 3000-nit display and precision dual-frequency GPS.", {"Case": "Aerospace-Grade 49mm Titanium", "Battery": "Up to 72 Hours in Low Power", "Depth": "100m Water Resistance"}),
        ("Anker 737 Power Bank (PowerCore 24K, 140W Fast Output)", "Anker", 11999.0, "Ultra-powerful 24,000mAh portable charger with smart digital display and Power Delivery 3.1.", {"Capacity": "24,000 mAh", "Max Output": "140W USB-C PD 3.1", "Ports": "2 USB-C + 1 USB-A"})
    ]

    decor_items = [
        ("Green Soul Monster Ultimate Ergonomic High-Back Chair", "Green Soul", 16490.0, "Premium executive ergonomic work-from-home chair with magnetic memory foam headrest.", {"Mechanism": "Multi-Lock Frog Tilt", "Armrests": "4D Adjustable", "Lumbar": "Built-In Dynamic Support"}),
        ("Modern Wall-Mounted Floating Hexagon Shelves (Set of 3)", "DecoCraft", 999.0, "Rustic paulownia wood and matte black metal honeycomb shelves for empty living room walls.", {"Material": "Solid Wood & Heavy Gauge Steel", "Capacity": "8 kg Per Shelf", "Installation": "Invisible Mounting Hardware Included"}),
        ("Minimalist Solid Teak Wood Round Coffee Table", "Urban Living", 4890.0, "Sleek Scandinavian silhouette with water-resistant walnut finish and tapered brass-tipped legs.", {"Dimensions": "75cm Diameter x 45cm Height", "Top Material": "Solid Engineered Teak", "Assembly": "5-Minute Tool-Free Setup"}),
        ("Warm Amber Ambient LED Dimmable Arc Floor Lamp", "Philips Hue", 3499.0, "Tall modern arched floor standing lamp with foot switch and woven fabric lampshade.", {"Height": "175 cm", "Bulb Base": "E27 Warm Glow (9W Included)", "Switch": "Stepless Foot Pedal Dimmer"}),
        ("Large Velvet Corner Sectional L-Shape Sofa (Teal Blue)", "HomeTown", 28990.0, "Plush high-density foam cushioned corner couch that fills living room corner spaces perfectly.", {"Configuration": "Left-Aligned L-Shape 5-Seater", "Upholstery": "Stain-Resistant Dutch Velvet", "Frame": "Kiln-Dried Salwood"}),
        ("Hand-Woven Geometric Persian Moroccan Floor Rug (5x7 Ft)", "CarpetZone", 2499.0, "Ultra-soft micro-chenille area carpet with anti-skid TPR rubber backing.", {"Size": "150 cm x 210 cm (5x7 Feet)", "Material": "High-Density Chenille", "Washable": "Machine Washable"}),
        ("Set of 3 Minimalist Modern Botanical Framed Wall Art", "ArtStreet", 899.0, "Museum-grade 300 GSM matte canvas prints encased in sleek black lightweight frames.", {"Dimensions": "30x40 cm Each Frame", "Paper": "300 GSM Archival Matte", "Glass": "Anti-Glare Acrylic Sheet"}),
        ("Self-Watering Indoor Potted Ficus Bonsai Plant with Ceramic Pot", "Ugaoo", 649.0, "Natural air-purifying indoor houseplant suited for study desks, counters, or empty corners.", {"Plant Type": "Ficus Ginseng Bonsai", "Pot": "White Gloss Ceramic 6-Inch", "Care": "Low Maintenance / Weekly Water"})
    ]

    category_buckets = [
        ('Kitchen & Dining', kitchen_items, 95),
        ('Kids Fashion & Toys', kids_items, 85),
        ('Mens Fashion & Wear', mens_items, 85),
        ('Womens Fashion & Ethnic', womens_items, 95),
        ('Electronics & Gadgets', tech_items, 80),
        ('Home Decor & Space Furnishings', decor_items, 60)
    ]

    total_idx = 0
    for cat_name, archetypes, target_count in category_buckets:
        cat_images = images.get(cat_name, images['Electronics & Gadgets'])
        for i in range(target_count):
            total_idx += 1
            base_archetype = archetypes[i % len(archetypes)]
            img = cat_images[i % len(cat_images)]
            
            # Variant generation for natural 500 catalog diversity
            var_num = (i // len(archetypes)) + 1
            if var_num == 1:
                name = base_archetype[0]
                brand = base_archetype[1]
                price = base_archetype[2]
                desc = base_archetype[3]
                specs = base_archetype[4]
            else:
                suffixes = ["Pro Edition", "Festive Edition", "Classic Series", "Prime Series", "Eco Series", "Deluxe Pack", "Ultra Collection", "Smart Edition", "Signature Edition", "Gold Edition"]
                suffix = suffixes[(var_num - 2) % len(suffixes)]
                name = f"{base_archetype[0]} ({suffix} v{var_num})"
                brand = base_archetype[1]
                # Modulate price slightly (+/- 5% to 15%)
                multiplier = 1.0 + (((i * 7) % 25) - 10) / 100.0
                price = round(max(150.0, base_archetype[2] * multiplier), -1)
                if base_archetype[2] <= 250:
                    price = float(base_archetype[2]) # Keep the 200 product consistent!
                desc = f"{base_archetype[3]} Upgraded {suffix} designed for enhanced durability and performance."
                specs = dict(base_archetype[4])
                specs["Model Variant"] = f"{suffix} - {2026 + (i % 2)}"

            products.append({
                'name': name,
                'brand': brand,
                'category': cat_name,
                'description': desc,
                'image_url': img,
                'base_price': float(price),
                'rating': round(4.0 + ((i * 13) % 10) / 10.0, 1),
                'review_count': 15 + ((i * 37) % 350),
                'stock': 12 + ((i * 19) % 85),
                'specs': specs
            })

    # Ensure product with exact ₹200.00 is at index 0 or near top for effortless demonstration!
    products[0]['base_price'] = 200.0
    products[0]['name'] = "Kitchen Pro Multi-Blade Peeler & Slicer Set"
    
    return products

def seed_database(force=True):
    with app.app_context():
        print("Rebuilding database with 500 Products, Multi-Seller Risk Transparency, Coupons & College Team...")
        db.drop_all()
        db.create_all()

        # 1. ACADEMIC PROJECT TEAM & USERS
        # Guide: Smt. P.V. Vaishnavi (Password: vaishnavi, Roll: smt.p.v.vaishnavi)
        guide_user = User(
            name="Smt. P.V. Vaishnavi",
            email="vaishnavi@ucetw.ac.in",
            role="guide",
            roll_number="smt.p.v.vaishnavi",
            designation="Project Guide",
            phone="+91 94401 23456",
            address="UCETW Faculty Quarters, Kakatiya University, Warangal, Telangana - 506009"
        )
        guide_user.set_password("vaishnavi")
        db.session.add(guide_user)

        # Team 10 AIML Members
        team_members_data = [
            ("V. Poojarani", "23568T3055@ucetw.ac.in", "23568T3055", "poojarani", "Team 10 AIML Member"),
            ("P. Anusha", "245683064L@ucetw.ac.in", "245683064L", "anusha", "Team 10 AIML Member"),
            ("G. Deepika", "23568T3018@ucetw.ac.in", "23568T3018", "deepika", "Team 10 AIML Member"),
            ("D. Pavani Alekhya", "23568T3012@ucetw.ac.in", "23568T3012", "pavani", "Team 10 AIML Member"),
            ("K. Prathyusha", "23568T3029@ucetw.ac.in", "23568T3029", "prathyusha", "Team 10 AIML Member"),
        ]

        created_team_users = []
        for name, email, roll, pwd, desig in team_members_data:
            u = User(
                name=name,
                email=email,
                role="user",
                roll_number=roll,
                designation=desig,
                phone="+91 98480 12345",
                address="University College of Engineering & Technology for Women, Kakatiya University, Warangal"
            )
            u.set_password(pwd)
            db.session.add(u)
            created_team_users.append(u)

        # Demo regular shopper & Master Admin
        demo_user = User(
            name="Pooja Sharma",
            email="demo@bargainkart.com",
            role="user",
            roll_number="DEMO-2026",
            designation="Demo Shopper",
            phone="+91 98451 23456",
            address="42 Prestige Tech Park, Marathahalli, Bengaluru, Karnataka - 560103"
        )
        demo_user.set_password("Demo@123")
        db.session.add(demo_user)

        admin_user = User(
            name="System Administrator",
            email="admin@bargainkart.com",
            role="admin",
            roll_number="ADMIN-001",
            designation="Master Administrator",
            phone="+91 99000 11223",
            address="BargainKart E-Commerce HQ, 100 Ft Road, Indiranagar, Bengaluru - 560038"
        )
        admin_user.set_password("Admin@123")
        db.session.add(admin_user)

        db.session.flush()
        print(f"[*] Seeded Guide (Smt. P.V. Vaishnavi) and {len(created_team_users)} Team 10 AIML Members.")

        # 2. FESTIVAL COUPONS (Bathukamma & Diwali Offers)
        coupons = [
            Coupon(
                code="BATHUKAMMA20",
                title="Bathukamma Floral Festival Special - ₹20 Flat OFF",
                discount_type="FLAT",
                discount_value=20.0,
                festival_tag="BATHUKAMMA",
                description="Special Telangana Floral Festival Offer! Flat ₹20 discount on all products. E.g. ₹200 item comes down to ₹180!"
            ),
            Coupon(
                code="DIWALI10",
                title="Diwali Festival of Lights - 10% Instant Concession",
                discount_type="PERCENT",
                discount_value=10.0,
                festival_tag="DIWALI",
                description="Celebrate Diwali with 10% discount on entire cart! E.g. ₹200 product discount is ₹20 -> final price ₹180!"
            ),
            Coupon(
                code="BATHUKAMMA-SPECIAL",
                title="Bathukamma Grand Celebration - Flat ₹20 Off",
                discount_type="FLAT",
                discount_value=20.0,
                festival_tag="BATHUKAMMA",
                description="Flat ₹20 direct festival concession with instant checkout!"
            ),
            Coupon(
                code="DIWALI-DHAMAKA",
                title="Diwali Dhamaka Flash Coupon - 15% Off",
                discount_type="PERCENT",
                discount_value=15.0,
                festival_tag="DIWALI",
                description="Special festive 15% discount for gaming participants!"
            ),
            Coupon(
                code="FESTIVE15",
                title="Telangana Festive Season 15% Super Saver",
                discount_type="PERCENT",
                discount_value=15.0,
                festival_tag="FESTIVAL",
                description="Save 15% across Kitchen, Ethnic Fashion and Decor!"
            ),
            Coupon(
                code="HAGGLE10",
                title="AI Haggle Mini-Game Victory Voucher - 10% Off",
                discount_type="PERCENT",
                discount_value=10.0,
                festival_tag="GAME",
                description="Awarded for winning the Interactive Bargain Mini-Game!"
            ),
            Coupon(
                code="SANKRANTI15",
                title="Sankranti Harvest Dhamaka - 15% Off",
                discount_type="PERCENT",
                discount_value=15.0,
                festival_tag="SANKRANTI",
                description="15% festive harvest savings on traditional fashion and home items!"
            ),
            Coupon(
                code="DUSSEHRA20",
                title="Dussehra Vijayadashami Deals - 20% Off",
                discount_type="PERCENT",
                discount_value=20.0,
                festival_tag="DUSSEHRA",
                description="20% victory discount on premium products and kitchen essentials!"
            ),
            Coupon(
                code="UGADI12",
                title="Ugadi Telugu New Year Celebration - 12% Off",
                discount_type="PERCENT",
                discount_value=12.0,
                festival_tag="UGADI",
                description="12% Telugu New Year festive concession on all catalog items!"
            ),
            Coupon(
                code="SUMMER25",
                title="Beat the Heat Summer Mega Sale - 25% Off",
                discount_type="PERCENT",
                discount_value=25.0,
                festival_tag="SUMMER",
                description="25% summer discount on cool home decor and casual apparel!"
            ),
            Coupon(
                code="BIGBILLION30",
                title="Big Billion Super Deals Day - 30% Off",
                discount_type="PERCENT",
                discount_value=30.0,
                festival_tag="BIGBILLION",
                description="30% massive shopping carnival discount on selected items!"
            ),
            Coupon(
                code="WEEKEND10",
                title="Weekend Flash Savings Voucher - 10% Off",
                discount_type="PERCENT",
                discount_value=10.0,
                festival_tag="WEEKEND",
                description="10% flash discount for weekend shopping sprees!"
            ),
            Coupon(
                code="GAME10",
                title="Game Zone Victor Coupon - 10% Off",
                discount_type="PERCENT",
                discount_value=10.0,
                festival_tag="GAME",
                description="10% discount for gaming champions! Product price: Rs.300 -> Final: Rs.270!"
            ),
            Coupon(
                code="SPIN10",
                title="Spin the Wheel Lucky Coupon - 10% Off",
                discount_type="PERCENT",
                discount_value=10.0,
                festival_tag="GAME",
                description="Won on Spin the Wheel! 10% off your next purchase."
            ),
            Coupon(
                code="QUIZ15",
                title="Daily Shopping Quiz Master - 15% Off",
                discount_type="PERCENT",
                discount_value=15.0,
                festival_tag="GAME",
                description="Scored 3/3 on Shopping Quiz! 15% discount unlocked."
            ),
            Coupon(
                code="HUNTER20",
                title="Deal Hunter Arcade Champion - 20% Off",
                discount_type="PERCENT",
                discount_value=20.0,
                festival_tag="GAME",
                description="Caught 50+ deal points in arcade hunter! 20% off."
            ),
            Coupon(
                code="SCRATCH25",
                title="Golden Scratch Card Surprise - 25% Off",
                discount_type="PERCENT",
                discount_value=25.0,
                festival_tag="GAME",
                description="Revealed golden scratch discount! 25% off."
            ),
            Coupon(
                code="CHALLENGE30",
                title="Shopping Challenge VIP Pass - 30% Off",
                discount_type="PERCENT",
                discount_value=30.0,
                festival_tag="GAME",
                description="Completed all shopping milestones! 30% VIP discount."
            )
        ]
        for c in coupons:
            db.session.add(c)
        db.session.flush()
        print(f"[*] Seeded {len(coupons)} Festival Coupons including BATHUKAMMA20 and DIWALI10.")

        # 3. SELLERS (Diverse Risk Categories)
        sellers_data = [
            Seller(name="UCETW Verified Official Retail", email="ucetw.official@bargainkart.in", rating=4.95, verified=True, account_age_days=1500, dispute_rate=0.005, total_sales=24000, risk_status="SAFE", location="Warangal, Telangana"),
            Seller(name="Apple India Authorized Retail", email="apple.retail@bargainkart.in", rating=4.9, verified=True, account_age_days=1420, dispute_rate=0.008, total_sales=18500, risk_status="SAFE", location="Mumbai, Maharashtra"),
            Seller(name="KitchenKing Prime Direct", email="kitchenking@bargainkart.in", rating=4.85, verified=True, account_age_days=1100, dispute_rate=0.012, total_sales=14200, risk_status="SAFE", location="Hyderabad, Telangana"),
            Seller(name="TechDirect Electronics Ltd", email="techdirect@bargainkart.in", rating=4.8, verified=True, account_age_days=980, dispute_rate=0.015, total_sales=12400, risk_status="SAFE", location="Bengaluru, Karnataka"),
            Seller(name="FabEthnic Traditional Weaves", email="fabethnic@bargainkart.in", rating=4.75, verified=True, account_age_days=850, dispute_rate=0.018, total_sales=9200, risk_status="SAFE", location="Warangal, Telangana"),
            Seller(name="KidsParadise Toys & Apparel", email="kidsparadise@bargainkart.in", rating=4.65, verified=True, account_age_days=620, dispute_rate=0.022, total_sales=6800, risk_status="SAFE", location="Chennai, Tamil Nadu"),
            Seller(name="HomeElegance Space Decor", email="homeelegance@bargainkart.in", rating=4.7, verified=True, account_age_days=710, dispute_rate=0.019, total_sales=7400, risk_status="SAFE", location="Bengaluru, Karnataka"),
            # Moderate Risk Sellers (Marketplaces)
            Seller(name="BargainBazaar Surat Wholesalers", email="bazaar@bargainsurat.in", rating=4.1, verified=False, account_age_days=310, dispute_rate=0.048, total_sales=2800, risk_status="MODERATE_RISK", location="Surat, Gujarat"),
            Seller(name="DiscountHub Multi-Store", email="sales@discounthub.co.in", rating=3.9, verified=False, account_age_days=240, dispute_rate=0.055, total_sales=1900, risk_status="MODERATE_RISK", location="New Delhi, Delhi"),
            Seller(name="FastTrack Imports Hub", email="fasttrack@imports.in", rating=3.8, verified=False, account_age_days=180, dispute_rate=0.062, total_sales=1400, risk_status="MODERATE_RISK", location="Kolkata, West Bengal"),
            # High Risk Sellers
            Seller(name="SuperClearance Outlet 2026", email="contact@superclearance2026.xyz", rating=2.8, verified=False, account_age_days=25, dispute_rate=0.14, total_sales=180, risk_status="HIGH_RISK", location="Jaipur, Rajasthan"),
            Seller(name="NoReturn DeepDiscount Warehouse", email="deals@noreturnwarehouse.cc", rating=2.6, verified=False, account_age_days=18, dispute_rate=0.18, total_sales=110, risk_status="HIGH_RISK", location="Nagpur, Maharashtra")
        ]
        for s in sellers_data:
            db.session.add(s)
        db.session.flush()

        safe_sellers = [s for s in sellers_data if s.risk_status == "SAFE"]
        mod_sellers = [s for s in sellers_data if s.risk_status == "MODERATE_RISK"]
        high_sellers = [s for s in sellers_data if s.risk_status == "HIGH_RISK"]

        # 4. 500 PRODUCTS & MULTI-SELLER LISTINGS
        raw_products = build_500_products()
        created_products = []
        today = date.today()

        for idx, p_info in enumerate(raw_products):
            # Select primary seller based on category
            primary_seller = safe_sellers[idx % len(safe_sellers)]
            
            p = Product(
                name=p_info['name'],
                brand=p_info['brand'],
                category=p_info['category'],
                description=p_info['description'],
                image_url=p_info['image_url'],
                base_price=p_info['base_price'],
                seller_id=primary_seller.id,
                rating=p_info['rating'],
                review_count=p_info['review_count'],
                stock=p_info['stock'],
                specs_json=json.dumps(p_info['specs'])
            )
            db.session.add(p)
            db.session.flush()
            created_products.append(p)

            # Create 3 Multi-Seller Listings with Risk Transparency:
            # 1. Official/Prime Safe Seller
            sp_safe = ProductSellerPrice(
                product_id=p.id,
                seller_id=primary_seller.id,
                seller_name=primary_seller.name,
                platform_name="BargainKart Direct (Prime Verified)",
                price=p.base_price,
                is_current_seller=True,
                in_stock=True,
                delivery_days=2,
                seller_rating=primary_seller.rating,
                risk_status="SAFE",
                trust_score=98.5,
                return_policy="7-Day Free Replacement & Brand Warranty"
            )
            db.session.add(sp_safe)

            # 2. Moderate Risk Marketplace Seller (Offers slight discount ~4% to 8%)
            mod_seller = mod_sellers[idx % len(mod_sellers)]
            discount_mod = round(p.base_price * 0.05, 0)
            if p.base_price == 200.0:
                mod_price = 190.0
            else:
                mod_price = max(100.0, p.base_price - discount_mod)
                
            sp_mod = ProductSellerPrice(
                product_id=p.id,
                seller_id=mod_seller.id,
                seller_name=mod_seller.name,
                platform_name="Surat Marketplace Direct",
                price=mod_price,
                is_current_seller=False,
                in_stock=True,
                delivery_days=4,
                seller_rating=mod_seller.rating,
                risk_status="MODERATE_RISK",
                trust_score=78.0,
                return_policy="5-Day Return Window (Buyer Pays Shipping)"
            )
            db.session.add(sp_mod)

            # 3. High Risk / Clearance Seller (Cheapest ~10% to 15% off, but warning risk!)
            high_seller = high_sellers[idx % len(high_sellers)]
            discount_high = round(p.base_price * 0.12, 0)
            if p.base_price == 200.0:
                high_price = 175.0
            else:
                high_price = max(90.0, p.base_price - discount_high)

            sp_high = ProductSellerPrice(
                product_id=p.id,
                seller_id=high_seller.id,
                seller_name=high_seller.name,
                platform_name="Clearance Warehouse (Unverified)",
                price=high_price,
                is_current_seller=False,
                in_stock=True,
                delivery_days=7,
                seller_rating=high_seller.rating,
                risk_status="HIGH_RISK",
                trust_score=42.0,
                return_policy="As-Is / Final Sale (No Returns Accepted)"
            )
            db.session.add(sp_high)

            # Add Price History (for price trends chart)
            for d in [30, 20, 10, 0]:
                hist_date = today - timedelta(days=d)
                delta_price = round(p.base_price * (1.0 + (((idx + d) % 7) - 3) * 0.01), 0)
                ph = PriceHistory(
                    product_id=p.id,
                    recorded_date=hist_date,
                    price=delta_price,
                    market_average=round(p.base_price * 1.02, 0)
                )
                db.session.add(ph)

        print(f"[*] Successfully seeded {len(created_products)} Products with 3 Multi-Seller Listings each ({len(created_products)*3} total seller quotes)!")

        # 5. SAMPLE ORDERS & TRACKING TIMELINE
        # Seed an order for demo user with item at ₹180 (negotiated with Bathukamma coupon)
        p200 = created_products[0] # Kitchen Pro Multi-Blade Peeler & Slicer Set (base_price = 200)
        order_200 = Order(
            order_number="BK-ORD-TELANGANA2026",
            user_id=demo_user.id,
            total_amount=180.0,
            original_amount=200.0,
            total_savings=20.0,
            status="Confirmed",
            payment_method="UPI / GPay (Simulated) - Bathukamma Festive Deal",
            shipping_address="42 Prestige Tech Park, Outer Ring Road, Marathahalli, Bengaluru - 560103",
            tracking_number="BK-TRK-88291044"
        )
        db.session.add(order_200)
        db.session.flush()

        oi_200 = OrderItem(
            order_id=order_200.id,
            product_id=p200.id,
            product_name=f"{p200.name} (Coupons: BATHUKAMMA20 Applied)",
            quantity=1,
            unit_price=180.0,
            original_price=200.0,
            savings=20.0
        )
        db.session.add(oi_200)

        # 7-Step Tracking Timeline for the ₹180 Festive Order
        now = datetime.now(timezone.utc)
        timeline_steps = [
            ("Order Placed", "Festive order verified with coupon BATHUKAMMA20 (-₹20 savings). Total: ₹180.", "Warangal / Hyderabad Central Hub", now - timedelta(hours=3), True),
            ("Payment Confirmed", "Simulated UPI authorization completed at ₹180.", "Payment Processing Gateway", now - timedelta(hours=2, minutes=50), True),
            ("Quality Verified", "AI Authenticity check passed with 98% confidence score.", "Inspection Center", now - timedelta(hours=2, minutes=30), True),
            ("Packed & Sealed", "Box sealed with festive tamper-evident holographic seal.", "Central Warehouse", now - timedelta(hours=1, minutes=45), True),
            ("Shipped", "Package handed over to BargainExpress Priority Logistics.", "Telangana Logistics Hub", now - timedelta(minutes=45), True),
            ("Out for Delivery", "Courier executive assigned for contactless doorstep drop-off.", "Local Delivery Node", now + timedelta(hours=4), False),
            ("Delivered", "Shipment delivered and digital signature recorded.", "Customer Destination", now + timedelta(hours=8), False)
        ]
        for title, desc, loc, ts, done in timeline_steps:
            te = TrackingEvent(
                order_id=order_200.id,
                status_title=title,
                description=desc,
                location=loc,
                timestamp=ts,
                completed=done
            )
            db.session.add(te)

        # 6. SAMPLE NEGOTIATION WITH BATHUKAMMA COUPON
        sample_neg = Negotiation(
            user_id=demo_user.id,
            product_id=p200.id,
            initial_price=200.0,
            user_offer=180.0,
            ai_counter_offer=180.0,
            final_price=180.0,
            status="SETTLED",
            rounds=1,
            savings=20.0,
            discount_percent=10.0,
            transcript_json=json.dumps([
                {
                    'round': 1,
                    'user_offer': 180.0,
                    'ai_counter_offer': 180.0,
                    'status': 'ACCEPTED',
                    'message': 'Bathukamma Festival coupon BATHUKAMMA20 activated! Price locked at ₹180 (Original: ₹200).',
                    'strategy': 'FESTIVAL_SPECIAL',
                    'timestamp': '12:00:00'
                }
            ])
        )
        db.session.add(sample_neg)

        # 7. SAMPLE REVIEWS & AUTHENTICITY CHECKS
        sample_reviews = [
            ("Smt. P.V. Vaishnavi", 5, "Outstanding Quality & Verified Authenticity", "Tested this kitchen tool thoroughly. Genuine 304 steel material and razor-sharp cutting edge."),
            ("V. Poojarani", 5, "Amazing Bargain with Festival Coupon!", "Got this product for ₹180 with BATHUKAMMA20 code. Fast 2-day delivery and genuine packaging."),
            ("P. Anusha", 5, "Price Transparency Feature is Superb", "Compared different sellers before buying. Verified safe seller delivered genuine item."),
            ("G. Deepika", 5, "Clean finish and durable", "The AI recommended this for our kitchen and it works great. Worth every rupee."),
            ("D. Pavani Alekhya", 5, "Verified Safe Seller", "Zero risk buying from verified seller with transparent risk badges."),
            ("K. Prathyusha", 5, "Festive Game is Fun", "Spun the festival wheel and won BATHUKAMMA20 coupon, got the ₹200 product for ₹180!")
        ]
        for name, rating, title, comment in sample_reviews:
            r = Review(
                product_id=p200.id,
                user_name=name,
                rating=rating,
                title=title,
                comment=comment,
                verified_purchase=True,
                sentiment_score=0.95
            )
            db.session.add(r)

        # Pre-seed authenticity check
        ac = AuthenticityCheck(
            user_id=demo_user.id,
            product_id=p200.id,
            confidence_score=97.5,
            risk_level="LOW",
            seller_score=98.0,
            price_anomaly_score=96.0,
            spec_consistency_score=98.0,
            review_nlp_score=95.0,
            image_integrity_score=99.0,
            verdict="Authentic & Certified Safe",
            explanation=f"AI multi-factor assessment confirms {p200.name} has optimal seller credentials and authentic material certification.",
            evidence_json=json.dumps({
                'seller_consistency': {'score': 98.0, 'status': 'Optimal'},
                'price_anomaly': {'score': 96.0, 'status': 'Optimal'},
                'spec_consistency': {'score': 98.0, 'status': 'Optimal'},
                'review_signals': {'score': 95.0, 'status': 'Optimal'},
                'image_similarity': {'score': 99.0, 'status': 'Optimal'}
            })
        )
        db.session.add(ac)

        db.session.commit()
        print("===============================================================================")
        print("DATABASE SUCCESSFULLY SEEDED WITH:")
        print(f" - {len(created_products)} Products across 6 categories")
        print(f" - {len(created_products) * 3} Seller quotes with Safe / Moderate / High Risk badges")
        print(" - Guide: Smt. P.V. Vaishnavi (Password: vaishnavi, Roll/User: smt.p.v.vaishnavi)")
        print(" - Team 10 AIML: V. Poojarani, P. Anusha, G. Deepika, D. Pavani Alekhya, K. Prathyusha")
        print(" - Festival Coupons: BATHUKAMMA20 (Rs.200 -> Rs.180), DIWALI10, etc.")
        print(" - Order #BK-ORD-TELANGANA2026 placed at Rs.180 with live tracking")
        print("===============================================================================")

if __name__ == '__main__':
    seed_database()
