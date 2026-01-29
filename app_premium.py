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
from src.ui_pages_premium import render_reminder_page, render_pharmacy_locator_page

logger = setup_logger(__name__)

# Premium Page Configuration
st.set_page_config(
    page_title="MediMate - Intelligence Hub",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Premium CSS
def load_premium_styles():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    load_premium_styles()
except:
    pass  # Fallback if CSS file not found

# Initialize Auth
if 'auth' not in st.session_state:
    st.session_state.auth = AuthManager()
if 'user' not in st.session_state:
    st.session_state.user = None

# === LOGIN / AUTHENTICATION GATE ===
if not st.session_state.user:
    # Hero Landing Page
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        # Hero Section
        st.markdown("""
            <div class='fade-in' style='text-align: center; margin: 3rem 0 2rem 0;'>
                <div style='font-size: 72px; margin-bottom: 1rem;'>🧬</div>
                <h1 class='hero-text' style='margin-bottom: 0.5rem;'>MediMate Intelligence</h1>
                <p class='body-text' style='font-size: 18px; opacity: 0.8;'>
                    Decode your prescription DNA with neural precision
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Authentication Tabs
        tab1, tab2 = st.tabs(["🔐 Access Vault", "🆕 Create Vault"])
        
        with tab1:
            st.markdown("<div class='glass-card' style='margin-top: 2rem;'>", unsafe_allow_html=True)
            
            with st.form("vault_access", clear_on_submit=False):
                st.markdown("<p class='label-text'>Identity Credentials</p>", unsafe_allow_html=True)
                username = st.text_input("Vault ID", placeholder="Your unique identifier", label_visibility="collapsed")
                password = st.text_input("Access Key", type="password", placeholder="Secure passphrase", label_visibility="collapsed")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("🔓 Unlock Intelligence Hub", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.error("⚠️ Signal Lost: Both credentials required")
                    else:
                        success, msg = st.session_state.auth.login_user(username, password)
                        if success:
                            st.session_state.user = username
                            st.success("✅ Vault Unlocked")
                            st.rerun()
                        else:
                            st.error(f"❌ Access Denied: {msg}")
            
            st.markdown("</div>", unsafe_allow_html=True)
                            
        with tab2:
            st.markdown("<div class='glass-card' style='margin-top: 2rem;'>", unsafe_allow_html=True)
            
            with st.form("vault_creation", clear_on_submit=True):
                st.markdown("<p class='label-text'>New Vault Configuration</p>", unsafe_allow_html=True)
                new_user = st.text_input("Create Vault ID", placeholder="Choose unique identifier", label_visibility="collapsed")    
                new_pass = st.text_input("Set Access Key", type="password", placeholder="Minimum 6 characters", label_visibility="collapsed")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_reg = st.form_submit_button("🔐 Initialize Health Vault", use_container_width=True)
                
                if submit_reg:
                    if new_user and new_pass:
                        success, msg = st.session_state.auth.register_user(new_user, new_pass)
                        if success:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"⚠️ {msg}")
                    else:
                        st.error("⚠️ All fields required for vault initialization")
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Trust Signals
        st.markdown("""
            <div style='text-align: center; margin-top: 4rem;' class='fade-in'>
                <div class='glass-card' style='display: inline-flex; align-items: center; gap: 2rem; padding: 1.5rem 2.5rem;'>
                    <div style='display: flex; align-items: center; gap: 0.5rem;'>
                        <span style='font-size: 24px;'>🧠</span>
                        <span class='label-text'>AI Powered</span>
                    </div>
                    <div style='width: 1px; height: 30px; background: var(--glass-white-strong);'></div>
                    <div style='display: flex; align-items: center; gap: 0.5rem;'>
                        <span style='font-size: 24px;'>🔒</span>
                        <span class='label-text'>Bank-Grade Security</span>
                    </div>
                    <div style='width: 1px; height: 30px; background: var(--glass-white-strong);'></div>
                    <div style='display: flex; align-items: center; gap: 0.5rem;'>
                        <span style='font-size: 24px;'>⚡</span>
                        <span class='label-text'>Instant Analysis</span>
                    </div>
                </div>
                <p class='micro-text' style='margin-top: 2rem; opacity: 0.6;'>
                    MediMate Intelligence • Neural Prescription Analysis Platform<br>
                    Not a substitute for professional medical advice
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.stop()

# === MAIN APPLICATION ===

# Initialize All Managers
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

# Self-healing OTC Manager check
try:
    if st.session_state.otc_manager.get_otc_list() and isinstance(st.session_state.otc_manager.get_otc_list()[0], str):
        logger.info("Detecting legacy OTCManager. Re-initializing...")
        st.session_state.otc_manager = OTCManager()
except Exception as e:
    logger.error(f"Error checking OTCManager: {e}")
    st.session_state.otc_manager = OTCManager()

# Session State
if 'uploaded_files_map' not in st.session_state:
    st.session_state.uploaded_files_map = {}

# === PREMIUM SIDEBAR ===
with st.sidebar:
    # User Identity Badge
    st.markdown(f"""
        <div class='glass-card' style='padding: 1rem; text-align: center; margin-bottom: 1.5rem;'>
            <div style='font-size: 48px; margin-bottom: 0.5rem;'>👤</div>
            <p class='label-text'>Vault: {st.session_state.user}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Language Selector
    lang_mgr = st.session_state.language_manager
    languages = lang_mgr.get_all_languages()
    
    st.markdown("<p class='label-text'>🌍 Global Access Mode</p>", unsafe_allow_html=True)
    selected_lang = st.selectbox(
        "Language",
        options=list(languages.keys()),
        format_func=lambda x: languages[x],
        index=list(languages.keys()).index(st.session_state.user_language),
        key="lang_selector",
        label_visibility="collapsed"
    )
    
    if selected_lang != st.session_state.user_language:
        st.session_state.user_language = selected_lang
        lang_mgr.set_language(selected_lang)
        st.rerun()
    
    st.divider()
    
    # Navigation
    if "navigation" not in st.session_state:
        st.session_state.navigation = "Intelligence Hub"
        
    lang = st.session_state.language_manager
    
    st.markdown("<p class='label-text'>🧭 Neural Command Center</p>", unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        [
            "Intelligence Hub",
            "Dose Protocol",
            "Care Network",
            "Safety Genome"
        ],
        key="navigation",
        label_visibility="collapsed"
    )

    # Prescription DNA Scanner (only on Hub page)
    if page == "Intelligence Hub":
        st.divider()
        st.markdown("<p class='section-header' style='font-size: 18px;'>📄 Prescription DNA</p>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Scan Intelligence",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload prescription for neural analysis"
        )
        
        if uploaded_file:
            existing_p_id = st.session_state.memory.get_prescription_by_filename(
                st.session_state.user, uploaded_file.name
            )
            
            if existing_p_id:
                if st.session_state.get('current_view') != existing_p_id:
                    st.info("📌 Prescription DNA already indexed. Switching...")
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
                    with st.spinner("🧬 Processing Intelligence..."):
                        data = st.session_state.extractor.extract_data(file_path)
                        
                        if data:
                            st.success("✅ DNA Decoded")
                            
                            # Vectorize
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
                            
                            # Generate Title
                            med_names = [m.get('name', 'Unknown') for m in data.get('medicines', [])]
                            if med_names:
                                title = f"DNA: {', '.join(med_names[:2])}"
                                if len(med_names) > 2:
                                    title += "..."
                            else:
                                title = f"DNA: {uploaded_file.name}"
                            
                            st.session_state.memory.get_or_create_session(
                                st.session_state.user, file_id, 
                                title=title, filename=uploaded_file.name, details=meds_str
                            )
                            
                            st.success("📊 Indexed in Neural DB")
                            st.session_state.current_view = file_id
                            st.rerun()
                        else:
                            st.error("⚠️ Extraction Failed")

        st.divider()
        
        # Prescription DNA Archive
        st.markdown("<p class='label-text'>🗂️ DNA Archive</p>", unsafe_allow_html=True)
        
        user_prescriptions = st.session_state.memory.get_user_prescriptions(st.session_state.user)
        
        if not user_prescriptions:
            st.info("No DNA records yet")
        
        for p_data in user_prescriptions:
            p_id = p_data['id']
            p_title = p_data['title']
            
            if st.button(f"📄 {p_title}", key=p_id, use_container_width=True):
                st.session_state.current_view = p_id
                st.rerun()
    
    # Vault Exit
    st.divider()
    if st.button("🔒 Lock Vault", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# === MAIN CONTENT AREA ===
lang = st.session_state.language_manager

# Route to appropriate page
if page == "Dose Protocol":
    render_reminder_page()

elif page == "Care Network":
    render_pharmacy_locator_page()

elif page == "Safety Genome":
    st.markdown("<h1 class='display-text fade-in'>🛡️ Safety Genome Database</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='insight-panel fade-in'>
            <div class='insight-icon'>💊</div>
            <h3 class='card-header'>OTC Medicine Intelligence</h3>
            <p class='body-text'>
                Verified database of over-the-counter medicines safe for general use.
                Always consult a healthcare professional for personalized advice.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Search
    search_query = st.text_input(
        "🔍 Search Safety Genome",
        placeholder="Enter compound name, brand, or medical use...",
        label_visibility="collapsed"
    )
    
    try:
        if search_query:
            with st.spinner("🧬 Scanning Neural Database..."):
                results = st.session_state.otc_manager.search_otc_db(search_query)
                if results:
                    st.dataframe(
                        results,
                        use_container_width=True,
                        column_config={
                            "medicine_name": st.column_config.TextColumn("Compound Identity"),
                            "type": st.column_config.TextColumn("Category")
                        }
                    )
                else:
                    st.warning("⚠️ No matches in genome database")
        else:
            raw_list = st.session_state.otc_manager.get_otc_list()
            display_list = []
            for item in raw_list:
                display_list.append({
                    "Compound Identity": item['medicine_name'],
                    "Category": item['metadata'].get('type', 'General')
                })
            st.dataframe(
                display_list,
                use_container_width=True,
                column_config={
                    "Compound Identity": st.column_config.TextColumn("Compound Identity", width="large"),
                    "Category": st.column_config.TextColumn("Category", width="medium")
                }
            )
            
    except Exception as e:
        st.error(f"⚠️ Genome Database Error: {e}")

elif page == "Intelligence Hub":
    # Determine active view
    if 'current_view' not in st.session_state:
        st.session_state.current_view = None
    
    if st.session_state.current_view is None:
        # Welcome State
        st.markdown("""
            <div class='fade-in' style='text-align: center; margin: 6rem 0;'>
                <div style='font-size: 96px; margin-bottom: 1.5rem;'>🧬</div>
                <h1 class='hero-text'>Intelligence Hub</h1>
                <p class='body-text' style='font-size: 18px; opacity: 0.8; margin-top: 1rem;'>
                    Upload a prescription to begin neural analysis<br>
                    or select an archived DNA record from the sidebar
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Feature Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class='glass-card fade-in'>
                    <div class='insight-icon'>📊</div>
                    <h3 class='card-header'>Prescription DNA</h3>
                    <p class='body-text'>
                        Advanced OCR + AI extraction of prescription data with medical-grade accuracy
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class='glass-card fade-in'>
                    <div class='insight-icon'>🤖</div>
                    <h3 class='card-header'>Clinical Co-Pilot</h3>
                    <p class='body-text'>
                        Interactive AI assistant answers questions about your prescriptions instantly
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class='glass-card fade-in'>
                    <div class='insight-icon'>🛡️</div>
                    <h3 class='card-header'>Risk Genome</h3>
                    <p class='body-text'>
                        Real-time OTC safety verification powered by vector intelligence
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
    else:
        # Active Prescription View - Clinical Co-Pilot
        user_prescriptions = st.session_state.memory.get_user_prescriptions(st.session_state.user)
        selected_prescription_id = st.session_state.current_view
        current_title = next((p['title'] for p in user_prescriptions if p['id'] == selected_prescription_id), "Unknown DNA")
        
        st.session_state.session_id = st.session_state.memory.get_or_create_session(
            st.session_state.user, selected_prescription_id
        )
        
        details_text = st.session_state.memory.get_session_details(st.session_state.session_id)

        # Header
        st.markdown(f"<h1 class='display-text fade-in'>💬 Clinical Co-Pilot: {current_title}</h1>", unsafe_allow_html=True)
        
        # Medicine Details Card
        if details_text:
            with st.expander("📋 Compound Identity & Protocol", expanded=True):
                st.markdown(f"<pre class='body-text'>{details_text}</pre>", unsafe_allow_html=True)

        # OTC Risk Analysis
        if st.session_state.get('current_view'):
            with st.container():
                if st.checkbox("🛡️ Run Safety Genome Analysis", key=f"genome_check_{st.session_state.session_id}"):
                    active_p_id = st.session_state.current_view
                    
                    if details_text:
                        cache_key = f"otc_{active_p_id}"
                        
                        if cache_key not in st.session_state:
                            db_result = st.session_state.memory.get_otc_result(st.session_state.session_id)
                            
                            if db_result:
                                st.session_state[cache_key] = db_result
                            else:
                                with st.spinner("🧬 Analyzing compound safety signals..."):
                                    result = st.session_state.otc_manager.check_medicines_with_llm([details_text])
                                    st.session_state[cache_key] = result
                                    
                                    if "error" not in result:
                                        st.session_state.memory.save_otc_result(st.session_state.session_id, result)
                        
                        otc_result = st.session_state[cache_key]
                        
                        if "error" in otc_result:
                            st.error(f"⚠️ Analysis Failed: {otc_result['error']}")
                        else:
                            with st.expander("🔬 Risk Genome Analysis", expanded=True):
                                otc_meds = otc_result.get("otc_medicines", [])
                                consult_meds = otc_result.get("consult_medicines", [])
                                
                                if otc_meds and consult_meds:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown("""
                                            <div class='insight-panel' style='border-color: var(--mint-signal);'>
                                                <h3 class='card-header' style='color: var(--mint-signal);'>✅ Clear Signal</h3>
                                        """, unsafe_allow_html=True)
                                        for item in otc_meds:
                                            st.write(f"**{item['name']}**")
                                            st.caption(item['reason'])
                                        st.markdown("</div>", unsafe_allow_html=True)
                                    
                                    with col2:
                                        st.markdown("""
                                            <div class='insight-panel' style='border-color: var(--coral-pulse);'>
                                                <h3 class='card-header' style='color: var(--coral-pulse);'>⚠️ Risk Detected</h3>
                                        """, unsafe_allow_html=True)
                                        for item in consult_meds:
                                            st.write(f"**{item['name']}**")
                                            st.caption(item['reason'])
                                        st.markdown("</div>", unsafe_allow_html=True)
                                        
                                elif otc_meds:
                                    st.success("✅ All compounds show clear safety signals")
                                    for item in otc_meds:
                                        st.write(f"- **{item['name']}**: {item['reason']}")
                                elif consult_meds:
                                    st.warning("⚠️ Risk signals detected - professional consultation recommended")
                                    for item in consult_meds:
                                        st.write(f"- **{item['name']}**: {item['reason']}")
                                else:
                                    st.info("No compounds found for analysis")
                    else:
                        st.info("No compound data available for genome analysis")

        # Chat Interface
        history = st.session_state.memory.get_history(st.session_state.session_id)
        st.session_state.messages = [{"role": msg['role'], "content": msg['content']} for msg in history]
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Clinical Query Input
        if prompt := st.chat_input("Ask Clinical Co-Pilot anything about your prescription..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner("🧠 Processing neural query..."):
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
                
                st.rerun()
