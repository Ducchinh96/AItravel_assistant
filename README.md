# Travles - Travel Assistant Project

## Overview
Travles is a Django-based travel assistant application that provides AI-powered travel recommendations and chat functionality. The application integrates with the Groq API to provide intelligent travel suggestions based on user input.

## Core Technologies
- **Python 3.8+**
- **Django 5.1.1** - Web framework
- **MySQL** - Database
- **Django REST Framework** - API development
- **Groq API** - AI integration for travel recommendations

## Project Structure

```
.
├── app/                 # Main Django application
│   ├── migrations/      # Database migration files
│   ├── utils/           # Utility functions (AI integration)
│   ├── admin.py         # Django admin configuration
│   ├── apps.py          # App configuration
│   ├── models.py        # Data models
│   ├── serializers.py   # Data serialization
│   ├── urls.py          # App URL routing
│   └── views.py         # View logic and API endpoints
├── travles/             # Django project settings
│   ├── settings.py      # Project configuration
│   ├── urls.py          # Main URL routing
│   └── wsgi.py          # WSGI deployment configuration
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── manage.py            # Django management script
```

## Key Features

1. **AI-Powered Travel Suggestions**
   - Intelligent travel recommendations based on user input
   - Detailed travel itineraries with schedules, dining options, and accommodation suggestions

2. **User Authentication**
   - User registration and login
   - JWT-based authentication
   - Password reset functionality

3. **Chat History**
   - Stores conversation history with the AI assistant
   - Retrieves previous conversations

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/suggest-trip/` | POST | Get AI-powered travel suggestions |
| `/api/chat-turns/history/<int:pk>/` | GET | Retrieve chat history |
| `/api/register/` | POST | User registration |
| `/api/login/` | POST | User login |
| `/api/logout/` | POST | User logout |

## Setup and Installation

### Prerequisites
- Python 3.8+
- MySQL database
- Groq API key

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd travles
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root with your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Database setup**
   ```bash
   # Create migrations
   python manage.py makemigrations
   
   # Apply migrations
   python manage.py migrate
   
   # Create a superuser (optional)
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - API endpoints: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Dependencies

See `requirements.txt` for a complete list of dependencies:

```
Django==5.1.1
djangorestframework==3.14.0
mysqlclient==2.2.0
python-dotenv==1.0.0
openai==1.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
```