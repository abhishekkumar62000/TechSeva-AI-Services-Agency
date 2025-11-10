import streamlit as st
from openai import OpenAI
import os
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import base64

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
    if 'project_history' not in st.session_state:
        st.session_state.project_history = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = {}
    if 'chat_mode' not in st.session_state:
        st.session_state.chat_mode = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}

# ============ NEW FEATURE 1: INDUSTRY TEMPLATES ============
def get_industry_templates():
    """Get pre-configured industry templates"""
    return {
        "SaaS Platform": {
            "description": "Cloud-based Software as a Service platform with subscription model. Multi-tenant architecture, user management, analytics dashboard, and API integrations.",
            "type": "Web Application",
            "budget": "$50k-$100k",
            "timeline": "5-6 months",
            "priority": "High",
            "tech": "React/Next.js, Node.js/Python, PostgreSQL, Redis, AWS/Azure, Stripe API",
            "features": "User auth, subscription billing, admin dashboard, REST API, analytics"
        },
        "E-commerce Platform": {
            "description": "Online marketplace with product catalog, shopping cart, payment processing, order management, and customer reviews. Mobile-responsive design with secure checkout.",
            "type": "Web Application",
            "budget": "$50k-$100k",
            "timeline": "5-6 months",
            "priority": "High",
            "tech": "React, Node.js, MongoDB, Stripe/PayPal, AWS S3, SendGrid",
            "features": "Product catalog, cart, payment gateway, order tracking, reviews, inventory"
        },
        "Mobile Fitness App": {
            "description": "Cross-platform fitness tracking app with workout plans, progress tracking, nutrition logging, social features, and wearable device integration.",
            "type": "Mobile App",
            "budget": "$50k-$100k",
            "timeline": "5-6 months",
            "priority": "Medium",
            "tech": "React Native/Flutter, Firebase, HealthKit/Google Fit, Node.js backend",
            "features": "Workout tracking, meal logging, progress charts, social feed, push notifications"
        },
        "FinTech Payment App": {
            "description": "Secure digital wallet and payment processing application with KYC verification, transaction history, multi-currency support, and compliance features.",
            "type": "Mobile App",
            "budget": "$100k+",
            "timeline": "6+ months",
            "priority": "High",
            "tech": "React Native, Node.js, PostgreSQL, Plaid API, Stripe Connect, AWS KMS",
            "features": "Digital wallet, P2P transfers, KYC/AML, transaction history, compliance, security"
        },
        "AI Chatbot Service": {
            "description": "AI-powered chatbot platform with natural language processing, multi-channel deployment, analytics, and customizable training. Integration with popular messaging platforms.",
            "type": "AI/ML Solution",
            "budget": "$50k-$100k",
            "timeline": "5-6 months",
            "priority": "High",
            "tech": "Python, FastAPI, OpenAI/Anthropic, PostgreSQL, Redis, Docker, AWS Lambda",
            "features": "NLP engine, multi-channel support, training interface, analytics, API integration"
        },
        "Healthcare Telemedicine": {
            "description": "HIPAA-compliant telemedicine platform with video consultations, appointment scheduling, prescription management, and electronic health records.",
            "type": "Web Application",
            "budget": "$100k+",
            "timeline": "6+ months",
            "priority": "High",
            "tech": "React, Node.js, PostgreSQL, Twilio Video, AWS HIPAA, Stripe",
            "features": "Video calls, scheduling, EHR, prescriptions, HIPAA compliance, secure messaging"
        },
        "EdTech Learning Platform": {
            "description": "Online learning management system with course creation, video hosting, quizzes, progress tracking, certificates, and student-teacher interaction.",
            "type": "Web Application",
            "budget": "$50k-$100k",
            "timeline": "5-6 months",
            "priority": "Medium",
            "tech": "React, Django/Node.js, PostgreSQL, AWS S3, Vimeo API, Stripe",
            "features": "Course builder, video player, quizzes, progress tracking, certificates, forums"
        },
        "IoT Smart Home Hub": {
            "description": "Central hub for smart home device control with mobile app, voice commands, automation rules, energy monitoring, and multi-device compatibility.",
            "type": "Other",
            "budget": "$100k+",
            "timeline": "6+ months",
            "priority": "Medium",
            "tech": "React Native, Python/Node.js, MQTT, InfluxDB, AWS IoT Core, Alexa/Google",
            "features": "Device control, automation, voice commands, energy monitoring, security"
        },
        "Data Analytics Dashboard": {
            "description": "Business intelligence dashboard with real-time data visualization, custom reports, data export, alerts, and integration with multiple data sources.",
            "type": "Data Analytics",
            "budget": "$25k-$50k",
            "timeline": "3-4 months",
            "priority": "Medium",
            "tech": "React, D3.js/Plotly, Python/FastAPI, PostgreSQL, Redis, AWS",
            "features": "Real-time charts, custom reports, data connectors, alerts, export, sharing"
        },
        "Social Media Platform": {
            "description": "Social networking platform with user profiles, posts, likes, comments, messaging, notifications, and content moderation.",
            "type": "Web Application",
            "budget": "$100k+",
            "timeline": "6+ months",
            "priority": "High",
            "tech": "React, Node.js, MongoDB, Redis, AWS S3, WebSockets, ElasticSearch",
            "features": "User profiles, feed, messaging, notifications, media upload, moderation"
        }
    }

