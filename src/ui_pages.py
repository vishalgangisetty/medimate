import streamlit as st
from datetime import datetime, date


def render_reminder_page():
    lang = st.session_state.language_manager
    st.markdown(f"<h1 class='animate-header'><span class='gradient-text'>{lang.get_text('medicine_reminder')}</span></h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        f"📅 {lang.get_text('add_reminder')}", 
        f"⏰ Today's Schedule",
        f"📊 Adherence Stats"
    ])
    
    with tab1:
        st.subheader(lang.get_text("add_reminder"))
        
        col1, col2 = st.columns(2)
        with col1:
            medicine_name = st.text_input(lang.get_text("medicine_name"))
            dosage = st.text_input(lang.get_text("dosage"), placeholder="e.g., 1 tablet, 5ml")
            frequency = st.selectbox(lang.get_text("frequency"), [
                lang.get_text("daily"),
                lang.get_text("twice_daily"),
                lang.get_text("thrice_daily"),
            ])
        
        with col2:
            start_date_input = st.date_input("Start Date", value=date.today())
            start_date = start_date_input[0] if isinstance(start_date_input, tuple) else start_date_input
            duration_days = st.number_input(lang.get_text("duration"), min_value=1, value=7)
            with_food = st.checkbox(lang.get_text("with_food"))
        
        times = []
        if frequency == lang.get_text("daily"):
            time1 = st.time_input("Time", value=datetime.strptime("09:00", "%H:%M").time())
            times = [time1.strftime("%H:%M")]
        elif frequency == lang.get_text("twice_daily"):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                time1 = st.time_input("Morning", value=datetime.strptime("09:00", "%H:%M").time())
            with col_t2:
                time2 = st.time_input("Evening", value=datetime.strptime("21:00", "%H:%M").time())
            times = [time1.strftime("%H:%M"), time2.strftime("%H:%M")]
        elif frequency == lang.get_text("thrice_daily"):
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                time1 = st.time_input("Morning", value=datetime.strptime("09:00", "%H:%M").time())
            with col_t2:
                time2 = st.time_input("Afternoon", value=datetime.strptime("14:00", "%H:%M").time())
            with col_t3:
                time3 = st.time_input("Night", value=datetime.strptime("21:00", "%H:%M").time())
            times = [time1.strftime("%H:%M"), time2.strftime("%H:%M"), time3.strftime("%H:%M")]
        
        instructions = st.text_area("Instructions", placeholder="e.g., Take after meal")
        
        add_to_calendar = st.checkbox("📅 Add to Google Calendar", value=False)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(lang.get_text("save"), use_container_width=True):
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
                        st.success(f"✅ Reminder added for {medicine_name}!")
                        
                        if add_to_calendar:
                            try:
                                from src.calendar_integration import CalendarIntegration
                                calendar = CalendarIntegration()
                                cal_result = calendar.create_multiple_reminder_events(
                                    medicine_name, dosage, times, start_date.isoformat(),
                                    duration_days, instructions
                                )
                                if cal_result['success']:
                                    st.success(f"✅ Added to Google Calendar! ({cal_result['created']}/{cal_result['total']} events)")
                                else:
                                    st.warning("⚠️ Reminder saved but Calendar sync failed. Check credentials.json")
                            except Exception as e:
                                st.warning(f"⚠️ Calendar integration error: {str(e)}")
                        
                        st.balloons()
                    else:
                        st.error(f"Error: {result['error']}")
                else:
                    st.error("Please fill all required fields")
    
    with tab2:
        st.subheader("Today's Medication Schedule")
        
        todays_reminders = st.session_state.reminder_manager.get_todays_reminders(st.session_state.user)
        
        if not todays_reminders:
            st.info("No medications scheduled for today")
        else:
            for reminder in todays_reminders:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        icon = "✅" if reminder['taken'] else "⏰"
                        st.markdown(f"### {icon} {reminder['medicine_name']}")
                        st.write(f"**{reminder['dosage']}** at **{reminder['time']}**")
                        if reminder['with_food']:
                            st.write("🍽️ " + lang.get_text("with_food"))
                        if reminder['instructions']:
                            st.caption(reminder['instructions'])
                    
                    with col2:
                        if not reminder['taken']:
                            if st.button(lang.get_text("mark_taken"), key=f"taken_{reminder['_id']}_{reminder['time']}"):
                                result = st.session_state.reminder_manager.mark_as_taken(
                                    st.session_state.user,
                                    reminder['medicine_name'],
                                    reminder['time']
                                )
                                if result['success']:
                                    st.success("Marked!")
                                    st.rerun()
                    
                    with col3:
                        if not reminder['taken']:
                            if st.button("Skip", key=f"skip_{reminder['_id']}_{reminder['time']}"):
                                result = st.session_state.reminder_manager.mark_as_skipped(
                                    st.session_state.user,
                                    reminder['medicine_name'],
                                    reminder['time']
                                )
                                if result['success']:
                                    st.warning("Skipped")
                                    st.rerun()
                    
                    st.divider()
    
    with tab3:
        st.subheader("Medication Adherence")
        
        days_filter = st.selectbox("Period", [7, 14, 30], format_func=lambda x: f"Last {x} days")
        
        stats = st.session_state.reminder_manager.get_adherence_stats(st.session_state.user, days_filter)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Doses", stats['total_doses'])
        with col2:
            st.metric("Taken", stats['taken'], delta_color="normal")
        with col3:
            st.metric("Skipped", stats['skipped'], delta_color="inverse")
        with col4:
            st.metric("Adherence Rate", f"{stats['adherence_rate']}%")
        
        # Show all reminders with delete option
        st.divider()
        st.subheader("All Reminders")
        
        all_reminders = st.session_state.reminder_manager.get_user_reminders(st.session_state.user, active_only=False)
        
        if all_reminders:
            for reminder in all_reminders:
                with st.expander(f"{'✅' if reminder['is_active'] else '❌'} {reminder['medicine_name']} - {reminder['dosage']}"):
                    st.write(f"**Frequency:** {reminder['frequency']}")
                    st.write(f"**Times:** {', '.join(reminder['times'])}")
                    st.write(f"**Duration:** {reminder['start_date']} to {reminder['end_date']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Toggle Active/Inactive", key=f"toggle_{reminder['_id']}"):
                            result = st.session_state.reminder_manager.toggle_reminder(
                                reminder['_id'],
                                not reminder['is_active']
                            )
                            if result['success']:
                                st.rerun()
                    with col2:
                        if st.button(lang.get_text("delete"), key=f"del_{reminder['_id']}"):
                            result = st.session_state.reminder_manager.delete_reminder(reminder['_id'])
                            if result['success']:
                                st.success("Deleted!")
                                st.rerun()
        else:
            st.info("No reminders set yet")


