import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import io

# Page configuration
st.set_page_config(
    page_title="LTV data",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# AppsFlyer API configuration
API_BASE_URL = "https://hq1.appsflyer.com/api/master-agg-data/v4/app"
TOKEN = "eyJhbGciOiJBMjU2S1ciLCJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwidHlwIjoiSldUIiwiemlwIjoiREVGIn0.dGjmXmbbG3UOtUOmeAhKRhlL466oak8HRQ-DQSQK9IQFWZgR-Zl5oQ.g-fgbB91nXU1CcE2.gqImrk2du3wPYyzI-pLjyCyJyF3aqj_LHlHZEIxrjt4v2HhCN_OXx3daofPJRm_sJOIOMxnGujDga_5zU8b2qpr6bTuB2-YUywZIYRXIWM0D7s1tCBc8O9tvY_V3Vb3sOf5PZ4YwCMqO7ig-xEbHRa57pP9H90nAKIWU09cFg8uJFJDWNaBSV7qYEwv0cpozwhjztKs8ME7TuqBnS31D9YXosxaXeJPq8Px1fHtTTll0ZW3WJE-RSD_a2mOoaQFvCVpl9yXTzBiJ7MqjJYVFhcQsSfv2E3pBHiZPFwvI1EzEHQ-lOVDzcVgDSfkQ9cs4YR2CQX4LV1Tf3UUFzX8bcPQs_Qd4jADFBSlA8n0w_oAAMJRGiN1Vw7SRNGeZs1CJXJWlUkmKVSt4ByIIUUpWcQqEl4BHUE5sUtY-1TYqteOuYLoAnPzOcvrJCTwplTpbTNqq6axe_yq--iBXEQaulUBCnrwcAOEokjvLEkjOduMg9gBhaO8f93MislDBnPOkPnN4_runyD45q49tnYzRfMsK9cE.-OEJKOl5ZsDL4c8f1fQARg"

# Game configurations
GAMES = {
    "2248": {
        "name": "2248 Number Puzzle Game",
        "package_id": "com.inspiredsquare.jupiter"
    },
    "X2": {
        "name": "X2 Blocks Game", 
        "package_id": "com.inspiredsquare.blocks"
    }
}

# Page configurations
PAGES = {
    "Camp + Media_source + Geo": {
        "groupings": "c,pid,geo",
        "description": "Data grouped by Campaign, Publisher ID, and Geography"
    },
    "Camp + Media_source": {
        "groupings": "c,pid",
        "description": "Data grouped by Campaign and Publisher ID"
    },
    "Media_source Only": {
        "groupings": "pid",
        "description": "Data grouped by Publisher ID only"
    }
}

def fetch_appsflyer_data(package_id, start_date, end_date, groupings):
    """Fetch data from AppsFlyer API"""
    url = f"{API_BASE_URL}/{package_id}"
    
    params = {
        "from": start_date.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "groupings": groupings,
        "kpis": "cost,revenue,arpu_ltv,installs"
    }
    
    headers = {
        "accept": "text/csv",
        "authorization": f"Bearer {TOKEN}"
    }
    
    try:
        with st.spinner(f"🔄 Fetching data for {package_id}..."):
            response = requests.get(url, headers=headers, params=params)
            
        if response.status_code == 200:
            # Parse CSV data
            csv_data = io.StringIO(response.text)
            df = pd.read_csv(csv_data)
            return df, None
        else:
            # Provide helpful error messages
            if response.status_code == 401:
                return None, "Authentication Error: Please check if the API token is valid and has proper permissions."
            elif response.status_code == 403:
                return None, "Permission Error: The token doesn't have access to this app's data."
            elif response.status_code == 404:
                return None, "App Not Found: The package ID might be incorrect or the app doesn't exist."
            else:
                return None, f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Request Error: {str(e)}"

def main():
    # Header - smaller and more compact
    st.header("LTV data")
    
    # Sidebar for controls - compact layout
    with st.sidebar:
        st.markdown("### Controls")
        # Page selection
        selected_page = st.selectbox(
            "Choose grouping:",
            options=list(PAGES.keys())
        )
        
        # Game selection
        selected_game_key = st.selectbox(
            "Choose a game:",
            options=list(GAMES.keys()),
            format_func=lambda x: f"{GAMES[x]['name']} ({x})"
        )
        
        selected_game = GAMES[selected_game_key]
        
        # Date range selection - more compact
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            max_value=datetime.now()
        )
        
        end_date = st.date_input(
            "End Date", 
            value=datetime.now(),
            max_value=datetime.now()
        )
        
        # Auto-fetch data for last 30 days on first load
        if 'first_load' not in st.session_state:
            st.session_state.first_load = True
            st.session_state.fetch_clicked = True
            st.session_state.selected_game = selected_game
            st.session_state.selected_page = selected_page
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
        
        # Validate date range
        if start_date > end_date:
            st.error("Start date cannot be after end date!")
            return
        
        # Fetch button
        if st.button("🚀 Fetch Data", type="primary", use_container_width=True):
            st.session_state.fetch_clicked = True
            st.session_state.selected_game = selected_game
            st.session_state.selected_page = selected_page
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
    
    # Main content area
    if hasattr(st.session_state, 'fetch_clicked') and st.session_state.fetch_clicked:
        # Fetch real data
        df, error = fetch_appsflyer_data(
            st.session_state.selected_game['package_id'],
            st.session_state.start_date,
            st.session_state.end_date,
            PAGES[st.session_state.selected_page]['groupings']
        )
        
        if error:
            st.error(f"❌ {error}")
        elif df is not None:
            # Format the dataframe for better display
            df_display = df.copy()
            
            # Format cost columns to 0 decimal places
            cost_columns = [col for col in df_display.columns if 'cost' in col.lower()]
            for col in cost_columns:
                if col in df_display.columns and df_display[col].dtype in ['int64', 'float64']:
                    df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else x)
            
            # Format LTV and revenue columns to 2 decimal places
            ltv_revenue_columns = [col for col in df_display.columns if any(term in col.lower() for term in ['ltv', 'revenue', 'arpu'])]
            for col in ltv_revenue_columns:
                if col in df_display.columns and df_display[col].dtype in ['int64', 'float64']:
                    df_display[col] = df_display[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else x)
            
            # Data table - full height and width
            st.dataframe(
                df_display,
                use_container_width=True,
                height=600
            )
    
    else:
        # Empty state - no content until user clicks fetch
        pass

if __name__ == "__main__":
    main()
