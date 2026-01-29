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


# Global database manager instance
db_manager = DatabaseManager()
