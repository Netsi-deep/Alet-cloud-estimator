import io
import random
import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = FastAPI(title="Alet Cloud Resource Cost & Usage Estimator")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResourceRequest(BaseModel):
    vcpu_cores: int      # 1 - 64
    ram_gb: int          # 2 - 256
    storage_gb: int      # 20 - 2000
    monthly_sms: int     # 0 - 500,000

class PDFQuoteRequest(BaseModel):
    client_name: str
    client_email: str
    org_name: str
    billing_cycle: str  # 'hourly', 'monthly', 'yearly'
    resources: ResourceRequest

@app.post("/api/calculate")
def calculate_costs(data: ResourceRequest):
    vcpu_rate_per_hour = 0.035
    ram_rate_per_hour = 0.005
    storage_rate_per_month = 0.10
    hours_in_month = 730
    
    vcpu_hourly = data.vcpu_cores * vcpu_rate_per_hour
    ram_hourly = data.ram_gb * ram_rate_per_hour
    storage_hourly = (data.storage_gb * storage_rate_per_month) / hours_in_month
    
    cloud_hourly_total = vcpu_hourly + ram_hourly + storage_hourly
    
    vcpu_monthly = vcpu_hourly * hours_in_month
    ram_monthly = ram_hourly * hours_in_month
    storage_monthly = data.storage_gb * storage_rate_per_month
    
    cloud_monthly_total = vcpu_monthly + ram_monthly + storage_monthly
    
    sms_monthly = 0
    sms_count = data.monthly_sms
    if sms_count <= 10000:
        sms_monthly = sms_count * 0.02
    else:
        sms_monthly = (10000 * 0.02) + ((sms_count - 10000) * 0.015)
        
    total_monthly = cloud_monthly_total + sms_monthly
    
    vcpu_yearly = vcpu_monthly * 12
    ram_yearly = ram_monthly * 12
    storage_yearly = storage_monthly * 12
    sms_yearly = sms_monthly * 12
    total_yearly = total_monthly * 12
    
    return {
        "status": "success",
        "breakdown": {
            "hourly": {
                "vCPU_cost": round(vcpu_hourly, 4),
                "RAM_cost": round(ram_hourly, 4),
                "Storage_cost": round(storage_hourly, 4),
                "total_hourly_cost": round(cloud_hourly_total, 4)
            },
            "monthly": {
                "vCPU_cost": round(vcpu_monthly, 2),
                "RAM_cost": round(ram_monthly, 2),
                "Storage_cost": round(storage_monthly, 2),
                "SMS_cost": round(sms_monthly, 2),
                "total_monthly_cost": round(total_monthly, 2)
            },
            "yearly": {
                "vCPU_cost": round(vcpu_yearly, 2),
                "RAM_cost": round(ram_yearly, 2),
                "Storage_cost": round(storage_yearly, 2),
                "SMS_cost": round(sms_yearly, 2),
                "total_yearly_cost": round(total_yearly, 2)
            }
        }
    }

@app.post("/api/generate-pdf")
def generate_pdf(data: PDFQuoteRequest):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#008A2E'),  # ወደ ደማቁ አረንጓዴ ተቀይሯል
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=15
    )
    
    elements.append(Paragraph("AletCloud & SMS Ethiopia", title_style))
    elements.append(Paragraph("Official Resource Cost Quotation", subtitle_style))
    
    quote_id = f"AC-Q-{random.randint(100000, 999999)}"
    quote_date = datetime.date.today().strftime("%B %d, %Y")
    valid_until = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%B %d, %Y")
    
    meta_data = [
        [Paragraph(f"<b>Quote ID:</b> {quote_id}", styles['Normal']), Paragraph(f"<b>Date:</b> {quote_date}", styles['Normal'])],
        [Paragraph(f"<b>Client:</b> {data.client_name} ({data.org_name})", styles['Normal']), Paragraph(f"<b>Valid Until:</b> {valid_until}", styles['Normal'])],
        [Paragraph(f"<b>Email:</b> {data.client_email}", styles['Normal']), Paragraph(f"<b>Billing Cycle:</b> {data.billing_cycle.capitalize()}", styles['Normal'])]
    ]
    meta_table = Table(meta_data, colWidths=[270, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9FAFB')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 15))
    
    res = data.resources
    vcpu_rate = 0.035
    ram_rate = 0.005
    storage_rate = 0.10
    hours = 730
    
    if data.billing_cycle == 'hourly':
        vcpu_c = res.vcpu_cores * vcpu_rate
        ram_c = res.ram_gb * ram_rate
        storage_c = (res.storage_gb * storage_rate) / hours
        sms_c = 0
        total_c = vcpu_c + ram_c + storage_c
    elif data.billing_cycle == 'monthly':
        vcpu_c = res.vcpu_cores * vcpu_rate * hours
        ram_c = res.ram_gb * ram_rate * hours
        storage_c = res.storage_gb * storage_rate
        sms_c = (res.monthly_sms * 0.02) if res.monthly_sms <= 10000 else ((10000 * 0.02) + ((res.monthly_sms - 10000) * 0.015))
        total_c = vcpu_c + ram_c + storage_c + sms_c
    else:
        m_vcpu = res.vcpu_cores * vcpu_rate * hours
        m_ram = res.ram_gb * ram_rate * hours
        m_storage = res.storage_gb * storage_rate
        m_sms = (res.monthly_sms * 0.02) if res.monthly_sms <= 10000 else ((10000 * 0.02) + ((res.monthly_sms - 10000) * 0.015))
        vcpu_c = m_vcpu * 12
        ram_c = m_ram * 12
        storage_c = m_storage * 12
        sms_c = m_sms * 12
        total_c = vcpu_c + ram_c + storage_c + sms_c

    table_data = [
        ["Resource Description", "Quantity / Specs", "Cost"],
        ["vCPU Compute", f"{res.vcpu_cores} Cores", f"${vcpu_c:.2f}"],
        ["RAM Memory", f"{res.ram_gb} GB", f"${ram_c:.2f}"],
        ["NVMe Storage", f"{res.storage_gb} GB", f"${storage_c:.2f}"],
        ["SMS Volume", f"{res.monthly_sms:,} SMS", f"${sms_c:.2f}"],
        ["Total Cost", f"({data.billing_cycle.upper()})", f"${total_c:.2f}"]
    ]
    
    t = Table(table_data, colWidths=[200, 200, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#008A2E')),  # ወደ ደማቁ አረንጓዴ ተቀይሯል
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F3F4F6')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    buffer.seek(0)
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename={quote_id}.pdf"}
    )

@app.get("/")
def read_index():
    return FileResponse("index.html")

app.mount("/", StaticFiles(directory="."), name="static")