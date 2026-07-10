import pandas as pd
import sqlite3
import datetime

PROJECT_VENDOR_MAPPING = {
    'NHP': ['Encardio Rite', 'Aquasense'],
    'Atal Bhujal Yojana': ['Swan Environmental', 'Engineering & Enviro'],
    'Departmental': ['Aquasense', 'Engineering & Enviro']
}

def clean_and_validate_data():
    raw_csv_path = "daily_dwlr_data.csv"
    try:
        # File read karna
        df = pd.read_csv(raw_csv_path)
    except FileNotFoundError:
        print("❌ CSV file nahi mili. Kripya pehle daily_dwlr_data.csv file upload karein.")
        return

    # 1. Aapki file ke column names ko hamare system ke mutabik rename karna
    df.rename(columns={
        'Station ID': 'Station_ID', 
        'Corrected Water Level(m)': 'Water_Level_mbgl'
    }, inplace=True)

    # Blank IDs drop karna
    df.dropna(subset=['Station_ID'], inplace=True)
    df['Water_Level_mbgl'].fillna(-999, inplace=True)

    # 2. Jo columns aapki file mein nahi hain, unhe default values ke sath add karna
    if 'District' not in df.columns:
        df['District'] = "Unknown District"
        
    if 'Project_Name' not in df.columns:
        df['Project_Name'] = "Departmental" # Default project
        
    if 'Vendor_Name' not in df.columns:
        df['Vendor_Name'] = "Aquasense" # Default vendor (Mapped to Departmental)

    # 3. Status set karna
    def evaluate_status(row):
        # Agar water level -999 hai, toh inactivate kar do
        if row['Water_Level_mbgl'] == -999:
            return 'Inactive'
        return 'Active'

    df['Current_Status'] = df.apply(evaluate_status, axis=1)
    df['Ingestion_Date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 4. Database mein save karna
    conn = sqlite3.connect('groundwater_mis.db')
    df.to_sql('dwlr_master', conn, if_exists='replace', index=False)
    conn.close()
    
    print("✅ Success: Aapka actual data system mein theek se process aur update ho gaya hai!")

if __name__ == "__main__":
    clean_and_validate_data()