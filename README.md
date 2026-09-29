# Anti-Generic Engine

An AI-powered idea analysis and refinement platform designed to help users examine ideas, identify assumptions, discover tensions, and develop stronger project concepts.

## 🚀 Live Demo

https://anti-generic-engine.vercel.app

## 📌 About the Project

Anti-Generic Engine is a full-stack AI application that acts as a thinking and decision-support tool.

Instead of simply generating generic ideas, the platform analyzes an idea and helps users explore:

- Originality and differentiation
- Potential challenges and tensions
- Key assumptions
- Opportunities for refinement
- Practical considerations
- Areas that may require deeper validation

Users can create an account, sign in, submit ideas, and continue working with their saved projects.

> **🔐 Important Note – Login & Usage:**  
> Users can create an account and log in using the same email/username and password they provided during registration. The email/username field does not require a real Gmail account; values such as `user@example.com` can be used as an example. The same credentials can be used to access the account from different devices.
> ## Judge Login Credentials

### Important Note for Judges

The Judge Login section was available in the version shown in our demonstration video. After the video was recorded, the Judge Login section was removed from the deployed website to avoid displaying the credentials directly on the website.

The application is successfully deployed and working. The credentials below are provided only for the purpose of hackathon evaluation.

**Judge Email:** judge@antigeneric.app 
**Judge Password:** Inkloom-Judge-2026

> The current deployed website may look slightly different from the version shown in the demonstration video because the Judge Login section was removed afterward for security and privacy reasons.
>
> **💳 Usage & Charges:**  
> The platform provides limited usage for regular users, while judges have designated access for project evaluation. Usage limits and applicable charges may vary depending on the type of user and platform usage.

## ✨ Key Features

- User registration and login
- Secure authentication
- AI-powered idea analysis
- Project persistence
- Recent project history
- Conversation-based refinement
- Judge/demo access
- MongoDB data storage
- Responsive web interface
- Deployed full-stack application

## 🧠 AI Integration

The application uses the Groq API to process user ideas and generate structured analysis and refinement responses.

## 🛠️ Technology Stack

### Frontend
- JavaScript
- HTML
- CSS

### Backend
- Python
- FastAPI

### Database
- MongoDB

### AI
- Groq API

### Deployment
- Vercel
- Render

## 🔐 Authentication

The application supports:

- New user registration
- Existing user sign-in
- User-specific saved projects
- Judge/demo access

Authentication-related credentials and API keys are stored using environment variables and are not included in the repository.

## 📂 Project Structure

```text
Anti-Generic-Engine/
│
├── frontend/
│   └── Frontend application
│
├── backend/
│   └── FastAPI backend
│
├── .gitignore
├── README.md
├── vercel.json
└── yarn.lock
