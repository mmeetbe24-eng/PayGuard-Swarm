import re
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class AnomalyFlag(BaseModel):
    category: str
    severity: str  # LOW, MEDIUM, CRITICAL
    description: str
    evidence: str

class DOMSanitizationReport(BaseModel):
    is_safe: bool
    risk_score: float  # 0.0 (Clean) to 1.0 (Critical Threat)
    sanitized_text: str
    flags: List[AnomalyFlag] = Field(default_factory=list)
    raw_length: int
    sanitized_length: int

class DOMSanitizer:
    """
    Adversarial DOM & Payload Inspector.
    Detects zero-width steganography, CSS-hidden prompt injections, 
    and hostile overriding directives embedded in merchant pages.
    """
    
    # Zero-width and invisible unicode characters used for steganographic prompt injection
    ZERO_WIDTH_PATTERN = re.compile(r'[\u200B-\u200D\uFEFF\u200E\u200F\u202A-\u202E]')
    
    # CSS hidden injection heuristics
    CSS_HIDDEN_PATTERNS = [
        (re.compile(r'style=[\'"][^\'"]*display\s*:\s*none[^\'"]*[\'"]', re.I), "Hidden display (display:none)"),
        (re.compile(r'style=[\'"][^\'"]*visibility\s*:\s*hidden[^\'"]*[\'"]', re.I), "Hidden visibility (visibility:hidden)"),
        (re.compile(r'style=[\'"][^\'"]*opacity\s*:\s*0[^\'"]*[\'"]', re.I), "Zero opacity element"),
        (re.compile(r'style=[\'"][^\'"]*font-size\s*:\s*(?:0|1)px[^\'"]*[\'"]', re.I), "Microscopic font size (0-1px)"),
        (re.compile(r'style=[\'"][^\'"]*(?:color\s*:\s*(?:white|#fff|#ffffff);[^\'"]*background\s*:\s*(?:white|#fff|#ffffff)|color\s*:\s*transparent)[^\'"]*[\'"]', re.I), "Camouflaged color font trap"),
        (re.compile(r'style=[\'"][^\'"]*text-indent\s*:\s*-[0-9]{3,5}px[^\'"]*[\'"]', re.I), "Off-screen negative indent"),
    ]
    
    # Semantic Prompt Injection keywords targeting commerce agents
    PROMPT_INJECTION_KEYWORDS = [
        (r'system\s+override', "Explicit System Override Directive", "CRITICAL"),
        (r'disregard\s+(?:all\s+)?previous\s+instructions?', "Instruction Wiping Attempt", "CRITICAL"),
        (r'ignore\s+(?:budget|ceiling|price|instructions?)', "Budget Boundary Bypass Attempt", "CRITICAL"),
        (r'charge\s+[₹\$]?[0-9]+', "Unsanctioned Price Inflation Command", "HIGH"),
        (r'new\s+system\s+prompt', "System Prompt Hijacking", "CRITICAL"),
        (r'hidden\s+(?:fee|surcharge|insurance)', "Stealth Surcharge Disclosure", "MEDIUM"),
        (r'approve\s+(?:order|payment)\s+unconditionally', "Autonomous Bypass Trigger", "CRITICAL")
    ]

    @classmethod
    def inspect_and_sanitize(cls, raw_html_or_text: str) -> DOMSanitizationReport:
        flags: List[AnomalyFlag] = []
        raw_len = len(raw_html_or_text)
        risk_score = 0.0

        # 1. Detect zero-width characters
        zero_width_matches = cls.ZERO_WIDTH_PATTERN.findall(raw_html_or_text)
        if zero_width_matches:
            flags.append(AnomalyFlag(
                category="STEGANOGRAPHY",
                severity="CRITICAL",
                description=f"Detected {len(zero_width_matches)} invisible zero-width unicode characters.",
                evidence=f"{len(zero_width_matches)} chars stripped"
            ))
            risk_score += 0.4

        # Strip zero-width characters
        cleaned = cls.ZERO_WIDTH_PATTERN.sub('', raw_html_or_text)

        # 2. Check for executable code / script injection
        script_match = re.search(r'<script\b[^>]*>([\s\S]*?)<\/script>', cleaned, re.IGNORECASE)
        if script_match:
            risk_score += 0.5
            flags.append(AnomalyFlag(
                category="XSS_SCRIPT_INJECTION",
                severity="CRITICAL",
                description="Executable <script> tag detected in merchant markup.",
                evidence=script_match.group(0)[:80]
            ))

        event_handler_match = re.search(r'\bon[a-z]+\s*=', cleaned, re.IGNORECASE)
        if event_handler_match:
            risk_score += 0.3
            flags.append(AnomalyFlag(
                category="DOM_EVENT_HANDLER_INJECTION",
                severity="HIGH",
                description="Inline JavaScript event handler detected.",
                evidence=event_handler_match.group(0)
            ))

        # 3. Detect CSS Hidden injection tags
        for pattern, desc in cls.CSS_HIDDEN_PATTERNS:
            matches = pattern.findall(cleaned)
            if matches:
                flags.append(AnomalyFlag(
                    category="CSS_INJECTION",
                    severity="HIGH",
                    description=desc,
                    evidence=matches[0][:80]
                ))
                risk_score += 0.3

        # 3. Detect Prompt Injection Semantic Directives
        for pattern, desc, severity in cls.PROMPT_INJECTION_KEYWORDS:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if match:
                score_increment = 0.4 if severity == "CRITICAL" else 0.2
                risk_score += score_increment
                flags.append(AnomalyFlag(
                    category="PROMPT_INJECTION",
                    severity=severity,
                    description=desc,
                    evidence=match.group(0)
                ))

        # Clamp risk score between 0.0 and 1.0
        final_risk_score = min(round(risk_score, 2), 1.0)
        is_safe = final_risk_score < 0.35 and not any(f.severity == "CRITICAL" for f in flags)

        # Strip full HTML tags for clean downstream agent reasoning
        clean_text = re.sub(r'<[^>]+>', ' ', cleaned)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        return DOMSanitizationReport(
            is_safe=is_safe,
            risk_score=final_risk_score,
            sanitized_text=clean_text,
            flags=flags,
            raw_length=raw_len,
            sanitized_length=len(clean_text)
        )
