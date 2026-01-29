"""
Medical-grade UI Pages
Hospital-style interfaces for medication schedule and pharmacy finder
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from src.utils import setup_logger

logger = setup_logger(__name__)

def render_medication_schedule_page():
    """My Medications - User-friendly medication tracking interface"""
    
    lang_mgr = st.session_state.get('language_manager')
    if not lang_mgr:
        from src.language import LanguageManager
        lang_mgr = LanguageManager() # Fallback
        
    title = lang_mgr.get_text("my_medications")
    st.markdown(f"<h1 style='color: var(--primary-teal);'>💊 {title}</h1>", unsafe_allow_html=True)
    
    # Tabs
    t1 = lang_mgr.get_text("current_medications")
    t2 = lang_mgr.get_text("add_medication")
    t3 = lang_mgr.get_text("my_progress")
    
    tab1, tab2, tab3 = st.tabs([f"📋 {t1}", f"➕ {t2}", f"📈 {t3}"])
    
    with tab1:
        render_active_schedule()
    
    with tab2:
        render_add_medication()
    
    with tab3:
        render_adherence_report()


def render_active_schedule():
    """Display active medication schedule"""
    
    reminder_mgr = st.session_state.reminder_manager
    user = st.session_state.user
    
    # Get active reminders
    reminders = reminder_mgr.get_user_reminders(user, active_only=True)
    
    if not reminders:
        st.markdown("""
            <div class='medical-card' style='text-align: center; padding: 3rem;'>
                <div style='font-size: 64px; margin-bottom: 1rem; color: var(--text-tertiary);'>💊</div>
                <h3 style='color: var(--text-secondary);'>No Active Medications</h3>
                <p style='color: var(--text-tertiary);'>
                    Use the "Add Medication" tab to create a new medication schedule
                </p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    # Today's schedule
    st.markdown("<div class='medical-card'><h3 class='medical-card-header'>📅 Today's Schedule</h3>", unsafe_allow_html=True)
    
    today = date.today()
    today_logs = reminder_mgr.get_logs_for_date(user, today)
    
    for reminder in reminders:
        med_name = reminder.get('medicine_name', 'Unknown')
        times = reminder.get('times', [])
        
        for time_str in times:
            # Try to infer time slot or just assume generic
            slot = "Dose"
            try:
                h = int(time_str.split(':')[0])
                if 5 <= h < 12: slot = "Morning"
                elif 12 <= h < 17: slot = "Afternoon"
                else: slot = "Night"
            except:
                pass
                
            # Check logs
            # We match by medicine name and scheduled_time
            log_entry = next((log for log in today_logs if log['medicine_name'] == med_name and log.get('scheduled_time') == time_str), None)
            
            status = "✅ Taken" if log_entry and log_entry.get('status') == 'taken' else "⏰ Pending"
            color = "var(--success-green)" if log_entry and log_entry.get('status') == 'taken' else "var(--warning-orange)"
            
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{med_name}** • {slot}")
            with col2:
                st.markdown(f"🕐 {time_str}")
            with col3:
                st.markdown(f"<span style='color: {color};'>{status}</span>", unsafe_allow_html=True)
            
            st.markdown("---")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Log dose
    st.markdown("<br><h3 style='color: var(--primary-teal);'>✏️ Log Dose</h3>", unsafe_allow_html=True)
    
    with st.form("log_dose_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            medicine_options = [r.get('medicine_name', 'Unknown') for r in reminders]
            selected_medicine = st.selectbox("Select Medication", medicine_options)
        
        with col2:
            time_slot = st.selectbox("Time Slot", ["morning", "afternoon", "night"])
        
        status = st.radio("Status", ["taken", "missed"], horizontal=True)
        notes = st.text_area("Notes (Optional)", placeholder="Add any notes about this dose...")
        
        submit = st.form_submit_button("📝 Log Dose", use_container_width=True)
        
        if submit:
            try:
                reminder_mgr.log_medicine_intake(
                    user, selected_medicine, time_slot, 
                    status, notes if notes else ""
                )
                st.success("✅ Dose logged successfully")
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ Failed to log dose: {str(e)}")
                logger.error(f"Dose logging error: {e}")


def render_add_medication():
    """Add new medication to schedule"""
    
    st.markdown("""
        <div class='medical-card'>
            <h3 class='medical-card-header'>➕ Add New Medication</h3>
            <p style='color: var(--text-secondary); margin-bottom: 1.5rem;'>
                Create a medication reminder schedule
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("add_medication_form", clear_on_submit=True):
        medicine_name = st.text_input(
            "Medication Name *",
            placeholder="e.g., Aspirin 100mg",
            help="Enter the full medication name with dosage"
        )
        
        st.markdown("<p class='label'>⏰ Schedule Times</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            morning_enabled = st.checkbox("Morning Dose")
            morning_time = st.time_input("Morning Time", value=datetime.strptime("08:00", "%H:%M").time(), disabled=not morning_enabled)
        
        with col2:
            afternoon_enabled = st.checkbox("Afternoon Dose")
            afternoon_time = st.time_input("Afternoon Time", value=datetime.strptime("14:00", "%H:%M").time(), disabled=not afternoon_enabled)
        
        with col3:
            night_enabled = st.checkbox("Night Dose")
            night_time = st.time_input("Night Time", value=datetime.strptime("21:00", "%H:%M").time(), disabled=not night_enabled)
        
        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=date.today() + timedelta(days=30))
        
        notes = st.text_area(
            "Instructions (Optional)",
            placeholder="e.g., Take with food, Avoid alcohol...",
            help="Add any special instructions"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("💾 Save Medication Schedule", use_container_width=True)
        
        if submit:
            if not medicine_name:
                st.error("⚠️ Medication name is required")
            elif not (morning_enabled or afternoon_enabled or night_enabled):
                st.error("⚠️ Please select at least one dose time")
            elif end_date < start_date:
                st.error("⚠️ End date must be after start date")
            else:
                schedule = {}
                if morning_enabled:
                    schedule['morning'] = morning_time.strftime("%H:%M")
                if afternoon_enabled:
                    schedule['afternoon'] = afternoon_time.strftime("%H:%M")
                if night_enabled:
                    schedule['night'] = night_time.strftime("%H:%M")
                
                try:
                    reminder_mgr = st.session_state.reminder_manager
                    
                    # Calculate derived values
                    duration_days = (end_date - start_date).days
                    if duration_days < 1:
                        duration_days = 1
                        
                    times_list = sorted(list(schedule.values()))
                    frequency_str = "Daily"
                    if len(times_list) == 2:
                        frequency_str = "Twice Daily"
                    elif len(times_list) == 3:
                        frequency_str = "Thrice Daily"
                    
                    reminder_mgr.add_reminder(
                        user_id=st.session_state.user,
                        medicine_name=medicine_name,
                        dosage="As specified", # Default value since UI doesn't ask for it separate
                        frequency=frequency_str,
                        times=times_list,
                        duration_days=duration_days,
                        start_date=start_date.strftime("%Y-%m-%d"),
                        instructions=notes
                    )
                    st.success(f"✅ Medication schedule created for {medicine_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Failed to create schedule: {str(e)}")
                    logger.error(f"Reminder creation error: {e}")


def render_adherence_report():
    """Display adherence statistics and reports"""
    
    reminder_mgr = st.session_state.reminder_manager
    user = st.session_state.user
    
    st.markdown("""
        <div class='medical-card'>
            <h3 class='medical-card-header'>📈 My Medication Progress</h3>
            <p style='color: var(--text-secondary);'>
                Track your medication compliance and progress over time
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        stats = reminder_mgr.get_adherence_stats(user)
        
        # Summary Cards
        col1, col2, col3 = st.columns(3)
        
        total = stats.get('total_reminders', 0)
        taken = stats.get('taken_count', 0)
        missed = stats.get('missed_count', 0)
        
        adherence_rate = (taken / total * 100) if total > 0 else 0
        
        with col1:
            st.markdown(f"""
                <div class='medical-card' style='text-align: center; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);'>
                    <div style='font-size: 36px; color: var(--primary-teal); margin-bottom: 0.5rem;'>{total}</div>
                    <p class='label'>Total Doses</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class='medical-card' style='text-align: center; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);'>
                    <div style='font-size: 36px; color: var(--success-green); margin-bottom: 0.5rem;'>{taken}</div>
                    <p class='label'>Doses Taken</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class='medical-card' style='text-align: center; background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);'>
                    <div style='font-size: 36px; color: var(--error-red); margin-bottom: 0.5rem;'>{missed}</div>
                    <p class='label'>Doses Missed</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Adherence Rate
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='medical-card' style='text-align: center;'>
                <div style='font-size: 48px; color: var(--primary-teal); margin-bottom: 0.5rem; font-weight: 700;'>
                    {adherence_rate:.1f}%
                </div>
                <p class='label'>Adherence Rate</p>
                <p style='color: var(--text-secondary); font-size: 14px;'>
                    {'Excellent compliance' if adherence_rate >= 90 else 'Good compliance' if adherence_rate >= 75 else 'Needs improvement'}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Per-Medicine Details
        reminder_details = stats.get('reminder_details', [])
        
        if reminder_details:
            st.markdown("<br><h3 style='color: var(--primary-teal);'>💊 Per-Medication Report</h3>", unsafe_allow_html=True)
            
            for detail in reminder_details:
                med_name = detail.get('medicine_name', 'Unknown')
                med_taken = detail.get('taken', 0)
                med_missed = detail.get('missed', 0)
                med_total = med_taken + med_missed
                med_rate = (med_taken / med_total * 100) if med_total > 0 else 0
                
                st.markdown(f"""
                    <div class='medical-card'>
                        <h4 style='color: var(--text-primary); margin-bottom: 1rem;'>{med_name}</h4>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <span style='color: var(--success-green);'>✅ {med_taken} taken</span> • 
                                <span style='color: var(--error-red);'>❌ {med_missed} missed</span>
                            </div>
                            <div style='font-size: 24px; color: var(--primary-teal); font-weight: 600;'>
                                {med_rate:.0f}%
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error("⚠️ Failed to load adherence statistics")
        logger.error(f"Adherence stats error: {e}")


def render_pharmacy_finder_page():
    """Find Pharmacy - User-friendly pharmacy locator"""
    
    lang_mgr = st.session_state.get('language_manager')
    if not lang_mgr:
        from src.language import LanguageManager
        lang_mgr = LanguageManager()
        
    title = lang_mgr.get_text("find_pharmacy")
    st.markdown(f"<h1 style='color: var(--primary-teal);'>🏪 {title}</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='medical-card'>
            <h3 class='medical-card-header'>Find Nearby Pharmacies</h3>
            <p style='color: var(--text-secondary);'>
                Locate pharmacies near your location or search by address
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Search Tabs
    t1 = lang_mgr.get_text("gps_location")
    t2 = lang_mgr.get_text("address_search")
    
    tab1, tab2 = st.tabs([f"📍 {t1}", f"🔍 {t2}"])
    
    with tab1:
        render_gps_search()
    
    with tab2:
        render_address_search()


def render_gps_search():
    """GPS-based pharmacy search"""
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='medical-card'>
            <p style='color: var(--text-secondary); margin-bottom: 1rem;'>
                📍 Use your device's GPS to find pharmacies within a specific radius
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        latitude = st.number_input(
            "Latitude",
            value=13.0827,
            format="%.6f",
            help="Enter your GPS latitude"
        )
    
    with col2:
        longitude = st.number_input(
            "Longitude",
            value=80.2707,
            format="%.6f",
            help="Enter your GPS longitude"
        )
    
    radius = st.slider(
        "Search Radius (meters)",
        min_value=500,
        max_value=10000,
        value=5000,
        step=500,
        help="Set the search radius around your location"
    )
    
    if st.button("🔍 Find Pharmacies", use_container_width=True):
        with st.spinner("🔄 Searching for pharmacies..."):
            try:
                pharmacy_locator = st.session_state.pharmacy_locator
                results = pharmacy_locator.find_nearby_pharmacies(latitude, longitude, radius)
                
                if results:
                    st.success(f"✅ Found {len(results)} pharmacies")
                    
                    for i, pharmacy in enumerate(results, 1):
                        render_pharmacy_card(pharmacy, i)
                else:
                    st.warning("⚠️ No pharmacies found in this area. Try increasing the search radius.")
                    
            except Exception as e:
                st.error(f"⚠️ Search failed: {str(e)}")
                logger.error(f"GPS pharmacy search error: {e}")


def render_address_search():
    """Address-based pharmacy search"""
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='medical-card'>
            <p style='color: var(--text-secondary); margin-bottom: 1rem;'>
                🏠 Enter an address to find nearby pharmacies
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    address = st.text_input(
        "Enter Address",
        placeholder="e.g., 123 Main Street, Chennai, Tamil Nadu",
        help="Enter a full address including city and state"
    )
    
    radius = st.slider(
        "Search Radius (meters)",
        min_value=500,
        max_value=10000,
        value=5000,
        step=500,
        help="Set the search radius around the address",
        key="address_radius"
    )
    
    if st.button("🔍 Search by Address", use_container_width=True):
        if not address:
            st.error("⚠️ Please enter an address")
        else:
            with st.spinner("🔄 Geocoding address and searching..."):
                try:
                    pharmacy_locator = st.session_state.pharmacy_locator
                    
                    # Geocode address
                    coords = pharmacy_locator.geocode_address(address)
                    
                    if coords:
                        lat, lng = coords
                        st.info(f"📍 Location found: {lat:.6f}, {lng:.6f}")
                        
                        # Find pharmacies
                        results = pharmacy_locator.find_nearby_pharmacies(lat, lng, radius)
                        
                        if results:
                            st.success(f"✅ Found {len(results)} pharmacies")
                            
                            for i, pharmacy in enumerate(results, 1):
                                render_pharmacy_card(pharmacy, i)
                        else:
                            st.warning("⚠️ No pharmacies found near this address. Try increasing the search radius.")
                    else:
                        st.error("⚠️ Unable to locate address. Please verify and try again.")
                        
                except Exception as e:
                    st.error(f"⚠️ Search failed: {str(e)}")
                    logger.error(f"Address pharmacy search error: {e}")


def render_pharmacy_card(pharmacy: Dict, index: int):
    """Render a single pharmacy card with full details"""
    
    name = pharmacy.get('name', 'Unnamed Pharmacy')
    address = pharmacy.get('address', 'Address not available')
    distance = pharmacy.get('distance', 0)
    rating = pharmacy.get('rating', 0)
    is_open = pharmacy.get('is_open_now', False)
    phone = pharmacy.get('phone', 'Not available')
    lat = pharmacy.get('latitude', 0)
    lng = pharmacy.get('longitude', 0)
    
    status_color = "#10B981" if is_open else "#EF4444"
    status_text = "🟢 Open Now" if is_open else "🔴 Closed"
    
    # Google Maps direction link
    maps_link = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
    
    st.markdown(f"""
        <div class='medical-card' style='margin-bottom: 1.5rem;'>
            <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;'>
                <div style='flex: 1;'>
                    <h3 style='color: #F1F5F9; margin-bottom: 0.5rem; font-size: 20px;'>{index}. {name}</h3>
                    <p style='color: #94A3B8; margin: 0.3rem 0; font-size: 14px;'>📍 {address}</p>
                    <p style='color: #94A3B8; margin: 0.3rem 0; font-size: 14px;'>📞 {phone}</p>
                </div>
                <div style='text-align: right;'>
                    <span style='color: {status_color}; font-weight: 600; display: block; margin-bottom: 0.5rem; font-size: 14px;'>
                        {status_text}
                    </span>
                    <span style='color: #94A3B8; font-size: 14px;'>⭐ {rating}/5</span>
                </div>
            </div>
            <div style='display: flex; gap: 1rem; align-items: center; padding-top: 1rem; border-top: 1px solid #334155;'>
                <span style='color: #10B981; font-weight: 600; font-size: 15px;'>📏 {distance:.0f}m away</span>
                <a href="{maps_link}" target="_blank" style='background: linear-gradient(135deg, #10B981 0%, #34D399 100%); color: white; padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px;'>
                    🧭 Get Directions
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)
