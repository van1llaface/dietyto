# Longevity Diet App - Learning Roadmap

This is your step-by-step guide to building a complete web app. Each phase teaches you concepts AND builds working code.

## Why This Order?
Learning to code is like building a house:
- **Backend (Phase 1-2)** = foundations and walls (the server that stores data)
- **Frontend (Phase 3)** = walls and roof (what users see and interact with)
- **Integration (Phase 4)** = connecting everything together
- **Deployment (Phase 5)** = moving into the house (putting it online)

---

## Phase 1: Backend Basics (Week 1-2)
**What you'll learn**: How to create an API that responds to requests

### Concepts
- What is an API?
- What is FastAPI?
- How HTTP requests work (GET, POST)
- How to write your first endpoint

### Deliverables
- Working FastAPI server that responds to requests
- First 2-3 simple endpoints
- Understanding of how client-server communication works

### Files to Create
- `backend/requirements.txt` - Your Python dependencies
- `backend/app.py` - Your first API
- `backend/README.md` - How to run it

---

## Phase 2: Database & Models (Week 2-3)
**What you'll learn**: How to store and retrieve data

### Concepts
- What is a database?
- Relational databases (PostgreSQL)
- Database schema design
- ORM (Object-Relational Mapping) with SQLAlchemy
- Models: Recipe, User, NutritionInfo, MealPlan

### Deliverables
- Recipe database with 20 sample recipes
- User accounts system
- Endpoints to retrieve recipes

### Files to Create
- `backend/database.py` - Database connection
- `backend/models.py` - Data structures
- `backend/schemas.py` - Data validation
- Sample recipe data

---

## Phase 3: Frontend Basics (Week 3-4)
**What you'll learn**: How to build user interfaces with React

### Concepts
- What is React?
- Components and JSX
- State management
- Making API calls from frontend

### Deliverables
- Simple recipe list page
- Recipe detail page
- Basic meal planner page

### Files to Create
- `frontend/App.js` - Main React app
- `frontend/pages/Recipes.js`
- `frontend/pages/MealPlanner.js`
- `frontend/api/fetch.js` - Communication with backend

---

## Phase 4: Integration & Polish (Week 4-5)
**What you'll learn**: Making everything work together smoothly

### Concepts
- Authentication (login/logout)
- Error handling
- Loading states
- Data persistence

### Deliverables
- User login system
- Save meal plans
- Nutrition tracking dashboard

---

## Phase 5: Deployment (Week 5-6)
**What you'll learn**: Getting your app online

### Concepts
- Environment variables
- Production vs development
- Deploying backend and frontend
- Domain setup

### Deliverables
- Live app accessible via URL
- Both frontend and backend online

---

## How to Use This Roadmap

1. **Start with Phase 1, Step 1**
2. **Follow the "Why" explanations** to understand concepts
3. **Build the code** as shown
4. **Test it** (you'll have scripts to run)
5. **Move to next step only when current step works**
6. **Ask questions** - understanding is more important than speed

Each phase has a dedicated learning guide with:
- Concept explanations
- Code examples
- "Why this matters" sections
- Common mistakes to avoid
- Testing instructions

---

## Your Tech Stack (Explained)

| Component | Technology | Why? |
|-----------|-----------|------|
| Backend Server | FastAPI | Modern, fast, great for beginners, built-in API documentation |
| Language | Python | Readable, forgiving, great for learning |
| Database | PostgreSQL | Reliable, scalable, industry standard |
| Frontend | React | Most popular, best learning resources, mobile-friendly |
| Frontend Language | JavaScript/JSX | Powers interactive UIs |

---

## Prerequisites
Before starting, make sure you have:
- [ ] Python 3.9+ installed
- [ ] Node.js installed (for React)
- [ ] Git installed
- [ ] VS Code or your preferred editor
- [ ] Terminal/Command prompt comfort level: beginner is fine!

---

**Ready to start? Go to `PHASE_1_GETTING_STARTED.md`**
