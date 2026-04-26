# Phase 1: Backend Basics - Getting Started

## What We're Building
You're going to create a **web server** that:
1. Listens for requests (like a restaurant taking orders)
2. Processes them (like the kitchen preparing food)
3. Sends responses back (like serving the plate)

This is called an **API** (Application Programming Interface).

---

## What is an API?

Think of it this way:
- **Restaurant analogy**: 
  - You (client) order food from a waiter (API)
  - The waiter takes your order to the kitchen (server)
  - The kitchen prepares it and sends it back (server responds)
  - You get your food (response)

- **Technical terms**:
  - **Client** = Your frontend (React app on user's browser)
  - **API** = The waiter (rules for communication)
  - **Server** = The kitchen (processes requests, has data)
  - **Response** = The food you receive

---

## What is FastAPI?

FastAPI is a **Python framework** that makes creating APIs super easy.

| Without FastAPI | With FastAPI |
|-----------------|--------------|
| 50+ lines of code to start | 10 lines |
| Lots of manual setup | Automatic documentation |
| Hard to organize routes | Clear, organized routes |

**Why FastAPI?**
1. ✅ Fast to learn
2. ✅ Less boilerplate code
3. ✅ Automatic API docs (you'll see this!)
4. ✅ Built-in validation
5. ✅ Great error messages

---

## Step 1: Set Up Your Backend Environment

### Why we do this:
You need to install Python packages (libraries) in an isolated space so your project doesn't conflict with other projects on your computer. Think of it like a dedicated workspace.

### Step-by-step:

**1. Open Terminal/Command Prompt in your project folder**

Navigate to: `c:\Users\S3014G\Desktop\notes\lngvt\backend`

```bash
cd c:\Users\S3014G\Desktop\notes\lngvt\backend
```

**2. Create a Virtual Environment**

```bash
python -m venv venv
```

What this does:
- Creates a folder called `venv` with a fresh Python installation
- Keeps your project's packages isolated

**3. Activate the Virtual Environment**

On Windows:
```bash
venv\Scripts\activate
```

You should now see `(venv)` at the start of your terminal prompt.

**4. Create `requirements.txt`**

Create a file `requirements.txt` with this content:

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
```

**Why each package?**
- `fastapi` = the framework
- `uvicorn` = runs your server
- `pydantic` = validates data
- `python-multipart` = handles form data

**5. Install Dependencies**

```bash
pip install -r requirements.txt
```

Wait for it to finish. You should see "Successfully installed" messages.

**Troubleshooting:**
- If `pip install` fails, make sure your virtual environment is activated (you see `(venv)` in terminal)
- If Python isn't found, make sure Python 3.9+ is installed

---

## Step 2: Create Your First API

**Create a file:** `backend/app.py`

```python
from fastapi import FastAPI

# Create a FastAPI application
app = FastAPI()

# Define your first endpoint
@app.get("/")
def read_root():
    """
    This is the root endpoint.
    The @app.get("/") decorator means:
    - "get" = HTTP method (retrieving data)
    - "/" = the URL path (requests to http://localhost:8000/)
    """
    return {"message": "Welcome to the Longevity Diet API!"}

# Another endpoint example
@app.get("/health")
def health_check():
    """
    This endpoint is used to check if the server is running.
    Requests to http://localhost:8000/health will get a response.
    """
    return {"status": "healthy"}
```

**What this does:**
- Line 1: Imports FastAPI
- Line 4: Creates your app instance
- Line 7: `@app.get("/")` = decorator saying "when someone requests the root path with GET method, run this function"
- Line 8-12: The function that runs when the request comes in
- Lines 14-19: A second endpoint for health checking

---

## Step 3: Run Your Server

**In your terminal (make sure you're in backend folder and venv is activated):**

```bash
uvicorn app:main --reload
```

**Wait, what?**
- `uvicorn` = the server runner
- `app:main` = ??? (We'll fix this!)
- `--reload` = automatically restarts when you change code

### Oops! We need to fix the code first.

Edit `backend/app.py` and add this at the bottom:

```python
# Add this at the very bottom of app.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

**Now try again:**

```bash
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## Step 4: Test Your API

**Open your browser and visit:**
- http://localhost:8000/ → You'll see `{"message":"Welcome to the Longevity Diet API!"}`
- http://localhost:8000/health → You'll see `{"status":"healthy"}`

**But wait, there's more!** 

Go to: http://localhost:8000/docs

This is FastAPI's **automatic interactive documentation**. You can see all your endpoints and test them right here! This is one of FastAPI's superpowers.

---

## Step 5: Understanding Decorators (Why `@app.get()/`)

This might look weird if you haven't seen decorators before.

**What is `@app.get("/")`?**

It's Python syntax that says: "Register this function as an endpoint for GET requests to `/`"

Equivalent explanation:
```python
# What the decorator does behind the scenes:
@app.get("/")
def read_root():
    return {"message": "Welcome"}

# Is like doing this:
def read_root():
    return {"message": "Welcome"}

app.endpoints["/"] = read_root  # Register it
```

**Common HTTP methods:**
- `@app.get()` = Retrieve data (read-only)
- `@app.post()` = Create new data
- `@app.put()` = Update existing data
- `@app.delete()` = Remove data

---

## Checkpoint: What You Just Learned

✅ What an API is (recipes + the kitchen analogy)
✅ What FastAPI is (framework for building APIs)
✅ How to set up a Python virtual environment
✅ How to install packages with pip
✅ How to write your first FastAPI endpoint
✅ How to run your server
✅ How to test it in browser
✅ What decorators do

---

## Common Problems & Solutions

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError: fastapi" | Virtual environment not activated. Do `venv\Scripts\activate` |
| "Port 8000 already in use" | Change port: `uvicorn app:app --port 8001` |
| "No module pip" | Make sure Python 3.9+ is installed |
| Changes not taking effect | Make sure `--reload` is enabled |

---

## Next Steps

Once this is working and you understand it:
1. **Practice**: Add more endpoints (try creating a `/recipes` endpoint that returns a list)
2. **Read**: Review what `@app.get()` means until it clicks
3. **Experiment**: What happens if you change the message?
4. **When ready**: Move to "Phase 1, Step 2" for database setup

---

## Questions to Think About

Before moving forward, ask yourself:
- What does a "request" look like? (Check browser network tab)
- How does the browser know where to send the request?
- What would happen if I returned a list instead of a dictionary?
- How would the frontend send data to the backend?

**When you can answer these, you're ready for the next step!**
