import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def display_dashboard(patients_df, visits_df, resources_df, costs_df):
    """Display the main dashboard with all metrics"""
    cols = st.columns(6)

    # Metrics calculations
    sa_citizens = len(patients_df[patients_df['nationality'] == "South African"])
    legal_immigrants = len(patients_df[patients_df['legal_status'] == "Valid"])
    needs_review = len(patients_df[patients_df.get('status', '').astype(str).str.contains("Review", na=False)])

    # Safely fetch metrics with fallback values
    beds_available = resources_df['beds_available'].iloc[0] if 'beds_available' in resources_df and not resources_df.empty else 0
    med_stock = resources_df['medication_stock'].iloc[0] if 'medication_stock' in resources_df and not resources_df.empty else 0
    today_cost = costs_df['daily_cost'].iloc[0] if 'daily_cost' in costs_df and not costs_df.empty else 0

    # Display metrics
    cols[0].metric("SA Patients", sa_citizens)
    cols[1].metric("Legal Immigrants", legal_immigrants)
    cols[2].metric("Needs Review", needs_review)
    cols[3].metric("Beds Available", beds_available)
    cols[4].metric("Med Stock", f"{med_stock} days")
    cols[5].metric("Today's Cost", f"R{today_cost:,.2f}")

    # Admin tools
    if st.sidebar.checkbox("🛠️ Admin Tools", True):
        tab1, tab2, tab3 = st.tabs(["Patient Management", "Resource Control", "Financials"])

        with tab1:
            st.subheader("Patient Verification")

            if 'full_name' in patients_df.columns and not patients_df.empty:
                selected_patient = st.selectbox("Select Patient", patients_df['full_name'].dropna())
                patient_data = patients_df[patients_df['full_name'] == selected_patient].iloc[0]

                # Display patient details
                cols = st.columns(2)
                cols[0].write(f"**Name:** {patient_data['full_name']}")
                cols[1].write(f"**Status:** {patient_data.get('status', 'Unknown')}")
                cols[0].write(f"**ID Number:** {patient_data.get('id_number', 'N/A')}")
                cols[1].write(f"**Nationality:** {patient_data['nationality']}")

                # Convert visit_date to datetime.date safely
                visits_df['visit_date'] = pd.to_datetime(visits_df['visit_date'], errors='coerce').dt.date

                # Filter recent visits (last 7 days)
                recent_visits = visits_df[
                    (visits_df['patient_name'] == patient_data['full_name']) &
                    (visits_df['visit_date'] >= (datetime.now().date() - timedelta(days=7)))
                ]

                st.write(f"**Visits (7 days):** {len(recent_visits)}")

                if patient_data['nationality'] != "South African":
                    if st.button("🚨 Refer for Deportation"):
                        st.warning(f"Referred {patient_data['full_name']} to Home Affairs")

                    if st.button("💳 Generate Invoice"):
                        st.success(f"Invoice amount: R{patient_data.get('estimated_cost', 0):.2f}")
            else:
                st.info("No patients available to verify.")

        with tab2:
            st.subheader("Resource Monitoring")
            res_cols = st.columns(3)

            med_stock_tab = resources_df['medication_stock'].iloc[0] if 'medication_stock' in resources_df and not resources_df.empty else 0
            beds_avail_tab = resources_df['beds_available'].iloc[0] if 'beds_available' in resources_df and not resources_df.empty else 0
            staff_tab = resources_df['staff_available'].iloc[0] if 'staff_available' in resources_df and not resources_df.empty else 0
            utilization = resources_df['utilization'].iloc[0] if 'utilization' in resources_df and not resources_df.empty else 0

            res_cols[0].metric("Medication Stock", f"{med_stock_tab} days")
            res_cols[1].metric("Available Beds", beds_avail_tab)
            res_cols[2].metric("Staff On Duty", staff_tab)

            st.progress(utilization / 100 if utilization else 0)

        with tab3:
            st.subheader("Financial Overview")
            daily_cost = costs_df['daily_cost'].iloc[0] if 'daily_cost' in costs_df and not costs_df.empty else 0
            avg_cost = costs_df['avg_patient_cost'].iloc[0] if 'avg_patient_cost' in costs_df and not costs_df.empty else 0

            st.write(f"**Today's Expenditure:** R{daily_cost:,.2f}")
            st.write(f"**Avg Cost per Patient:** R{avg_cost:,.2f}")

            cost_cols = ['medication_cost', 'staff_cost', 'facility_cost']
            if all(col in costs_df.columns for col in cost_cols):
                cost_data = costs_df[cost_cols].melt(var_name="Cost Type", value_name="Amount")
                st.bar_chart(cost_data.set_index("Cost Type"))
            else:
                st.warning("Cost breakdown data not available")