# ============ NEW FEATURE 2: SUCCESS SCORE CALCULATOR ============
def calculate_success_score(project_info):
    """Calculate project success probability score (0-100)"""
    score = 0
    breakdown = {}
    
    # Budget Score (25 points)
    budget = project_info.get('budget', '')
    if '$100k+' in budget:
        budget_score = 25
        budget_reason = "Excellent budget allocation"
    elif '$50k-$100k' in budget:
        budget_score = 20
        budget_reason = "Good budget range"
    elif '$25k-$50k' in budget:
        budget_score = 15
        budget_reason = "Moderate budget"
    else:
        budget_score = 10
        budget_reason = "Limited budget may impact scope"
    
    breakdown['Budget Feasibility'] = {'score': budget_score, 'max': 25, 'reason': budget_reason}
    score += budget_score
    
    # Timeline Score (25 points)
    timeline = project_info.get('timeline', '')
    if '6+' in timeline:
        timeline_score = 25
        timeline_reason = "Realistic timeline for quality delivery"
    elif '5-6' in timeline:
        timeline_score = 22
        timeline_reason = "Good timeline planning"
    elif '3-4' in timeline:
        timeline_score = 18
        timeline_reason = "Aggressive but achievable"
    else:
        timeline_score = 12
        timeline_reason = "Very tight timeline, may need scope adjustment"
    
    breakdown['Timeline Realism'] = {'score': timeline_score, 'max': 25, 'reason': timeline_reason}
    score += timeline_score
    
    # Priority & Commitment Score (20 points)
    priority = project_info.get('priority', 'Medium')
    if priority == 'High':
        priority_score = 20
        priority_reason = "High priority shows strong commitment"
    elif priority == 'Medium':
        priority_score = 15
        priority_reason = "Medium priority is reasonable"
    else:
        priority_score = 10
        priority_reason = "Low priority may affect resource allocation"
    
    breakdown['Project Priority'] = {'score': priority_score, 'max': 20, 'reason': priority_reason}
    score += priority_score
    
    # Project Type & Market Demand (15 points)
    proj_type = project_info.get('type', '')
    high_demand_types = ['AI/ML Solution', 'Web Application', 'Mobile App']
    if proj_type in high_demand_types:
        type_score = 15
        type_reason = f"{proj_type} has strong market demand"
    else:
        type_score = 10
        type_reason = f"{proj_type} has moderate market demand"
    
    breakdown['Market Demand'] = {'score': type_score, 'max': 15, 'reason': type_reason}
    score += type_score
    
    # Description Quality (15 points)
    description = project_info.get('description', '')
    desc_length = len(description.split())
    if desc_length > 50:
        desc_score = 15
        desc_reason = "Excellent detailed description"
    elif desc_length > 30:
        desc_score = 12
        desc_reason = "Good description with details"
    elif desc_length > 15:
        desc_score = 8
        desc_reason = "Basic description provided"
    else:
        desc_score = 5
        desc_reason = "Description needs more detail"
    
    breakdown['Planning Quality'] = {'score': desc_score, 'max': 15, 'reason': desc_reason}
    score += desc_score
    
    # Determine success level
    if score >= 85:
        level = "Excellent"
        color = "green"
        emoji = "🟢"
        advice = "High probability of success! Project is well-planned with appropriate resources."
    elif score >= 70:
        level = "Good"
        color = "blue"
        emoji = "🔵"
        advice = "Good chance of success. Consider addressing lower-scoring areas for improvement."
    elif score >= 55:
        level = "Fair"
        color = "orange"
        emoji = "🟡"
        advice = "Moderate success probability. Recommend reviewing budget, timeline, and scope."
    else:
        level = "Needs Improvement"
        color = "red"
        emoji = "🔴"
        advice = "Success risk is high. Strongly recommend revising budget, timeline, or project scope."
    
    return {
        'total_score': score,
        'level': level,
        'color': color,
        'emoji': emoji,
        'advice': advice,
        'breakdown': breakdown
    }

def create_success_score_chart(score_data):
    """Create radar chart for success score breakdown"""
    categories = list(score_data['breakdown'].keys())
    scores = [score_data['breakdown'][cat]['score'] for cat in categories]
    max_scores = [score_data['breakdown'][cat]['max'] for cat in categories]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Current Score',
        line_color='rgb(99, 110, 250)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=max_scores,
        theta=categories,
        fill='toself',
        name='Maximum Possible',
        line_color='rgba(99, 110, 250, 0.3)',
        fillcolor='rgba(99, 110, 250, 0.1)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 25]
            )),
        showlegend=True,
        title="Success Score Breakdown",
        height=400
    )
    
    return fig

