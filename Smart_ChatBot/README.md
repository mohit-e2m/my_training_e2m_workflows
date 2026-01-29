# Smart Chatbot with Lead Collection

A professional chatbot system with integrated lead collection and management dashboard.

## Features

- ✅ **User Registration** - Collects name and email before chat access
- ✅ **Chat History Tracking** - Saves all conversations to database
- ✅ **Admin Dashboard** - View leads, chat history, and analytics
- ✅ **RAG-Powered Responses** - Uses ChromaDB and embeddings for intelligent answers
- ✅ **Predefined Questions** - Quick access to common queries
- ✅ **CSV Export** - Export all leads for CRM integration

## Quick Start

### Single Command Startup (Recommended)

```bash
cd /Users/developer/Desktop/my_training_e2m_workflows/Smart_ChatBot
./start.sh
```

This will start both backend and frontend servers automatically.

### Access Points

- **Main Application**: http://localhost:8000/index.html
- **Admin Dashboard**: http://localhost:8000/admin.html
- **Backend API**: http://localhost:5000

### Admin Access

1. Click "Admin" link in the navigation menu
2. Enter credentials:
   - **Username**: `admin`
   - **Password**: `admin`

## Manual Startup (Alternative)

If you prefer to run servers separately:

### Backend Server

```bash
cd backend
source venv/bin/activate
python3 app.py
```

Backend runs on: http://localhost:5000

### Frontend Server

```bash
cd frontend
python3 server.py
```

Frontend runs on: http://localhost:8000

## Project Structure

```
Smart_ChatBot/
├── backend/
│   ├── app.py              # Flask API server
│   ├── database.py         # SQLAlchemy models and DB manager
│   ├── requirements.txt    # Python dependencies
│   ├── chatbot.db         # SQLite database (auto-created)
│   └── venv/              # Python virtual environment
├── frontend/
│   ├── index.html         # Main chatbot page
│   ├── admin.html         # Admin dashboard
│   ├── script.js          # Chatbot logic
│   ├── admin.js           # Admin dashboard logic
│   ├── styles.css         # Main styles
│   ├── admin.css          # Admin styles
│   └── server.py          # No-cache HTTP server
└── start.sh               # Startup script
```

## Database Schema

### Users Table
- `id` - Primary key
- `name` - User's name
- `email` - User's email (unique)
- `created_at` - Registration timestamp
- `last_active` - Last activity timestamp

### Chat Messages Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `question` - User's question
- `answer` - Bot's response
- `source` - Response source ('predefined' or 'rag')
- `timestamp` - Message timestamp

## API Endpoints

### User Endpoints
- `POST /api/user/register` - Register new user
- `GET /api/user/history/<user_id>` - Get user's chat history

### Chat Endpoint
- `POST /api/chat` - Send message and get response

### Admin Endpoints
- `GET /api/admin/leads` - Get all leads
- `GET /api/admin/stats` - Get statistics

### Questions Endpoint
- `GET /api/questions` - Get predefined questions

## Browser Caching Fix

The frontend server (`server.py`) includes cache control headers to prevent browser caching issues during development:

```python
Cache-Control: no-store, no-cache, must-revalidate, max-age=0
Pragma: no-cache
Expires: 0
```

If you still see old content:
1. Hard refresh: `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows/Linux)
2. Clear browser cache
3. Use incognito/private mode

## Customization

### Change Admin Credentials

Edit `frontend/script.js`, find the `openAdminLogin` function:

```javascript
if (username === 'admin' && password === 'admin') {
    // Change 'admin' to your desired credentials
}
```

### Modify Welcome Messages

Edit `frontend/index.html`:
- Line 117: Registration welcome message
- Line 144: Chat welcome message

### Update Company Information

Edit `backend/app.py` to change the website URLs being scraped:

```python
urls_to_scrape = [
    'https://www.e2msolutions.com/',
    'https://www.e2msolutions.com/services',
    # Add your URLs here
]
```

## Troubleshooting

### Port Already in Use

```bash
# Kill processes on port 5000 and 8000
lsof -ti:5000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### Database Issues

Delete the database file to reset:

```bash
rm backend/chatbot.db
```

The database will be recreated on next startup.

### Backend Not Starting

Make sure virtual environment is activated and dependencies are installed:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

## Dependencies

### Backend
- Flask 3.0.0
- Flask-CORS 4.0.0
- chromadb 0.4.22
- sentence-transformers 2.2.2
- SQLAlchemy 2.0.25
- beautifulsoup4 4.12.2
- requests 2.31.0

### Frontend
- No external dependencies
- Uses vanilla JavaScript, HTML, and CSS

## Production Deployment

For production use:

1. **Change admin credentials** to strong passwords
2. **Use PostgreSQL** instead of SQLite
3. **Add proper authentication** for admin dashboard
4. **Use HTTPS** for all connections
5. **Set up proper CORS** policies
6. **Use production WSGI server** (gunicorn, uWSGI)
7. **Add rate limiting** to prevent abuse

## License

MIT License - Feel free to use and modify for your projects.

## Support

For issues or questions, contact your development team.
