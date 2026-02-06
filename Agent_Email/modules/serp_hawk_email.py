"""
SERP Hawk email generator - creates personalized cold emails based on market analysis.
"""
import google.generativeai as genai
import os
import json

def get_model():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def generate_serp_hawk_email(company_info, market_analysis, service_matches, contact=None):
    """
    Generates a personalized B2B cold email for SERP Hawk.
    
    Args:
        company_info: Dict with company_name, what_they_do, contacts, etc.
        market_analysis: Dict with industry, growth_potential, competitors, etc.
        service_matches: Dict with recommended_services and email_hook
        contact: Optional specific contact person to address
    
    Returns:
        Dict with subject and body (HTML format)
    """
    model = get_model()
    
    # Prepare recipient context
    if contact and contact.get('name'):
        recipient_name = contact.get('name', '').split()[0]
        recipient_role = contact.get('role', 'Team Member')
        salutation = f"Hi {recipient_name},"
        personalization = f"I noticed you're the {recipient_role} at {company_info.get('company_name')}"
    else:
        salutation = f"Hi {company_info.get('company_name')} Team,"
        personalization = f"I came across {company_info.get('company_name')}"
    
    # Extract service details
    services = service_matches.get('recommended_services', [])[:3]
    service_names = [s.get('service_name') for s in services]
    
    # Build service descriptions
    service_descriptions = ""
    for i, svc in enumerate(services, 1):
        service_descriptions += f"""
        {i}. **{svc.get('service_name')}**: {svc.get('why_relevant')}
           Expected Impact: {svc.get('expected_impact')}
        """
    
    company_name = company_info.get('company_name', 'your company')
    industry = market_analysis.get('industry', 'your industry')
    growth_potential = market_analysis.get('growth_potential', '')
    pain_points = market_analysis.get('pain_points', [])
    email_hook = service_matches.get('email_hook', '')
    
    prompt = f"""
    Write a RESULTS-FOCUSED, transformation-driven sales email from SERP Hawk to {company_name}.
    
    CRITICAL STYLE REQUIREMENTS:
    - DO NOT talk about "who we are" or company history
    - FOCUS 100% on RESULTS, BENEFITS, and TRANSFORMATION
    - Use "Imagine..." storytelling to paint the outcome
    - Highlight what they GET, not what we do
    - Make it feel like a game-changer, not a service pitch
    
    Context About Target:
    - Company: {company_name}
    - Industry: {industry}
    - Pain Points: {json.dumps(pain_points)}
    - Growth Potential: {growth_potential}
    
    Our Solutions That Solve Their Problems:
    {service_descriptions}
    
    EXAMPLE STYLE TO FOLLOW:
    "Imagine waking up to find 100 qualified leads already in your inbox, 
    your SEO rankings climbing while you sleep, and your competitors wondering 
    what happened... All automated. No manual work."
    
    Email Structure:
    1. Opening: "Imagine..." scenario showing the TRANSFORMATION
       - Paint vivid picture of their business AFTER our services
       - Focus on outcomes: more leads, higher rankings, increased revenue
    
    2. The Problem (briefly): What's holding them back NOW
       - Reference their specific pain points
       - Show you understand their struggle

    3. **Introduction & Solutions** (CRITICAL):
       - Introduce SERP Hawk as a partner ready to solve these exact issues.
       - Explicitly mention: "At SERP Hawk, we are ready to provide [Service 1], [Service 2], and [Service 3] to help you [benefit]."
       - Ensure this connects the "Who we are" with "What we can do for you" in a service-oriented way.
    
    4. The Solution Details (benefits-focused):
       - NOT "We offer SEO services"
       - YES "Your website ranks #1 for your key terms, bringing 300+ qualified leads monthly"
       - List 2-3 specific OUTCOMES they'll get
       - Use numbers and tangible results
    
    5. Proof: One quick credibility line
       - "We've done this for 50+ {industry} businesses"
       - Keep it brief, not about us
    
    6. CTA: Simple and direct
       - "Click here to see how: [link]" OR
       - "Reply 'INTERESTED' and I'll send the details"
       - Phone: 089213 81769
    
    7. P.S.: Create urgency or give bonus insight
       - "P.S. We're only taking 5 clients this month"
       - "P.S. {industry} businesses using our system see 3x ROI in 90 days"
    
    TONE:
    - Exciting and benefit-driven (like the Matt Bacak email)
    - Short, punchy sentences
    - Focus on THEM, not US
    - Paint the dream outcome
    
    Length: Keep it SHORT (200 words max) - people scan emails
    
    Subject Line:
    - Benefit-focused, creates curiosity
    - Examples: "3x Your Leads While You Sleep?", "Your Competitors Are Using This...", "The {industry} Growth Hack Nobody's Talking About"
    
    Output Format (JSON):
    {{
        "subject": "Benefit-driven subject line",
        "body_html": "HTML email focusing on RESULTS and TRANSFORMATION"
    }}
    
    Remember: NO company background, NO "we are a premier agency" - ONLY what THEY get!
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        email_data = json.loads(content.strip())
        
        # Ensure we have HTML formatting
        if 'body_html' not in email_data and 'body' in email_data:
            email_data['body_html'] = format_plain_to_html(email_data['body'])
        
        return email_data
        
    except Exception as e:
        print(f"Error generating SERP Hawk email: {e}")
        # Fallback email - build the service list first
        service_list_html = ""
        for s in services[:3]:
            service_name = s.get('service_name', '')
            expected_impact = s.get('expected_impact', 'Significant growth and visibility')
            service_list_html += f"<li><strong>{expected_impact}</strong></li>"
        
        # Benefit-focused fallback email
        body_html = f"""
            <p><strong>Imagine This:</strong></p>
            
            <p>Your phone rings with qualified leads while you sleep.<br>
            Your website ranks #1 for your most profitable keywords.<br>
            Your competitors wonder what changed.</p>
            
            <p>That's what happens when you get your digital marketing RIGHT.</p>
            
            <p><strong>Here's what you get:</strong></p>
            <ul>
                {service_list_html}
            </ul>
            
            <p>No fluff. No theories. Just results.</p>
            
            <p><strong>Want to see how?</strong><br>
            Reply "INTERESTED" or call <strong>089213 81769</strong></p>
            
            <p>— Brajesh Kumar<br>
            SERP Hawk<br>
            📧 Brajesh.kumar@dapros.com.mx | 📞 089213 81769</p>
            
            <p><em>P.S. We're only taking 5 new clients this month. Don't miss out.</em></p>
            """
        
        return {
            "subject": f"3x Your {industry if industry != 'Unknown' else 'Business'} Leads?",
            "body_html": body_html
        }

def format_plain_to_html(plain_text):
    """
    Converts plain text email to HTML format.
    """
    # Split into paragraphs
    paragraphs = plain_text.split('\n\n')
    html_paragraphs = [f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()]
    return '\n'.join(html_paragraphs)
