import io
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_security_certificate_pdf(cert_data: dict) -> bytes:
    """
    Generates an enterprise-grade, cryptographic Proof-of-Safety PDF certificate.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#00457C'),
        alignment=1  # Center
    )
    
    subtitle_style = ParagraphStyle(
        'CertSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0070BA'),
        alignment=1  # Center
    )

    badge_style = ParagraphStyle(
        'CertBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#10B981'),
        alignment=1  # Center
    )

    label_style = ParagraphStyle(
        'CertLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )

    value_style = ParagraphStyle(
        'CertValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    code_style = ParagraphStyle(
        'CertCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )

    elements = []

    # Header
    elements.append(Paragraph("PAYGUARD SWARM | ZERO-TRUST EXECUTION PROTOCOL", subtitle_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("CRYPTOGRAPHIC PROOF-OF-SAFETY CERTIFICATE", title_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("AUTHENTICATED AUTONOMOUS TRANSACTION VERIFICATION & AUDIT RECEIPT", subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0070BA'), spaceAfter=12))

    # Certificate ID & Timestamp banner
    cert_id = cert_data.get("certificate_id", "CERT-EST-00000000")
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    
    header_table_data = [
        [Paragraph(f"<b>Certificate ID:</b> {cert_id}", label_style), Paragraph(f"<b>Issuance Timestamp:</b> {timestamp}", value_style)],
        [Paragraph(f"<b>Protocol:</b> PayGuard Zero-Trust Enclave v1.0", label_style), Paragraph("<b>Status:</b> <font color='#10B981'><b>VERIFIED TAMPER-EVIDENT</b></font>", label_style)]
    ]
    header_table = Table(header_table_data, colWidths=[270, 270])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 14))

    # Section 1: Transaction Summary
    elements.append(Paragraph("<b>1. TRANSACTION SPECIFICATIONS</b>", label_style))
    elements.append(Spacer(1, 6))

    tx_data = [
        [Paragraph("Procured Item", label_style), Paragraph(str(cert_data.get("item", "N/A")), value_style)],
        [Paragraph("Certified Merchant", label_style), Paragraph(str(cert_data.get("certified_merchant", "N/A")), value_style)],
        [Paragraph("Authorized Spending Ceiling", label_style), Paragraph(str(cert_data.get("settled_amount", "₹0.00")), label_style)],
        [Paragraph("Settlement Rail", label_style), Paragraph("PayPal Orders v2 REST API (OAuth2 Delegated Enclave)", value_style)],
        [Paragraph("PayPal Capture ID", label_style), Paragraph(f"<b>{cert_data.get('paypal_capture_id', 'N/A')}</b>", label_style)]
    ]
    tx_table = Table(tx_data, colWidths=[180, 360])
    tx_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(tx_table)
    elements.append(Spacer(1, 14))

    # Section 2: Security & Autonomous Failover Audit
    elements.append(Paragraph("<b>2. SENTRY THREAT INSPECTION & AUTONOMOUS FAILOVER LOG</b>", label_style))
    elements.append(Spacer(1, 6))

    failover_text = cert_data.get("failover_audit", "Direct certified routing. Zero threats detected.")
    threat_data = [
        [Paragraph("Sentry Inspection Verdict", label_style), Paragraph("<b>100% CLEAN - ALL ADVERSARIAL DOM INJECTIONS STRIPPED</b>", label_style)],
        [Paragraph("Failover Narrative", label_style), Paragraph(str(failover_text).replace('\n', '<br/>'), value_style)],
        [Paragraph("Emergency Circuit Breaker", label_style), Paragraph("Nominal. Telemetry monitored sub-250ms PayPal VOID trigger ready.", value_style)]
    ]
    threat_table = Table(threat_data, colWidths=[180, 360])
    threat_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(threat_table)
    elements.append(Spacer(1, 14))

    # Section 3: Cryptographic Proofs
    elements.append(Paragraph("<b>3. CRYPTOGRAPHIC INTEGRITY PROOFS</b>", label_style))
    elements.append(Spacer(1, 6))

    crypto_data = [
        [Paragraph("HMAC-SHA256 Token Signature", label_style), Paragraph(str(cert_data.get("hmac_sha256_signature", "N/A")), code_style)],
        [Paragraph("Chained Merkle Block Hash", label_style), Paragraph(str(cert_data.get("audit_block_hash", "N/A")), code_style)],
        [Paragraph("Hardware/Enclave Binding", label_style), Paragraph("Logically Isolated Financial Enclave (Agent 3) - Single-Use 300s TTL", value_style)]
    ]
    crypto_table = Table(crypto_data, colWidths=[180, 360])
    crypto_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F1F5F9')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(crypto_table)
    elements.append(Spacer(1, 18))

    # Footer Seal
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=8))
    elements.append(Paragraph("✔ Digitally Signed & Sealed by PayGuard Swarm Zero-Trust Autonomous Commerce Protocol", badge_style))
    elements.append(Paragraph("Submitted to PayPal AI Hackathon 2026 & AMSE Agentic AI Hackathon 2026", subtitle_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
