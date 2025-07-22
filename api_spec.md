# 📘 API Specification – ZUS Coffee AI Chatbot

This document outlines the public API endpoints for the chatbot system.

---

## 🧠 1. Chat Endpoint

**POST `/chat`**

Chat entrypoint that handles intent parsing, memory tracking, and tool calling.

### Request (JSON)
```json
{
  "message": "What time does the SS2 outlet open?",
  "session_id": "user_123"
}
```

### Response (200 OK)
```json
{
  "message": "The SS2 outlet opens at 9:00 AM",
  "session_id": "user_123",
  "action_taken": "tool_call_outlets",
  "entities_extracted": {
    "specific_outlet": "SS2",
    "query_type": "opening_hours"
  }
}
```

---

## 🔢 2. Calculator Endpoint

**POST `/api/calculate`**

Evaluate math expressions securely.

### Request
```json
{ "expression": "5 * (3 + 2)" }
```

### Response
```json
{ "expression": "5 * (3 + 2)", "result": 25 }
```

---

## ☕ 3. Products Endpoint (RAG)

**GET `/api/products?query=tumbler`**

Semantic search over ZUS drinkware.

### Response
```json
{
  "query": "tumbler",
  "results": [
    {
      "id": "zus-tumbler-black",
      "name": "ZUS Coffee Tumbler Black",
      "description": "...",
      "similarity_score": 0.92
    }
  ],
  "summary": "I found 3 tumblers made of stainless steel...",
  "total_found": 3
}
```

---

## 📍 4. Outlets Endpoint (Text2SQL)

**GET `/api/outlets?query=SS2 opening hours`**

NL → SQL for outlet DB.

### Response
```json
{
  "query": "SS2 opening hours",
  "sql_query": "SELECT name, location, opening_hours FROM outlets WHERE ...",
  "results": [
    {
      "name": "ZUS Coffee SS2",
      "location": "SS2, Petaling Jaya",
      "opening_hours": "7:00 AM - 10:00 PM"
    }
  ],
  "total_found": 1
}
```

---

## 🧪 5. Health Check

**GET `/health`**

Returns:
```json
{ "status": "healthy", "service": "mindhive-chatbot" }
```

---

## 📂 Admin Tools (Optional)

- **POST `/api/products/add`**
- **POST `/api/outlets/add`**
- **GET `/api/outlets/schema`** – debugging aid

---
