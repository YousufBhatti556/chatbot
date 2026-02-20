# Setup Instructions for MakTek Chatbot with Persistent & Semantic Memory

This document provides instructions on how to set up the updated chatbot locally. The chatbot now uses PostgreSQL for persistent conversation history and Pinecone for semantic retrieval.

## Prerequisites

1. **Python 3.9+**
2. **PostgreSQL** installed and running locally (or via Docker).
3. **Pinecone Account** (Free tier is fine).
4. **Groq Account** (For the LLM).

---

## 1. PostgreSQL Setup

You need to have a running PostgreSQL instance and a database for the chatbot.

### Options to run Postgres:
**Option A: Mac App / Homebrew**
```bash
brew install postgresql
brew services start postgresql
```

**Option B: Docker**
```bash
docker run --name chatbot-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

### Create the Database:
Open `psql` or your database manager and create the database:
```sql
CREATE DATABASE chatbot_db;
```

*(Note: The `db.py` initialization will automatically create the required `users`, `conversations`, and `messages` tables when the bot starts).*

---

## 2. Pinecone Setup

1. Go to [Pinecone](https://app.pinecone.io/) and create a free account.
2. Get your **API Key** from the API Keys tab.
3. The chatbot will automatically attempt to create the `chatbot-memory` index the first time it runs if it does not exist. The required dimension is **384** (which matches `sentence-transformers/all-MiniLM-L6-v2`).

---

## 3. Environment Variables

Create a `.env` file in the `chatbot` folder (there is a `.env.example` you can copy).

```bash
cp .env.example .env
```

Edit the `.env` file with your credentials:
```env
# LangChain AI Credentials
GROQ_API_KEY=your_groq_api_key_here

# Pinecone Credentials (Vector Memory)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=chatbot-memory

# PostgreSQL Credentials
DB_NAME=chatbot_db
DB_USER=postgres
DB_PASSWORD=your_password  # Default is often postgres or empty
DB_HOST=localhost
DB_PORT=5432
```

---

## 4. Install Dependencies

Install the updated requirements.

```bash
pip install -r requirements.txt
```

---

## 5. Run the Chatbot

Start the chatbot using the main file:

```bash
python main.py
```

- When the application starts, it will connect to PostgreSQL and Pinecone.
- Past chat history will be automatically stored per user and thread.
- Context will be semantically retrieved from previous entries across threads.