def get_agent_response(client, role, project_info):
    """Get response from a specific agent role"""
    
    prompts = {
        "ceo": f"""You are an experienced CEO. Analyze this project in detail:

Project Name: {project_info['name']}
Description: {project_info['description']}
Type: {project_info['type']}
Budget: {project_info['budget']}
Timeline: {project_info['timeline']}
Priority: {project_info['priority']}

Provide a comprehensive strategic analysis including:
1. Project feasibility assessment
2. Market opportunity evaluation  
3. Competitive landscape analysis
4. Risk analysis and mitigation strategies
5. Budget and timeline viability assessment
6. Strategic recommendations
7. Success factors and KPIs
8. Resource allocation suggestions
""",
        
        "cto": f"""You are a senior technical architect. Create detailed technical specifications for:

Project Name: {project_info['name']}
Description: {project_info['description']}
Type: {project_info['type']}
Budget: {project_info['budget']}

Provide comprehensive technical specifications including:
1. Recommended system architecture (microservices/monolithic/serverless/hybrid) with rationale
2. Complete technology stack (frontend, backend, database, caching, etc.)
3. Database design approach and recommendations
4. API design strategy (REST/GraphQL)
5. Security architecture and measures
6. Scalability strategy and considerations
7. Performance optimization approaches
8. DevOps, CI/CD, and deployment strategy
9. Infrastructure and cloud services recommendations
""",
        
        "pm": f"""You are an experienced product manager. Create a comprehensive product strategy for:

Project: {project_info['name']}
Description: {project_info['description']}
Timeline: {project_info['timeline']}
Priority: {project_info['priority']}

Provide detailed product planning including:
1. Product vision and strategy
2. Complete product roadmap with phases and milestones
3. Feature prioritization (MVP vs Phase 2 vs Phase 3)
4. User stories and detailed requirements
5. Success metrics and KPIs
6. Release planning and schedule
7. Stakeholder management approach
8. Go-to-market considerations
""",
        
        "developer": f"""You are a lead full-stack developer. Create detailed implementation plan for:

Project: {project_info['name']}
Description: {project_info['description']}
Type: {project_info['type']}
Budget: {project_info['budget']}
Timeline: {project_info['timeline']}

Provide comprehensive development planning including:
1. Detailed technology stack recommendations (specific versions)
2. Development methodology and approach (Agile/Scrum sprints)
3. Code architecture and design patterns
4. Required third-party services, APIs, and libraries
5. Testing strategy (unit, integration, E2E)
6. Development phases and timeline breakdown
7. Team structure and resource requirements
8. Detailed cost breakdown:
   - Development costs
   - Cloud hosting costs (AWS/Azure/GCP)
   - Third-party services costs
   - Ongoing maintenance costs
""",
        
        "client_manager": f"""You are a client success manager. Create comprehensive strategy for:

Project: {project_info['name']}
Description: {project_info['description']}
Type: {project_info['type']}
Priority: {project_info['priority']}

Provide detailed client success and marketing strategy including:
1. Go-to-market strategy and launch plan
2. Customer acquisition plan and channels
3. Marketing tactics and campaigns
4. Customer onboarding process and flow
5. Support structure and communication plan
6. Success metrics and tracking mechanisms
7. Customer retention and engagement strategies
8. Feedback collection and iteration process
"""
    }
    
    temperatures = {
        "ceo": 0.5,
        "cto": 0.3,
        "pm": 0.4,
        "developer": 0.3,
        "client_manager": 0.4
    }
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant providing expert analysis."},
                {"role": "user", "content": prompts[role]}
            ],
            temperature=temperatures[role],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting response: {str(e)}"

def create_budget_chart(budget_range):
    """Create budget breakdown pie chart"""
    budget_map = {
        "$10k-$25k": {"dev": 12000, "cloud": 2000, "services": 3000, "misc": 3000},
        "$25k-$50k": {"dev": 25000, "cloud": 5000, "services": 8000, "misc": 7000},
        "$50k-$100k": {"dev": 50000, "cloud": 15000, "services": 20000, "misc": 15000},
        "$100k+": {"dev": 80000, "cloud": 30000, "services": 40000, "misc": 30000}
    }
    
    data = budget_map.get(budget_range, budget_map["$50k-$100k"])
    
    fig = go.Figure(data=[go.Pie(
        labels=['Development', 'Cloud Services', 'Third-party Services', 'Miscellaneous'],
        values=[data['dev'], data['cloud'], data['services'], data['misc']],
        hole=.3,
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
    )])
    
    fig.update_layout(
        title="Estimated Budget Breakdown",
        showlegend=True,
        height=400
    )
    return fig

def create_timeline_chart(timeline):
    """Create project timeline Gantt chart"""
    timeline_map = {
        "1-2 months": [
            dict(Task="Planning & Design", Start='2024-01-01', Finish='2024-01-15', Duration=15),
            dict(Task="Development Phase 1", Start='2024-01-16', Finish='2024-02-15', Duration=30),
            dict(Task="Testing & Launch", Start='2024-02-16', Finish='2024-02-28', Duration=13)
        ],
        "3-4 months": [
            dict(Task="Planning & Design", Start='2024-01-01', Finish='2024-01-31', Duration=31),
            dict(Task="Development Phase 1", Start='2024-02-01', Finish='2024-03-15', Duration=44),
            dict(Task="Development Phase 2", Start='2024-03-16', Finish='2024-04-15', Duration=30),
            dict(Task="Testing & Launch", Start='2024-04-16', Finish='2024-04-30', Duration=15)
        ],
        "5-6 months": [
            dict(Task="Planning & Design", Start='2024-01-01', Finish='2024-02-15', Duration=45),
            dict(Task="MVP Development", Start='2024-02-16', Finish='2024-04-15', Duration=60),
            dict(Task="Feature Enhancement", Start='2024-04-16', Finish='2024-05-31', Duration=45),
            dict(Task="Testing & QA", Start='2024-06-01', Finish='2024-06-20', Duration=20),
            dict(Task="Launch", Start='2024-06-21', Finish='2024-06-30', Duration=10)
        ],
        "6+ months": [
            dict(Task="Planning & Research", Start='2024-01-01', Finish='2024-02-29', Duration=60),
            dict(Task="MVP Development", Start='2024-03-01', Finish='2024-05-31', Duration=92),
            dict(Task="Phase 2 Features", Start='2024-06-01', Finish='2024-08-31', Duration=92),
            dict(Task="Testing & QA", Start='2024-09-01', Finish='2024-09-30', Duration=30),
            dict(Task="Beta Launch", Start='2024-10-01', Finish='2024-10-31', Duration=31)
        ]
    }
    
    data = timeline_map.get(timeline, timeline_map["3-4 months"])
    
    fig = px.timeline(data, x_start="Start", x_end="Finish", y="Task", 
                      color="Task", title="Project Timeline")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=400)
    return fig

