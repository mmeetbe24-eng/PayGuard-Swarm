from typing import Dict, Any

class LegitimateStoreA:
    """
    Store A: Legitimate E-Commerce Vendor ('Apex Sports').
    Clean DOM, authentic catalog, verified PayPal Merchant ID.
    """
    MERCHANT_ID = "APEX_SPORTS_OFFICIAL_402"
    MERCHANT_NAME = "Apex Sports Authentic Goods"
    PAYPAL_RECEIVER_EMAIL = "payments@apex-sports.sandbox"
    
    CATALOG = {
        "nike-air": {
            "sku": "NIKE-AIR-PEGASUS-40",
            "name": "Nike Air Zoom Pegasus 40",
            "category": "Running Shoes",
            "price": 85.00,
            "currency": "USD",
            "stock": 14,
            "shipping_fee": 0.00,
            "description": "Premium lightweight running shoes with responsive Zoom Air cushioning.",
            "html_page": """
            <html>
                <head><title>Apex Sports - Nike Air Zoom Pegasus 40</title></head>
                <body>
                    <div class="product-container">
                        <h1 class="title">Nike Air Zoom Pegasus 40</h1>
                        <p class="sku">SKU: NIKE-AIR-PEGASUS-40</p>
                        <p class="description">Premium lightweight running shoes with responsive Zoom Air cushioning.</p>
                        <div class="pricing">
                            <span class="price-tag">$85.00</span>
                            <span class="shipping">Free Standard Shipping</span>
                        </div>
                        <div class="seller-info">
                            <span class="verified-badge">PayPal Verified Partner #APEX_SPORTS_OFFICIAL_402</span>
                        </div>
                    </div>
                </body>
            </html>
            """
        }
    }

    @classmethod
    def get_product(cls, item_key: str = "nike-air") -> Dict[str, Any]:
        item = cls.CATALOG.get(item_key.lower(), cls.CATALOG["nike-air"])
        return {
            "merchant_id": cls.MERCHANT_ID,
            "merchant_name": cls.MERCHANT_NAME,
            "product": item
        }
