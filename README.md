🌀 ScrumFlow — a lightweight Scrum management web app for sprint planning and team collaboration.
Shows project hierarchy: goals → monthly → weekly → daily tasks.
Includes progress tracking and meeting scheduling.
Built for a Team Project university course (React, FastAPI, SQLite3, Docker).

---

## 🎯 Project Purpose

The purpose of this project is to **create a useful web application for team collaboration** and to successfully complete our **Team Project course** by demonstrating our **cohesion, organization, and teamwork**.  

Additionally, we aim to **gain experience in working as a team**, **designing effective sprint plans**, and **following them consistently** throughout the development process.

---

## 👥 Team Roles

**Kyrylo Levonchuk, Kyrylo Vasyliev** — Backend Developers  
- Authentication  
- Database  
- API & Routing  

**Artem Ratushnyi, Marup Khashimov** — Frontend Developers  
- User Interface Design
- React Components
- Responsive Design

**Oleksandr Knyshuk** - CI/CD Engineer
- Docker Deployment
- GitHub Actions
- Infrastructure Management

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 20.x or higher
- **Python** 3.11 or higher
- **Docker** and **Docker Compose** (optional, for containerized setup)
- **Git** for version control

### Local Development Setup

#### Option 1: Docker Compose (Recommended)

The easiest way to run the entire stack:

```bash
# Clone the repository
git clone <repository-url>
cd TeamProject

# Start all services (backend + frontend)
docker-compose -f docker-compose.dev.yml up

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:3000
```

#### Option 2: Manual Setup

**Backend Setup:**

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Setup:**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Start the development server
npm run dev
```

### Running Tests

**Backend Tests:**

```bash
cd backend
pytest                    # Run all tests
pytest --cov=app         # Run tests with coverage
pytest -v                # Verbose output
```

**Frontend Tests:**

```bash
cd frontend
npm run test             # Run tests
npm run test:coverage    # Run tests with coverage
npm run test:ui          # Run tests with UI
```

### Code Quality & Linting

**Backend:**

```bash
cd backend
black .                  # Format code
flake8 .                # Lint code
mypy app                # Type checking
```

**Frontend:**

```bash
cd frontend
npm run format          # Format code with Prettier
npm run lint            # Lint code with ESLint
npm run lint:fix        # Auto-fix linting issues
```

---

## 🏗️ Project Structure

```
TeamProject/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database configuration
│   │   ├── models/         # SQLAlchemy models
│   │   └── main.py         # Application entry point
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend Docker image
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── tests/         # Frontend tests
│   ├── package.json       # Node dependencies
│   └── Dockerfile         # Frontend Docker image
│
├── db/                    # Database files (SQLite)
├── .github/
│   └── workflows/         # CI/CD pipelines
├── docker-compose.yml     # Production compose
└── docker-compose.dev.yml # Development compose
```

---

## 🔄 CI/CD Pipeline

Our project uses GitHub Actions for continuous integration and deployment:

### Workflows

1. **Backend CI** (`backend-ci.yml`)
   - Runs on push/PR to backend files
   - Linting (Black, Flake8, MyPy)
   - Unit tests with coverage
   - Docker build and test

2. **Frontend CI** (`frontend-ci.yml`)
   - Runs on push/PR to frontend files
   - Linting (ESLint, Prettier)
   - Type checking (TypeScript)
   - Unit tests with coverage
   - Docker build and test

3. **Pull Request Checks** (`pr-checks.yml`)
   - Validates PR title format
   - Checks for merge conflicts
   - Runs security scans
   - Enforces code quality

4. **Deploy to Staging** (`deploy-staging.yml`)
   - Deploys `develop` branch to staging
   - Builds and pushes Docker images
   - Automatic deployment

5. **Deploy to Production** (`deploy-production.yml`)
   - Deploys `main` branch to production
   - Runs integration tests
   - Builds and pushes Docker images
   - Manual approval required

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches

---

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Building Individual Images

```bash
# Build backend
docker build -t scrumflow-backend ./backend

# Build frontend
docker build -t scrumflow-frontend ./frontend
```

### Environment Variables

Both services use environment variables for configuration:

**Backend** (`.env` in `backend/`):
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret key
- `ALLOWED_ORIGINS` - CORS allowed origins

**Frontend** (`.env` in `frontend/`):
- `VITE_API_URL` - Backend API URL
- `VITE_APP_NAME` - Application name
- `VITE_APP_VERSION` - Application version

---

## 📊 Database Migrations

We use Alembic for database migrations:

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

---

## 🤝 Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Ensure all tests pass
4. Run linters and formatters
5. Submit a pull request with conventional commit format

### Commit Message Format

```
type: description

Types: feat, fix, docs, style, refactor, test, chore, ci
Example: feat: add user authentication endpoint
```

---

## 📝 API Documentation

Once the backend is running, API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Troubleshooting

### Common Issues

**Backend won't start:**
- Check if port 8000 is available
- Ensure virtual environment is activated
- Verify all dependencies are installed

**Frontend won't start:**
- Check if port 3000 is available
- Delete `node_modules` and run `npm install` again
- Clear npm cache: `npm cache clean --force`

**Docker issues:**
- Ensure Docker daemon is running
- Check available disk space
- Try rebuilding images: `docker-compose build --no-cache`

---

## 📄 License

This project is created for educational purposes as part of a university Team Project course.

---

## 👨‍💻 Development Team

Built with dedication by the ScrumFlow team:
- Backend: Kyrylo Levonchuk, Kyrylo Vasyliev
- Frontend: Artem Ratushnyi, Marup Khashimov
- CI/CD: Oleksandr Knyshuk
