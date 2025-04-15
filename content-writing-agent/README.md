
# 📝 Content AI Agent

An intelligent, automated content creation system powered by specialized AI agents — built to generate high-quality, well-researched content on artificial intelligence topics with minimal human intervention.

---

## 📋 Overview

The **Content AI Agent** is a modular, multi-agent system designed to automate the full content pipeline — from news monitoring to final publishing. Each agent is purpose-built to tackle one phase of the process, ensuring accuracy, quality, and efficiency.

---

## ✨ Key Features

- 🔍 **Automated Content Discovery** – Monitors top AI and tech sources for trending topics
- 🧠 **Content Classification** – Identifies topics, categories, and key entities
- 📚 **Research & Analysis** – Aggregates facts from reliable sources
- ✍️ **Intelligent Writing** – Creates coherent, structured long-form content
- ✅ **Fact Checking** – Validates claims and key information
- 🪄 **Proofreading & Enhancement** – Refines grammar, tone, and clarity
- 📤 **Publishing Optimization** – Formats for different platforms (blogs, newsletters, etc.)

---

## 🧠 Architecture

The system revolves around a **Coordinator Agent**, which triggers specialized agents in sequence:

```
Coordinator Agent
├── Web Monitor Agent       → Finds relevant AI news
├── Classification Agent    → Detects content type & topic
├── Research Agent          → Gathers detailed info
├── Writing Agent           → Composes structured content
├── Fact Check Agent        → Verifies accuracy
├── Proofreading Agent      → Enhances readability
└── Publishing Agent        → Prepares for publication
```

---

## ⚙️ Tech Stack

| Purpose           | Tools / Libraries             |
|-------------------|-------------------------------|
| LLM Inference     | Hugging Face Transformers     |
| Prompt Chaining   | Custom Python agents          |
| NLP Utilities     | spaCy, NLTK (optional)        |
| API Serving       | FastAPI (optional extension)  |
| Deployment Ready  | Docker (optional)             |

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.10 or higher
- Hugging Face API key (for model access)

### 🧪 Installation

```bash
git clone https://github.com/munieshwar16/Proftolio_Projects.git
cd Proftolio_Projects/content-writing-agent
pip install -r requirements.txt
```



---

## ▶️ Run the Content AI Agent

```bash
python api.py
```

Or test it directly using:

```bash
python test_api.py
```

---

## 🖼 Example Output

**Prompt**: "Write an article about recent breakthroughs in multimodal LLMs."  
**Generated**:
> Multimodal LLMs are reshaping AI by integrating visual, auditory, and textual inputs into a unified system. Recent advancements by OpenAI, DeepMind, and Meta...

---

## 📌 Folder Structure

```
content-writing-agent/
├── agents/           # Modular agent classes
├── services/         # Core business logic
├── templates/        # HTML/output templates
├── data/             # Sample prompts, metadata
├── api.py            # Main FastAPI service
├── test_api.py       # API testing script
└── requirements.txt
```

---

## 🙌 Author

**Evakattu Muni Eshwar**  
🎓 Master’s in Artificial Intelligence, San Jose State University  
🔗 [LinkedIn](https://www.linkedin.com/in/evakattumunieshwar/) | [GitHub](https://github.com/munieshwar16)

---

## ⭐ Bonus Projects

Check out my other Generative AI work:
- 🌌 [Dream Reconstruction Engine](../dream-reconstructor-3d)
- 🔎 [Recovery Assistant RAG](../Recovery_Assistant_RAG)
- 🚘 [Driver Drowsiness Detection (CNN)](../Driver_Drowsiness_CNN)

---

![Banner](./assets/banner.png)


> 💡 _This project is designed for future extensibility into newsletter generation, SEO content automation, and voice-based writing interfaces._
