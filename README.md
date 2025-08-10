# ISOLAB Agri Support

A comprehensive Flask-based web application for managing agricultural equipment, clients, and workflow processes. Built with Firebase/Firestore backend and role-based access control.
 run
## 🌟 Features

### Core Functionality
- **Client Management** - Complete client database with contact information and location tracking
- **Machine Management** - Track agricultural equipment through entire lifecycle
- **Workflow System** - Multi-stage workflow management (Assembly → Testing → Delivery)
- **User Management** - Role-based access control with different permission levels
- **Dashboard Analytics** - Real-time statistics and task management

### User Roles
- **Admin** - Full system access, user management, client management
- **Supervisor** - Workflow oversight and team management
- **Assembly Tech** - Assembly stage operations
- **Testing Tech** - Quality control and testing procedures
- **Delivery Manager** - Delivery coordination and logistics

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Firebase project with Firestore enabled
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "ISOLAB project"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Firebase**
   - Download your Firebase service account key
   - Place it in `config/` directory
   - Update the path in `blueprints/firebase_config.py`

5. **Set up environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open http://localhost:5000
   - Default admin credentials: admin/admin123

## 🐳 Docker Deployment

### Build and Run
```bash
# Build the image
docker build -t isolab-agri-support .

# Run with Docker Compose
docker-compose up -d
```

### Production Deployment
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

## ☁️ Google Cloud Deployment

### App Engine Deployment
```bash
# Install Google Cloud SDK
gcloud init

# Deploy to App Engine
gcloud app deploy app.yaml

# Deploy with environment variables
gcloud app deploy app.yaml env_variables.yaml
```

### Configuration
- Update `app.yaml` with your project settings
- Configure `env_variables.yaml` with production values
- Ensure Firebase credentials are properly set

## 📁 Project Structure

```
ISOLAB project/
├── app.py                 # Main Flask application
├── blueprints/           # Application modules
│   ├── clients.py        # Client management
│   ├── machines.py       # Machine management
│   ├── users.py          # User management
│   ├── workflow.py       # Workflow system
│   ├── dashboard.py      # Dashboard and analytics
│   ├── login.py          # Authentication
│   ├── stages.py         # Workflow stages
│   └── firebase_config.py # Firebase configuration
├── static/              # Static assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   ├── templates/      # HTML templates
│   │   ├── dashboard.html
│   │   ├── clients.html
│   │   ├── voir-machines.html
│   │   └── users.html
│   └── images/         # Images and icons
├── config/             # Configuration files
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose setup
├── app.yaml          # Google App Engine config
└── README.md         # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# Firebase Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=config/your-service-account.json

# Application Settings
APP_NAME=ISOLAB Agri Support
SUPPORT_EMAIL=support@isolab.com
```

### Firebase Setup
1. Create a Firebase project
2. Enable Firestore database
3. Create service account with admin privileges
4. Download service account key JSON file
5. Place in `config/` directory

## 📊 Database Schema

### Collections
- **users** - User accounts and roles
- **clients** - Client information and contacts
- **machines** - Equipment tracking and status
- **stages** - Workflow stage definitions
- **machine_history** - Audit trail and workflow progression

### Sample Data Structure
```json
{
  "machines": {
    "machine_id": {
      "serialNumber": "OLIVIA-001",
      "ficheNumber": "FT-001",
      "machineType": "Olivia Standard",
      "clientId": "client_id",
      "currentStage": "assembly",
      "status": "active"
    }
  }
}
```

## 🛠️ Development

### Adding New Features
1. Create new blueprint in `blueprints/`
2. Add routes and business logic
3. Create corresponding templates
4. Add navigation in templates
5. Update requirements if needed

### Testing
```bash
# Run tests (when available)
python -m pytest tests/

# Manual testing with sample data
python scripts/seed_database.py
```

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

## 🔒 Security

### Authentication
- Session-based authentication
- Role-based access control
- Password hashing with secure algorithms

### Data Protection
- HTTPS enforcement in production
- Firebase security rules
- Input validation and sanitization

### Best Practices
- Environment variables for sensitive data
- Regular security updates
- Audit logging for critical operations

## 📈 Monitoring & Analytics

### Health Checks
- Application health endpoints
- Database connectivity monitoring
- Performance metrics

### Logging
- Structured logging with levels
- Error tracking and alerting
- User activity auditing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test thoroughly
4. Commit with descriptive messages: `git commit -m "Add new feature"`
5. Push to your fork: `git push origin feature/new-feature`
6. Create a Pull Request

### Development Guidelines
- Write tests for new functionality
- Update documentation as needed
- Follow existing code patterns
- Ensure backward compatibility

## 📞 Support

### Getting Help
- **Email**: support@isolab.com
- **Documentation**: See inline code comments
- **Issues**: Create GitHub issues for bugs

### Common Issues
- **Firebase Connection**: Check service account credentials
- **Permission Denied**: Verify user roles and Firebase rules
- **Build Failures**: Ensure all dependencies are installed

## 📄 License

This project is proprietary software developed for ISOLAB Agri Support. All rights reserved.

## 🔄 Version History

### v1.0.0 (Current)
- Initial release with core functionality
- Client and machine management
- Multi-stage workflow system
- Role-based access control
- Dashboard and analytics

### Planned Features
- Mobile responsive design
- API documentation
- Advanced reporting
- Email notifications
- Backup and restore functionality

---

**ISOLAB Agri Support** - Système de gestion pour équipements agricoles