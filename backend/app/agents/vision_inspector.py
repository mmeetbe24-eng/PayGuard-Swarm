import json
import re
import io
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel
from backend.app.config import settings

logger = logging.getLogger(__name__)

class VisionProductResult(BaseModel):
    is_valid_product: bool
    product_title: str
    category: str
    color_or_style: str
    estimated_price_usd: float
    search_directive: str
    confidence_notes: str

class MultimodalVisionInspector:
    """
    Multimodal Visual Product Inspector powered by 100% pure online Google Gemini Cloud Vision.
    Performs authentic multimodal semantic visual understanding without hardcoded chromatic heuristics,
    color guesswork, or aspect-ratio assumptions.
    """

    @classmethod
    def inspect_product_image(cls, image_bytes: bytes, mime_type: str = "image/jpeg", filename: str = "", *args, **kwargs) -> VisionProductResult:
        """
        Inspect product image using 100% live Google Gemini Cloud Multimodal Vision.
        Zero hardcoded guesses: if cloud vision is unauthenticated or unreachable,
        honestly reports unclassified reference without hallucinating products.
        """
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return VisionProductResult(
                is_valid_product=False,
                product_title="Uploaded Product Reference",
                category="Unclassified",
                color_or_style="Image Reference",
                estimated_price_usd=kwargs.get("active_budget", 50.0),
                search_directive="Find and buy product using PayPal",
                confidence_notes="Gemini API key not configured. Cloud visual detection offline."
            )

        prompt = """
        You are an expert e-commerce catalog visual inspector.
        Inspect the uploaded product image with extreme precision.
        
        Return ONLY a valid JSON object with the following fields:
        {
          "is_valid_product": true,
          "product_title": "<Precise specific product title, e.g. 'Double-Door Refrigerator' or 'Smart LED Television' or 'Apple MacBook Pro Laptop' or 'Sony WH-1000XM5 Headphones'>",
          "category": "<e.g. Large Appliances, Consumer Electronics, Computers & Tech, Food & Grocery, Footwear, Fashion & Apparel>",
          "color_or_style": "<Specific visual color, texture, style or material observed in the image>",
          "estimated_price_inr": <Realistic estimated retail market price in Indian Rupees (INR ₹), e.g. 50, 799, 6999, 24990, 40000>,
          "search_directive": "<Crisp e-commerce shopping directive under appropriate budget, e.g. 'Find and buy Double-Door Refrigerator under ₹28000 using PayPal'>",
          "confidence_notes": "<Brief 1-sentence description of the visual features observed in the photo>"
        }
        
        CRITICAL RULES:
        - Analyze the ACTUAL image content dynamically.
        - All pricing MUST be in Indian Rupees (₹ / INR).
        - If the image is not a recognizable retail product, set "is_valid_product": false.
        - Output strictly valid JSON without markdown fences.
        """

        # 1. Try google-genai SDK
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

            candidate_models = [
                settings.DEFAULT_GEMINI_MODEL,
                "gemini-3.5-flash",
                "gemini-flash-latest",
                "gemini-3.1-flash-lite",
                "gemini-3.8-flash"
            ]
            # Deduplicate while preserving order
            seen = set()
            models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[prompt, image_part]
                    )
                    if response and response.text:
                        text = response.text.strip()
                        json_match = re.search(r'\{.*\}', text, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group(0))
                            title = str(data.get("product_title", "")).strip().replace('\\', '')
                            est_p = float(data.get("estimated_price_inr", data.get("estimated_price_usd", 1000.0)))
                            if title and len(title) > 2:
                                return VisionProductResult(
                                    is_valid_product=bool(data.get("is_valid_product", True)),
                                    product_title=title,
                                    category=str(data.get("category", "General")),
                                    color_or_style=str(data.get("color_or_style", "Standard")),
                                    estimated_price_usd=max(10.0, est_p),
                                    search_directive=str(data.get("search_directive", f"Find and buy {title} under ₹{max(50.0, round(est_p, 2))} using PayPal")),
                                    confidence_notes=str(data.get("confidence_notes", f"Live cloud vision match identified by Google Gemini ({model_name})."))
                                )
                except Exception as inner_e:
                    logger.debug(f"Gemini SDK attempt with {model_name} failed: {inner_e}")
                    continue
        except Exception as sdk_e:
            logger.debug(f"Gemini GenAI SDK invocation failed: {sdk_e}")

        # 2. Try Direct HTTP REST fallback
        try:
            import base64, requests
            b64_img = base64.b64encode(image_bytes).decode("utf-8")
            rest_payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inlineData": {"mimeType": mime_type, "data": b64_img}}
                    ]
                }]
            }
            key_str = str(api_key).strip()
            headers = {"Content-Type": "application/json"}
            for m_id in ["gemini-3.5-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_id}:generateContent?key={key_str}"
                try:
                    r = requests.post(url, json=rest_payload, headers=headers, timeout=8.0)
                    if r.status_code == 200:
                        candidates = r.json().get("candidates", [])
                        if candidates:
                            raw_txt = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            m = re.search(r'\{.*\}', raw_txt, re.DOTALL)
                            if m:
                                data = json.loads(m.group(0))
                                title = str(data.get("product_title", "")).strip().replace('\\', '')
                                est_p = float(data.get("estimated_price_inr", data.get("estimated_price_usd", 1000.0)))
                                if title and len(title) > 2:
                                    return VisionProductResult(
                                        is_valid_product=bool(data.get("is_valid_product", True)),
                                        product_title=title,
                                        category=str(data.get("category", "General")),
                                        color_or_style=str(data.get("color_or_style", "Standard")),
                                        estimated_price_usd=max(10.0, est_p),
                                        search_directive=str(data.get("search_directive", f"Find and buy {title} under ₹{max(50.0, round(est_p, 2))} using PayPal")),
                                        confidence_notes=str(data.get("confidence_notes", f"Live cloud vision match identified by Google Gemini REST ({m_id})."))
                                    )
                except Exception as rest_e:
                    logger.debug(f"REST attempt with {m_id} failed: {rest_e}")
                    continue
        except Exception as e:
            logger.warning(f"Gemini REST direct invocation error: {e}")

        # Pure zero-guess fallback: honestly return unclassified reference
        return VisionProductResult(
            is_valid_product=False,
            product_title="Uploaded Product Reference",
            category="Unclassified",
            color_or_style="Image Reference",
            estimated_price_usd=kwargs.get("active_budget", 50.0),
            search_directive="Find and buy product using PayPal",
            confidence_notes="Cloud multimodal vision unreachable. No heuristic guesswork performed."
        )

vision_inspector = MultimodalVisionInspector()
