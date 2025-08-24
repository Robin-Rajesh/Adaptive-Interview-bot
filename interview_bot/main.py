# main.py - Streamlit Application
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import json

# Import our core modules
from core import UserManager, QuestionGenerator, AnswerEvaluator, ConversationManager
from config.settings import Config
from utils.evaluation_metrics import EvaluationMetrics

# Page configuration
st.set_page_config(
    page_title="Adaptive Interview Preparation Bot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aggressive CSS for maximum text visibility and contrast
st.markdown("""
<style>
    /* FORCE WHITE BACKGROUND FOR ENTIRE APP */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* FORCE BLACK TEXT FOR ALL ELEMENTS */
    body, html, div, p, span, h1, h2, h3, h4, h5, h6, li, ul, ol {
        color: #000000 !important;
        background: inherit;
    }
    
    /* MAIN CONTENT AREA - WHITE BG BLACK TEXT */
    .main {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    .main .block-container {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* ALL STREAMLIT MARKDOWN ELEMENTS */
    .stMarkdown,
    .stMarkdown *,
    div[data-testid="stMarkdownContainer"],
    div[data-testid="stMarkdownContainer"] * {
        color: #000000 !important;
        background-color: transparent !important;
    }
    
    /* HEADINGS - DARK COLORS */
    .stMarkdown h1 { color: #1a1a1a !important; font-weight: 700 !important; }
    .stMarkdown h2 { color: #1a1a1a !important; font-weight: 700 !important; }
    .stMarkdown h3 { color: #1a1a1a !important; font-weight: 600 !important; }
    .stMarkdown h4 { color: #1a1a1a !important; font-weight: 600 !important; }
    .stMarkdown h5 { color: #1a1a1a !important; font-weight: 500 !important; }
    .stMarkdown h6 { color: #1a1a1a !important; font-weight: 500 !important; }
    
    /* PARAGRAPHS AND TEXT */
    .stMarkdown p,
    .stMarkdown span,
    .stMarkdown div,
    .stMarkdown li {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* STRONG AND BOLD TEXT */
    .stMarkdown strong,
    .stMarkdown b {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* CUSTOM HEADER */
    .main-header {
        font-size: 2.5rem !important;
        font-weight: bold !important;
        text-align: center !important;
        color: #0066cc !important;
        margin-bottom: 2rem !important;
        text-shadow: none !important;
    }
    
    /* METRIC CARDS - WHITE BG, DARK TEXT */
    .metric-card {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 1.5rem !important;
        border: 2px solid #0066cc !important;
        border-radius: 8px !important;
        margin: 1rem 0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    .metric-card h4 {
        color: #0066cc !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        font-size: 1.2rem !important;
    }
    
    .metric-card p {
        color: #000000 !important;
        font-weight: 500 !important;
        margin: 0 !important;
        line-height: 1.4 !important;
    }
    
    /* QUESTION CARDS - WHITE BG, BLACK TEXT */
    .question-card {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 2rem !important;
        border: 3px solid #ff6600 !important;
        border-radius: 8px !important;
        margin: 1.5rem 0 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }
    
    .question-card h4 {
        color: #cc4400 !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        margin-bottom: 1rem !important;
    }
    
    .question-card h5 {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
        line-height: 1.5 !important;
        background-color: #f8f9fa !important;
        padding: 1rem !important;
        border: 2px solid #28a745 !important;
        border-radius: 6px !important;
        margin-top: 1rem !important;
    }
    
    .question-card p {
        color: #000000 !important;
        font-weight: 500 !important;
        margin: 0.5rem 0 !important;
    }
    
    .question-card strong {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* FEEDBACK CARDS */
    .feedback-positive {
        background-color: #ffffff !important;
        color: #006600 !important;
        border: 3px solid #28a745 !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    .feedback-positive h5,
    .feedback-positive p {
        color: #006600 !important;
        font-weight: 600 !important;
    }
    
    .feedback-negative {
        background-color: #ffffff !important;
        color: #cc0000 !important;
        border: 3px solid #dc3545 !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    .feedback-negative h5,
    .feedback-negative p {
        color: #cc0000 !important;
        font-weight: 600 !important;
    }
    
    /* SIDEBAR - DARK BACKGROUND, WHITE TEXT */
    .css-1d391kg,
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
    }
    
    .css-1d391kg *,
    section[data-testid="stSidebar"] *,
    .css-1d391kg .stMarkdown *,
    section[data-testid="stSidebar"] .stMarkdown * {
        color: #ffffff !important;
        background: inherit !important;
    }
    
    /* SIDEBAR BUTTONS */
    .css-1d391kg .stButton button,
    section[data-testid="stSidebar"] .stButton button {
        background-color: #0066cc !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    /* FORM ELEMENTS - DARK TEXT ON WHITE */
    .stSelectbox label,
    .stTextInput label,
    .stTextArea label,
    .stSlider label,
    .stMultiSelect label {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    .stSelectbox div,
    .stTextInput div,
    .stTextArea div,
    .stTextInput input,
    .stTextArea textarea {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #cccccc !important;
    }
    
    /* BUTTONS - WHITE TEXT ON COLORED BACKGROUND */
    .stButton button {
        background-color: #0066cc !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    /* METRICS */
    .metric-container,
    div[data-testid="metric-container"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #dddddd !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* ALERT BOXES */
    .stAlert,
    .stSuccess,
    .stWarning,
    .stError,
    .stInfo {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    .stAlert > div,
    .stSuccess > div,
    .stWarning > div,
    .stError > div,
    .stInfo > div {
        color: #000000 !important;
    }
    
    /* EXPANDERS */
    .streamlit-expanderHeader {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* PROGRESS BAR */
    .stProgress .st-bo {
        background-color: #e6e6e6 !important;
    }
    
    /* OVERRIDE ANY REMAINING INVISIBLE TEXT */
    div, p, span, h1, h2, h3, h4, h5, h6, li, label, strong, b, em, i {
        color: #000000 !important;
    }
    
    /* SPECIFIC OVERRIDES FOR COMMON STREAMLIT CLASSES */
    .element-container,
    .stVerticalBlock,
    .stHorizontalBlock {
        color: #000000 !important;
    }
    
    /* ENSURE ALL TEXT IS VISIBLE */
    * {
        text-shadow: none !important;
    }
    
    /* FINAL CATCH-ALL */
    body * {
        color: #000000 !important;
    }
    
    /* SIDEBAR EXCEPTION */
    .css-1d391kg *,
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

class InterviewBotApp:
    def __init__(self):
        self.config = Config()
        self.user_manager = UserManager()
        self.conversation_manager = ConversationManager()
        self.evaluation_metrics = EvaluationMetrics()
        
        # Initialize session state
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = None
        if 'current_session' not in st.session_state:
            st.session_state.current_session = None
        if 'page' not in st.session_state:
            st.session_state.page = 'home'
    
    def run(self):
        """Main application runner"""
        
        # Sidebar navigation
        self.render_sidebar()
        
        # Main content based on current page
        if st.session_state.page == 'home':
            self.render_home_page()
        elif st.session_state.page == 'profile':
            self.render_profile_page()
        elif st.session_state.page == 'interview':
            self.render_interview_page()
        elif st.session_state.page == 'analytics':
            self.render_analytics_page()
        elif st.session_state.page == 'settings':
            self.render_settings_page()
    
    def render_sidebar(self):
        """Render the sidebar navigation"""
        with st.sidebar:
            st.markdown("# 🎯 Navigation")
            
            # Navigation buttons
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.page = 'home'
                st.rerun()
            
            if st.button("👤 Profile", use_container_width=True):
                st.session_state.page = 'profile'
                st.rerun()
            
            if st.button("💬 Start Interview", use_container_width=True):
                st.session_state.page = 'interview'
                st.rerun()
            
            if st.button("📊 Analytics", use_container_width=True):
                st.session_state.page = 'analytics'
                st.rerun()
            
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.page = 'settings'
                st.rerun()
            
            st.markdown("---")
            
            # User info if logged in
            if st.session_state.user_profile:
                st.markdown("### Current User")
                st.markdown(f"**{st.session_state.user_profile['name']}**")
                st.markdown(f"Domain: {st.session_state.user_profile['domain']}")
                st.markdown(f"Level: {st.session_state.user_profile['experience_level']}")
    
    def render_home_page(self):
        """Render the home page"""
        st.markdown('<div class="main-header">🎯 Adaptive Interview Preparation Bot</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### Welcome to your personalized interview preparation platform!
        
        This AI-powered system helps you practice interviews with:
        - **Adaptive Question Generation**: Questions tailored to your domain and experience level
        - **Real-time Evaluation**: Instant feedback on your answers
        - **Progress Tracking**: Monitor your improvement over time
        - **Personalized Recommendations**: Get specific advice for improvement
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>🧠 Smart Questions</h4>
                <p>AI-generated questions based on job descriptions and your profile</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4>📈 Real-time Feedback</h4>
                <p>Instant evaluation using semantic analysis and keyword matching</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h4>🎯 Personalized Learning</h4>
                <p>Adaptive difficulty and personalized improvement recommendations</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick start section
        st.markdown("### Quick Start")
        
        if not st.session_state.user_profile:
            st.warning("👤 Please create your profile first to get started!")
            if st.button("Create Profile Now", type="primary"):
                st.session_state.page = 'profile'
                st.rerun()
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Start Practice Interview", type="primary", use_container_width=True):
                    st.session_state.page = 'interview'
                    st.rerun()
            with col2:
                if st.button("📊 View Your Progress", use_container_width=True):
                    st.session_state.page = 'analytics'
                    st.rerun()
    
    def render_profile_page(self):
        """Render the profile management page"""
        st.markdown("# 👤 User Profile")
        
        if st.session_state.user_profile:
            self.render_existing_profile()
        else:
            self.render_profile_creation()
    
    def render_existing_profile(self):
        """Render existing user profile"""
        profile = st.session_state.user_profile
        
        st.success(f"Welcome back, {profile['name']}!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Profile Information")
            st.markdown(f"**Name:** {profile['name']}")
            st.markdown(f"**Email:** {profile['email']}")
            st.markdown(f"**Domain:** {profile['domain']}")
            st.markdown(f"**Experience Level:** {profile['experience_level']}")
        
        with col2:
            # Get user analytics
            if 'user_id' in profile:
                analytics = self.user_manager.get_user_analytics(profile['user_id'])
                
                st.markdown("### Quick Stats")
                st.metric("Total Sessions", analytics['total_sessions'])
                st.metric("Average Score", f"{analytics['average_score']:.1%}")
                st.metric("Trend", analytics['improvement_trend'])
        
        st.markdown("---")
        
        # Profile update form
        with st.expander("Update Profile"):
            self.render_profile_update_form(profile)
    
    def render_profile_creation(self):
        """Render profile creation form"""
        st.markdown("### Create Your Profile")
        st.markdown("Tell us about yourself to get personalized interview practice!")
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *", placeholder="Enter your full name")
                email = st.text_input("Email *", placeholder="your.email@example.com")
            
            with col2:
                domain = st.selectbox("Domain *", self.config.SUPPORTED_DOMAINS)
                experience_level = st.selectbox("Experience Level *", 
                                              ["Beginner", "Intermediate", "Advanced"])
            
            submitted = st.form_submit_button("Create Profile", type="primary")
            
            if submitted:
                if name and email and domain and experience_level:
                    result = self.user_manager.create_user_profile(
                        name, email, domain, experience_level
                    )
                    
                    if result['status'] == 'success':
                        st.session_state.user_profile = result
                        st.success("Profile created successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"Error: {result['message']}")
                else:
                    st.error("Please fill in all required fields")
    
    def render_profile_update_form(self, current_profile):
        """Render form to update existing profile"""
        with st.form("update_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name", value=current_profile['name'])
                email = st.text_input("Email", value=current_profile['email'])
            
            with col2:
                domain = st.selectbox("Domain", self.config.SUPPORTED_DOMAINS, 
                                    index=self.config.SUPPORTED_DOMAINS.index(current_profile['domain']))
                experience_level = st.selectbox("Experience Level", 
                                              ["Beginner", "Intermediate", "Advanced"],
                                              index=["Beginner", "Intermediate", "Advanced"].index(current_profile['experience_level']))
            
            if st.form_submit_button("Update Profile"):
                # Update profile logic would go here
                st.success("Profile updated successfully!")
    
    def render_interview_page(self):
        """Render the interview practice page"""
        if not st.session_state.user_profile:
            st.warning("Please create your profile first!")
            if st.button("Go to Profile"):
                st.session_state.page = 'profile'
                st.rerun()
            return
        
        st.markdown("# 💬 Interview Practice")
        
        # Check if there's an active session
        if st.session_state.current_session is None:
            self.render_interview_setup()
        else:
            self.render_active_interview()
    
    def render_interview_setup(self):
        """Render interview session setup"""
        st.markdown("### Start New Interview Session")
        
        with st.form("interview_setup"):
            col1, col2 = st.columns(2)
            
            with col1:
                domain = st.selectbox("Interview Domain", 
                                    self.config.SUPPORTED_DOMAINS,
                                    index=self.config.SUPPORTED_DOMAINS.index(st.session_state.user_profile['domain']))
                
                num_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5)
            
            with col2:
                question_types = st.multiselect("Question Types", 
                                              ["technical", "behavioral", "situational"],
                                              default=["technical", "behavioral"])
                
                job_description = st.text_area("Job Description (Optional)", 
                                             placeholder="Paste job description here for more targeted questions...",
                                             height=100)
            
            if st.form_submit_button("Start Interview", type="primary"):
                if question_types:
                    # Start new session
                    session_preferences = {
                        "num_questions": num_questions,
                        "question_types": question_types,
                        "difficulty_progression": True
                    }
                    
                    result = self.conversation_manager.start_interview_session(
                        user_id=st.session_state.user_profile['user_id'],
                        domain=domain,
                        job_description=job_description,
                        session_preferences=session_preferences
                    )
                    
                    if result['status'] == 'success':
                        st.session_state.current_session = result
                        st.success("Interview session started!")
                        st.rerun()
                    else:
                        st.error(f"Error starting session: {result['message']}")
                else:
                    st.error("Please select at least one question type")
    
    def render_active_interview(self):
        """Render active interview session"""
        session = st.session_state.current_session
        session_id = session['session_id']
        
        # Get current session status
        session_status = self.conversation_manager.get_session_status(session_id)
        
        if not session_status:
            st.error("⚠️ Session not found. This can happen when the app restarts.")
            st.info("Your session data has been lost, but you can start a new interview session.")
            st.session_state.current_session = None
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Start New Session", type="primary"):
                    st.rerun()
            with col2:
                if st.button("📊 View Analytics"):
                    st.session_state.page = 'analytics'
                    st.rerun()
            return
        
        # Display progress
        current_q = session_status['current_question_index']
        total_q = len(session_status['questions'])
        progress = current_q / total_q if total_q > 0 else 0
        
        st.markdown("### Interview in Progress")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.progress(progress, text=f"Question {current_q + 1} of {total_q}")
        with col2:
            if st.button("⏸️ Pause"):
                self.conversation_manager.pause_session(session_id)
                st.info("Session paused")
        with col3:
            if st.button("🛑 End Early"):
                result = self.conversation_manager.end_session_early(session_id)
                st.session_state.current_session = None
                st.info("Session ended")
                st.rerun()
        
        # Current question
        if current_q < total_q:
            current_question = session_status['questions'][current_q]
            
            st.markdown(f"""
            <div class="question-card">
                <h4>Question {current_q + 1}</h4>
                <p><strong>Type:</strong> {current_question['type'].title()}</p>
                <p><strong>Difficulty:</strong> {current_question['difficulty']}</p>
                <h5>{current_question['question']}</h5>
            </div>
            """, unsafe_allow_html=True)
            
            # Answer input
            user_answer = st.text_area("Your Answer:", height=150, 
                                     placeholder="Type your detailed answer here...")
            
            if st.button("Submit Answer", type="primary"):
                if user_answer.strip():
                    with st.spinner("Evaluating your answer..."):
                        result = self.conversation_manager.process_answer(session_id, user_answer)
                    
                    if result['status'] == 'question_answered':
                        # Display evaluation
                        self.display_answer_evaluation(result['evaluation'])
                        
                        # Auto-advance to next question
                        st.success("Answer submitted! Moving to next question...")
                        st.rerun()
                    
                    elif result['status'] == 'session_completed':
                        # Session completed
                        st.session_state.current_session = None
                        self.display_session_completion(result)
                    else:
                        st.error("Error processing answer")
                else:
                    st.error("Please provide an answer")
        else:
            st.info("Session completed! Check your results.")
    
    def display_answer_evaluation(self, evaluation):
        """Display answer evaluation results"""
        st.markdown("### Answer Evaluation")
        
        # Primary Score metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Overall Score", f"{evaluation['overall_score']:.1%}")
        with col2:
            st.metric("Content Relevance", f"{evaluation['semantic_score']:.1%}")
        with col3:
            st.metric("Keyword Usage", f"{evaluation['keyword_score']:.1%}")
        with col4:
            st.metric("Structure", f"{evaluation['structure_score']:.1%}")
        
        # Advanced NLP Metrics (if available)
        if evaluation.get('nlp_metrics'):
            st.markdown("#### Advanced NLP Metrics")
            nlp_metrics = evaluation['nlp_metrics']
            
            # ROUGE, BLEU, and F1 scores
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                rouge_scores = nlp_metrics['rouge_scores']
                st.metric("ROUGE-1", f"{rouge_scores['rouge1']:.3f}", 
                         help="Measures unigram overlap with reference")
            with col2:
                st.metric("ROUGE-L", f"{rouge_scores['rougeL']:.3f}", 
                         help="Measures longest common subsequence")
            with col3:
                st.metric("BLEU Score", f"{nlp_metrics['bleu_score']:.3f}", 
                         help="Measures precision of n-gram matches")
            with col4:
                f1_score = nlp_metrics['f1_metrics']['f1_score']
                st.metric("F1-Score", f"{f1_score:.3f}", 
                         help="Harmonic mean of precision and recall")
            
            # Baseline Comparison
            st.markdown("#### Baseline Comparison")
            baseline = nlp_metrics['baseline_comparison']
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("vs Reference", f"{baseline['user_vs_reference']:.3f}", 
                         help="Composite score compared to reference answers")
            with col2:
                category = baseline['performance_category']
                category_color = {
                    'Excellent': '🟢', 'Good': '🔵', 
                    'Average': '🟡', 'Needs Improvement': '🔴'
                }.get(category, '⚪')
                st.markdown(f"**NLP Category:** {category_color} {category}")
        
        # Feedback
        feedback_class = "feedback-positive" if evaluation['overall_score'] > 0.6 else "feedback-negative"
        st.markdown(f"""
        <div class="{feedback_class}">
            <h5>Feedback:</h5>
            <p>{evaluation['feedback']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Strengths and improvements
        col1, col2 = st.columns(2)
        with col1:
            if evaluation['strengths']:
                st.markdown("**Strengths:**")
                for strength in evaluation['strengths']:
                    st.markdown(f"✅ {strength}")
        
        with col2:
            if evaluation['improvements']:
                st.markdown("**Areas for Improvement:**")
                for improvement in evaluation['improvements']:
                    st.markdown(f"📈 {improvement}")
    
    def display_session_completion(self, result):
        """Display session completion summary"""
        st.markdown("# 🎉 Session Complete!")
        
        summary = result['session_summary']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Questions Answered", summary['total_questions'])
        with col2:
            st.metric("Average Score", f"{summary['average_score']:.1%}")
        with col3:
            st.metric("Duration", f"{summary['duration_minutes']} min")
        with col4:
            st.metric("Performance", summary['performance_level'])
        
        # Detailed feedback
        st.markdown("### Comprehensive Feedback")
        st.info(result['comprehensive_feedback'])
        
        # Recommendations
        st.markdown("### Recommendations for Improvement")
        for i, rec in enumerate(result['recommendations'], 1):
            st.markdown(f"{i}. {rec}")
        
        # Performance visualization
        self.render_session_performance_chart(result['detailed_metrics'])
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start New Session", type="primary"):
                st.session_state.current_session = None
                st.rerun()
        with col2:
            if st.button("View Detailed Analytics"):
                st.session_state.page = 'analytics'
                st.rerun()
    
    def render_session_performance_chart(self, metrics):
        """Render performance visualization"""
        st.markdown("### Performance Breakdown")
        
        # Create radar chart
        categories = ['Content Relevance', 'Technical Knowledge', 'Communication Structure']
        values = [
            metrics['semantic_average'],
            metrics['keyword_average'], 
            metrics['structure_average']
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Your Performance'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_analytics_page(self):
        """Render analytics and progress tracking page with static demo data"""
        if not st.session_state.user_profile:
            st.warning("Please create your profile first!")
            return
        
        st.markdown("# 📊 Analytics & Progress")
        
        # Static demo analytics data with advanced NLP metrics
        demo_analytics = {
            'total_sessions': 8,
            'average_score': 0.73,
            'improvement_trend': 'Improving',
            'recent_sessions': 3,
            'score_history': [0.65, 0.58, 0.72, 0.68, 0.75, 0.71, 0.78, 0.81],
            # Advanced NLP metrics trends
            'nlp_metrics_history': {
                'rouge1_scores': [0.45, 0.42, 0.51, 0.48, 0.55, 0.52, 0.58, 0.62],
                'bleu_scores': [0.38, 0.35, 0.44, 0.41, 0.47, 0.45, 0.51, 0.55],
                'f1_scores': [0.52, 0.48, 0.61, 0.57, 0.64, 0.60, 0.67, 0.72]
            },
            'baseline_comparisons': {
                'user_vs_expert': [0.68, 0.65, 0.74, 0.71, 0.77, 0.75, 0.81, 0.84],
                'performance_categories': ['Average', 'Average', 'Good', 'Good', 'Good', 'Good', 'Excellent', 'Excellent']
            },
            'sessions_data': [
                {
                    'domain': 'Software Engineering',
                    'session_date': '2025-01-20',
                    'session_avg_score': 0.81,
                    'questions_asked': 5,
                    'session_duration': 18,
                    'nlp_metrics': {
                        'rouge1': 0.62, 'bleu': 0.55, 'f1': 0.72,
                        'baseline_vs_expert': 0.84, 'category': 'Excellent'
                    }
                },
                {
                    'domain': 'Software Engineering',
                    'session_date': '2025-01-18',
                    'session_avg_score': 0.78,
                    'questions_asked': 4,
                    'session_duration': 15,
                    'nlp_metrics': {
                        'rouge1': 0.58, 'bleu': 0.51, 'f1': 0.67,
                        'baseline_vs_expert': 0.81, 'category': 'Excellent'
                    }
                },
                {
                    'domain': 'Software Engineering',
                    'session_date': '2025-01-15',
                    'session_avg_score': 0.71,
                    'questions_asked': 6,
                    'session_duration': 22,
                    'nlp_metrics': {
                        'rouge1': 0.52, 'bleu': 0.45, 'f1': 0.60,
                        'baseline_vs_expert': 0.75, 'category': 'Good'
                    }
                },
                {
                    'domain': 'Data Science',
                    'session_date': '2025-01-12',
                    'session_avg_score': 0.68,
                    'questions_asked': 5,
                    'session_duration': 20,
                    'nlp_metrics': {
                        'rouge1': 0.48, 'bleu': 0.41, 'f1': 0.57,
                        'baseline_vs_expert': 0.71, 'category': 'Good'
                    }
                },
                {
                    'domain': 'Software Engineering',
                    'session_date': '2025-01-10',
                    'session_avg_score': 0.65,
                    'questions_asked': 4,
                    'session_duration': 16,
                    'nlp_metrics': {
                        'rouge1': 0.42, 'bleu': 0.35, 'f1': 0.48,
                        'baseline_vs_expert': 0.65, 'category': 'Average'
                    }
                }
            ]
        }
        
        # Overview metrics
        st.markdown("### Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sessions", demo_analytics['total_sessions'])
        with col2:
            st.metric("Average Score", f"{demo_analytics['average_score']:.1%}")
        with col3:
            st.metric("Improvement Trend", demo_analytics['improvement_trend'])
        with col4:
            st.metric("Recent Sessions", demo_analytics['recent_sessions'])
        
        # Progress chart
        st.markdown("### Score Progress Over Time")
        
        df = pd.DataFrame({
            'Session': range(1, len(demo_analytics['score_history']) + 1),
            'Score': [score * 100 for score in demo_analytics['score_history']]
        })
        
        fig = px.line(df, x='Session', y='Score', 
                     title='Interview Performance Over Time',
                     markers=True)
        fig.update_layout(yaxis_range=[0, 100])
        fig.update_yaxes(title='Score (%)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Advanced NLP Metrics Trends
        st.markdown("### Advanced NLP Metrics Trends")
        
        # Create tabs for different metric views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 NLP Scores", "🎯 Baseline Comparison", "📊 Metric Breakdown", "🔍 Performance Analysis"])
        
        with tab1:
            # NLP metrics over time
            nlp_df = pd.DataFrame({
                'Session': range(1, len(demo_analytics['nlp_metrics_history']['rouge1_scores']) + 1),
                'ROUGE-1': [score * 100 for score in demo_analytics['nlp_metrics_history']['rouge1_scores']],
                'BLEU': [score * 100 for score in demo_analytics['nlp_metrics_history']['bleu_scores']],
                'F1-Score': [score * 100 for score in demo_analytics['nlp_metrics_history']['f1_scores']]
            })
            
            fig_nlp = px.line(nlp_df.melt(id_vars=['Session'], var_name='Metric', value_name='Score'), 
                             x='Session', y='Score', color='Metric',
                             title='NLP Metrics Evolution Over Time',
                             markers=True)
            fig_nlp.update_layout(yaxis_range=[0, 100])
            fig_nlp.update_yaxes(title='Score (%)')
            st.plotly_chart(fig_nlp, use_container_width=True)
            
            # Latest scores
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Latest ROUGE-1", f"{demo_analytics['nlp_metrics_history']['rouge1_scores'][-1]:.3f}")
            with col2:
                st.metric("Latest BLEU", f"{demo_analytics['nlp_metrics_history']['bleu_scores'][-1]:.3f}")
            with col3:
                st.metric("Latest F1", f"{demo_analytics['nlp_metrics_history']['f1_scores'][-1]:.3f}")
        
        with tab2:
            # Baseline comparison trends
            baseline_df = pd.DataFrame({
                'Session': range(1, len(demo_analytics['baseline_comparisons']['user_vs_expert']) + 1),
                'User vs Expert Baseline': [score * 100 for score in demo_analytics['baseline_comparisons']['user_vs_expert']]
            })
            
            fig_baseline = px.line(baseline_df, x='Session', y='User vs Expert Baseline',
                                 title='Performance vs Expert Baseline Over Time',
                                 markers=True, line_shape='spline')
            
            # Add reference lines
            fig_baseline.add_hline(y=80, line_dash="dash", line_color="green", 
                                  annotation_text="Excellent Threshold (80%)")
            fig_baseline.add_hline(y=60, line_dash="dash", line_color="orange", 
                                  annotation_text="Good Threshold (60%)")
            fig_baseline.update_layout(yaxis_range=[0, 100])
            fig_baseline.update_yaxes(title='Baseline Comparison Score (%)')
            st.plotly_chart(fig_baseline, use_container_width=True)
            
            # Category distribution
            st.markdown("#### Performance Category Distribution")
            categories = demo_analytics['baseline_comparisons']['performance_categories']
            category_counts = pd.Series(categories).value_counts()
            
            fig_pie = px.pie(values=category_counts.values, names=category_counts.index,
                           title="Performance Categories Across Sessions")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with tab3:
            # Detailed metric breakdown
            st.markdown("#### Latest Session Detailed Metrics")
            
            # Create a radar chart for the latest session's metrics
            latest_metrics = {
                'Content Relevance': demo_analytics['score_history'][-1],
                'ROUGE-1 Score': demo_analytics['nlp_metrics_history']['rouge1_scores'][-1],
                'BLEU Score': demo_analytics['nlp_metrics_history']['bleu_scores'][-1],
                'F1-Score': demo_analytics['nlp_metrics_history']['f1_scores'][-1],
                'vs Expert Baseline': demo_analytics['baseline_comparisons']['user_vs_expert'][-1]
            }
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=list(latest_metrics.values()),
                theta=list(latest_metrics.keys()),
                fill='toself',
                name='Latest Performance',
                line_color='rgb(255, 165, 0)'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=True,
                title="Latest Session Multi-Metric Performance"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Metric explanations
            st.markdown("#### Metric Explanations")
            with st.expander("📖 Understanding Your Metrics"):
                st.markdown("""
                **ROUGE-1**: Measures unigram (single word) overlap between your answer and reference answers. Higher scores indicate better content coverage.
                
                **BLEU Score**: Evaluates precision of n-gram matches between your response and reference answers. Commonly used in machine translation and text generation.
                
                **F1-Score**: Harmonic mean of precision and recall for answer quality prediction. Balances both accuracy and completeness.
                
                **vs Expert Baseline**: Composite score comparing your performance to expert-level reference answers across all metrics.
                """)
        
        with tab4:
            # Performance analysis and insights
            st.markdown("#### Performance Analysis & Insights")
            
            # Calculate trends
            recent_improvement = demo_analytics['score_history'][-1] - demo_analytics['score_history'][-3]
            rouge_improvement = demo_analytics['nlp_metrics_history']['rouge1_scores'][-1] - demo_analytics['nlp_metrics_history']['rouge1_scores'][-3]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📈 Recent Trends**")
                trend_color = "🟢" if recent_improvement > 0 else "🔴" if recent_improvement < 0 else "🟡"
                st.markdown(f"{trend_color} Overall Score: {recent_improvement:+.1%} (last 3 sessions)")
                
                rouge_color = "🟢" if rouge_improvement > 0 else "🔴" if rouge_improvement < 0 else "🟡"
                st.markdown(f"{rouge_color} ROUGE-1: {rouge_improvement:+.3f} (last 3 sessions)")
                
                current_category = demo_analytics['baseline_comparisons']['performance_categories'][-1]
                st.markdown(f"🎯 Current Level: **{current_category}**")
            
            with col2:
                st.markdown("**🎯 Strengths & Areas for Improvement**")
                latest_scores = {
                    'Overall': demo_analytics['score_history'][-1],
                    'ROUGE-1': demo_analytics['nlp_metrics_history']['rouge1_scores'][-1],
                    'BLEU': demo_analytics['nlp_metrics_history']['bleu_scores'][-1],
                    'F1': demo_analytics['nlp_metrics_history']['f1_scores'][-1]
                }
                
                # Find strongest and weakest areas
                strongest = max(latest_scores, key=latest_scores.get)
                weakest = min(latest_scores, key=latest_scores.get)
                
                st.markdown(f"✅ **Strongest Area**: {strongest} ({latest_scores[strongest]:.3f})")
                st.markdown(f"📈 **Focus Area**: {weakest} ({latest_scores[weakest]:.3f})")
            
            # Comparative analysis
            st.markdown("**📊 Comparative Analysis**")
            avg_user_score = sum(demo_analytics['score_history']) / len(demo_analytics['score_history'])
            avg_rouge = sum(demo_analytics['nlp_metrics_history']['rouge1_scores']) / len(demo_analytics['nlp_metrics_history']['rouge1_scores'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Your Average", f"{avg_user_score:.1%}", help="Your overall average performance")
            with col2:
                benchmark_score = 0.70  # Simulated benchmark
                delta = avg_user_score - benchmark_score
                st.metric("vs Platform Average", f"{benchmark_score:.1%}", 
                         delta=f"{delta:+.1%}", help="Compared to other users")
            with col3:
                expert_score = 0.85  # Simulated expert baseline
                expert_delta = avg_user_score - expert_score
                st.metric("vs Expert Baseline", f"{expert_score:.1%}", 
                         delta=f"{expert_delta:+.1%}", help="Compared to expert-level answers")
        
        # Recent sessions detail with advanced metrics
        st.markdown("### Recent Sessions")
        for i, session in enumerate(demo_analytics['sessions_data'][:5]):
            category_emoji = {
                'Excellent': '🟢', 'Good': '🔵', 
                'Average': '🟡', 'Needs Improvement': '🔴'
            }.get(session['nlp_metrics']['category'], '⚪')
            
            with st.expander(f"Session {i+1} - {session['domain']} ({session['session_date']}) {category_emoji}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Average Score:** {session['session_avg_score']:.1%}")
                    st.write(f"**Questions Asked:** {session['questions_asked']}")
                    st.write(f"**Duration:** {session['session_duration']} min")
                with col2:
                    st.write(f"**Domain:** {session['domain']}")
                    st.write(f"**NLP Category:** {session['nlp_metrics']['category']}")
                    st.write(f"**vs Baseline:** {session['nlp_metrics']['baseline_vs_expert']:.3f}")
                
                # Advanced metrics for this session
                st.markdown("**Advanced Metrics:**")
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                with metrics_col1:
                    st.metric("ROUGE-1", f"{session['nlp_metrics']['rouge1']:.3f}")
                with metrics_col2:
                    st.metric("BLEU", f"{session['nlp_metrics']['bleu']:.3f}")
                with metrics_col3:
                    st.metric("F1-Score", f"{session['nlp_metrics']['f1']:.3f}")
        
        # Static recommendations
        recommendations = [
            "Focus on structuring your answers using the STAR method (Situation, Task, Action, Result)",
            "Practice explaining technical concepts in simple terms",
            "Work on providing specific examples from your experience",
            "Continue regular practice to build confidence",
            "Review feedback from previous sessions and work on identified weak areas"
        ]
        
        st.markdown("### Personalized Recommendations")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    
    def render_settings_page(self):
        """Render settings page"""
        st.markdown("# ⚙️ Settings")
        
        st.markdown("### Application Settings")
        
        with st.expander("API Configuration"):
            st.info("API keys are configured via environment variables for security.")
            st.code("""
            Required Environment Variables:
            - OPENAI_API_KEY: Your OpenAI API key
            """)
        
        with st.expander("Supported Domains"):
            st.write("Currently supported interview domains:")
            for domain in self.config.SUPPORTED_DOMAINS:
                st.markdown(f"• {domain}")
        
        with st.expander("Evaluation Settings"):
            st.write(f"**Similarity Threshold:** {self.config.SIMILARITY_THRESHOLD}")
            st.write(f"**Min Answer Length:** {self.config.MIN_ANSWER_LENGTH} characters")
            st.write(f"**Max Questions per Session:** {self.config.MAX_QUESTIONS_PER_SESSION}")
        
        st.markdown("### Data Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export My Data"):
                st.info("Data export functionality would be implemented here")
        with col2:
            if st.button("Clear Session Data"):
                if st.checkbox("I understand this will clear all my session data"):
                    st.warning("This feature would clear session data (not implemented in demo)")

# Run the application
if __name__ == "__main__":
    app = InterviewBotApp()
    app.run()