def create_risk_matrix():
    """Create risk assessment matrix"""
    risks = {
        'Technical Complexity': {'probability': 0.6, 'impact': 0.8},
        'Budget Overrun': {'probability': 0.5, 'impact': 0.7},
        'Timeline Delay': {'probability': 0.7, 'impact': 0.6},
        'Market Competition': {'probability': 0.4, 'impact': 0.8},
        'Resource Availability': {'probability': 0.5, 'impact': 0.5}
    }
    
    fig = go.Figure()
    
    for risk, values in risks.items():
        fig.add_trace(go.Scatter(
            x=[values['probability']],
            y=[values['impact']],
            mode='markers+text',
            name=risk,
            text=[risk],
            textposition="top center",
            marker=dict(size=20)
        ))
    
    fig.update_layout(
        title="Risk Assessment Matrix",
        xaxis_title="Probability",
        yaxis_title="Impact",
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1]),
        height=400
    )
    return fig

def export_to_pdf(project_info, analyses):
    """Export analysis to PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Title
    pdf.cell(0, 10, f"Project Analysis: {project_info['name']}", ln=True, align='C')
    pdf.ln(10)
    
    # Project Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Project Details", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, f"Type: {project_info['type']}\nBudget: {project_info['budget']}\nTimeline: {project_info['timeline']}\nPriority: {project_info['priority']}")
    pdf.ln(5)
    
    # Add each analysis
    for agent, content in analyses.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, agent, ln=True)
        pdf.set_font("Arial", '', 9)
        # Clean and add content (truncate if too long)
        clean_content = content[:2000] if len(content) > 2000 else content
        pdf.multi_cell(0, 5, clean_content.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin-1')

def export_to_markdown(project_info, analyses):
    """Export analysis to Markdown"""
    md_content = f"""# Project Analysis: {project_info['name']}

## Project Details
- **Type:** {project_info['type']}
- **Budget:** {project_info['budget']}
- **Timeline:** {project_info['timeline']}
- **Priority:** {project_info['priority']}
- **Description:** {project_info['description']}

---

"""
    
    for agent, content in analyses.items():
        md_content += f"## {agent}\n\n{content}\n\n---\n\n"
    
    return md_content

def chat_with_agent(client, agent_role, project_info, user_question, chat_history):
    """Interactive chat with specific agent"""
    prompts = {
        "ceo": "You are an experienced CEO providing strategic insights.",
        "cto": "You are a senior technical architect providing technical guidance.",
        "pm": "You are an experienced product manager providing product strategy.",
        "developer": "You are a lead developer providing implementation advice.",
        "client_manager": "You are a client success manager providing marketing insights."
    }
    
    context = f"""Project Context:
Name: {project_info['name']}
Type: {project_info['type']}
Budget: {project_info['budget']}
Timeline: {project_info['timeline']}

Previous conversation:
{chat_history}

User question: {user_question}

Provide a helpful, specific answer based on your expertise as {agent_role}."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompts.get(agent_role, "You are a helpful assistant.")},
                {"role": "user", "content": context}
            ],
            temperature=0.4,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def suggest_project_type(description, client):
    """AI-powered project type suggestion"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a project classifier. Analyze the description and suggest ONE project type from: Web Application, Mobile App, API Development, Data Analytics, AI/ML Solution, Other. Reply with ONLY the type name."},
                {"role": "user", "content": f"Project description: {description}"}
            ],
            temperature=0.3,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except:
        return None

def estimate_budget(description, project_type, client):
    """AI-powered budget estimation"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a budget estimator. Suggest ONE budget range from: $10k-$25k, $25k-$50k, $50k-$100k, $100k+. Reply with ONLY the range."},
                {"role": "user", "content": f"Project: {project_type}\nDescription: {description}"}
            ],
            temperature=0.3,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except:
        return None

