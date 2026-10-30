# 🎯 Adaptive Interview Preparation Bot

An AI-powered mock interview app. It generates interview questions tailored to your field and experience level, scores your answers with NLP metrics, gives AI feedback, and tracks your progress over time.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama_3-F55036)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

## ✨ Features

- **User profiles** with domain and experience level
- **Adaptive question generation** using Llama 3 on Groq. Difficulty increases as the session goes on, and template questions are used if the API is unavailable.
- **Follow-up questions** based on your previous answer
- **Answer evaluation** that combines:
  - semantic similarity (TF-IDF)
  - expected keyword coverage
  - answer structure
  - ROUGE, BLEU and F1 scores
- **AI-written feedback** with strengths and areas to improve
- **Analytics dashboard** with Plotly charts: NLP scores, baseline comparison, metric breakdown and performance analysis
- **Session history** stored in SQLite

Supported domains: Software Engineering, Data Science, Product Management, Marketing, Finance, Human Resources, Sales and Design.

## 🚀 Getting Started

```bash
cd interview_bot
pip install -r requirements.txt
cp .env.template .env        # then add your GROQ_API_KEY
python run.py                # checks setup, then starts the Streamlit app
```

Or start the app directly with `streamlit run main.py`. You can get a free Groq API key at [console.groq.com](https://console.groq.com/).

## ⚙️ Configuration

Settings live in `interview_bot/config/settings.py`:

| Setting | Default |
|---|---|
| `GROQ_MODEL` | `llama3-8b-8192` |
| `SIMILARITY_THRESHOLD` | `0.7` |
| `MAX_QUESTIONS_PER_SESSION` | `10` |

## 📂 Project Structure

```
interview_bot/
├── main.py                      # Streamlit app (home, profile, interview, analytics, settings)
├── run.py                       # Startup checks and launcher
├── config/settings.py           # Configuration
├── core/
│   ├── question_generator.py    # LLM and template-based question generation
│   ├── answer_evaluator.py      # Scoring and AI feedback
│   ├── conversation_manager.py  # Interview session flow
│   └── user_manager.py          # Profiles and recommendations
├── database/models.py           # SQLite tables and queries
├── utils/evaluation_metrics.py  # ROUGE / BLEU helpers
└── test_advanced_evaluation.py  # Evaluation tests
```

`capstone_report.md` and `report_formatting_guide.md` contain the project report template.
