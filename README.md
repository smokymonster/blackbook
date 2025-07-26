# Blackbook Production - SAT Test Platform

A comprehensive web-based SAT test preparation platform built with Flask, featuring interactive test-taking, question management, and AI-powered question analysis.

## 🚀 Features

- **Interactive SAT Testing**: Full-featured SAT test simulation with timed modules
- **Question Bank Management**: Extensive database of SAT questions organized by test date and form
- **AI-Powered Analysis**: Automatic question classification and difficulty assessment using OpenAI
- **User Authentication**: Secure login/registration system
- **Progress Tracking**: Bookmark questions, save answers, and track performance
- **Multiple Test Forms**: Support for various SAT test forms (US/International, different dates)
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🏗️ Architecture

### Backend
- **Flask**: Python web framework
- **MongoDB**: Database for question storage and user data
- **OpenAI API**: AI-powered question analysis and classification
- **Session Management**: Secure user session handling

### Frontend
- **HTML/CSS/JavaScript**: Responsive web interface
- **AJAX**: Dynamic content loading and navigation
- **Bootstrap**: UI framework for responsive design

## 📁 Project Structure

```
Blackbook Production/
├── app.py                 # Main Flask application
├── upload_db.py          # Question upload and processing utility
├── sat_routes.py         # SAT-specific route handlers
├── auth/                 # Authentication module
│   ├── __init__.py
│   └── routes.py
├── templates/            # HTML templates
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── SAT/             # SAT-specific templates
│   └── Bluebook/        # Test interface templates
├── static/              # Static assets
│   ├── images/
│   └── js/
├── sat/                 # SAT question data
│   ├── March 2025 US Form A/
│   ├── December 2024 International Form B/
│   └── ... (other test forms)
└── requirements.txt     # Python dependencies
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB instance
- OpenAI API key

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Blackbook Production"
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/your-database

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Server Configuration
HOST=0.0.0.0
PORT=8100
```

### 5. Database Setup
Ensure MongoDB is running and accessible with the connection string in your `.env` file.

### 6. Run the Application
```bash
# Development mode
python app.py

# Or with explicit Python path
.venv/bin/python app.py
```

The application will be available at:
- Local: http://127.0.0.1:8100
- Network: http://[your-ip]:8100

## 📊 Question Management

### Uploading Questions
Use the `upload_db.py` script to process and upload SAT questions:

```bash
python upload_db.py
```

This script will:
- Process all folders in the `sat/` directory
- Analyze questions using AI for skill classification
- Generate unique IDs across all collections
- Upload to appropriate MongoDB collections based on test date

### Question Format
Questions should be stored in JSON format with the following structure:

```json
{
  "question": "Question text here...",
  "article": "Context/passage if applicable",
  "options": [
    {"name": "A", "content": "Option A text"},
    {"name": "B", "content": "Option B text"},
    {"name": "C", "content": "Option C text"},
    {"name": "D", "content": "Option D text"}
  ],
  "correct": "A",
  "type": "mcq" // or "grid" for free response
}
```

## 🎯 Usage

### For Students
1. **Register/Login**: Create an account or log in
2. **Select Test**: Choose from available SAT test forms
3. **Take Test**: Navigate through questions, bookmark important ones
4. **Submit**: Review answers and submit when complete

### For Administrators
1. **Upload Questions**: Use the upload utility to add new test forms
2. **Monitor Usage**: Track student progress and performance
3. **Manage Content**: Add/remove test forms and questions

## 🔐 Security Features

- **Environment Variables**: Sensitive configuration stored in `.env`
- **Session Management**: Secure user sessions with CSRF protection
- **Input Validation**: All user inputs are validated and sanitized
- **Authentication**: Required for accessing test content

## 🌐 Deployment

### Local Network Access
The app is configured to run on `0.0.0.0:8100`, making it accessible from any device on your local network.

### Production Deployment
For production deployment, consider:
- Using a production WSGI server (Gunicorn, uWSGI)
- Setting up reverse proxy (nginx)
- Enabling HTTPS
- Using environment-specific configuration
- Setting up monitoring and logging

Example with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8100 app:app
```

## 📝 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### SAT Testing
- `GET /sat/test/<test_date>/<region>/<form>` - Start a test
- `GET /sat/test/question/<module>/<question>` - Get specific question
- `POST /sat/test/submit_answer` - Submit answer
- `POST /sat/test/navigate` - Navigate between questions
- `POST /toggle_bookmark` - Toggle question bookmark

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please contact [your-email@example.com] or create an issue in the repository.

## 🔄 Version History

- **v1.0.0** - Initial release with basic SAT testing functionality
- **v1.1.0** - Added AI-powered question analysis
- **v1.2.0** - Enhanced user interface and mobile responsiveness

---

**Note**: This is an educational tool designed to help students prepare for the SAT. All test content should be used in accordance with educational fair use policies.
