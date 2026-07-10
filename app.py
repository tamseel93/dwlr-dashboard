import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Ground Water DWLR MIS Portal", layout="wide")

# Database se data load karne ka function
def get_mis_data():
    conn = sqlite3.connect('groundwater_mis.db')
    df = pd.read_sql("SELECT * FROM dwlr_master", conn)
    conn.close()
    return df

st.title("💧 Ground Water Telemetry & Asset Management Portal")
st.subheader("Project-wise Vendor Deployment & Status Tracking")

try:
    df_master = get_mis_data()
    
    # Live KPI Cards
    total_dwlr = len(df_master)
    active_dwlr = len(df_master[df_master['Current_Status'] == 'Active'])
    inactive_dwlr = len(df_master[df_master['Current_Status'] == 'Inactive'])
    
    st.markdown("### 📊 Live Summary")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total DWLR Installed", total_dwlr)
    kpi2.metric("🟢 Active Status", active_dwlr)
    kpi3.metric("🔴 Inactive (Action Required)", inactive_dwlr)
    
    st.markdown("---")
    
    # Navigation Tabs
    tab_filter, tab_vendor_analytics = st.tabs(["🔍 Dependent Filter Explorer", "🏢 Vendor Performance Matrix"])
    
    with tab_filter:
        st.markdown("### 🎯 Smart Relational Filtering")
        
        # Step 1: Project Dropdown
        project_options = ['All Projects'] + list(df_master['Project_Name'].unique())
        selected_project = st.selectbox("1. प्रोजेक्ट का चयन करें (Select Project):", project_options)
        
        # Step 2: DYNAMIC Vendor Dropdown based on chosen project
        # Agar specific project selected hai, toh database se sirf uske active vendors nikalenge
        if selected_project != 'All Projects':
            filtered_by_proj = df_master[df_master['Project_Name'] == selected_project]
            vendor_options = ['All Target Vendors'] + list(filtered_by_proj['Vendor_Name'].unique())
        else:
            vendor_options = ['All Target Vendors'] + list(df_master['Vendor_Name'].unique())
            
        selected_vendor = st.selectbox("2. वेन्डर का चयन करें (Select Vendor):", vendor_options)
        
        # Step 3: Status Filter
        selected_status = st.radio("3. साइट की स्थिति (Device Status):", ['All', 'Active', 'Inactive'], horizontal=True)
        
        # Filtering logic application
        final_df = df_master.copy()
        if selected_project != 'All Projects':
            final_df = final_df[final_df['Project_Name'] == selected_project]
        if selected_vendor != 'All Target Vendors':
            final_df = final_df[final_df['Vendor_Name'] == selected_vendor]
        if selected_status != 'All':
            final_df = final_df[final_df['Current_Status'] == selected_status]
            
        st.markdown(f"**Filtered Results ({len(final_df)} Stations Found):**")
        st.dataframe(final_df, use_container_width=True)
        
        # Download Feature for the filtered view
        csv_data = final_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Current Filtered Data as CSV",
            data=csv_data,
            file_name="filtered_dwlr_report.csv",
            mime='text/csv'
        )
        
    with tab_vendor_analytics:
        st.markdown("### 📋 Project & Vendor Deployment Mapping")
        st.write("Aapke defined rules ke mutabik actual inventory breakdown:")
        
        # Grouping data to show allocation structure
        summary_table = df_master.groupby(['Project_Name', 'Vendor_Name', 'Current_Status']).size().reset_index(name='Total Units')
        st.dataframe(summary_table, use_container_width=True)

except Exception as e:
    st.error("Database initialization matrix empty. Kripya `db_updater.py` run karke pipeline active karein.")