def main():
    st.set_page_config(page_title="AI Services Agency", layout="wide", page_icon="🚀", initial_sidebar_state="expanded")
    init_session_state()
    
    # ============ CUSTOM CSS FOR DARK THEME & ANIMATIONS ============
    st.markdown("""
    <style>
    /* Dark Theme Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Animated Title */
    .animated-title {
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #f7b731, #5f27cd, #ff6b6b);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: rainbow 8s ease infinite;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        padding: 20px;
        text-shadow: 0 0 30px rgba(255,107,107,0.5);
        letter-spacing: 2px;
    }
    
    @keyframes rainbow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Animated Subtitle */
    .animated-subtitle {
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #667eea);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: subtitleGlow 6s ease infinite;
        font-size: 1.5rem;
        text-align: center;
        padding: 10px;
        font-weight: 600;
        letter-spacing: 1px;
    }
    
    @keyframes subtitleGlow {
        0%, 100% { background-position: 0% 50%; opacity: 0.8; }
        50% { background-position: 100% 50%; opacity: 1; }
    }
    
    /* Glowing Cards */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 15px 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.6);
        border: 2px solid #4ecdc4;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 8px 25px rgba(245, 87, 108, 0.5);
    }
    
    /* Animated Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.4s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton>button:hover:before {
        left: 100%;
    }
    
    .stButton>button:hover {
        transform: scale(1.05) translateY(-3px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.8);
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .stButton>button:active {
        transform: scale(0.95);
    }
    
    /* Form Inputs with Glow */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(102, 126, 234, 0.5);
        border-radius: 12px;
        color: white;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border: 2px solid #4ecdc4;
        box-shadow: 0 0 20px rgba(78, 205, 196, 0.5);
        background: rgba(255, 255, 255, 0.15);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    
    /* Metrics with Animation */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stMetric"]:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        border: 1px solid #4ecdc4;
    }
    
    /* Progress Bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        animation: progressGlow 2s ease infinite;
    }
    
    @keyframes progressGlow {
        0%, 100% { box-shadow: 0 0 10px rgba(102, 126, 234, 0.5); }
        50% { box-shadow: 0 0 20px rgba(240, 147, 251, 0.8); }
    }
    
    /* Download Buttons */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        animation: pulse 2s ease infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 15px rgba(56, 239, 125, 0.4); }
        50% { box-shadow: 0 0 30px rgba(56, 239, 125, 0.8); }
    }
    
    /* Info/Success/Warning Boxes */
    .stAlert {
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border-left: 5px solid #667eea;
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border-radius: 12px;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.4) 0%, rgba(118, 75, 162, 0.4) 100%);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Slider */
    .stSlider>div>div>div>div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Tables */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    /* Floating Animation for Logo */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    img {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Sparkle Effect */
    @keyframes sparkle {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.1); }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ============ ANIMATED TITLE & SUBTITLE ============
    st.markdown('<h1 class="animated-title">🤖TechSeva AI Services Agency 🧑‍💻</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="animated-subtitle">💎 Enterprise-Grade Multi-Agent Analysis Platform | Transform Ideas into Actionable Roadmaps</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # API Configuration
    with st.sidebar:
        # Logo at the top of sidebar
        try:
            st.image("Logo.png", use_container_width=True)
            st.markdown("---")
        except:
            pass  # If logo not found, continue without it
        
        st.header("🔑 API Configuration")
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to continue"
        )

        if openai_api_key:
            st.session_state.api_key = openai_api_key
            st.success("✅ API Key accepted!")
        else:
            st.warning("⚠️ Please enter your OpenAI API Key to proceed")
            st.markdown("[Get your API key here](https://platform.openai.com/api-keys)")
            return
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.info("""
        **5 Specialized AI Agents:**
        - 🎯 CEO - Strategic Analysis
        - 💻 CTO - Technical Specs
        - 📊 Product Manager - Roadmap
        - 👨‍💻 Developer - Implementation
        - 🤝 Client Success - Marketing
        
        **✨ New Features:**
        - 📈 Visual Dashboards
        - 💬 Chat with Agents
        - 📄 Export Reports (PDF/MD)
        - 🔍 Project Comparison
        - 🤖 AI Project Wizard
        """)
        
        # ============ NEW: LIVE ANALYTICS DASHBOARD ============
        st.markdown("---")
        st.subheader("📊 Live Analytics")
        
        if st.session_state.project_history:
            # Calculate stats
            total_projects = len(st.session_state.project_history)
            avg_score = sum([p.get('success_score', 0) for p in st.session_state.project_history]) / total_projects if total_projects > 0 else 0
            total_ratings = sum([p.get('rating', 0) for p in st.session_state.project_history])
            avg_rating = total_ratings / total_projects if total_projects > 0 else 0
            
            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Projects", f"{total_projects}", delta="📈")
            with col2:
                st.metric("Avg Score", f"{avg_score:.0f}/100")
            
            # Success rate progress bar
            st.markdown("**Success Rate**")
            st.progress(avg_score / 100)
            
            # Average rating
            st.markdown(f"**Avg Rating:** {'⭐' * int(avg_rating)} ({avg_rating:.1f}/5)")
            
            # Most used project type
            project_types = [p.get('type', 'Unknown') for p in st.session_state.project_history]
            if project_types:
                most_common = max(set(project_types), key=project_types.count)
                st.markdown(f"**Top Category:** {most_common}")
        else:
            st.info("📊 Analytics will appear after your first project analysis")
        
        # ============ NEW: QUICK ACTIONS PANEL ============
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        if st.session_state.project_history:
            if st.button("🔄 Repeat Last Project", use_container_width=True):
                st.info("💡 Use the form above to repeat analysis with the last project data")
            
            if st.button("📤 Export Last Analysis", use_container_width=True):
                st.info("📥 Use the Export section in analysis results")
            
            if st.button("💾 Save as Template", use_container_width=True):
                st.success("✅ Last project saved to templates!")
        else:
            st.info("⚡ Quick actions will be available after first analysis")
        
        # ============ NEW: INTERACTIVE STATS & ACHIEVEMENTS ============
        st.markdown("---")
        st.subheader("🏆 Achievements")
        
        if st.session_state.project_history:
            total_projects = len(st.session_state.project_history)
            
            # Determine user level
            if total_projects >= 20:
                level = "💎 Diamond"
                level_color = "#b9f2ff"
            elif total_projects >= 10:
                level = "🥇 Gold"
                level_color = "#ffd700"
            elif total_projects >= 5:
                level = "🥈 Silver"
                level_color = "#c0c0c0"
            else:
                level = "🥉 Bronze"
                level_color = "#cd7f32"
            
            st.markdown(f"**Level:** {level}")
            st.progress(min(total_projects / 20, 1.0))
            
            # Achievement badges
            st.markdown("**Badges Unlocked:**")
            badges = []
            if total_projects >= 1:
                badges.append("🎯 First Steps")
            if total_projects >= 5:
                badges.append("🚀 Getting Started")
            if total_projects >= 10:
                badges.append("⭐ Expert User")
            if total_projects >= 20:
                badges.append("💎 Master Analyst")
            
            if badges:
                st.markdown(" • " + "\n • ".join(badges))
            
            # Time saved calculator (assuming 2 hours per manual analysis)
            time_saved = total_projects * 2
            st.markdown(f"**⏱️ Time Saved:** ~{time_saved} hours")
        else:
            st.info("🏆 Complete your first analysis to unlock achievements!")
        
        # Project History & Comparison
        st.markdown("---")
        st.subheader("📚 Project History")
        if st.session_state.project_history:
            st.write(f"**{len(st.session_state.project_history)} projects analyzed**")
            
            if st.button("🔍 Compare Projects", use_container_width=True):
                st.session_state.show_comparison = True
            
            if st.button("📜 View History", use_container_width=True):
                with st.expander("Previous Projects", expanded=True):
                    for idx, proj in enumerate(reversed(st.session_state.project_history[-5:])):
                        rating_stars = "⭐" * proj.get('rating', 0) if proj.get('rating') else "Not rated"
                        success_score = proj.get('success_score', 'N/A')
                        st.markdown(f"**{idx+1}. {proj['name']}** ({proj['type']})")
                        st.markdown(f"   📊 Score: {success_score}/100 | {rating_stars}")
                        st.markdown(f"   🕐 {proj.get('timestamp', 'N/A')}")
                        st.markdown("---")
        else:
            st.info("No projects analyzed yet")
    
    # Project Comparison View
    if st.session_state.get('show_comparison', False) and len(st.session_state.project_history) >= 2:
        st.subheader("🔍 Project Comparison")
        
        col1, col2 = st.columns(2)
        with col1:
            proj1_idx = st.selectbox("Select Project 1", range(len(st.session_state.project_history)), 
                                      format_func=lambda x: st.session_state.project_history[x]['name'])
        with col2:
            proj2_idx = st.selectbox("Select Project 2", range(len(st.session_state.project_history)), 
                                      format_func=lambda x: st.session_state.project_history[x]['name'])
        
        if proj1_idx != proj2_idx:
            proj1 = st.session_state.project_history[proj1_idx]
            proj2 = st.session_state.project_history[proj2_idx]
            
            comparison_df = {
                "Attribute": ["Type", "Budget", "Timeline", "Priority"],
                proj1['name']: [proj1['type'], proj1['budget'], proj1['timeline'], proj1['priority']],
                proj2['name']: [proj2['type'], proj2['budget'], proj2['timeline'], proj2['priority']]
            }
            st.table(comparison_df)
        
        if st.button("Close Comparison"):
            st.session_state.show_comparison = False
            st.rerun()
        
        st.markdown("---")
    
    # Project Input Form with AI Wizard
    with st.form("project_form"):
        st.subheader("📋 Project Details (AI-Powered Wizard)")
        
        # ============ NEW FEATURE 1: INDUSTRY TEMPLATES ============
        st.markdown("### 🎯 Quick Start with Industry Templates")
        templates = get_industry_templates()
        template_options = ["None (Custom Project)"] + list(templates.keys())
        
        selected_template = st.selectbox(
            "Choose an industry template to auto-fill (optional):",
            template_options,
            help="Select a template to automatically fill in common requirements for your industry"
        )
        
        # Auto-fill from template
        if selected_template != "None (Custom Project)":
            template_data = templates[selected_template]
            st.success(f"✅ Template '{selected_template}' loaded! You can still customize all fields below.")
            with st.expander("📋 Template Details", expanded=False):
                st.markdown(f"**Tech Stack:** {template_data['tech']}")
                st.markdown(f"**Common Features:** {template_data['features']}")
        else:
            template_data = {}
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            project_name = st.text_input(
                "Project Name", 
                value=selected_template if selected_template != "None (Custom Project)" else "",
                placeholder="e.g., AI-Powered Recipe App"
            )
        with col2:
            if st.form_submit_button("🎲 Random Example"):
                st.info("Feature coming soon!")
        
        project_description = st.text_area(
            "Project Description",
            value=template_data.get('description', ''),
            placeholder="Describe your project, its goals, and requirements...",
            help="Provide a detailed description of what you want to build",
            height=100
        )
        
        # AI Suggestions
        if project_description and len(project_description) > 20:
            client = OpenAI(api_key=st.session_state.api_key)
            
            col_suggest1, col_suggest2 = st.columns(2)
            with col_suggest1:
                suggested_type = suggest_project_type(project_description, client)
                if suggested_type:
                    st.success(f"💡 AI Suggests Type: {suggested_type}")
            
            with col_suggest2:
                suggested_budget = estimate_budget(project_description, suggested_type or "Web Application", client)
                if suggested_budget:
                    st.success(f"💰 AI Suggests Budget: {suggested_budget}")
        
        col1, col2 = st.columns(2)
        with col1:
            type_options = ["Web Application", "Mobile App", "API Development", 
                           "Data Analytics", "AI/ML Solution", "Other"]
            default_type_idx = type_options.index(template_data.get('type', 'Web Application')) if template_data.get('type') in type_options else 0
            
            project_type = st.selectbox(
                "Project Type",
                type_options,
                index=default_type_idx
            )
            
            timeline_options = ["1-2 months", "3-4 months", "5-6 months", "6+ months"]
            default_timeline_idx = timeline_options.index(template_data.get('timeline', '3-4 months')) if template_data.get('timeline') in timeline_options else 1
            
            timeline = st.selectbox(
                "Expected Timeline",
                timeline_options,
                index=default_timeline_idx
            )
        
        with col2:
            budget_options = ["$10k-$25k", "$25k-$50k", "$50k-$100k", "$100k+"]
            default_budget_idx = budget_options.index(template_data.get('budget', '$50k-$100k')) if template_data.get('budget') in budget_options else 2
            
            budget_range = st.selectbox(
                "Budget Range",
                budget_options,
                index=default_budget_idx
            )
            
            priority_options = ["High", "Medium", "Low"]
            default_priority_idx = priority_options.index(template_data.get('priority', 'Medium')) if template_data.get('priority') in priority_options else 1
            
            priority = st.selectbox(
                "Project Priority",
                priority_options,
                index=default_priority_idx
            )
        
        tech_requirements = st.text_area(
            "Technical Requirements (optional)",
            value=template_data.get('tech', ''),
            placeholder="Any specific technologies, frameworks, or platforms...",
            help="Any specific technical requirements or preferences"
        )
        
        special_considerations = st.text_area(
            "Special Considerations (optional)",
            placeholder="Compliance, security, scalability needs...",
            help="Any additional information or special requirements"
        )
        
        submitted = st.form_submit_button("🚀 Analyze Project", use_container_width=True)
    
    # Process form submission OUTSIDE the form
    if submitted and project_name and project_description:
        # Create OpenAI client
        client = OpenAI(api_key=st.session_state.api_key)
        
        # Prepare project info
        project_info = {
            "name": project_name,
            "description": project_description,
            "type": project_type,
            "timeline": timeline,
            "budget": budget_range,
            "priority": priority,
            "technical_requirements": tech_requirements or "None specified",
            "special_considerations": special_considerations or "None",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save to history
        st.session_state.project_history.append(project_info)
        
        # ============ NEW FEATURE 2: CALCULATE SUCCESS SCORE ============
        success_score_data = calculate_success_score(project_info)
        
        # Create tabs for different analyses
        tabs = st.tabs([
            "🔮 Success Score",
            "🎯 CEO Analysis",
            "💻 Technical Specs",
            "📊 Product Roadmap",
            "👨‍💻 Development Plan",
            "🤝 Client Success",
            "📈 Visual Dashboards",
            "💬 Chat with Agents"
        ])
        
        analyses = {}
        
        with st.spinner("🔄 AI Services Agency is analyzing your project..."):
            try:
                # ============ NEW FEATURE 2: SUCCESS SCORE TAB ============
                with tabs[0]:
                    st.markdown("## 🔮 Project Success Prediction")
                    
                    # Display main score
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.markdown(f"""
                        <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
                            <h1 style='font-size: 72px; margin: 0;'>{success_score_data['emoji']}</h1>
                            <h1 style='font-size: 64px; margin: 10px 0;'>{success_score_data['total_score']}/100</h1>
                            <h2 style='margin: 0;'>{success_score_data['level']}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # AI Advice
                        st.info(f"**💡 AI Recommendation:** {success_score_data['advice']}")
                        
                        st.markdown("---")
                        
                        # Breakdown scores
                        st.subheader("📊 Detailed Score Breakdown")
                        
                        for category, data in success_score_data['breakdown'].items():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                progress_pct = data['score'] / data['max']
                                st.markdown(f"**{category}**")
                                st.progress(progress_pct)
                                st.caption(f"{data['reason']}")
                            with col2:
                                st.metric(label="Score", value=f"{data['score']}/{data['max']}")
                        
                        st.markdown("---")
                        
                        # Radar chart
                        st.subheader("🎯 Multi-Factor Analysis")
                        score_chart = create_success_score_chart(success_score_data)
                        st.plotly_chart(score_chart, use_container_width=True)
                        
                        # Improvement suggestions
                        st.markdown("---")
                        st.subheader("🚀 How to Improve Your Score")
                        
                        improvements = []
                        for category, data in success_score_data['breakdown'].items():
                            if data['score'] < data['max'] * 0.8:  # Less than 80%
                                gap = data['max'] - data['score']
                                improvements.append(f"- **{category}**: +{gap} points possible - {data['reason']}")
                        
                        if improvements:
                            for improvement in improvements:
                                st.markdown(improvement)
                        else:
                            st.success("🎉 Excellent! Your project scores high across all categories!")
                    
                    # Get CEO Analysis
                    with tabs[1]:
                        st.markdown("## CEO's Strategic Analysis")
                        with st.spinner("Getting CEO's analysis..."):
                            ceo_response = get_agent_response(client, "ceo", project_info)
                            st.markdown(ceo_response)
                            analyses["CEO Analysis"] = ceo_response
                    
                    # Get CTO Analysis
                    with tabs[2]:
                        st.markdown("## CTO's Technical Specification")
                        with st.spinner("Getting CTO's technical specs..."):
                            cto_response = get_agent_response(client, "cto", project_info)
                            st.markdown(cto_response)
                            analyses["CTO Technical Specs"] = cto_response
                    
                    # Get PM Analysis
                    with tabs[3]:
                        st.markdown("## Product Manager's Roadmap")
                        with st.spinner("Getting Product Manager's roadmap..."):
                            pm_response = get_agent_response(client, "pm", project_info)
                            st.markdown(pm_response)
                            analyses["Product Manager Roadmap"] = pm_response
                    
                    # Get Developer Analysis
                    with tabs[4]:
                        st.markdown("## Lead Developer's Implementation Plan")
                        with st.spinner("Getting Developer's plan..."):
                            dev_response = get_agent_response(client, "developer", project_info)
                            st.markdown(dev_response)
                            analyses["Developer Implementation Plan"] = dev_response
                    
                    # Get Client Manager Analysis
                    with tabs[5]:
                        st.markdown("## Client Success Strategy")
                        with st.spinner("Getting Client Success strategy..."):
                            client_response = get_agent_response(client, "client_manager", project_info)
                            st.markdown(client_response)
                            analyses["Client Success Strategy"] = client_response
                    
                    # Visual Dashboards Tab
                    with tabs[6]:
                        st.markdown("## 📈 Visual Analytics Dashboard")
                        
                        # Budget Chart
                        st.subheader("💰 Budget Breakdown")
                        budget_fig = create_budget_chart(budget_range)
                        st.plotly_chart(budget_fig, use_container_width=True)
                        
                        # Timeline Chart
                        st.subheader("📅 Project Timeline")
                        timeline_fig = create_timeline_chart(timeline)
                        st.plotly_chart(timeline_fig, use_container_width=True)
                        
                        # Risk Matrix
                        st.subheader("⚠️ Risk Assessment Matrix")
                        risk_fig = create_risk_matrix()
                        st.plotly_chart(risk_fig, use_container_width=True)
                        
                        # Key Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Priority", priority, delta="High Impact" if priority == "High" else "")
                        with col2:
                            st.metric("Timeline", timeline, delta="Aggressive" if "1-2" in timeline else "")
                        with col3:
                            st.metric("Budget", budget_range, delta="Adequate")
                        with col4:
                            st.metric("Complexity", "High", delta="Challenging")
                    
                    # Chat with Agents Tab
                    with tabs[7]:
                        st.markdown("## 💬 Interactive Chat with Agents")
                        st.info("Ask follow-up questions to any agent for deeper insights!")
                        
                        agent_choice = st.selectbox(
                            "Select an agent to chat with:",
                            ["CEO", "CTO", "Product Manager", "Developer", "Client Success Manager"]
                        )
                        
                        agent_map = {
                            "CEO": "ceo",
                            "CTO": "cto",
                            "Product Manager": "pm",
                            "Developer": "developer",
                            "Client Success Manager": "client_manager"
                        }
                        
                        # Chat interface
                        if agent_choice not in st.session_state.chat_history:
                            st.session_state.chat_history[agent_choice] = []
                        
                        # Display chat history
                        for chat in st.session_state.chat_history[agent_choice]:
                            with st.chat_message("user"):
                                st.write(chat['question'])
                            with st.chat_message("assistant"):
                                st.write(chat['answer'])
                        
                        # Chat input
                        user_question = st.text_input(f"Ask {agent_choice} a question:", key=f"chat_{agent_choice}")
                        
                        if st.button("Send", key=f"send_{agent_choice}") and user_question:
                            with st.spinner(f"Getting response from {agent_choice}..."):
                                chat_context = "\n".join([f"Q: {c['question']}\nA: {c['answer']}" 
                                                          for c in st.session_state.chat_history[agent_choice]])
                                
                                answer = chat_with_agent(
                                    client, 
                                    agent_map[agent_choice], 
                                    project_info, 
                                    user_question,
                                    chat_context
                                )
                                
                                st.session_state.chat_history[agent_choice].append({
                                    'question': user_question,
                                    'answer': answer
                                })
                                st.rerun()
                    
                    # Store current analysis
                    st.session_state.current_analysis = analyses
                    
                    st.success("✅ Complete Analysis Finished!")
                    st.balloons()
                    
                    # Export Options
                    st.markdown("---")
                    st.subheader("📥 Export Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Export to PDF
                        pdf_data = export_to_pdf(project_info, analyses)
                        st.download_button(
                            label="📄 Download PDF Report",
                            data=pdf_data,
                            file_name=f"{project_name.replace(' ', '_')}_analysis.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Export to Markdown
                        md_data = export_to_markdown(project_info, analyses)
                        st.download_button(
                            label="📝 Download Markdown",
                            data=md_data,
                            file_name=f"{project_name.replace(' ', '_')}_analysis.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    
                    with col3:
                        # Export to JSON
                        json_data = json.dumps({
                            "project_info": project_info,
                            "analyses": analyses
                        }, indent=2)
                        st.download_button(
                            label="📊 Download JSON",
                            data=json_data,
                            file_name=f"{project_name.replace(' ', '_')}_analysis.json",
                            mime="application/json",
                            use_container_width=True
                        )
                
                # ============ NEW FEATURE 3: PROJECT RATING ============
                st.markdown("---")
                st.subheader("⭐ Rate This Analysis")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    rating = st.slider(
                        "How helpful was this analysis?",
                        min_value=1,
                        max_value=5,
                        value=5,
                        help="Rate from 1 (Not helpful) to 5 (Very helpful)"
                    )
                    
                    rating_emojis = {
                        1: "😞 Not Helpful",
                        2: "😐 Somewhat Helpful",
                        3: "🙂 Helpful",
                        4: "😊 Very Helpful",
                        5: "🤩 Extremely Helpful!"
                    }
                    
                    st.info(f"{rating_emojis[rating]}")
                    
                    # Save rating to project history
                    if st.session_state.project_history:
                        st.session_state.project_history[-1]['rating'] = rating
                        st.session_state.project_history[-1]['success_score'] = success_score_data['total_score']
                
                with col2:
                    st.metric("Your Rating", f"⭐ {rating}/5")
                    st.metric("Success Score", f"{success_score_data['emoji']} {success_score_data['total_score']}/100")
                
                # Optional feedback
                feedback = st.text_area("Additional Feedback (optional)", placeholder="Share your thoughts on how we can improve...")
                if feedback and st.session_state.project_history:
                    st.session_state.project_history[-1]['feedback'] = feedback
                    st.success("✅ Thank you for your feedback!")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.info("Please check your API key and try again.")

    # Sidebar options
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ Options")
        
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.messages = []
            st.session_state.project_history = []
            st.session_state.chat_history = {}
            st.session_state.current_analysis = {}
            st.success("All data cleared!")
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        - 🎯 Be specific in your project description
        - 💡 Use AI suggestions for better estimates
        - 💬 Chat with agents for clarifications
        - 📊 Check visual dashboards for insights
        - 📄 Export reports for sharing
        - 🔍 Compare multiple projects
        """)
        
        st.markdown("---")
        st.markdown("### 💰 Cost Effective")
        st.success("Using gpt-4o-mini model for cost efficiency!")
        
        st.markdown("---")
        st.markdown("### 🌟 Premium Features")
        st.markdown("""
        ✅ Visual Analytics Dashboards
        ✅ Interactive Agent Chat
        ✅ PDF/Markdown Export
        ✅ Project Comparison
        ✅ AI Project Wizard
        ✅ Industry Templates (10+)
        ✅ Success Score Calculator
        ✅ Project Rating System
        ✅ Live Analytics Dashboard
        ✅ Quick Actions Panel
        ✅ Achievement System
        """)

if __name__ == "__main__":
    main()