from typing import Dict, Any

class OverpricedStoreC:
    """
    Store C: Premium Retailer ('Prime Athletics').
    Legitimate merchant, but price ($110.00) exceeds user's $90 ceiling.
    Used by Agent 1 to demonstrate deal comparison and budget filtering.
    """
    MERCHANT_ID = "PRIME_ATHLETICS_OFFICIAL_108"
    MERCHANT_NAME = "Prime Athletics Premium Goods"

    CATALOG = {
        "nike-air": {
            "sku": "NIKE-AIR-PEGASUS-PREMIUM",
            "name": "Nike Air Zoom Pegasus 40 (Retail MSRP)",
            "category": "Running Shoes",
            "price": 110.00,
            "currency": "USD",
            "stock": 25,
            "shipping_fee": 9.99,
            "description": "Full retail price edition without promotional discount.",
            "html_page": """
            <html>
                <head><title>Prime Athletics - Nike Air Zoom</title></head>
                <body>
                    <div class="product-page">
                        <h1>Nike Air Zoom Pegasus 40</h1>
                        <p class="price">$110.00</p>
                        <p class="shipping">Shipping: $9.99</p>
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
