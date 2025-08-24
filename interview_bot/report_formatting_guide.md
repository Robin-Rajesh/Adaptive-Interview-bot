# Report Formatting Guide: Figures, Tables, and Citations

## 1. Figures and Diagrams

### 1.1 System Architecture Diagrams

**Tools to Create Diagrams:**
- Draw.io (free, web-based)
- Lucidchart
- Microsoft Visio
- Mermaid (code-based diagrams)

**Example System Architecture Diagram Structure:**
```
┌─────────────────────────────────────┐
│           Frontend Layer            │
│  ┌─────────────┐ ┌─────────────────┐│
│  │ Web Client  │ │ Mobile Client   ││
│  └─────────────┘ └─────────────────┘│
└─────────────────┬───────────────────┘
                  │ REST API
┌─────────────────▼───────────────────┐
│           Backend Layer             │
│  ┌─────────────────────────────────┐│
│  │      Application Server         ││
│  │  ┌───────────┐ ┌─────────────┐  ││
│  │  │NLP Engine │ │Auth Service │  ││
│  │  └───────────┘ └─────────────┘  ││
│  └─────────────────────────────────┘│
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│            Data Layer               │
│  ┌─────────────┐ ┌─────────────────┐│
│  │  Database   │ │  File Storage   ││
│  │  (SQLite)   │ │   (Local/Cloud) ││
│  └─────────────┘ └─────────────────┘│
└─────────────────────────────────────┘
```

### 1.2 Data Flow Diagrams

**Example Interview Processing Flow:**
```
User Input → Text Preprocessing → NLP Analysis → Scoring → Response Generation → Display Results
    ↓              ↓                  ↓           ↓              ↓               ↓
Database     Pattern Matching    Intent Recog.  Evaluation    Template Fill   UI Update
Logging      Tokenization        Entity Extr.   Algorithm     Logic          Feedback
```

### 1.3 Database Schema Diagrams

Use Entity Relationship Diagrams (ERD) to show table relationships:

```
[Users] 1─────∞ [Interviews] 1─────∞ [Responses]
   │                │                    │
   │                │                    │
   ▼                ▼                    ▼
user_id          interview_id        response_id
username         user_id (FK)        interview_id (FK)
email            position            question_id (FK)
role             status              response_text
created_at       score               score
                 created_at          timestamp
```

## 2. Tables

### 2.1 Performance Results Table

| Metric | Baseline | Target | Achieved | Improvement | Status |
|--------|----------|--------|----------|-------------|---------|
| Response Accuracy | 65% | >85% | 87% | +22% | ✅ Met |
| Processing Time | 3.2s | <2s | 1.5s | -53% | ✅ Met |
| Memory Usage | 512MB | <256MB | 198MB | -61% | ✅ Met |
| Concurrent Users | 10 | >50 | 75 | +650% | ✅ Met |

### 2.2 Feature Comparison Table

| Feature | Our System | HireVue | Pymetrics | Mya |
|---------|------------|---------|-----------|-----|
| Natural Language Processing | Advanced | Basic | N/A | Advanced |
| Real-time Feedback | Yes | No | Yes | Yes |
| Custom Questions | Yes | Yes | No | Limited |
| Bias Detection | Partial | Yes | Yes | No |
| Cost (per interview) | $0.50 | $15 | $25 | $8 |
| Setup Time | 1 day | 2 weeks | 1 week | 3 days |

### 2.3 Test Results Table

| Test Case | Input | Expected Output | Actual Output | Pass/Fail |
|-----------|-------|-----------------|---------------|-----------|
| TC001 | "I have 5 years of Python experience" | High technical score | 8.5/10 | Pass |
| TC002 | "I work well in teams" | Medium behavioral score | 7.2/10 | Pass |
| TC003 | Empty response | Error handling | "Please provide a response" | Pass |

## 3. Charts and Graphs

### 3.1 Performance Over Time (Line Chart)

```
Accuracy Improvement Over Development Iterations

  100% ┼                                    ●
       │                               ●
   90% ┼                          ●
       │                     ●
   80% ┼                ●
       │           ●
   70% ┼      ●
       │ ●
   60% ┼
       └─────────────────────────────────────
       Iter1  Iter2  Iter3  Iter4  Iter5  Iter6
```

### 3.2 User Satisfaction (Bar Chart)

```
User Satisfaction Ratings

5 Stars ████████████████████████████████ 45%
4 Stars ████████████████████████ 30%
3 Stars ███████████ 15%
2 Stars ████ 6%
1 Star  ██ 4%
```

### 3.3 Response Distribution (Pie Chart)

```
Interview Question Categories

Technical Skills: 40%
Behavioral: 25%
Experience: 20%
Problem Solving: 15%
```

## 4. Code Listings

### 4.1 Key Algorithm Implementation

