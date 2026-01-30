"""
Flask API for Smart Chatbot
Handles predefined Q&A, web scraping, RAG retrieval, and LLM integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
from dotenv import load_dotenv
from qa_data import get_all_questions, find_matching_answer
from scraper import E2MScraper
from vector_store import VectorStore
from database import db_manager
from email_utils import EmailSender

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize components
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
vector_store = VectorStore(persist_directory=os.getenv('CHROMA_PERSIST_DIR', './chroma_db'))
scraper = E2MScraper()

# Initialize database
db_manager.init_db()
db_manager.init_default_smtp_settings()
print("Database initialized")

# Check if we need to do initial scraping
if vector_store.get_collection_count() == 0:
    print("Vector store is empty. Performing initial website scraping...")
    scraped_data = scraper.scrape_website(max_pages=10)
    vector_store.add_scraped_content(scraped_data)
    print(f"Initial scraping complete. Vector store now has {vector_store.get_collection_count()} chunks")

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """Return all predefined questions"""
    try:
        questions = get_all_questions()
        return jsonify({
            'success': True,
            'questions': questions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user/register', methods=['POST'])
def register_user():
    """Register a new user or return existing user"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        
        if not name or not email:
            return jsonify({
                'success': False,
                'error': 'Name and email are required'
            }), 400
        
        # Create or get user
        user = db_manager.create_user(name, email)
        
        # Get user's recent questions
        recent_questions = db_manager.get_user_history(user.id, limit=5)
        
        return jsonify({
            'success': True,
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'recent_questions': recent_questions
        })
        
    except Exception as e:
        print(f"Error in register endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user/history/<int:user_id>', methods=['GET'])
def get_user_history(user_id):
    """Get user's chat history"""
    try:
        history = db_manager.get_user_history(user_id, limit=10)
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages
    1. Check predefined Q&A
    2. Search vector database
    3. Generate response using Groq LLM
    4. Save message to database
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Step 1: Check predefined Q&A
        predefined_answer = find_matching_answer(user_message)
        if predefined_answer:
            # Save to database if user_id provided
            if user_id:
                db_manager.save_chat_message(user_id, user_message, predefined_answer, 'predefined')
            
            return jsonify({
                'success': True,
                'response': predefined_answer,
                'source': 'predefined',
                'metadata': {
                    'type': 'static_qa'
                }
            })
        
        # Step 2: Search vector database for relevant content
        relevant_docs = vector_store.search(user_message, n_results=3)
        
        if not relevant_docs or len(relevant_docs) == 0:
            # If no relevant content, try scraping more pages
            print("No relevant content found. Attempting additional scraping...")
            new_scraped_data = scraper.scrape_website(max_pages=5)
            if new_scraped_data:
                vector_store.add_scraped_content(new_scraped_data)
                relevant_docs = vector_store.search(user_message, n_results=3)
        
        # Step 3: Generate response using Groq LLM with retrieved context
        context = "\n\n".join([doc['text'] for doc in relevant_docs])
        
        system_prompt = """You are a helpful customer service assistant for E2M Solutions, a white label partner for digital agencies. 
You provide accurate, friendly, and professional responses about the company's services, billing, and offerings.
Use the provided context to answer questions accurately. If the context doesn't contain relevant information, 
provide a helpful general response and suggest contacting E2M Solutions directly for specific details."""

        user_prompt = f"""Context from E2M Solutions website:
{context}

User question: {user_message}

Please provide a helpful and accurate response based on the context above."""

        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",  # Using Groq's Llama model
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = chat_completion.choices[0].message.content
        
        
        # Check if the response suggests contacting support or indicates lack of information
        support_phrases = [
            "i couldn't find",
            "i don't have",
            "i recommend",
            "please contact",
            "reach out",
            "get in touch",
            "couldn't find any information",
            "no information",
            "not available in the context",
            "not explicitly mentioned",
            "it seems like",
            "i'd be happy to help",
            "no direct reference"
        ]
        
        suggest_support = any(phrase in response_text.lower() for phrase in support_phrases)
        
        # If suggesting support, append a clear CTA
        if suggest_support:
            response_text += "\n\n**Click the 'Need Help?' button below to connect with our team or create a support ticket.**"

        # Save to database if user_id provided
        if user_id:
            db_manager.save_chat_message(user_id, user_message, response_text, 'rag')
        
        return jsonify({
            'success': True,
            'response': response_text,
            'source': 'rag',
            'suggest_support': suggest_support,
            'metadata': {
                'type': 'generated',
                'num_sources': len(relevant_docs),
                'sources': [{'url': doc['metadata'].get('url'), 'title': doc['metadata'].get('title')} for doc in relevant_docs]
            }
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    """Manually trigger website scraping"""
    try:
        scraped_data = scraper.scrape_website(max_pages=10)
        chunks_added = vector_store.add_scraped_content(scraped_data)
        
        return jsonify({
            'success': True,
            'message': f'Scraped {len(scraped_data)} pages, added {chunks_added} chunks to vector store'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about vector store"""
    try:
        return jsonify({
            'success': True,
            'stats': {
                'total_chunks': vector_store.get_collection_count(),
                'predefined_questions': len(get_all_questions())
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/leads', methods=['GET'])
def get_leads():
    """Get all leads for admin dashboard"""
    try:
        leads = db_manager.get_all_leads()
        
        return jsonify({
            'success': True,
            'leads': leads
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get analytics for admin dashboard"""
    try:
        stats = db_manager.get_analytics()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/support/ticket', methods=['POST'])
def create_support_ticket():
    """Create a new support ticket and send email notification"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        if not user_id or not subject or not message:
            return jsonify({
                'success': False,
                'error': 'user_id, subject, and message are required'
            }), 400
        
        # Get user details
        user = db_manager.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Create ticket
        ticket = db_manager.create_support_ticket(user_id, subject, message)
        
        # Get SMTP settings and send email
        smtp_settings = db_manager.get_smtp_settings()
        if smtp_settings:
            try:
                email_sender = EmailSender(smtp_settings)
                email_sent = email_sender.send_support_ticket_email(
                    user.name,
                    user.email,
                    subject,
                    message,
                    ticket.id
                )
            except Exception as email_error:
                print(f"Error sending email: {str(email_error)}")
                email_sent = False
        else:
            print("SMTP settings not configured")
            email_sent = False
        
        return jsonify({
            'success': True,
            'ticket_id': ticket.id,
            'email_sent': email_sent,
            'message': 'Support ticket created successfully'
        })
        
    except Exception as e:
        print(f"Error creating support ticket: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/tickets', methods=['GET'])
def get_all_tickets():
    """Get all support tickets for admin dashboard"""
    try:
        tickets = db_manager.get_all_tickets()
        
        return jsonify({
            'success': True,
            'tickets': tickets
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/smtp-settings', methods=['GET'])
def get_smtp_settings():
    """Get SMTP settings (excluding password)"""
    try:
        settings = db_manager.get_smtp_settings()
        
        if settings:
            return jsonify({
                'success': True,
                'settings': settings.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'SMTP settings not configured'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/smtp-settings', methods=['POST'])
def update_smtp_settings():
    """Update SMTP settings"""
    try:
        data = request.get_json()
        
        sender_email = data.get('sender_email', '').strip()
        smtp_server = data.get('smtp_server', '').strip()
        smtp_port = data.get('smtp_port')
        smtp_username = data.get('smtp_username', '').strip()
        smtp_password = data.get('smtp_password', '').strip()
        use_ssl = data.get('use_ssl', False)
        recipient_email = data.get('recipient_email', '').strip()
        
        # Check required fields (password is optional for updates)
        if not all([sender_email, smtp_server, smtp_port, smtp_username, recipient_email]):
            return jsonify({
                'success': False,
                'error': 'All fields except password are required'
            }), 400
        
        # If password is empty, get existing password
        if not smtp_password:
            existing_settings = db_manager.get_smtp_settings()
            if existing_settings:
                smtp_password = existing_settings.smtp_password
            else:
                return jsonify({
                    'success': False,
                    'error': 'Password is required for initial setup'
                }), 400
        
        settings = db_manager.update_smtp_settings(
            sender_email,
            smtp_server,
            smtp_port,
            smtp_username,
            smtp_password,
            use_ssl,
            recipient_email
        )
        
        return jsonify({
            'success': True,
            'message': 'SMTP settings updated successfully',
            'settings': settings.to_dict()
        })
        
    except Exception as e:
        print(f"Error updating SMTP settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/admin/test-email', methods=['POST'])
def send_test_email():
    """Send a test email to verify SMTP configuration"""
    try:
        data = request.get_json()
        recipient = data.get('recipient_email', '').strip()
        
        if not recipient:
            return jsonify({
                'success': False,
                'error': 'Recipient email is required'
            }), 400
        
        # Get SMTP settings
        smtp_settings = db_manager.get_smtp_settings()
        if not smtp_settings:
            return jsonify({
                'success': False,
                'error': 'SMTP settings not configured'
            }), 404
        
        # Send test email
        try:
            email_sender = EmailSender(smtp_settings)
            
            # Create a test ticket for demonstration
            email_sent = email_sender.send_support_ticket_email(
                user_name='Test User',
                user_email=recipient,
                subject='Test Email - SMTP Configuration',
                message='This is a test email to verify your SMTP configuration is working correctly. If you receive this email, your settings are configured properly!',
                ticket_id=0
            )
            
            if email_sent:
                return jsonify({
                    'success': True,
                    'message': f'Test email sent successfully to {recipient}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to send test email'
                }), 500
                
        except Exception as email_error:
            print(f"Error sending test email: {str(email_error)}")
            return jsonify({
                'success': False,
                'error': f'Email sending failed: {str(email_error)}'
            }), 500
        
    except Exception as e:
        print(f"Error in test email endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"Starting Smart Chatbot API on port {port}...")
    print(f"Vector store has {vector_store.get_collection_count()} chunks")
    app.run(debug=True, host='0.0.0.0', port=port)
