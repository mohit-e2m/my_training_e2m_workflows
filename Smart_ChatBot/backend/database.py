"""
Database Manager for Smart Chatbot
Handles user data and chat history storage using SQLAlchemy and SQLite
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database setup
DATABASE_URL = "sqlite:///chatbot.db"
Base = declarative_base()

# Models
class User(Base):
    """User model for storing lead information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to chat messages
    messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }


class ChatMessage(Base):
    """Chat message model for storing conversation history"""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source = Column(String(50))  # 'predefined' or 'rag'
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="messages")
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question': self.question,
            'answer': self.answer,
            'source': self.source,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class SupportTicket(Base):
    """Support ticket model for storing user support requests"""
    __tablename__ = 'support_tickets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default='open')  # 'open', 'in_progress', 'closed'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User")
    
    def to_dict(self):
        """Convert ticket to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SMTPSettings(Base):
    """SMTP settings model for email configuration"""
    __tablename__ = 'smtp_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_email = Column(String(255), nullable=False)
    smtp_server = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False)
    smtp_username = Column(String(255), nullable=False)
    smtp_password = Column(String(255), nullable=False)
    use_ssl = Column(Integer, default=0)  # 0 = False, 1 = True
    recipient_email = Column(String(255), nullable=False)  # Email to receive tickets
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert settings to dictionary (excluding password)"""
        return {
            'id': self.id,
            'sender_email': self.sender_email,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'smtp_username': self.smtp_username,
            'use_ssl': bool(self.use_ssl),
            'recipient_email': self.recipient_email,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Database manager class
class DatabaseManager:
    """Manages database operations for the chatbot"""
    
    def __init__(self, db_url=DATABASE_URL):
        """Initialize database connection"""
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
    def init_db(self):
        """Initialize database and create tables"""
        Base.metadata.create_all(self.engine)
        print("Database initialized successfully")
        
    def create_user(self, name, email):
        """
        Create a new user or return existing user by email
        
        Args:
            name (str): User's name
            email (str): User's email
            
        Returns:
            User: User object
        """
        session = self.Session()
        try:
            # Check if user already exists
            user = session.query(User).filter_by(email=email).first()
            
            if user:
                # Update last active time
                user.last_active = datetime.utcnow()
                session.commit()
                # Refresh to ensure all attributes are loaded
                session.refresh(user)
            else:
                # Create new user
                user = User(name=name, email=email)
                session.add(user)
                session.commit()
                # Refresh to ensure all attributes are loaded
                session.refresh(user)
            
            # Make user object persistent by expunging from session
            session.expunge(user)
            return user
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_chat_message(self, user_id, question, answer, source='rag'):
        """
        Save a chat message to the database
        
        Args:
            user_id (int): User's ID
            question (str): User's question
            answer (str): Bot's answer
            source (str): Source of answer ('predefined' or 'rag')
            
        Returns:
            ChatMessage: Saved message object
        """
        session = self.Session()
        try:
            message = ChatMessage(
                user_id=user_id,
                question=question,
                answer=answer,
                source=source
            )
            session.add(message)
            
            # Update user's last active time
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.last_active = datetime.utcnow()
            
            session.commit()
            return message
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_user_history(self, user_id, limit=5):
        """
        Get user's recent chat history
        
        Args:
            user_id (int): User's ID
            limit (int): Number of recent messages to retrieve
            
        Returns:
            list: List of message dictionaries
        """
        session = self.Session()
        try:
            messages = session.query(ChatMessage)\
                .filter_by(user_id=user_id)\
                .order_by(ChatMessage.timestamp.desc())\
                .limit(limit)\
                .all()
            
            return [msg.to_dict() for msg in messages]
            
        finally:
            session.close()
    
    def get_all_leads(self):
        """
        Get all users (leads) with their message counts
        
        Returns:
            list: List of user dictionaries with message counts
        """
        session = self.Session()
        try:
            users = session.query(User).all()
            
            leads = []
            for user in users:
                user_dict = user.to_dict()
                user_dict['message_count'] = len(user.messages)
                leads.append(user_dict)
            
            return leads
            
        finally:
            session.close()
    
    def get_analytics(self):
        """
        Get analytics data for admin dashboard
        
        Returns:
            dict: Analytics data including total users, messages, top questions
        """
        session = self.Session()
        try:
            total_users = session.query(User).count()
            total_messages = session.query(ChatMessage).count()
            
            # Get top 10 most asked questions
            from sqlalchemy import func
            top_questions = session.query(
                ChatMessage.question,
                func.count(ChatMessage.question).label('count')
            ).group_by(ChatMessage.question)\
             .order_by(func.count(ChatMessage.question).desc())\
             .limit(10)\
             .all()
            
            # Get recent activity (last 10 messages)
            recent_activity = session.query(ChatMessage)\
                .order_by(ChatMessage.timestamp.desc())\
                .limit(10)\
                .all()
            
            return {
                'total_users': total_users,
                'total_messages': total_messages,
                'top_questions': [{'question': q[0], 'count': q[1]} for q in top_questions],
                'recent_activity': [msg.to_dict() for msg in recent_activity]
            }
            
        finally:
            session.close()
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID
        
        Args:
            user_id (int): User's ID
            
        Returns:
            User: User object or None
        """
        session = self.Session()
        try:
            return session.query(User).filter_by(id=user_id).first()
        finally:
            session.close()
    
    def create_support_ticket(self, user_id, subject, message):
        """
        Create a new support ticket
        
        Args:
            user_id (int): User's ID
            subject (str): Ticket subject
            message (str): Ticket message
            
        Returns:
            SupportTicket: Created ticket object
        """
        session = self.Session()
        try:
            ticket = SupportTicket(
                user_id=user_id,
                subject=subject,
                message=message
            )
            session.add(ticket)
            session.commit()
            session.refresh(ticket)
            session.expunge(ticket)
            return ticket
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_tickets(self):
        """
        Get all support tickets
        
        Returns:
            list: List of ticket dictionaries
        """
        session = self.Session()
        try:
            tickets = session.query(SupportTicket)\
                .order_by(SupportTicket.created_at.desc())\
                .all()
            return [ticket.to_dict() for ticket in tickets]
        finally:
            session.close()
    
    def get_smtp_settings(self):
        """
        Get SMTP settings (returns first record or None)
        
        Returns:
            SMTPSettings: SMTP settings object or None
        """
        session = self.Session()
        try:
            return session.query(SMTPSettings).first()
        finally:
            session.close()
    
    def update_smtp_settings(self, sender_email, smtp_server, smtp_port, 
                            smtp_username, smtp_password, use_ssl, recipient_email):
        """
        Update or create SMTP settings
        
        Args:
            sender_email (str): Sender email address
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP port
            smtp_username (str): SMTP username
            smtp_password (str): SMTP password
            use_ssl (bool): Whether to use SSL
            recipient_email (str): Email to receive tickets
            
        Returns:
            SMTPSettings: Updated settings object
        """
        session = self.Session()
        try:
            settings = session.query(SMTPSettings).first()
            
            if settings:
                # Update existing settings
                settings.sender_email = sender_email
                settings.smtp_server = smtp_server
                settings.smtp_port = smtp_port
                settings.smtp_username = smtp_username
                settings.smtp_password = smtp_password
                settings.use_ssl = 1 if use_ssl else 0
                settings.recipient_email = recipient_email
                settings.updated_at = datetime.utcnow()
            else:
                # Create new settings
                settings = SMTPSettings(
                    sender_email=sender_email,
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    smtp_username=smtp_username,
                    smtp_password=smtp_password,
                    use_ssl=1 if use_ssl else 0,
                    recipient_email=recipient_email
                )
                session.add(settings)
            
            session.commit()
            session.refresh(settings)
            session.expunge(settings)
            return settings
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def init_default_smtp_settings(self):
        """Initialize default SMTP settings if none exist"""
        session = self.Session()
        try:
            existing = session.query(SMTPSettings).first()
            if not existing:
                default_settings = SMTPSettings(
                    sender_email='mohit.pillai@e2m.solutions',
                    smtp_server='mail.infomaniak.com',
                    smtp_port=587,
                    smtp_username='mohit.pillai@e2m.solutions',
                    smtp_password='X-3ReJh-H8u%CcEh',
                    use_ssl=0,
                    recipient_email='rudra.joshi@e2m.solutions'
                )
                session.add(default_settings)
                session.commit()
                print("Default SMTP settings initialized")
        except Exception as e:
            session.rollback()
            print(f"Error initializing SMTP settings: {e}")
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()
