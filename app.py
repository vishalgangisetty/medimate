import streamlit as st
import os
import uuid
from datetime import datetime, date
from src.config import Config
from src.ingestion import IngestionManager
from src.extractor import PrescriptionExtractor
from src.vector_store import VectorStoreManager
from src.graph import RAGGraph
from src.memory import MemoryManager
from src.auth import AuthManager
from src.otc_manager import OTCManager
from src.reminder import ReminderManager
from src.pharmacy_locator import PharmacyLocator, SAMPLE_PHARMACIES
from src.language import LanguageManager
from src.utils import setup_logger
from src.ui_pages_medical import render_medication_schedule_page, render_pharmacy_finder_page
from src.voice_assistant import VoiceAssistant

logger = setup_logger(__name__)

# Medical Application Configuration
st.set_page_config(
    page_title="MediMate - Medical Records System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Medical CSS
def load_medical_styles():
    try:
        with open('modern_style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        pass  # Fallback if CSS file not found

load_medical_styles()

# Initialize Auth
if 'auth' not in st.session_state:
    st.session_state.auth = AuthManager()
if 'user' not in st.session_state:
    st.session_state.user = None

# === LOGIN / AUTHENTICATION ===
if not st.session_state.user:
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background: #1E293B;
            border-radius: 12px;
            padding: 6px;
            border: 1px solid #334155;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            color: #94A3B8;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
            color: white !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        st.markdown("""
            <div style='text-align: center; margin: 2rem 0 1.5rem 0;'>
                <div style='font-size: 56px; margin-bottom: 0.5rem;'>🏥</div>
                <h1 style='color: #10B981; font-weight: 700; margin: 0; font-size: 42px;'>MediMate</h1>
                <p style='color: #94A3B8; font-size: 15px; margin: 0.5rem 0 0 0;'>Your Personal Health Assistant</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("user_login", clear_on_submit=False):
                username = st.text_input("Username", placeholder="Username", key="login_user")
                password = st.text_input("Password", type="password", placeholder="Password", key="login_pass")
                submit = st.form_submit_button("Login", use_container_width=True, type="primary")
                
                if submit:
                    if not username or not password:
                        st.error("Please enter both fields")
                    else:
                        success, msg = st.session_state.auth.login_user(username, password)
                        if success:
                            st.session_state.user = username
                            st.success("Welcome back!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {msg}")
                            
        with tab2:
            with st.form("new_account", clear_on_submit=True):
                new_user = st.text_input("Username", placeholder="Choose a username", key="reg_user")    
                new_pass = st.text_input("Password", type="password", placeholder="At least 6 characters", key="reg_pass")
                submit_reg = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                
                if submit_reg:
                    if new_user and new_pass:
                        success, msg = st.session_state.auth.register_user(new_user, new_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.error("All fields required")

        st.markdown("""
            <div style='text-align: center; margin-top: 2rem;'>
                <p style='color: #999; font-size: 13px;'>🔒 Your data is encrypted and secure</p>
            </div>
        """, unsafe_allow_html=True)

    st.stop()

# === INITIALIZE MANAGERS ===
if 'extractor' not in st.session_state:
    st.session_state.extractor = PrescriptionExtractor()
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStoreManager()
if 'rag_graph' not in st.session_state:
    st.session_state.rag_graph = RAGGraph().build_graph()
if 'memory' not in st.session_state:
    st.session_state.memory = MemoryManager()
elif not hasattr(st.session_state.memory, 'get_otc_result'):
    st.session_state.memory = MemoryManager()
if 'otc_manager' not in st.session_state:
    st.session_state.otc_manager = OTCManager()
if 'reminder_manager' not in st.session_state:
    st.session_state.reminder_manager = ReminderManager()
if 'pharmacy_locator' not in st.session_state:
    st.session_state.pharmacy_locator = PharmacyLocator()
if 'language_manager' not in st.session_state:
    st.session_state.language_manager = LanguageManager()
if 'user_language' not in st.session_state:
    st.session_state.user_language = "en"
if 'voice_assistant' not in st.session_state:
    st.session_state.voice_assistant = VoiceAssistant()

# Self-healing OTC Manager
try:
    if st.session_state.otc_manager.get_otc_list() and isinstance(st.session_state.otc_manager.get_otc_list()[0], str):
        st.session_state.otc_manager = OTCManager()
except Exception as e:
    logger.error(f"Error checking OTCManager: {e}")
    st.session_state.otc_manager = OTCManager()

if 'uploaded_files_map' not in st.session_state:
    st.session_state.uploaded_files_map = {}

# Translation helper
def get_ui_text(key: str) -> str:
    """Get translated UI text using LanguageManager"""
    if 'language_manager' in st.session_state:
        return st.session_state.language_manager.get_text(key, st.session_state.get('user_language', 'en'))
    return key

# === MEDICAL SIDEBAR ===
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0 0.5rem 0; border-bottom: 1px solid #334155; margin-bottom: 1rem;'>
            <div style='font-size: 32px;'>👤</div>
            <p style='margin: 0.3rem 0 0 0; font-weight: 600; color: #10B981;'>{st.session_state.user}</p>
            <p style='margin: 0.5rem 0 0 0; font-size: 12px; color: #64748B;'>🎤 Voice Assistant Active</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Language
    lang_mgr = st.session_state.language_manager
    languages = lang_mgr.get_all_languages()
    
    # Language labels in their native script
    lang_labels = {
        "en": "🌍 English",
        "hi": "🌍 हिंदी",
        "ta": "🌍 தமிழ்",
        "te": "🌍 తెలుగు",
        "bn": "🌍 বাংলা",
        "mr": "🌍 मराठी",
        "gu": "🌍 ગુજરાતી",
        "kn": "🌍 ಕನ್ನಡ",
        "ml": "🌍 മലയാളം",
        "pa": "🌍 ਪੰਜਾਬੀ"
    }
    
    current_lang_code = st.session_state.user_language
    
    selected_lang = st.selectbox(
        lang_labels.get(current_lang_code, "🌍 Language"),
        options=list(languages.keys()),
        format_func=lambda x: languages[x],
        index=list(languages.keys()).index(st.session_state.user_language),
        key="lang_selector"
    )
    
    if selected_lang != st.session_state.user_language:
        st.session_state.user_language = selected_lang
        lang_mgr.set_language(selected_lang)
        st.session_state['lang_changed'] = True
        st.success(f"✓ {languages[selected_lang]}")
        st.rerun()
    
    st.divider()
    
    # Navigation
    if "navigation" not in st.session_state:
        st.session_state.navigation = get_ui_text("my_prescriptions")
    
    # Get translated menu items
    menu_items = [
        get_ui_text("my_prescriptions"),
        get_ui_text("my_medications"),
        get_ui_text("find_pharmacy"),
        get_ui_text("drug_info")
    ]
    
    page = st.radio(
        f"📋 {get_ui_text('menu')}",
        menu_items,
        key="navigation_radio"
    )

    # Upload Section
    if page == "My Prescriptions":
        st.markdown("<div style='margin: 1.5rem 0 1rem 0;'></div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "📄 Upload Prescription",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload prescription image or PDF"
        )
        
        if uploaded_file:
            existing_p_id = st.session_state.memory.get_prescription_by_filename(
                st.session_state.user, uploaded_file.name
            )
            
            if existing_p_id:
                if st.session_state.get('current_view') != existing_p_id:
                    st.info("📌 Prescription already in system. Loading...")
                    st.session_state.current_view = existing_p_id
                    st.rerun()
            else:
                file_id = str(uuid.uuid4())
                from src.utils import ensure_directory
                ensure_directory(Config.INPUT_DIR)
                
                file_path = os.path.join(Config.INPUT_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                if file_path not in st.session_state.uploaded_files_map.values():
                    with st.spinner("🔄 Processing prescription..."):
                        data = st.session_state.extractor.extract_data(file_path)
                        
                        if data:
                            st.success("✅ Prescription processed")
                            
                            med_details = []
                            for med in data.get('medicines', []):
                                timing = med.get('timing', {})
                                timing_str = f"Morning: {timing.get('morning')}, Afternoon: {timing.get('afternoon')}, Night: {timing.get('night')}, Instruction: {timing.get('instruction')}"
                                med_details.append(
                                    f"- {med.get('name')} (Qty: {med.get('quantity')}): {timing_str}, Freq: {med.get('frequency')}, Duration: {med.get('duration')}"
                                )
                            
                            meds_str = "\n".join(med_details)
                            text_content = f"Date: {data.get('date')}\n\nMedicines:\n{meds_str}\n\nNotes: {data.get('notes')}"
                            
                            metadata = {"filename": uploaded_file.name}
                            st.session_state.vector_store.add_prescription(file_id, [text_content], metadata)
                            
                            st.session_state.uploaded_files_map[file_id] = uploaded_file.name
                            
                            med_names = [m.get('name', 'Unknown') for m in data.get('medicines', [])]
                            if med_names:
                                title = f"Rx: {', '.join(med_names[:2])}"
                                if len(med_names) > 2:
                                    title += "..."
                            else:
                                title = f"Rx: {uploaded_file.name}"
                            
                            st.session_state.memory.get_or_create_session(
                                st.session_state.user, file_id, 
                                title=title, filename=uploaded_file.name, details=meds_str
                            )
                            
                            st.success("✅ Indexed in database")
                            st.session_state.current_view = file_id
                            st.rerun()
                        else:
                            st.error("⚠️ Failed to process prescription")

        st.markdown("<div style='margin: 1rem 0 0.5rem 0;'></div>", unsafe_allow_html=True)
        
        user_prescriptions = st.session_state.memory.get_user_prescriptions(st.session_state.user)
        
        if user_prescriptions:
            st.markdown("**🗂️ My Prescriptions**")
        else:
            st.info("No prescriptions yet")
        
        for p_data in user_prescriptions:
            p_id = p_data['id']
            p_title = p_data['title']
            
            if st.button(f"📄 {p_title}", key=p_id, use_container_width=True):
                st.session_state.current_view = p_id
                st.rerun()
    
    # Logout
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    if st.button(f"🚪 {get_ui_text('logout')}", use_container_width=True, type="secondary"):
        st.session_state.user = None
        st.rerun()

# === MAIN CONTENT ===
if page == get_ui_text("my_medications"):
    render_medication_schedule_page()

elif page == get_ui_text("find_pharmacy"):
    render_pharmacy_finder_page()

elif page == get_ui_text("drug_info"):
    st.markdown("<h1 style='color: #10B981;'>🛡️ Drug Information</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='medical-card'>
            <h3 class='medical-card-header'>💊 Over-the-Counter Medications</h3>
            <p style='color: #94A3B8; margin-bottom: 1rem;'>
                Verified list of medications approved for OTC purchase.
                Always consult a healthcare professional before use.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Voice search option
    col1, col2 = st.columns([5, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search Drug Database",
            placeholder="Enter drug name, brand, or use case...",
            label_visibility="collapsed",
            key="drug_search_text"
        )
    
    with col2:
        if st.button("🎤", key="voice_drug_search", help="Voice search", use_container_width=True):
            st.session_state['listening_drug'] = True
    
    # Handle voice search
    if st.session_state.get('listening_drug', False):
        with st.spinner("🎤 Listening... Speak drug name"):
            voice_assistant = st.session_state.voice_assistant
            current_lang = st.session_state.user_language
            speech_lang = voice_assistant.get_speech_language(current_lang)
            
            try:
                voice_search = voice_assistant.listen_from_microphone(language=speech_lang, timeout=5)
                if voice_search:
                    st.success(f"✓ Searching for: {voice_search}")
                    search_query = voice_search
                else:
                    st.error("❌ Could not understand. Please try again.")
            except Exception as e:
                st.error("❌ Microphone error. Please check permissions.")
                logger.error(f"Voice search error: {str(e)}")
            
            st.session_state['listening_drug'] = False
    
    try:
        if search_query:
            with st.spinner("🔄 Searching database..."):
                results = st.session_state.otc_manager.search_otc_db(search_query)
                if results:
                    st.dataframe(
                        results,
                        use_container_width=True,
                        column_config={
                            "medicine_name": st.column_config.TextColumn("Drug Name"),
                            "type": st.column_config.TextColumn("Category")
                        }
                    )
                else:
                    st.warning("⚠️ No matches found")
        else:
            raw_list = st.session_state.otc_manager.get_otc_list()
            display_list = []
            for item in raw_list:
                display_list.append({
                    "Drug Name": item['medicine_name'],
                    "Category": item['metadata'].get('type', 'General')
                })
            st.dataframe(
                display_list,
                use_container_width=True,
                column_config={
                    "Drug Name": st.column_config.TextColumn("Drug Name", width="large"),
                    "Category": st.column_config.TextColumn("Category", width="medium")
                }
            )
            
    except Exception as e:
        st.error(f"⚠️ Database error: Please try again")
        logger.error(f"OTC database error: {e}")

elif page == get_ui_text("my_prescriptions"):
    if 'current_view' not in st.session_state:
        st.session_state.current_view = None
    
    if st.session_state.current_view is None:
        # Welcome
        welcome_msg = get_ui_text("welcome")
        
        st.markdown(f"""
            <div style='text-align: center; margin: 3rem 0 2rem 0;'>
                <div style='font-size: 64px; margin-bottom: 1rem;'>🏥</div>
                <h1 style='color: #10B981; margin-bottom: 0.5rem;'>{welcome_msg}</h1>
                <p style='color: #94A3B8; font-size: 16px;'>Upload a prescription to get started</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Feature Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class='medical-card'>
                    <div style='font-size: 48px; margin-bottom: 1rem; color: var(--primary-teal);'>📊</div>
                    <h3 class='medical-card-header'>Prescription Analysis</h3>
                    <p style='color: var(--text-secondary);'>
                        AI-powered extraction of prescription data with medical-grade accuracy
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class='medical-card'>
                    <div style='font-size: 48px; margin-bottom: 1rem; color: var(--primary-teal);'>💬</div>
                    <h3 class='medical-card-header'>Clinical Assistant</h3>
                    <p style='color: var(--text-secondary);'>
                        Ask questions about prescriptions, dosages, and drug interactions
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class='medical-card'>
                    <div style='font-size: 48px; margin-bottom: 1rem; color: var(--primary-teal);'>🛡️</div>
                    <h3 class='medical-card-header'>Drug Safety Check</h3>
                    <p style='color: var(--text-secondary);'>
                        Real-time OTC medication safety verification and interaction alerts
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
    else:
        # Active Record View
        user_prescriptions = st.session_state.memory.get_user_prescriptions(st.session_state.user)
        selected_prescription_id = st.session_state.current_view
        current_title = next((p['title'] for p in user_prescriptions if p['id'] == selected_prescription_id), "Unknown Record")
        
        st.session_state.session_id = st.session_state.memory.get_or_create_session(
            st.session_state.user, selected_prescription_id
        )
        
        details_text = st.session_state.memory.get_session_details(st.session_state.session_id)

        # Header
        st.markdown(f"<h1 style='color: var(--primary-teal);'>💬 Clinical Review: {current_title}</h1>", unsafe_allow_html=True)
        
        # Medicine Details
        if details_text:
            with st.expander("📋 Prescription Details", expanded=True):
                st.markdown(f"<pre style='color: var(--text-primary);'>{details_text}</pre>", unsafe_allow_html=True)

        # Drug Safety Check
        if st.session_state.get('current_view'):
            with st.container():
                if st.checkbox("🛡️ Check Drug Safety", key=f"safety_check_{st.session_state.session_id}"):
                    active_p_id = st.session_state.current_view
                    
                    if details_text:
                        cache_key = f"otc_{active_p_id}"
                        
                        if cache_key not in st.session_state:
                            db_result = st.session_state.memory.get_otc_result(st.session_state.session_id)
                            
                            if db_result:
                                st.session_state[cache_key] = db_result
                            else:
                                with st.spinner("🔄 Checking drug safety..."):
                                    result = st.session_state.otc_manager.check_medicines_with_llm([details_text])
                                    st.session_state[cache_key] = result
                                    
                                    if "error" not in result:
                                        st.session_state.memory.save_otc_result(st.session_state.session_id, result)
                        
                        otc_result = st.session_state[cache_key]
                        
                        if "error" in otc_result:
                            st.error(f"⚠️ Safety check failed. Please try again.")
                            logger.error(f"OTC check error: {otc_result['error']}")
                        else:
                            with st.expander("🔬 Drug Safety Analysis", expanded=True):
                                otc_meds = otc_result.get("otc_medicines", [])
                                consult_meds = otc_result.get("consult_medicines", [])
                                
                                if otc_meds and consult_meds:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown("""
                                            <div class='medical-card' style='border-left: 4px solid var(--success-green);'>
                                                <h3 style='color: var(--success-green);'>✅ Safe for OTC Purchase</h3>
                                        """, unsafe_allow_html=True)
                                        for item in otc_meds:
                                            st.write(f"**{item['name']}**")
                                            st.caption(item['reason'])
                                        st.markdown("</div>", unsafe_allow_html=True)
                                    
                                    with col2:
                                        st.markdown("""
                                            <div class='medical-card' style='border-left: 4px solid var(--error-red);'>
                                                <h3 style='color: var(--error-red);'>⚠️ Requires Prescription</h3>
                                        """, unsafe_allow_html=True)
                                        for item in consult_meds:
                                            st.write(f"**{item['name']}**")
                                            st.caption(item['reason'])
                                        st.markdown("</div>", unsafe_allow_html=True)
                                        
                                elif otc_meds:
                                    st.success("✅ All medications are safe for OTC purchase")
                                    for item in otc_meds:
                                        st.write(f"- **{item['name']}**: {item['reason']}")
                                elif consult_meds:
                                    st.warning("⚠️ These medications require prescription consultation")
                                    for item in consult_meds:
                                        st.write(f"- **{item['name']}**: {item['reason']}")
                                else:
                                    st.info("No medications found for safety analysis")
                    else:
                        st.info("No prescription data available for safety check")

        # Chat Interface
        st.markdown("<h3 style='color: #10B981;'>💬 Ask Questions</h3>", unsafe_allow_html=True)
        
        # Voice input option
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("🎤", key="voice_chat", help="Speak your question", use_container_width=True):
                st.session_state['listening_chat'] = True
        
        # Handle voice input
        voice_input = None
        if st.session_state.get('listening_chat', False):
            with st.spinner("🎤 Listening... Speak now"):
                voice_assistant = st.session_state.voice_assistant
                current_lang = st.session_state.user_language
                speech_lang = voice_assistant.get_speech_language(current_lang)
                
                try:
                    voice_input = voice_assistant.listen_from_microphone(language=speech_lang, timeout=5)
                    if voice_input:
                        st.success(f"✓ Heard: {voice_input}")
                    else:
                        st.error("❌ Could not understand. Please try again.")
                except Exception as e:
                    st.error("❌ Microphone error. Please check permissions.")
                    logger.error(f"Voice input error: {str(e)}")
                
                st.session_state['listening_chat'] = False
        
        history = st.session_state.memory.get_history(st.session_state.session_id)
        st.session_state.messages = [{"role": msg['role'], "content": msg['content']} for msg in history]
        
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                # Add read aloud button for AI responses
                if msg["role"] == "ai":
                    if st.button("🔊", key=f"speak_{i}", help="Read aloud"):
                        try:
                            audio_bytes = st.session_state.voice_assistant.text_to_speech(
                                msg["content"], 
                                st.session_state.user_language
                            )
                            if audio_bytes:
                                st.audio(audio_bytes, format='audio/mp3')
                        except Exception as e:
                            st.error("Audio generation failed")

        # Clinical Query - use voice input if available
        prompt = voice_input if voice_input else st.chat_input("Ask about this prescription...")
        
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner("🔄 Analyzing query..."):
                inputs = {
                    "question": prompt,
                    "prescription_id": selected_prescription_id,
                    "session_id": st.session_state.session_id,
                    "context": [],
                    "answer": ""
                }
                
                result = st.session_state.rag_graph.invoke(inputs)
                answer = result["answer"]
                
                st.session_state.messages.append({"role": "ai", "content": answer})
                with st.chat_message("ai"):
                    st.markdown(answer)
                    # Auto-play response for voice query
                    if voice_input:
                        try:
                            audio_bytes = st.session_state.voice_assistant.text_to_speech(
                                answer, 
                                st.session_state.user_language
                            )
                            if audio_bytes:
                                st.audio(audio_bytes, format='audio/mp3', autoplay=True)
                        except:
                            pass
                
                st.rerun()