def render_pharmacy_locator_page():
    from src.pharmacy_locator import SAMPLE_PHARMACIES
    
    lang = st.session_state.language_manager
    st.markdown(f"<h1 class='animate-header'><span class='gradient-text'>{lang.get_text('pharmacy_locator')}</span></h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([f"🗺️ By Address", f"📍 By Coordinates", "📋 Sample Data"])
    
    with tab1:
        st.subheader("Search by Address")
        address = st.text_input("Enter your location", placeholder="e.g., Connaught Place, New Delhi")
        
        col1, col2 = st.columns(2)
        with col1:
            radius = st.number_input("Search Radius (km)", min_value=1, max_value=50, value=5, key="addr_radius")
        with col2:
            max_results = st.number_input("Max Results", min_value=5, max_value=20, value=10, key="addr_max")
        
        if st.button("🔍 Search Pharmacies", use_container_width=True, key="search_addr"):
            if not address:
                st.error("Please enter an address")
            else:
                with st.spinner("Finding location..."):
                    location = st.session_state.pharmacy_locator.geocode_address(address)
                    
                    if location:
                        st.success(f"📍 Found: {location['formatted_address']}")
                        
                        with st.spinner("Searching pharmacies..."):
                            pharmacies = st.session_state.pharmacy_locator.find_nearby_pharmacies(
                                location['latitude'], location['longitude'], radius * 1000, max_results
                            )
                            
                            if pharmacies:
                                st.success(f"Found {len(pharmacies)} pharmacies!")
                                display_pharmacies(pharmacies, location['latitude'], location['longitude'], lang)
                            else:
                                st.warning("No pharmacies found. Try increasing radius or check if Google Places API is enabled.")
                    else:
                        st.error("Could not find location. Please check address or try coordinates.")
    
    with tab2:
        st.subheader("Search by GPS Coordinates")
        st.markdown("""
        **Get your coordinates:**
        - Open Google Maps → Right-click your location → Click the coordinates to copy
        - Or use browser location (if enabled)
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=28.6139, format="%.6f")
            radius_coord = st.number_input("Search Radius (km)", min_value=1, max_value=50, value=5, key="coord_radius")
        with col2:
            longitude = st.number_input("Longitude", value=77.2090, format="%.6f")
            max_results_coord = st.number_input("Max Results", min_value=5, max_value=20, value=10, key="coord_max")
        
        if st.button(f"🔍 {lang.get_text('search')} Pharmacies", use_container_width=True, key="search_coord"):
            with st.spinner("Searching nearby pharmacies..."):
                pharmacies = st.session_state.pharmacy_locator.find_nearby_pharmacies(
                    latitude, longitude, radius_coord * 1000, max_results_coord
                )
                
                if pharmacies:
                    st.success(f"Found {len(pharmacies)} pharmacies!")
                    display_pharmacies(pharmacies, latitude, longitude, lang)
                else:
                    st.warning("No pharmacies found. Make sure Google Places API is enabled in your Google Cloud Console.")
    
    with tab3:
        st.subheader("Sample Pharmacy Data")
        st.info("This is demo data. Use search tabs for real results.")
        
        for pharmacy in SAMPLE_PHARMACIES:
            with st.container():
                st.markdown(f"### 🏥 {pharmacy['name']}")
                st.write(f"📍 {pharmacy['address']}")
                st.write(f"📞 {pharmacy['phone']}")
                st.write(f"⭐ {pharmacy['rating']}/5.0")
                status = lang.get_text("open_now") if pharmacy['open_now'] else lang.get_text("closed")
                color = "green" if pharmacy['open_now'] else "red"
                st.markdown(f"**Status:** :{color}[{status}]")
                st.divider()


def display_pharmacies(pharmacies, user_lat, user_lng, lang):
    for pharmacy in pharmacies:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### 🏥 {pharmacy['name']}")
                st.write(f"📍 {pharmacy['address']}")
                
                if pharmacy.get('phone'):
                    st.write(f"📞 **{lang.get_text('phone')}:** {pharmacy['phone']}")
                else:
                    st.write("📞 Phone: Not available")
                
                if pharmacy.get('rating'):
                    st.write(f"⭐ {pharmacy['rating']} ({pharmacy.get('total_ratings', 0)} reviews)")
                
                if pharmacy.get('open_now') is not None:
                    status = lang.get_text("open_now") if pharmacy['open_now'] else lang.get_text("closed")
                    color = "green" if pharmacy['open_now'] else "red"
                    st.markdown(f"**Status:** :{color}[{status}]")
                
                if pharmacy.get('website'):
                    st.markdown(f"🌐 [{pharmacy['website']}]({pharmacy['website']})")
            
            with col2:
                from src.pharmacy_locator import PharmacyLocator
                locator = PharmacyLocator()
                directions_url = locator.get_directions_url(
                    user_lat, user_lng,
                    pharmacy['latitude'], pharmacy['longitude']
                )
                st.link_button(lang.get_text("get_directions"), directions_url)
                
                distance = locator.calculate_distance(
                    user_lat, user_lng,
                    pharmacy['latitude'], pharmacy['longitude']
                )
                st.metric("Distance", f"{distance:.2f} km")
            
            st.divider()
                )
                
                if pharmacies:
                    st.success(f"Found {len(pharmacies)} pharmacies!")
                    
                    for pharmacy in pharmacies:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"### 🏥 {pharmacy['name']}")
                                st.write(f"📍 {pharmacy['address']}")
                                
                                if pharmacy.get('phone'):
                                    st.write(f"📞 **{lang.get_text('phone')}:** {pharmacy['phone']}")
                                else:
                                    st.write("📞 Phone: Not available")
                                
                                if pharmacy.get('rating'):
                                    st.write(f"⭐ {pharmacy['rating']} ({pharmacy.get('total_ratings', 0)} reviews)")
                                
                                if pharmacy.get('open_now') is not None:
                                    status = lang.get_text("open_now") if pharmacy['open_now'] else lang.get_text("closed")
                                    color = "green" if pharmacy['open_now'] else "red"
                                    st.markdown(f"**Status:** :{color}[{status}]")
                                
                                if pharmacy.get('website'):
                                    st.markdown(f"🌐 [{pharmacy['website']}]({pharmacy['website']})")
                            
                            with col2:
                                directions_url = st.session_state.pharmacy_locator.get_directions_url(
                                    latitude, longitude,
                                    pharmacy['latitude'], pharmacy['longitude']
                                )
                                st.link_button(lang.get_text("get_directions"), directions_url)
                                
                                distance = st.session_state.pharmacy_locator.calculate_distance(
                                    latitude, longitude,
                                    pharmacy['latitude'], pharmacy['longitude']
                                )
                                st.metric("Distance", f"{distance:.2f} km")
                            
                            st.divider()
                else:
                    st.warning("No pharmacies found in this area. Try increasing the search radius.")
    
    with tab2:
        st.subheader("Sample Pharmacy Data (Demo)")
        st.info("This is sample data for demonstration. Use the search feature with your location for real results.")
        
        for pharmacy in SAMPLE_PHARMACIES:
            with st.container():
                st.markdown(f"### 🏥 {pharmacy['name']}")
                st.write(f"📍 {pharmacy['address']}")
                st.write(f"📞 {pharmacy['phone']}")
                st.write(f"⭐ {pharmacy['rating']}/5.0")
                
                status = lang.get_text("open_now") if pharmacy['open_now'] else lang.get_text("closed")
                color = "green" if pharmacy['open_now'] else "red"
                st.markdown(f"**Status:** :{color}[{status}]")
                
                st.divider()
