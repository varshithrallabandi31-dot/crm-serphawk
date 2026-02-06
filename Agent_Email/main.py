"""
Cold Outreach CRM - FastAPI Application
Author: Senior Python Backend Engineer
"""
import os
import uuid
import warnings
# Suppress Google Generative AI future warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import traceback

from fastapi import FastAPI, Request, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from sqlmodel import Session, select, func, text
from dotenv import load_dotenv

# Database & Models
from database import (
    engine, 
    Company, 
    EmailLog, 
    create_db_and_tables, 
    get_session
)

# AI & Scraping Modules
from modules.scraper import scrape_website
from modules.llm_engine import analyze_content
from modules.market_analyzer import analyze_market, match_services
from modules.serp_hawk_email import generate_serp_hawk_email
from modules.image_generator import generate_email_image
from modules.email_sender import send_email_outlook

# Load environment variables
load_dotenv()

# Configuration
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "padilla@dapros.com") # Default sender for UI
HOURLY_EMAIL_LIMIT = int(os.getenv("HOURLY_EMAIL_LIMIT", 50))
OUTLOOK_EMAIL = os.getenv('OUTLOOK_EMAIL')
OUTLOOK_PASSWORD = os.getenv('OUTLOOK_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

# Create output directories
os.makedirs('static/generated_images', exist_ok=True)


# Custom Exceptions
class OutreachError(Exception):
    """Base exception for outreach eligibility errors"""
    pass


class DuplicateProspectError(OutreachError):
    """Raised when a prospect has already been contacted"""
    pass


class RateLimitExceededError(OutreachError):
    """Raised when hourly email limit is reached"""
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan - creates tables on startup
    """
    print("🚀 Starting Cold Outreach CRM...")
    print("📊 Creating database tables...")
    create_db_and_tables()
    
    # Simple migration for recommended_services
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS recommended_services VARCHAR(1000)"))
            conn.commit()
            print("✅ Database schema updated (recommended_services)")
    except Exception as e:
        print(f"⚠️ Schema update note: {e}")

    print("✅ Database ready!")
    
    # Try to install playwright browsers if needed (optional check)
    # print("Checking Playwright browsers...")
    # os.system("playwright install chromium") 
    
    yield
    print("👋 Shutting down Cold Outreach CRM...")


# Initialize FastAPI app
app = FastAPI(
    title="Cold Outreach CRM",
    description="A simple CRM for managing cold email outreach",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        # Add your Railway frontend URL here after deployment:
        # "https://your-frontend-production-xxxx.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================================
# BUSINESS LOGIC - The "Gatekeeper" Middleware
# ============================================================================

def check_outreach_eligibility(session: Session, website_url: str) -> dict:
    """
    Gatekeeper function that checks if we can send an outreach email.
    """
    result = {
        "eligible": True,
        "existing_company": None,
        "emails_sent_last_hour": 0
    }
    
    # Normalize URL for comparison
    normalized_url = website_url.strip().lower()
    if not normalized_url.startswith(('http://', 'https://')):
        normalized_url = 'https://' + normalized_url
    
    # Rule A: Duplicate Check
    statement = select(Company).where(Company.website_url == normalized_url)
    existing_company = session.exec(statement).first()
    
    if existing_company:
        result["existing_company"] = existing_company
        if existing_company.email_sent_status:
            raise DuplicateProspectError(
                f"❌ Prospecting email already sent to {existing_company.company_name} "
                f"({existing_company.website_url}) on {existing_company.created_at.strftime('%Y-%m-%d %H:%M')}"
            )
    
    # Rule B: Rate Limiter
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    rate_limit_statement = select(func.count(EmailLog.id)).where(
        EmailLog.sender_email == SENDER_EMAIL,
        EmailLog.sent_at > one_hour_ago
    )
    emails_sent_count = session.exec(rate_limit_statement).one()
    result["emails_sent_last_hour"] = emails_sent_count
    
    if emails_sent_count >= HOURLY_EMAIL_LIMIT:
        raise RateLimitExceededError(
            f"⏳ Hourly email limit ({HOURLY_EMAIL_LIMIT}) reached. "
            f"You've sent {emails_sent_count} emails in the last hour. "
            f"Please wait before sending more."
        )
    
    return result


# ============================================================================
# ROUTES - API
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - indicates API is running.
    """
    return {
        "message": "Cold Outreach CRM API is running",
        "frontend": "http://localhost:3000",
        "docs": "/docs"
    }




# ============================================================================
# PROCESS ROUTES - Add Lead & Send Email (CRM Style)
# ============================================================================

@app.post("/draft-lead")
async def draft_lead(
    company_name: str = Form(...),
    website_url: str = Form(...),
    primary_email: str = Form(...),
    session: Session = Depends(get_session)
):
    """
    Step 1: Check eligibility, analyze URL, and return Draft (NO SENDING)
    """
    try:
        # Normalize URL
        normalized_url = website_url.strip().lower()
        if not normalized_url.startswith(('http://', 'https://')):
            normalized_url = 'https://' + normalized_url
        
        # Check eligibility (just for info, but don't block drafting yet? Or do block?)
        # Let's BLOCK if already sent, to warn user.
        eligibility = check_outreach_eligibility(session, normalized_url)
        
        print(f"🧐 Analyzing {normalized_url} for personalization...")
        
        # Scrape & Analyze
        scraped_text = await run_in_threadpool(scrape_website, normalized_url)
        
        subject = f"Partnership Opportunity with {company_name}"
        body_html = f"<p>Hi {company_name} Team,</p><p>We'd love to partner.</p>" 
        
        if scraped_text and not scraped_text.startswith("ERROR SCRAPING"):
            company_info = await run_in_threadpool(analyze_content, scraped_text)
            market_analysis = await run_in_threadpool(analyze_market, scraped_text, company_name)
            service_matches = await run_in_threadpool(match_services, market_analysis, company_info)
        else:
            print(f"⚠️ Scraping failed/empty: {scraped_text[:100] if scraped_text else 'None'}. Generating generic draft.")
            # Fallback to generic analysis based on name
            company_info = {'company_name': company_name, 'what_they_do': 'Unknown', 'contacts': []}
            market_analysis = {'industry': 'Unknown', 'pain_points': ['Lead Generation', 'Visibility'], 'growth_potential': 'High'}
            service_matches = {'recommended_services': [{'service_name': 'Organic SEO', 'why_relevant': 'Standard growth requirement', 'expected_impact': 'More leads'}], 'email_hook': 'Growth'}

        contact = {'name': company_name, 'email': primary_email, 'role': 'Decision Maker'}
        email_draft = await run_in_threadpool(
            generate_serp_hawk_email,
            company_info, market_analysis, service_matches, contact
        )
        
        if email_draft:
            subject = email_draft.get('subject', subject)
            body_html = email_draft.get('body_html', body_html)

        # Get services string
        services = service_matches.get('recommended_services', [])
        service_names = [s.get('service_name') for s in services]
        recommended_services_str = ", ".join(service_names) if service_names else None

        return JSONResponse({
            'success': True,
            'draft': {
                'subject': subject,
                'body': body_html,
                'company_name': company_name,
                'website_url': normalized_url,
                'primary_email': primary_email,
                'recommended_services': recommended_services_str
            }
        })

    except Exception as e:
        traceback.print_exc()
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@app.post("/send-lead")
async def send_lead(
    request: Request,
    data: dict,
    session: Session = Depends(get_session)
):
    """
    Step 2: Send the approved draft
    """
    try:
        to_email = data.get('primary_email')
        subject = data.get('subject')
        body_html = data.get('body')
        company_name = data.get('company_name')
        website_url = data.get('website_url')
        recommended_services = data.get('recommended_services')

        # Check eligibility/Rate Limit "just in case" (final gate)
        # Note: We skip duplicate check here if user forces send, or re-check.
        # Let's do a re-check to be safe.
        normalized_url = website_url.strip().lower()
        check_outreach_eligibility(session, normalized_url)

        # Send Email
        if OUTLOOK_EMAIL and OUTLOOK_PASSWORD:
            print(f"Sending email to {to_email} via Outlook...")
            await run_in_threadpool(
                send_email_outlook,
                to_email=to_email,
                subject=subject,
                body=body_html,
                sender_email=OUTLOOK_EMAIL,
                sender_password=OUTLOOK_PASSWORD,
                smtp_server=SMTP_SERVER,
                smtp_port=SMTP_PORT,
                html=True
            )
        else:
             print(f"SIMULATING email to {to_email}: {subject}")

        # DB Operations (Create Company + Log)
        # Check if company exists first
        stmt = select(Company).where(Company.website_url == normalized_url)
        company = session.exec(stmt).first()
        
        if not company:
            company = Company(
                company_name=company_name,
                website_url=normalized_url,
                primary_email=to_email,
                email_sender=SENDER_EMAIL,
                email_sent_status=True,
                recommended_services=recommended_services
            )
            session.add(company)
        else:
            company.email_sent_status = True
            company.primary_email = to_email # Update email if changed
            if recommended_services:
                company.recommended_services = recommended_services
            session.add(company)
            
        session.commit()
        session.refresh(company)

        # Log
        log = EmailLog(
            company_id=company.id,
            sender_email=SENDER_EMAIL,
            sent_at=datetime.utcnow()
        )
        session.add(log)
        session.commit()
        
        return JSONResponse({'success': True})

    except Exception as e:
        traceback.print_exc()
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@app.get("/activities")
async def get_activities(limit: int = 10, session: Session = Depends(get_session)):
    """
    Fetch recent email activities
    """
    statement = (
        select(EmailLog, Company)
        .join(Company, EmailLog.company_id == Company.id)
        .order_by(EmailLog.sent_at.desc())
        .limit(limit)
    )
    results = session.exec(statement).all()
    
    activities = []
    for log, comp in results:
        activities.append({
            'id': str(log.id), # Convert UUID to string
            'company_name': comp.company_name,
            'website_url': comp.website_url,
            'email': comp.primary_email,
            'sent_at': log.sent_at.isoformat(),
            'status': 'Sent',
            'recommended_services': comp.recommended_services
        })
        
    return JSONResponse({'activities': activities})


# ============================================================================
# AI ROUTES - SERP Hawk Logic
# ============================================================================

@app.post("/generate")
async def generate_ai_analysis(data: dict):
    """
    Complete SERP Hawk outreach workflow:
    1. Scrape website
    2. Analyze company
    3. Analyze market & competitors
    4. Match services
    5. Generate email
    6. Create image
    """
    urls = data.get('urls', [])
    results = []

    for url in urls:
        try:
            print(f"Processing: {url}")
            
            # Step 1: Scrape (run blocking code in threadpool)
            scraped_text = await run_in_threadpool(scrape_website, url)
            
            if not scraped_text or scraped_text.startswith("ERROR SCRAPING"):
                error_message = scraped_text if scraped_text else "Failed to scrape website"
                results.append({'url': url, 'error': error_message})
                continue

            # Step 2: Analyze company
            company_info = await run_in_threadpool(analyze_content, scraped_text)
            company_name = company_info.get('company_name', 'Unknown Company')

            # Step 3: Market analysis
            market_analysis = await run_in_threadpool(analyze_market, scraped_text, company_name)

            # Step 4: Match services
            service_matches = await run_in_threadpool(match_services, market_analysis, company_info)

            # Step 5: Generate email
            contacts = company_info.get('contacts', [])
            generated_emails = []
            
            if contacts:
                for contact in contacts:
                    email_draft = await run_in_threadpool(
                        generate_serp_hawk_email,
                        company_info, market_analysis, service_matches, contact
                    )
                    generated_emails.append({
                        'to_email': contact.get('email', ''),
                        'recipient_name': contact.get('name'),
                        'role': contact.get('role'),
                        'subject': email_draft.get('subject'),
                        'body': email_draft.get('body_html')
                    })
            else:
                email_draft = await run_in_threadpool(
                    generate_serp_hawk_email,
                    company_info, market_analysis, service_matches, None
                )
                generated_emails.append({
                    'to_email': '', # To be filled by user
                    'recipient_name': 'General',
                    'role': 'N/A',
                    'subject': email_draft.get('subject'),
                    'body': email_draft.get('body_html')
                })

            # Step 6: Generate beautiful email image
            services = service_matches.get('recommended_services', [])
            
            safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_company_name = safe_company_name.replace(' ', '_')[:50]
            
            image_filename = f"{safe_company_name}_email_image.html"
            image_path = os.path.join('static', 'generated_images', image_filename)
            
            generated_image = await run_in_threadpool(
                generate_email_image,
                company_name, services, image_path
            )

            results.append({
                'url': url,
                'analysis': {
                    'company_name': company_name,
                    'what_they_do': company_info.get('summary', 'Analysis available'),
                    'contacts': contacts
                },
                'emails': generated_emails,
                'image_url': f'/static/generated_images/{image_filename}' if generated_image else None
            })

        except Exception as e:
            traceback.print_exc()
            results.append({'url': url, 'error': str(e)})

    return JSONResponse(results)


@app.post("/send")
async def send_email_api(data: dict, session: Session = Depends(get_session)):
    """
    Send email using credentials and log to DB (AI Outreach version)
    """
    email_data = data.get('email_data')
    if not email_data:
        return JSONResponse({'success': False, 'error': 'No email data provided'}, status_code=400)

    sender_email = OUTLOOK_EMAIL
    sender_password = OUTLOOK_PASSWORD
    
    if not sender_email or not sender_password:
        return JSONResponse({'success': False, 'error': 'Email credentials not configured in .env'}), 500

    try:
        # Check eligibility/rate limit before sending
        # Note: We need a URL to check duplicates, but the AI UI sends email_data directly.
        # We'll treat this as "Ad-hoc" send, but still rate limit.
        
        # Rate Limit Check
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        rate_statement = select(func.count(EmailLog.id)).where(
            EmailLog.sender_email == SENDER_EMAIL,
            EmailLog.sent_at > one_hour_ago
        )
        emails_sent_count = session.exec(rate_statement).one()
        
        if emails_sent_count >= HOURLY_EMAIL_LIMIT:
             return JSONResponse({'success': False, 'error': 'Hourly rate limit exceeded'}, status_code=429)

        # Send Email
        await run_in_threadpool(
            send_email_outlook,
            to_email=email_data['to_email'],
            subject=email_data['subject'],
            body=email_data['body'],
            sender_email=sender_email,
            sender_password=sender_password,
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            html=True
        )
        
        # Log to DB
        # We might not have a Company ID if it came from the AI tool randomly.
        # For now, we'll try to find a company by email or create a "clean" one if needed.
        # But to avoid complexity, we can just log the rate limit and maybe create a minimal company.
        
        # Try to find company by email
        statement = select(Company).where(Company.primary_email == email_data['to_email'])
        company = session.exec(statement).first()
        
        if not company:
            # Create a shell company entry for logging purposes
            company = Company(
                company_name="AI Outreach Contact",
                website_url=f"ai-generated-{uuid.uuid4()}@example.com", # Placeholder
                primary_email=email_data['to_email'],
                email_sender=SENDER_EMAIL,
                email_sent_status=True
            )
            session.add(company)
            session.commit()
            session.refresh(company)
        else:
            company.email_sent_status = True
            session.add(company)
            session.commit()

        # Log
        email_log = EmailLog(
            company_id=company.id,
            sender_email=SENDER_EMAIL,
            sent_at=datetime.utcnow()
        )
        session.add(email_log)
        session.commit()

        return JSONResponse({'success': True})
        
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Cold Outreach CRM + AI"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )
