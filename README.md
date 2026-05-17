# AI Research Assistant Chatbot

An AI-powered research assistant chatbot that allows users to upload PDF documents and interact with them conversationally using Retrieval-Augmented Generation (RAG).

---

## Features

- Upload and analyze PDF documents
- AI-powered conversational Q&A
- Semantic search for retrieving relevant information
- Context-aware responses using LangChain
- OpenAI/Gemini API integration
- Research document summarization
- Document chunking and embeddings

---

## Tech Stack

### Backend
- Python
- Flask

### AI / LLM
- LangChain
- OpenAI API
- Gemini API

### NLP & Retrieval
- RAG (Retrieval-Augmented Generation)
- Semantic Search

---

## Project Structure

```bash
ai-research-assistant-chatbot/
├── app/
├── uploads/
├── embeddings/
├── templates/
├── static/
├── requirements.txt
├── app.py
└── README.md
```

---

## How It Works

1. User uploads PDF documents
2. Text is extracted and processed
3. Documents are chunked into smaller sections
4. Embeddings are generated
5. Semantic search retrieves relevant chunks
6. LLM generates contextual answers

---

## Roadmap

- Multi-document chat support
- Vector database integration
- Authentication system
- Docker deployment
- Chat history persistence
- Advanced citation generation

---

## Status

Project currently under active development.

---

## License

MIT License
