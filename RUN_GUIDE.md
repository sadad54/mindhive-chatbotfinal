# 🚀 How to Run the Mindhive AI Chatbot Project

This guide will help you set up and run the Mindhive AI Chatbot assessment project on Windows.

## 📋 Prerequisites

Before starting, ensure you have:

1. **Python 3.8 or higher** installed

   - Download from: https://python.org
   - Make sure Python is added to your system PATH

2. **Git** (optional, for cloning)
   - Download from: https://git-scm.com

## 🛠️ Quick Setup (Automated)

### Option 1: Using Batch Script (Recommended for Windows)

1. **Open Command Prompt** as Administrator (optional but recommended)

2. **Navigate to the project directory:**

   ```cmd
   cd d:\dev_projects\ChatBot
   ```

3. **Run the automated setup:**

   ```cmd
   setup.bat
   ```

   This script will:

   - Create a virtual environment
   - Install all dependencies
   - Set up the database and vector store
   - Create necessary directories

4. **Start the application:**
   ```cmd
   start.bat
   ```

### Option 2: Manual Setup

If you prefer manual setup or encounter issues with the automated script:

1. **Open PowerShell or Command Prompt**

2. **Navigate to project directory:**

   ```powershell
   cd d:\dev_projects\ChatBot
   ```

3. **Create virtual environment:**

   ```powershell
   python -m venv venv
   ```

4. **Activate virtual environment:**

   ```powershell
   # For PowerShell:
   venv\Scripts\Activate.ps1

   # For Command Prompt:
   venv\Scripts\activate.bat
   ```

5. **Upgrade pip:**

   ```powershell
   python -m pip install --upgrade pip
   ```

6. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```

7. **Run setup script:**

   ```powershell
   python setup_data.py
   ```

8. **Start the server:**
   ```powershell
   uvicorn app.main:app --reload
   ```

## 🌐 Accessing the Application

Once the server is running, you can access:

- **Main Chatbot Interface:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Alternative API Docs:** http://localhost:8000/redoc

## 🧪 Testing the Features

### 1. Sequential Conversation (Part 1)

Try these conversation flows in the chatbot:

```
User: "Is there an outlet in Petaling Jaya?"
Bot: "Yes! Which outlet are you referring to?"
User: "SS 2, what's the opening time?"
Bot: "The SS2 outlet opens at 7:00 AM"
```

### 2. Agentic Planning (Part 2)

The bot will automatically:

- Parse your intent
- Determine missing information
- Choose appropriate actions
- Execute tools as needed

### 3. Tool Integration (Part 3)

Test the calculator:

```
User: "Calculate 15 * 4"
Bot: "The result of 15 * 4 is 60"
```

### 4. RAG & Custom APIs (Part 4)

**Test Product Search:**

```
User: "What drinkware do you have?"
```

**Test Outlet Query:**

```
User: "Outlets in Kuala Lumpur"
```

### 5. API Endpoints

You can also test the APIs directly:

**Products API:**

```
GET http://localhost:8000/api/products?query=tumbler
```

**Outlets API:**

```
GET http://localhost:8000/api/outlets?query=SS2 outlet hours
```

**Calculator API:**

```
POST http://localhost:8000/api/calculate
Content-Type: application/json

{
  "expression": "2 + 3"
}
```

## 🔧 Troubleshooting

### Common Issues:

1. **Python not found:**

   - Ensure Python is installed and in your PATH
   - Try using `python3` instead of `python`

2. **Permission errors:**

   - Run Command Prompt as Administrator
   - Or use PowerShell with execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

3. **Module import errors:**

   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **FAISS installation issues:**

   - Install Microsoft Visual C++ Redistributable
   - Or use: `pip install faiss-cpu --no-cache-dir`

5. **Port already in use:**
   - Change port: `uvicorn app.main:app --reload --port 8001`
   - Or stop other applications using port 8000

### Checking Installation:

```powershell
# Check Python version
python --version

# Check if dependencies are installed
pip list

# Test individual components
python test_conversation.py
```

## 📁 Project Structure

```
ChatBot/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/                 # API endpoints
│   ├── chatbot/             # Conversation logic
│   ├── tools/               # Tool implementations
│   ├── models/              # Data schemas
│   └── templates/           # Frontend
├── tests/                   # Test files
├── data/                    # Database & vector store
├── setup_data.py            # Setup script
├── start.bat               # Windows startup script
└── requirements.txt        # Dependencies
```

## 🎯 Assessment Features Demonstrated

✅ **Part 1:** Sequential conversation with state management  
✅ **Part 2:** Agentic planning with intent classification  
✅ **Part 3:** Calculator tool integration with error handling  
✅ **Part 4:** RAG for products + Text2SQL for outlets  
✅ **Part 5:** Comprehensive error handling and security

## 📝 Next Steps

1. **Customize the data:** Add more products or outlets in the respective tools
2. **Extend functionality:** Add new tools or intents
3. **Deploy:** Use the FastAPI deployment guides for production
4. **Monitor:** Check logs in the `logs/` directory

## 🆘 Getting Help

If you encounter issues:

1. Check the logs in the terminal
2. Verify all dependencies are installed
3. Ensure virtual environment is activated
4. Try the manual setup process
5. Check Windows firewall/antivirus settings

---

🎉 **You're ready to explore the Mindhive AI Chatbot!**
