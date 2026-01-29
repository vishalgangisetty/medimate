import streamlit as st
from datetime import datetime, date


def render_reminder_page():
    """Dose Protocol - Premium Medicine Reminder System"""
    lang = st.session_state.language_manager
    
    st.markdown("""
        <h1 class='display-text fade-in'>💊 Smart Dose Protocol</h1>
        <p class='body-text' style='opacity: 0.8; margin-bottom: 2rem;'>
            Intelligent medication scheduling with adherence tracking and calendar sync
        </p>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        "📝 Configure Protocol",
        "⏰ Today's Dose Schedule",
        "📊 Adherence Intelligence"
    ])
    
    with tab1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 class='card-header'>Set New Dose Alert</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<p class='label-text'>Compound Identity</p>", unsafe_allow_html=True)
            medicine_name = st.text_input("Medicine", label_visibility="collapsed", placeholder="Enter compound name")
            
            st.markdown("<p class='label-text'>Dose Strength</p>", unsafe_allow_html=True)
            dosage = st.text_input("Dosage", label_visibility="collapsed", placeholder="e.g., 1 tablet, 5ml, 500mg")
            
            st.markdown("<p class='label-text'>Protocol Cycle</p>", unsafe_allow_html=True)
            frequency = st.selectbox(
                "Frequency",
                ["Daily", "Twice Daily", "Three Times Daily"],
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("<p class='label-text'>Treatment Arc Start</p>", unsafe_allow_html=True)
            start_date_input = st.date_input("Start", value=date.today(), label_visibility="collapsed")
            start_date = start_date_input[0] if isinstance(start_date_input, tuple) else start_date_input
            
            st.markdown("<p class='label-text'>Arc Duration (Days)</p>", unsafe_allow_html=True)
            duration_days = st.number_input("Duration", min_value=1, value=7, label_visibility="collapsed")
            
            with_food = st.checkbox("📍 Require food intake", value=False)
        
        # Timing Configuration
        st.markdown("<br><p class='label-text'>⏰ Dose Alert Times</p>", unsafe_allow_html=True)
        
        times = []
        if frequency == "Daily":
            time1 = st.time_input("Dose Time", value=datetime.strptime("09:00", "%H:%M").time())
            times = [time1.strftime("%H:%M")]
        elif frequency == "Twice Daily":
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                time1 = st.time_input("Morning Dose", value=datetime.strptime("09:00", "%H:%M").time())
            with col_t2:
                time2 = st.time_input("Evening Dose", value=datetime.strptime("21:00", "%H:%M").time())
            times = [time1.strftime("%H:%M"), time2.strftime("%H:%M")]
        elif frequency == "Three Times Daily":
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                time1 = st.time_input("Morning", value=datetime.strptime("09:00", "%H:%M").time())
            with col_t2:
                time2 = st.time_input("Afternoon", value=datetime.strptime("14:00", "%H:%M").time())
            with col_t3:
                time3 = st.time_input("Night", value=datetime.strptime("21:00", "%H:%M").time())
            times = [time1.strftime("%H:%M"), time2.strftime("%H:%M"), time3.strftime("%H:%M")]
        
        st.markdown("<br><p class='label-text'>Clinical Notes (Optional)</p>", unsafe_allow_html=True)
        instructions = st.text_area("Instructions", label_visibility="collapsed", placeholder="e.g., Take after meals, avoid alcohol")
        
        # Calendar Integration
        st.markdown("<br>", unsafe_allow_html=True)
        add_to_calendar = st.checkbox("📅 Sync to Google Calendar", value=False, 
                                      help="Creates recurring calendar events with reminders")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔐 Lock Protocol", use_container_width=True):
                if medicine_name and dosage and times and start_date:
                    result = st.session_state.reminder_manager.add_reminder(
                        user_id=st.session_state.user,
                        medicine_name=medicine_name,
                        dosage=dosage,
                        frequency=frequency,
                        times=times,
                        duration_days=duration_days,
                        start_date=start_date.isoformat(),
                        instructions=instructions,
                        with_food=with_food
                    )
                    
                    if result['success']:
                        st.success(f"✅ Protocol locked for {medicine_name}")
                        
                        if add_to_calendar:
                            try:
                                from src.calendar_integration import CalendarIntegration
                                calendar = CalendarIntegration()
                                cal_result = calendar.create_multiple_reminder_events(
                                    medicine_name, dosage, times, start_date.isoformat(),
                                    duration_days, instructions
                                )
                                if cal_result['success']:
                                    st.success(f"✅ Calendar synced! {cal_result['created']}/{cal_result['total']} events created")
                                else:
                                    st.warning("⚠️ Protocol saved but calendar sync failed. Check credentials.json")
                            except Exception as e:
                                st.warning(f"⚠️ Calendar integration error: {str(e)}")
                        
                        st.balloons()
                    else:
                        st.error(f"⚠️ Protocol lock failed: {result['error']}")
                else:
                    st.error("⚠️ All required fields must be completed")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<h3 class='card-header'>Today's Medication Schedule</h3>", unsafe_allow_html=True)
        
        todays_reminders = st.session_state.reminder_manager.get_todays_reminders(st.session_state.user)
        
        if not todays_reminders:
            st.info("📭 No doses scheduled for today")
        else:
            for reminder in todays_reminders:
                with st.container():
                    st.markdown("<div class='insight-panel'>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"<h4 class='card-header'>💊 {reminder['medicine_name']}</h4>", unsafe_allow_html=True)
                        st.write(f"**Dose:** {reminder['dosage']}")
                        if reminder.get('instructions'):
                            st.caption(f"📋 {reminder['instructions']}")
                    
                    with col2:
                        st.write(f"**Times:** {', '.join(reminder['times'])}")
                        st.write(f"**Cycle:** {reminder['frequency']}")
                        if reminder.get('with_food'):
                            st.caption("🍽️ Require food")
                    
                    with col3:
                        taken_today = reminder.get('taken_today', False)
                        if taken_today:
                            st.success("✅ Taken")
                        else:
                            if st.button("Mark Taken", key=f"mark_{reminder['id']}", use_container_width=True):
                                result = st.session_state.reminder_manager.mark_as_taken(
                                    reminder['id'], date.today().isoformat()
                                )
                                if result['success']:
                                    st.success("✅ Dose logged")
                                    st.rerun()
                                else:
                                    st.error("⚠️ Failed to log")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<h3 class='card-header'>Adherence Intelligence</h3>", unsafe_allow_html=True)
        
        stats = st.session_state.reminder_manager.get_adherence_stats(st.session_state.user)
        
        if stats:
            # Overview Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                    <div class='glass-card' style='text-align: center; padding: 1.5rem;'>
                        <p class='label-text'>Active Protocols</p>
                        <p class='display-text'>{}</p>
                    </div>
                """.format(stats['total_reminders']), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class='glass-card' style='text-align: center; padding: 1.5rem;'>
                        <p class='label-text'>Taken Doses</p>
                        <p class='display-text' style='color: var(--mint-signal);'>{}</p>
                    </div>
                """.format(stats['taken_count']), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                    <div class='glass-card' style='text-align: center; padding: 1.5rem;'>
                        <p class='label-text'>Missed Doses</p>
                        <p class='display-text' style='color: var(--coral-pulse);'>{}</p>
                    </div>
                """.format(stats['missed_count']), unsafe_allow_html=True)
            
            with col4:
                adherence = stats.get('adherence_rate', 0)
                color = "var(--mint-signal)" if adherence >= 80 else "var(--amber-caution)" if adherence >= 60 else "var(--coral-pulse)"
                st.markdown("""
                    <div class='glass-card' style='text-align: center; padding: 1.5rem;'>
                        <p class='label-text'>Adherence Rate</p>
                        <p class='display-text' style='color: {};'>{:.1f}%</p>
                    </div>
                """.format(color, adherence), unsafe_allow_html=True)
            
            # Detailed Stats
            st.markdown("<br>", unsafe_allow_html=True)
            for reminder_stat in stats.get('reminder_details', []):
                with st.expander(f"📊 {reminder_stat['medicine_name']} - {reminder_stat['dosage']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Total Doses:** {reminder_stat['total_doses']}")
                        st.write(f"**Taken:** {reminder_stat['taken']}")
                        st.write(f"**Missed:** {reminder_stat['missed']}")
                    with col2:
                        st.write(f"**Adherence:** {reminder_stat['adherence']:.1f}%")
                        st.write(f"**Times:** {', '.join(reminder_stat['times'])}")
                        
                        # Confidence meter
                        st.markdown(f"""
                            <div class='confidence-meter'>
                                <div class='confidence-fill' style='width: {reminder_stat['adherence']}%;'></div>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("📊 No adherence data available yet. Add your first dose protocol to begin tracking.")


def render_pharmacy_locator_page():
    """Care Network - Premium Pharmacy Locator"""
    from src.pharmacy_locator import SAMPLE_PHARMACIES
    
    lang = st.session_state.language_manager
    
    st.markdown("""
        <h1 class='display-text fade-in'>🏥 Care Network Radar</h1>
        <p class='body-text' style='opacity: 0.8; margin-bottom: 2rem;'>
            Discover nearby healthcare stations with real-time status and contact intelligence
        </p>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📍 Location Search", "🗺️ GPS Coordinates", "📋 Network Sample"])
    
    with tab1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 class='card-header'>Search by Address</h3>", unsafe_allow_html=True)
        
        st.markdown("<p class='label-text'>📍 Location Query</p>", unsafe_allow_html=True)
        address = st.text_input(
            "Address",
            placeholder="e.g., Connaught Place, New Delhi",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<p class='label-text'>Search Radius (km)</p>", unsafe_allow_html=True)
            radius = st.number_input("Radius", min_value=1, max_value=50, value=5, key="addr_radius", label_visibility="collapsed")
        with col2:
            st.markdown("<p class='label-text'>Max Results</p>", unsafe_allow_html=True)
            max_results = st.number_input("Max", min_value=5, max_value=20, value=10, key="addr_max", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Scan Care Network", use_container_width=True, key="search_addr"):
            if not address:
                st.error("⚠️ Location query required")
            else:
                with st.spinner("📡 Locating coordinates..."):
                    location = st.session_state.pharmacy_locator.geocode_address(address)
                    
                    if location:
                        st.success(f"✅ Location locked: {location['formatted_address']}")
                        
                        with st.spinner("🔍 Scanning network nodes..."):
                            pharmacies = st.session_state.pharmacy_locator.find_nearby_pharmacies(
                                location['latitude'], location['longitude'], radius * 1000, max_results
                            )
                            
                            if pharmacies:
                                st.success(f"✅ {len(pharmacies)} care stations discovered")
                                display_pharmacies_premium(pharmacies, location['latitude'], location['longitude'])
                            else:
                                st.warning("⚠️ No stations found. Increase radius or verify Google Places API is enabled.")
                    else:
                        st.error("⚠️ Location decode failed. Try GPS coordinates tab.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 class='card-header'>Precise GPS Coordinates</h3>", unsafe_allow_html=True)
        
        st.info("💡 Get coordinates: Google Maps → Right-click location → Click coordinates to copy")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<p class='label-text'>Latitude</p>", unsafe_allow_html=True)
            latitude = st.number_input("Lat", value=28.6139, format="%.6f", label_visibility="collapsed")
            
            st.markdown("<p class='label-text'>Search Radius (km)</p>", unsafe_allow_html=True)
            radius_coord = st.number_input("Radius", min_value=1, max_value=50, value=5, key="coord_radius", label_visibility="collapsed")
        
        with col2:
            st.markdown("<p class='label-text'>Longitude</p>", unsafe_allow_html=True)
            longitude = st.number_input("Long", value=77.2090, format="%.6f", label_visibility="collapsed")
            
            st.markdown("<p class='label-text'>Max Results</p>", unsafe_allow_html=True)
            max_results_coord = st.number_input("Max", min_value=5, max_value=20, value=10, key="coord_max", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Scan Network", use_container_width=True, key="search_coord"):
            with st.spinner("🔍 Scanning care network..."):
                pharmacies = st.session_state.pharmacy_locator.find_nearby_pharmacies(
                    latitude, longitude, radius_coord * 1000, max_results_coord
                )
                
                if pharmacies:
                    st.success(f"✅ {len(pharmacies)} care stations found")
                    display_pharmacies_premium(pharmacies, latitude, longitude)
                else:
                    st.warning("⚠️ No stations found. Verify Google Places API is enabled.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<h3 class='card-header'>Sample Network Data</h3>", unsafe_allow_html=True)
        st.info("📋 Demo data for interface preview. Use search tabs for live results.")
        
        for pharmacy in SAMPLE_PHARMACIES:
            st.markdown("<div class='insight-panel'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"<h4 class='card-header'>🏥 {pharmacy['name']}</h4>", unsafe_allow_html=True)
                st.write(f"📍 {pharmacy['address']}")
                st.write(f"📞 {pharmacy['phone']}")
                st.write(f"⭐ {pharmacy['rating']}/5.0")
                
                status = "Active Station" if pharmacy['open_now'] else "Offline Station"
                color = "var(--mint-signal)" if pharmacy['open_now'] else "var(--coral-pulse)"
                st.markdown(f"<p style='color: {color}; font-weight: 600;'>● {status}</p>", unsafe_allow_html=True)
            
            with col2:
                st.metric("Distance", "2.3 km")
            
            st.markdown("</div>", unsafe_allow_html=True)


def display_pharmacies_premium(pharmacies, user_lat, user_lng):
    """Display pharmacy results with premium design"""
    for pharmacy in pharmacies:
        st.markdown("<div class='insight-panel'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"<h4 class='card-header'>🏥 {pharmacy['name']}</h4>", unsafe_allow_html=True)
            st.write(f"📍 {pharmacy['address']}")
            
            if pharmacy.get('phone'):
                st.write(f"📞 **Contact:** {pharmacy['phone']}")
            else:
                st.caption("📞 Contact not available")
            
            if pharmacy.get('rating'):
                st.write(f"⭐ {pharmacy['rating']}/5.0 ({pharmacy.get('total_ratings', 0)} reviews)")
            
            if pharmacy.get('open_now') is not None:
                status = "Active Station" if pharmacy['open_now'] else "Offline Station"
                color = "var(--mint-signal)" if pharmacy['open_now'] else "var(--coral-pulse)"
                st.markdown(f"<p style='color: {color}; font-weight: 600; margin-top: 0.5rem;'>● {status}</p>", unsafe_allow_html=True)
            
            if pharmacy.get('website'):
                st.markdown(f"🌐 [Website]({pharmacy['website']})")
        
        with col2:
            from src.pharmacy_locator import PharmacyLocator
            locator = PharmacyLocator()
            
            directions_url = locator.get_directions_url(
                user_lat, user_lng,
                pharmacy['latitude'], pharmacy['longitude']
            )
            st.link_button("📍 Get Directions", directions_url, use_container_width=True)
            
            distance = locator.calculate_distance(
                user_lat, user_lng,
                pharmacy['latitude'], pharmacy['longitude']
            )
            st.metric("Distance", f"{distance:.2f} km")
        
        st.markdown("</div>", unsafe_allow_html=True)
