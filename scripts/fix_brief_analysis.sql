-- Fix AI analysis for content briefs with correct mandatory topics, content instructions, and company news
-- Based on manual extraction from the brief content

-- Update Brief ID 1 (August 2025)
UPDATE content_briefs
SET ai_analysis = jsonb_set(
    ai_analysis::jsonb,
    '{}',
    '{
        "key_topics": [
            "New Hire Introduction",
            "Operational Efficiency and Analysis",
            "SMART Program Application",
            "Competency Matrix Development",
            "Akson Studio Growth",
            "Anti-Mobbing Training",
            "Communication Improvement",
            "Onboarding Process Enhancement",
            "Energy Monitoring System",
            "CFD Simulations"
        ],
        "important_dates": [
            "August"
        ],
        "key_messages": [
            "Natalia Szarach joins the team as Operational Efficiency and Analysis Manager.",
            "Akson Elektro focuses on continuous improvement, innovation, and employee well-being.",
            "The company is actively seeking funding and developing internal resources."
        ],
        "target_focus": [
            "Employees",
            "Large industrial plants",
            "New hires"
        ],
        "priority_items": [
            "SMART Program application",
            "Competency matrix development"
        ],
        "content_suggestions": [
            "Blog post: How to improve energy efficiency in large industrial plants using modern monitoring systems (August)",
            "Blog post: CFD simulations as a fire protection element (August)",
            "Social media posts about Natalia Szarach joining the team",
            "Internal communication updates on SMART program progress",
            "Internal news about competency matrix development",
            "Updates on Akson Studio projects",
            "Information on anti-mobbing training sessions",
            "Communication about new communication guidelines",
            "Content showcasing improved onboarding process"
        ],
        "context_summary": "Akson Elektro welcomes Natalia Szarach as their new Operational Efficiency and Analysis Manager.  The company is working on several key initiatives, including applying for SMART program funding to improve operations and build a training center and R&D department.  They are also developing a competency matrix, creating training videos in their studio, conducting anti-mobbing training, improving internal communication, and refining the onboarding process.  Content is needed for August, including blog posts about energy monitoring systems and CFD simulations, as well as general updates on company activities.",
        "mandatory_topics": [
            "Energy monitoring system for large industrial plants - blog post with educational and advisory content about how to manage energy consumption using modern systems, referencing reports and energy challenges for large industrial facilities",
            "CFD simulations as a fire protection element - blog post explaining how CFD simulations contribute to fire safety"
        ],
        "content_instructions": [
            "2 social media posts should encourage reading blog entries",
            "Suggest blog topics for August",
            "One blog post must be about energy monitoring systems for large industrial plants",
            "One blog post must be about CFD simulations as fire protection element"
        ],
        "company_news": [
            "Natalia Szarach joined as Manager ds. efektywności operacyjnej i analiz (Manager of Operational Efficiency and Analysis) - responsible for process optimization, cost and revenue analysis, strategic cooperation with the Board, documentation oversight and process standardization, participation in internal projects and ensuring business continuity"
        ]
    }'::jsonb,
    true
)
WHERE id = 1;

-- Update Brief ID 2 (September 2025)
UPDATE content_briefs
SET ai_analysis = jsonb_set(
    ai_analysis::jsonb,
    '{}',
    '{
        "key_topics": [
            "New Hire Announcement",
            "Operational Efficiency and Analysis",
            "Energy Monitoring System",
            "CFD Simulations and Fire Safety",
            "SMART Program Application",
            "Competency Matrix Development",
            "Akson Studio Growth",
            "Anti-Mobbing Training",
            "Communication Improvement",
            "Onboarding Process Enhancement"
        ],
        "important_dates": [
            "August"
        ],
        "key_messages": [
            "Natalia Szarach joins the team as Operational Efficiency and Analysis Manager.",
            "Akson Elektro focuses on continuous improvement, cost optimization, and strategic partnerships.",
            "The company is actively seeking funding for innovation and development.",
            "Akson Elektro prioritizes employee development, well-being, and a positive work environment."
        ],
        "target_focus": [
            "Employees",
            "Large industrial plants",
            "New hires"
        ],
        "priority_items": [
            "SMART Program Application",
            "Competency Matrix Development"
        ],
        "content_suggestions": [
            "Blog post: How to optimize energy consumption in large industrial plants using modern monitoring systems (August)",
            "Blog post: CFD simulations as a crucial element of fire protection (August)",
            "Social media posts about Natalia Szarach joining the team",
            "Internal communication updates on SMART program application progress",
            "Internal communication updates on competency matrix development"
        ],
        "context_summary": "Natalia Szarach has joined Akson Elektro as the Manager of Operational Efficiency and Analysis. Her responsibilities include process optimization, cost analysis, strategic collaboration, and overseeing documentation.  The company is working on several key initiatives: applying for SMART program funding to improve operations and build a training center and R&D department; developing a competency matrix for employee development; expanding their studio to create training videos; conducting anti-mobbing training; improving internal communication; and refining the onboarding process.  Blog posts are planned for August focusing on energy monitoring systems and CFD simulations for fire safety.",
        "mandatory_topics": [
            "Energy monitoring system for large industrial plants - blog post with educational and advisory content about how to manage energy consumption using modern systems, referencing reports and energy challenges for large industrial facilities",
            "CFD simulations as a fire protection element - blog post explaining how CFD simulations contribute to fire safety"
        ],
        "content_instructions": [
            "2 social media posts should encourage reading blog entries",
            "Suggest blog topics for August",
            "One blog post must be about energy monitoring systems for large industrial plants",
            "One blog post must be about CFD simulations as fire protection element"
        ],
        "company_news": [
            "Natalia Szarach joined as Manager ds. efektywności operacyjnej i analiz (Manager of Operational Efficiency and Analysis) - responsible for process optimization, cost and revenue analysis, strategic cooperation with the Board, documentation oversight and process standardization, participation in internal projects and ensuring business continuity"
        ]
    }'::jsonb,
    true
)
WHERE id = 2;

-- Verify the updates
SELECT 
    id,
    title,
    ai_analysis->'mandatory_topics' as mandatory_topics,
    ai_analysis->'content_instructions' as content_instructions,
    ai_analysis->'company_news' as company_news
FROM content_briefs
WHERE id IN (1, 2);