```python
def evaluate_response(self, question, answer):
    """
    Evaluate candidate response using NLP techniques
    
    Args:
        question (str): The interview question
        answer (str): Candidate's response
        
    Returns:
        dict: Evaluation results with score and feedback
    """
    # Preprocess the response
    processed_answer = self.preprocess_text(answer)
    
    # Extract key features
    keywords = self.extract_keywords(processed_answer)
    sentiment = self.analyze_sentiment(processed_answer)
    
    # Calculate score based on multiple factors
    score = self.calculate_score({
        'keywords': keywords,
        'sentiment': sentiment,
        'length': len(processed_answer),
        'coherence': self.check_coherence(processed_answer)
    })
    
    return {
        'score': score,
        'feedback': self.generate_feedback(score, keywords),
        'details': {
            'keywords_found': keywords,
            'sentiment_score': sentiment,
            'coherence_rating': self.check_coherence(processed_answer)
        }
    }
```

## 5. Citations and References

### 5.1 APA Style (Recommended for Computer Science)

**Journal Articles:**
```
Smith, J. A., & Johnson, M. B. (2023). Natural language processing in automated interviews: A comprehensive review. Journal of AI Applications, 15(3), 45-62. https://doi.org/10.1000/jaia.2023.15.3.45
```

**Conference Papers:**
```
Chen, L., Wang, K., & Liu, P. (2022). Bias detection in AI-powered recruitment systems. In Proceedings of the International Conference on Machine Learning (pp. 234-241). ACM.
```

**Books:**
```
Brown, R., & Davis, S. (2021). Conversational AI: Design and implementation (2nd ed.). Tech Publishers.
```

**Websites/Online Resources:**
```
OpenAI. (2023). GPT-4 technical report. Retrieved from https://openai.com/research/gpt-4
```

**Software/Tools:**
```
Python Software Foundation. (2023). Python Language Reference (Version 3.11) [Computer software]. https://www.python.org/
```

### 5.2 IEEE Style (Alternative)

**Format:** [Number] Author, "Title," Journal, vol. X, no. Y, pp. start-end, Month Year.

**Examples:**
```
[1] J. A. Smith and M. B. Johnson, "Natural language processing in automated interviews: A comprehensive review," Journal of AI Applications, vol. 15, no. 3, pp. 45-62, Mar. 2023.

[2] L. Chen, K. Wang, and P. Liu, "Bias detection in AI-powered recruitment systems," in Proc. Int. Conf. Machine Learning, 2022, pp. 234-241.
```

## 6. Figure and Table Captions

### 6.1 Figure Captions

- Always place captions below figures
- Use "Figure X:" followed by descriptive text
- Include enough detail for readers to understand without referring to the main text

**Examples:**
```
Figure 1: System architecture diagram showing the three-layer design with frontend clients, backend processing services, and data storage components.

Figure 2: Interview accuracy comparison across different question categories, showing improvement over six development iterations.

Figure 3: User satisfaction distribution based on post-interview surveys (n=150 respondents).
```

### 6.2 Table Captions

- Always place captions above tables
- Use "Table X:" followed by descriptive text

**Examples:**
```
Table 1: Performance metrics comparison between target goals and achieved results across key system indicators.

Table 2: Feature comparison matrix showing capabilities of our interview bot system versus existing commercial solutions.
```

## 7. Formatting Guidelines

### 7.1 General Formatting

- Use consistent fonts (Times New Roman 12pt or Arial 11pt)
- 1.5 line spacing for body text
- 1-inch margins on all sides
- Page numbers in bottom right corner
- Headers with chapter/section names

### 7.2 Image Quality

- Minimum 300 DPI for printed reports
- PNG format for diagrams and screenshots
- JPEG for photographs
- Vector formats (SVG, PDF) when possible for scalability

### 7.3 Color Usage

- Use high contrast colors for accessibility
- Avoid red/green combinations (colorblind friendly)
- Consistent color scheme throughout the document
- Black and white printer-friendly versions

## 8. Tools and Resources

### 8.1 Diagram Creation Tools

**Free:**
- Draw.io (now diagrams.net)
- Mermaid (code-based)
- PlantUML
- Google Drawings

**Paid:**
- Lucidchart
- Microsoft Visio
- OmniGraffle (Mac)

### 8.2 Chart Creation Tools

**Python Libraries:**
- Matplotlib
- Seaborn
- Plotly
- Bokeh

**Excel/Google Sheets:**
- Built-in charting tools
- Easy export to images

### 8.3 Citation Management

**Free:**
- Zotero
- Mendeley Free

**Paid:**
- EndNote
- RefWorks

## 9. Quality Checklist

### 9.1 Before Submission

- [ ] All figures are clearly labeled and referenced in text
- [ ] Tables have descriptive captions and are properly formatted
- [ ] Citations are consistent throughout the document
- [ ] All references are complete and properly formatted
- [ ] Images are high resolution and clearly visible
- [ ] Color schemes are accessible and printer-friendly
- [ ] Page numbers and headers are correctly applied
- [ ] Cross-references to figures/tables work correctly
- [ ] Appendices are properly organized and labeled

### 9.2 Final Review

- [ ] Spelling and grammar check completed
- [ ] Technical accuracy verified
- [ ] Formatting consistency maintained
- [ ] All placeholder text replaced with actual content
- [ ] Word count meets requirements
- [ ] PDF export tested and verified

---

*This formatting guide ensures your capstone report meets professional academic standards with clear, accessible visual elements and proper citations.*
