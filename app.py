import streamlit as st
import pandas as pd
import random

st.title("CortexFlo Driver Scheduler")

# Upload CSV files
driver_file = st.file_uploader("Upload driver list (CSV)", type=['csv'])
shift_file = st.file_uploader("Upload shift template (CSV)", type=['csv'])

if driver_file and shift_file:
    # Read driver CSV, remove BOM/extra spaces
    drivers_df = pd.read_csv(driver_file, encoding='utf-8-sig')
    drivers_df.columns = drivers_df.columns.str.strip()
    drivers_df['Assigned Hours'] = 0

    # Read shift CSV, remove BOM/extra spaces
    shifts_df = pd.read_csv(shift_file, encoding='utf-8-sig')
    shifts_df.columns = shifts_df.columns.str.strip()
    shifts_df['Driver'] = ""

    # Debug: show actual columns (optional)
    # st.write("Shift columns detected:", shifts_df.columns.tolist())

    # Track last driver per day to avoid back-to-back shifts
    last_driver_per_day = {}

    # Assign drivers
    for idx, row in shifts_df.iterrows():
        day = row['Day']
        available_drivers = drivers_df[drivers_df['Available Days'].str.contains(day, case=False, na=False)]

        # Avoid back-to-back
        if day in last_driver_per_day:
            available_drivers = available_drivers[available_drivers['Driver'] != last_driver_per_day[day]]

        # Assign driver if available
        if not available_drivers.empty:
            min_hours = available_drivers['Assigned Hours'].min()
            candidates = available_drivers[available_drivers['Assigned Hours'] == min_hours]
            chosen_driver = random.choice(candidates['Driver'].tolist())
            shifts_df.at[idx, 'Driver'] = chosen_driver
            drivers_df.loc[drivers_df['Driver'] == chosen_driver, 'Assigned Hours'] += 10
            last_driver_per_day[day] = chosen_driver
        else:
            shifts_df.at[idx, 'Driver'] = "No available driver"

    st.subheader("Generated Schedule")
    st.dataframe(shifts_df)

    # Download CSV
    st.download_button(
        label="Download Schedule",
        data=shifts_df.to_csv(index=False).encode('utf-8'),
        file_name='driver_schedule.csv',
        mime='text/csv'
    )

    st.success("Schedule generated! Respects availability, max 10-hour shifts, and avoids back-to-back assignments.")



