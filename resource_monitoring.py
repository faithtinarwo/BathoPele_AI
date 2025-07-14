import streamlit as st
from datetime import datetime
import pytz
from resource_predictor import predict_resources

SA_TIMEZONE = pytz.timezone('Africa/Johannesburg')

def display_resource_monitoring(resources_df, visits_df):
    st.markdown('<div class="header"><h1>🏥 Resource Monitoring</h1></div>', unsafe_allow_html=True)
    st.subheader("Daily Hospital Resource Metrics")

    # Select hospital
    if resources_df.empty:
        st.warning("No resource data available.")
        return

    hospitals = resources_df['hospital'].dropna().unique()
    selected_hospital = st.selectbox("Select Hospital", hospitals)

    hospital_resources = resources_df[resources_df['hospital'] == selected_hospital]

    # Select resource type for prediction
    resource_types = ["Beds", "Doctors", "Nurses", "Medications"]
    selected_resource = st.selectbox("Select resource to predict", resource_types)

    # Prophet forecast
    forecast = predict_resources(selected_resource.lower())
    if forecast is not None:
        st.write(f"### Next 7 Days Forecast for {selected_resource}")
        st.dataframe(forecast, use_container_width=True)
    else:
        st.info("Not enough historical data for prediction.")

    # Display metrics by ward
    for _, ward_data in hospital_resources.iterrows():
        ward_name = ward_data.get('ward', 'Unknown')
        st.markdown(f"### 🏥 Ward: {ward_name}")

        cols = st.columns([1, 2, 2, 2])

        # Beds Metric
        total_beds = int(ward_data.get('total_beds', 0))
        available_beds = int(ward_data.get('available_beds', 0))
        bed_percentage = (available_beds / total_beds * 100) if total_beds > 0 else 0
        cols[0].metric("Available Beds", f"{available_beds}/{total_beds}", f"{bed_percentage:.1f}% available")

        # Staff Metric
        doctors = [d.strip() for d in str(ward_data.get('doctors', '')).split(',') if d.strip()]
        nurses = [n.strip() for n in str(ward_data.get('nurses', '')).split(',') if n.strip()]
        cols[1].markdown("**Doctors on Duty:**")
        for doctor in doctors:
            cols[1].markdown(f"- {doctor}")
        cols[1].markdown("**Nurses on Duty:**")
        for nurse in nurses:
            cols[1].markdown(f"- {nurse}")

        # Medication Stock Metric
        medications = [m.strip() for m in str(ward_data.get('medications', '')).split(',') if m.strip()]
        stocks = [s.strip() for s in str(ward_data.get('medication_stock', '')).split(',') if s.strip()]
        med_stock_map = {}
        for med, stock in zip(medications, stocks):
            med_stock_map[med] = int(stock) if stock.isdigit() else stock
        cols[2].markdown("**Medication Stock:**")
        for med, stock in med_stock_map.items():
            cols[2].markdown(f"- {med}: {stock}")

        # Today's patients in the ward
        today_str = datetime.now(SA_TIMEZONE).strftime('%Y-%m-%d')
        today_patients = visits_df[
            (visits_df['hospital'] == selected_hospital) &
            (visits_df['ward'] == ward_name) &
            (visits_df['visit_date'] == today_str)
        ]
        cols[3].markdown("**Patients Admitted Today:**")
        if not today_patients.empty:
            for pname in today_patients['patient_name']:
                cols[3].markdown(f"- {pname}")
        else:
            cols[3].markdown("_No new patients today_")

    # Hospital summary
    st.subheader("Hospital Daily Summary")
    total_hospital_beds = hospital_resources['total_beds'].sum()
    available_hospital_beds = hospital_resources['available_beds'].sum()
    st.metric("Total Beds Available", f"{available_hospital_beds}/{total_hospital_beds}")

    doctors_names = set()
    nurses_names = set()
    medication_stock_total = {}
    for _, ward in hospital_resources.iterrows():
        doctors_names.update([d.strip() for d in str(ward.get('doctors', '')).split(',') if d.strip()])
        nurses_names.update([n.strip() for n in str(ward.get('nurses', '')).split(',') if n.strip()])
        meds = [m.strip() for m in str(ward.get('medications', '')).split(',') if m.strip()]
        stocks = [s.strip() for s in str(ward.get('medication_stock', '')).split(',') if s.strip()]
        for med, stock in zip(meds, stocks):
            medication_stock_total[med] = medication_stock_total.get(med, 0) + (int(stock) if stock.isdigit() else 0)

    st.write("**Doctors on Duty Today:**")
    for d in sorted(doctors_names):
        st.write(f"- {d}")

    st.write("**Nurses on Duty Today:**")
    for n in sorted(nurses_names):
        st.write(f"- {n}")

    st.write("**Total Medication Stock Today:**")
    for med, stock in medication_stock_total.items():
        st.write(f"- {med}: {stock}")

