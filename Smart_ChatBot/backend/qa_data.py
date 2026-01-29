"""
Predefined Q&A pairs for E2M Solutions chatbot
These questions cover billing, core functionalities, and services
"""

PREDEFINED_QA = [
    # Billing Questions
    {
        "id": 1,
        "question": "What are your pricing models?",
        "answer": "E2M Solutions offers flexible pricing models tailored to your needs. We provide flat monthly rates with no long-term contracts, ensuring you can cancel anytime. Our pricing is transparent and based on the services you require. Contact us for a customized quote that fits your project scope.",
        "category": "billing"
    },
    {
        "id": 2,
        "question": "Do you have any setup fees?",
        "answer": "No, E2M Solutions does not charge any setup fees. We believe in transparent pricing with no hidden costs. You only pay for the services you use on a flat monthly rate basis.",
        "category": "billing"
    },
    {
        "id": 3,
        "question": "What payment methods do you accept?",
        "answer": "We accept multiple payment methods including credit cards, bank transfers, and online payment platforms. Our billing is flexible to accommodate your preferred payment process.",
        "category": "billing"
    },
    
    # Core Functionalities
    {
        "id": 4,
        "question": "What services does E2M Solutions offer?",
        "answer": "E2M Solutions is a trusted white label partner for digital agencies. We offer comprehensive services including web development, mobile app development, custom software solutions, UI/UX design, and dedicated development teams. Our plug-and-play teams integrate seamlessly with your existing operations.",
        "category": "core_functionality"
    },
    {
        "id": 5,
        "question": "What technologies do you work with?",
        "answer": "Our expert teams work with a wide range of modern technologies including React, Angular, Vue.js, Node.js, Python, Java, .NET, iOS (Swift), Android (Kotlin), React Native, Flutter, and various cloud platforms like AWS, Azure, and Google Cloud.",
        "category": "core_functionality"
    },
    {
        "id": 6,
        "question": "How do you ensure quality in your deliverables?",
        "answer": "We maintain 100% satisfaction guarantee through rigorous quality assurance processes, code reviews, automated testing, and continuous integration. Our teams follow industry best practices and agile methodologies to ensure timely, high-quality deliverables.",
        "category": "core_functionality"
    },
    
    # Services and Offers
    {
        "id": 7,
        "question": "What is your white label service?",
        "answer": "Our white label service allows digital agencies to hire our plug-and-play teams in just a few clicks. We work behind the scenes as an extension of your team, with no contracts and flat monthly rates. You can scale up or down as needed, and we guarantee 100% satisfaction.",
        "category": "services"
    },
    {
        "id": 8,
        "question": "Can I hire a dedicated remote team?",
        "answer": "Yes! E2M Solutions offers dedicated remote teams that work exclusively on your projects. Our teams are highly skilled, vetted professionals who integrate with your workflows and communication channels. You get the flexibility of remote work with the reliability of dedicated resources.",
        "category": "services"
    },
    {
        "id": 9,
        "question": "Do you offer ongoing support and maintenance?",
        "answer": "Absolutely! We provide comprehensive ongoing support and maintenance services for all our projects. This includes bug fixes, updates, performance optimization, security patches, and feature enhancements to ensure your applications run smoothly.",
        "category": "services"
    },
    {
        "id": 10,
        "question": "How quickly can I get started with E2M Solutions?",
        "answer": "You can get started in just a few clicks! Our streamlined onboarding process allows you to hire our plug-and-play teams quickly. Typically, we can have a team ready to start working on your project within 24-48 hours after initial consultation.",
        "category": "services"
    }
]

def get_all_questions():
    """Return list of all predefined questions"""
    return [{"id": qa["id"], "question": qa["question"], "category": qa["category"]} for qa in PREDEFINED_QA]

def find_matching_answer(user_query):
    """
    Find matching answer for user query from predefined Q&A
    Uses simple keyword matching and similarity
    """
    user_query_lower = user_query.lower().strip()
    
    # Direct match check
    for qa in PREDEFINED_QA:
        if qa["question"].lower() == user_query_lower:
            return qa["answer"]
    
    # Keyword-based matching
    for qa in PREDEFINED_QA:
        question_keywords = set(qa["question"].lower().split())
        query_keywords = set(user_query_lower.split())
        
        # If significant overlap in keywords (>60% match)
        if len(query_keywords) > 0:
            overlap = len(question_keywords.intersection(query_keywords))
            similarity = overlap / len(query_keywords)
            
            if similarity > 0.6:
                return qa["answer"]
    
    return None
