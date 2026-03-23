# Nazrul's Blog

A modern, full-featured blogging platform built with Flask.

## Features

- 🔐 User Authentication (Register, Login, Logout)
- ✍️ Create, Edit, Delete Posts
- 💬 Comments with Nested Replies
- ❤️ Like System (Posts & Comments)
- 🔍 Search Functionality
- 📄 Pagination
- 👤 User Profiles with Gravatar
- 🛡️ Admin Dashboard
- 🔒 Security Features (CSRF, Rate Limiting, Password Validation)
- 📱 Fully Responsive Design

## Tech Stack

- **Backend:** Flask, SQLAlchemy, PostgreSQL
- **Frontend:** Bootstrap 5, JavaScript
- **Security:** Flask-WTF, Flask-Limiter, Flask-Talisman
- **Authentication:** Flask-Login, Flask-Bcrypt

## Local Development

1. Clone the repository
```bash
git clone <your-repo-url>
cd blogpost1
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your SECRET_KEY
```

5. Run the application
```bash
python run.py
```

Visit `http://localhost:5000`

## Deployment

Deployed on [Railway](https://railway.app)

## Author

Nazrul Haque

## License

MIT