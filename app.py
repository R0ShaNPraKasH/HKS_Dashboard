import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import plotly.io as pio

# Force all Plotly charts to use black text, black axes, and a beige background by default
pio.templates["custom_beige"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="#F5F5DC",
        plot_bgcolor="#F5F5DC",
        font=dict(color="#000000"), # Black global font
        title=dict(font=dict(color="#000000")), # Black title font
        xaxis=dict(
            title_font=dict(color="#000000"), 
            tickfont=dict(color="#000000"), 
            gridcolor="#E2E2D0" # Faint, slightly darker beige for gridlines
        ),
        yaxis=dict(
            title_font=dict(color="#000000"), 
            tickfont=dict(color="#000000"), 
            gridcolor="#E2E2D0"
        ),
        legend=dict(
            font=dict(color="#000000"), 
            title_font=dict(color="#000000")
        )
    )
)
pio.templates.default = "custom_beige"


# --- 1. PAGE CONFIGURATION & CUSTOM CSS ---
st.set_page_config(page_title="Kochi HKS: Waste as a Liaison", layout="wide", initial_sidebar_state="expanded")


# Custom CSS for colors, hover effects, and oval buttons
st.markdown("""
    <style>
    /* Force Sidebar to be White */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #FFFFFF !important;
    }
    /* Force main text and headers to black */
    .stApp, h1, h2, h3, h4, h5, h6, p, label, div.stMarkdown, span {
        color: #000000 !important;
    }
    .stApp { background-color: #F5F5DC; } /* Beige */
    
    /* Elegant KPI Cards */
    div[data-testid="metric-container"] {
        background-color: #FCFCFA; /* Soft off-white */
        border: 2px solid #C5E1A5; /* Light green accent */
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.08); /* Soft drop shadow */
    }
    
    /* Increase KPI Title Font Size */
    div[data-testid="metric-container"] label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #333333 !important;
    }
    
    /* Increase KPI Number Font Size and Color */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        color: #2E5C31 !important; /* Deep forest green for the numbers */
        font-weight: bold;
    }
    
    /* Customizing Streamlit buttons */
    div.stButton > button:first-child {
        background-color: #C5E1A5; color: #000000; border-radius: 50px; border: none; transition: all 0.3s ease; width: 100%; font-weight: bold;
    }
    div.stButton > button:first-child:hover {
        background-color: #a3c47d; transform: scale(1.05); box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Fix Streamlit Table Colors */
    table { color: #000000 !important; }
    th, td { color: #000000 !important; background-color: #FDFDFD !important; border-color: #E2E2D0 !important; }
    thead tr th { background-color: #C5E1A5 !important; color: #000000 !important; font-weight: bold !important; }
    
            /* Fix the Streamlit Top Bar / Header */
    [data-testid="stHeader"] {
        background-color: #F5F5DC !important; /* Matches your beige background */
    }
    
    /* Ensure the menu icons and buttons in the top bar are black */
    [data-testid="stHeader"] * {
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA LOADING & PROCESSING ---
# --- 2. DATA LOADING & PROCESSING ---
@st.cache_data
def load_data():
    df = pd.read_excel("HKS_DATA_work.xlsx") # Replace with your file
    
    # FIX: Convert 1/0/True/False to Yes/No for safety columns
    safety_cols = ['Gloves', 'Footwear', 'Mask', 'Cap', 'Sanitizer', 'Uniform']
    for col in safety_cols:
        if col in df.columns:
            # Replace various forms of 1/0 with Yes/No
            df[col] = df[col].replace({1: 'Yes', 0: 'No', 1.0: 'Yes', 0.0: 'No', '1': 'Yes', '0': 'No', True: 'Yes', False: 'No'})
            
    # Pre-calculate Per Capita Waste
    df['Per Capita Waste (KG)'] = df['Weight in KG'] / df['Population']
    return df

df = load_data()

# Helper function to format large numbers into Indian system
def format_indian_system(num):
    if pd.isna(num):
        return "0"
    if num >= 10000000: # Greater than or equal to 1 Crore
        return f"{num / 10000000:.2f} Crore"
    elif num >= 100000: # Greater than or equal to 1 Lakh
        return f"{num / 100000:.1f} Lakh"
    elif num >= 1000: # Greater than or equal to 1 Thousand
        return f"{num / 1000:.1f} K"
    else:
        return f"{num:,.0f}" # Just standard formatting for smaller numbers

# Place this near the top of your app.py so all sections can use it!
def create_kpi_card(title, value):
    return f"""
    <div style="background-color: #E8E8D0; border-radius: 12px; padding: 20px; margin: 10px 0; 
                border-left: 6px solid #C5E1A5; box-shadow: 2px 4px 10px rgba(0,0,0,0.05);">
        <p style="margin: 0; font-size: 16px; color: #444444; font-weight: 600;">{title}</p>
        <h2 style="margin: 5px 0 0 0; color: #2E5C31; font-size: 28px;">{value}</h2>
    </div>
    """

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("Kochi_skyline.jpg", use_column_width=True)
    st.markdown("### Navigation")
    
    # Top-left oval buttons for Section selection
    selected_section = option_menu(
        menu_title=None,
        options=["City Overview", "The Faces of HKS", "On the Ground", "Scoring System", "Value Chains", "Waste as a Liaison"],
        icons=["building", "people", "map", "star", "diagram-3", "recycle"], # Added diagram-3 for the new section
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff"},
            "icon": {"color": "black", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"5px", "border-radius": "25px", "color": "black"},
            "nav-link-selected": {"background-color": "#C5E1A5", "font-weight": "bold"},
        }
    )
    
    st.markdown("---")
    st.markdown("### View Mode")
    
    # Bottom-left perspective toggle
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Kochi View"):
            st.session_state.view_mode = "Kochi"
    with col2:
        if st.button("Wardwise"):
            st.session_state.view_mode = "Wardwise"

# Initialize session state for view mode
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Kochi"

st.sidebar.markdown(f"**Current View:** {st.session_state.view_mode}")

# --- 4. SECTION LOGIC ---
st.title(selected_section)

if selected_section == "City Overview":
    
    # --- KPI Card Design Generator ---
    def create_kpi_card(title, value):
        return f"""
        <div style="background-color: #E8E8D0; border-radius: 12px; padding: 20px; margin: 10px 0; 
                    border-left: 6px solid #C5E1A5; box-shadow: 2px 4px 10px rgba(0,0,0,0.05);">
            <p style="margin: 0; font-size: 16px; color: #444444; font-weight: 600;">{title}</p>
            <h2 style="margin: 5px 0 0 0; color: #2E5C31; font-size: 28px;">{value}</h2>
        </div>
        """

    if st.session_state.view_mode == "Kochi":
        
        # --- 1. Header, Photo & Introduction (ONLY IN KOCHI VIEW) ---
        st.header("Kochi Municipal Corporation & The Haritha Karma Sena")
        
        # Placeholder for your actual HKS photo. Replace the URL with your local file path like "hks_team.jpg"
        
        img_col1, img_col2, img_col3 = st.columns([1, 2, 1]) 
        with img_col2:
            # Removed use_column_width to stop it from stretching
            st.image("HKS2.jpg", caption="Haritha Karma Sena in action. (Image taken from the Harithakera Mission website)")

        st.markdown("""
        **Introduction to the Haritha Karma Sena (HKS):**
        
        Kochi generates over 6.5 lac kilos of municipal waste every month across 19 wards. This system is managed by 252 members of Harithakarmasena (HKS) workers, mostly women, who carry out door-to-door waste collection from more than 41,000 households.

        The dashboard presents a city-level & ward-level overview of how this system works, based on data collected during our Kochi field study. It highlights waste generation across wards, household coverage, collection frequency, workforce distribution, and working conditions of HKS members.

        The aim is to give a clear picture of Kochi’s waste management system, showing both where it works well and where support may be needed.
        """)
        
        st.markdown("---")
        st.subheader("Aggregate Statistics (Surveyed Wards)")
        
        # --- Math & Variables ---
        total_wards = len(df['Ward Number'].unique())
        total_pop = df['Population'].sum()
        total_households = df['Num of Households'].sum()
        total_workers = df['Num of HKS Members'].sum()
        
        # Tonnes calculation
        total_waste_kg = df['Weight in KG'].sum()
        total_waste_tonnes = total_waste_kg / 1000 
        
        # KPI: Waste per Household
        waste_per_hh = total_waste_kg / total_households if total_households > 0 else 0
        
        # NEW KPI: Households per HKS worker
        hh_per_worker = total_households / total_workers if total_workers > 0 else 0
        
        # --- Top Row KPIs ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(create_kpi_card("Wards Surveyed", f"{total_wards}"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Total Population", format_indian_system(total_pop)), unsafe_allow_html=True)
        with col3:
            st.markdown(create_kpi_card("Total Households", format_indian_system(total_households)), unsafe_allow_html=True)
            
        # --- Middle Row KPIs ---
        col4, col5, col6 = st.columns(3)
        with col4:
            st.markdown(create_kpi_card("Total HKS Workers", f"{total_workers:,}"), unsafe_allow_html=True)
        with col5:
            st.markdown(create_kpi_card("Total Waste Generated", f"{total_waste_tonnes:,.1f} Tonnes"), unsafe_allow_html=True)
        with col6:
            st.markdown(create_kpi_card("Waste per Household", f"{waste_per_hh:,.1f} KG/HH"), unsafe_allow_html=True)

        # --- Bottom Row KPI (Centered for a clean UI layout) ---
        col7, col8, col9 = st.columns(3)
        with col8:
            st.markdown(create_kpi_card("Households per HKS Worker", f"{hh_per_worker:,.0f} HH/Worker"), unsafe_allow_html=True)

    else:
        st.subheader("Ward-wise Extremes & Comparisons")
        
        # Calculate Math for Wardwise view
        df['Weight in Tons'] = df['Weight in KG'] / 1000
        df['Waste per HH (KG)'] = df['Weight in KG'] / df['Num of Households']
        # Handle divide by zero just in case
        df['Waste per HH (KG)'] = df['Waste per HH (KG)'].fillna(0)
        
        # Extremes calculation
        max_waste_ward = df.loc[df['Weight in Tons'].idxmax()]
        min_waste_ward = df.loc[df['Weight in Tons'].idxmin()]
        
        max_hks_ward = df.loc[df['Num of HKS Members'].idxmax()]
        min_hks_ward = df.loc[df['Num of HKS Members'].idxmin()]
        
        max_hh_waste_ward = df.loc[df['Waste per HH (KG)'].idxmax()]
        min_hh_waste_ward = df.loc[df['Waste per HH (KG)'].idxmin()]

        # Ward-wise KPIs using the custom cards
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(create_kpi_card("Highest Waste Generated", f"{max_waste_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({max_waste_ward['Weight in Tons']:,.1f} Tonnes)</span>"), unsafe_allow_html=True)
            st.markdown(create_kpi_card("Most HKS Workers", f"{max_hks_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({max_hks_ward['Num of HKS Members']} workers)</span>"), unsafe_allow_html=True)
            st.markdown(create_kpi_card("Highest Waste per Household", f"{max_hh_waste_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({max_hh_waste_ward['Waste per HH (KG)']:.1f} KG/HH)</span>"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Lowest Waste Generated", f"{min_waste_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({min_waste_ward['Weight in Tons']:,.1f} Tonnes)</span>"), unsafe_allow_html=True)
            st.markdown(create_kpi_card("Fewest HKS Workers", f"{min_hks_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({min_hks_ward['Num of HKS Members']} workers)</span>"), unsafe_allow_html=True)
            st.markdown(create_kpi_card("Lowest Waste per Household", f"{min_hh_waste_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({min_hh_waste_ward['Waste per HH (KG)']:.1f} KG/HH)</span>"), unsafe_allow_html=True)

        st.markdown("---")
        
        # 3 Graphs for Wardwise
        st.subheader("Visual Comparisons")
        tab1, tab2, tab3 = st.tabs(["Waste Generated", "HKS Members", "Waste per Household"])
        
        def format_chart(fig, title):
            fig.update_layout(
                title=dict(text=title, font=dict(color='black', size=18)),
                plot_bgcolor='#F5F5DC', paper_bgcolor='#F5F5DC', font=dict(color='black'),
                xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),
                yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black'))
            )
            return fig

        with tab1:
            fig1 = px.bar(df, x='Ward Name', y='Weight in Tons', color_discrete_sequence=['#8ECAE6'])
            st.plotly_chart(format_chart(fig1, "Total Waste Generated by Ward (Tonnes)"), use_container_width=True, theme=None)
        with tab2:
            fig2 = px.bar(df, x='Ward Name', y='Num of HKS Members', color_discrete_sequence=['#C5E1A5'])
            st.plotly_chart(format_chart(fig2, "Number of HKS Members by Ward"), use_container_width=True, theme=None)
        with tab3:
            fig3 = px.bar(df, x='Ward Name', y='Waste per HH (KG)', color_discrete_sequence=['#F4A261'])
            st.plotly_chart(format_chart(fig3, "Waste Generated per Household (KG)"), use_container_width=True, theme=None)

elif selected_section == "The Faces of HKS":
    
    if st.session_state.view_mode == "Kochi":
        st.subheader("The Faces Behind the Work: City-Wide Demographics")
        
        col1, col2, col3 = st.columns(3) 
        
        avg_working_hrs = df['Working hrs'].mean()
        avg_hourly_rate = df['Hourly rate'].mean()
        
        # Calculate daily individual load: Total Waste / Total Workers / 30 days
        total_waste = df['Weight in KG'].sum()
        total_workers = df['Num of HKS Members'].sum()
        avg_daily_load = (total_waste / total_workers) / 30 if total_workers > 0 else 0
        
        # Replaced standard metrics with the custom KPI cards
        with col1:
            st.markdown(create_kpi_card("Average Working Hours", f"{avg_working_hrs:.1f} hrs"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Average Hourly Rate", f"₹ {avg_hourly_rate:.2f}"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_kpi_card("Avg Daily Individual Load", f"{avg_daily_load:.1f} KG/worker"), unsafe_allow_html=True)
            
        st.markdown("---")
        
        # --- Middle Row: Doughnut Charts ---
        st.subheader("Representation & Tech Access")
        col3, col4 = st.columns(2)
        
        # Gender Representation Doughnut
        total_females = df['Number of female HKS members'].sum()
        total_males = df['Number of male HKS members'].sum()
        
        fig_gender = px.pie(
            names=['Female', 'Male'], 
            values=[total_females, total_males], 
            hole=0.6,
            # FIX: Changed dark grey to light blue (#8ECAE6) so black text is perfectly visible!
            color_discrete_sequence=['#C5E1A5', '#8ECAE6'] 
        )
        fig_gender.update_layout(
            title=dict(text="Gender Distribution", font=dict(color='black', size=18)), 
            title_x=0.5,
            plot_bgcolor='#F5F5DC', paper_bgcolor='#F5F5DC',
            showlegend=False,
            font=dict(color='black') 
        )
        # Forces the labels directly on the pie chart to be black
        fig_gender.update_traces(textinfo='percent+label', textfont_color='black') 
        
        with col3:
            st.plotly_chart(fig_gender, use_container_width=True, theme=None)
            
        # Smartphone Coverage Doughnut
        total_hks = df['Num of HKS Members'].sum()
        total_smartphones = df['How many members use smartphones?'].sum()
        no_smartphones = total_hks - total_smartphones
        
        fig_tech = px.pie(
            names=['Smartphone Users', 'No Smartphone'], 
            values=[total_smartphones, no_smartphones], 
            hole=0.6,
            color_discrete_sequence=['#C5E1A5', '#e6e6e6'] 
        )
        fig_tech.update_layout(
            title=dict(text="Smartphone Coverage", font=dict(color='black', size=18)), 
            title_x=0.5,
            plot_bgcolor='#F5F5DC', paper_bgcolor='#F5F5DC',
            showlegend=False,
            font=dict(color='black') 
        )
        # Forces the labels directly on the pie chart to be black
        fig_tech.update_traces(textinfo='percent+label', textfont_color='black') 
        
        with col4:
            st.plotly_chart(fig_tech, use_container_width=True, theme=None)
            
        st.markdown("---")
        
        # --- Bottom Row: Safety Equipment Bar Chart ---
        st.subheader("Overall Safety Equipment Usage")
        # Assuming these columns contain 'Yes'/'No'. We count the 'Yes' responses and calculate %.
        safety_cols = ['Gloves', 'Footwear', 'Mask', 'Cap', 'Sanitizer', 'Uniform']
        safety_percentages = []
        
        for col in safety_cols:
            # Safely handle potential missing values or different text cases
            yes_count = df[col].astype(str).str.strip().str.lower().eq('yes').sum()
            percent = (yes_count / len(df)) * 100
            safety_percentages.append(percent)
            
        fig_safety = px.bar(
            x=safety_cols, 
            y=safety_percentages,
            labels={'x': 'Equipment', 'y': '% of Wards Using'},
            color_discrete_sequence=['#C5E1A5']
        )
        fig_safety.update_layout(
            plot_bgcolor='#F5F5DC', 
            paper_bgcolor='#F5F5DC',
            font=dict(color='black'), 
            yaxis=dict(
                range=[0, 100],
                title_font=dict(color='black'), 
                tickfont=dict(color='black'),   
                gridcolor='#E2E2D0'             
            ),
            xaxis=dict(
                title_font=dict(color='black'), 
                tickfont=dict(color='black')    
            )
        )
        
        # CRITICAL: theme=None stops Streamlit from turning the text white
        st.plotly_chart(fig_safety, use_container_width=True, theme=None)

    else:
        st.subheader("Ward-Wise Safety Equipment & Demographics")
        
        # Displaying the custom tick/cross table
        st.markdown("**Safety Gear Usage by Ward**")
        
        # Select the relevant columns for the table
        cols_to_show = ['Ward Name', 'Gloves', 'Footwear', 'Mask', 'Cap', 'Sanitizer', 'Uniform']
        safety_df = df[cols_to_show].copy()
        
        # Standardize strings just in case Excel has trailing spaces or mixed cases
        for col in cols_to_show[1:]:
            safety_df[col] = safety_df[col].astype(str).str.strip().str.capitalize()
            
        # Replace Yes/No with aesthetic emojis
        safety_df = safety_df.replace({'Yes': '✅', 'No': '❌', 'Nan': '➖'})
        
        # Display as a clean Streamlit dataframe
        st.dataframe(safety_df, hide_index=True, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Calculate daily individual load per ward
        df['Daily Individual Load'] = df['Weight in KG'] / df['Num of HKS Members'] / 30
        
        fig_load = px.bar(df, x='Ward Name', y='Daily Individual Load', color_discrete_sequence=['#F4A261']) # Soft orange
        # Reusing our format_chart helper function logic:
        fig_load.update_layout(
            title=dict(text="Daily Individual Load by Ward (KG/Worker)", font=dict(color='black', size=18)),
            plot_bgcolor='#F5F5DC', paper_bgcolor='#F5F5DC', font=dict(color='black'),
            xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),
            yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black'))
        )
        st.plotly_chart(fig_load, use_container_width=True, theme=None)

elif selected_section == "On the Ground":
    
    # --- Data Prep for Section 3 ---
    df['latitude'] = pd.to_numeric(df['Geo Location of Place of Waste Segregation _latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['Geo Location of Place of Waste Segregation _longitude'], errors='coerce')
    
    # Calculate Coverage Percentage
    df['Coverage_Pct'] = (df['Num of Residential units covered by HKS'] / df['Num of Households']) * 100
    df['Coverage_Pct'] = df['Coverage_Pct'].fillna(0) 

    df.loc[df['Coverage_Pct'] > 100, 'Coverage_Pct'] = 100

    # Extract Distances (checking for Exact names from your column list)
    # Using a soft match just in case there are trailing spaces in the Excel headers
    food_dist_col = [c for c in df.columns if 'food' in c.lower() and 'distance' in c.lower()][0]
    plastic_dist_col = [c for c in df.columns if 'plastic' in c.lower() and 'distance' in c.lower()][0]
    
    df['Distance to Food (km)'] = pd.to_numeric(df[food_dist_col], errors='coerce').fillna(0)
    df['Distance to Plastic (km)'] = pd.to_numeric(df[plastic_dist_col], errors='coerce').fillna(0)

    # Helper function to enforce black text and beige background on all charts
    def format_chart(fig, title):
        fig.update_layout(
            title=dict(text=title, font=dict(color='black', size=18)),
            plot_bgcolor='#F5F5DC', paper_bgcolor='#F5F5DC',
            font=dict(color='black'),
            xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black'), gridcolor='#E2E2D0'),
            yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black'), gridcolor='#E2E2D0'),
            legend=dict(font=dict(color='black'), title_font=dict(color='black'))
        )
        return fig

    if st.session_state.view_mode == "Kochi":
        st.subheader("On the Ground: City-Wide Coverage & Logistics")
        
        # --- Calculations ---
        total_covered = df['Num of Residential units covered by HKS'].sum()
        total_households = df['Num of Households'].sum()
        overall_coverage_pct = (total_covered / total_households) * 100 if total_households > 0 else 0
        total_non_res = pd.to_numeric(df['Num of non-residential units covered by HKS'], errors='coerce').sum()
        
        avg_dist_food = df['Distance to Food (km)'].mean()
        avg_dist_plastic = df['Distance to Plastic (km)'].mean()
        
        # --- Top Row: KPIs ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(create_kpi_card("Total Res. Units Covered", f"{total_covered:,.0f}"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Overall Household Coverage", f"{overall_coverage_pct:.1f}%"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_kpi_card("Total Non-Residential Units", f"{total_non_res:,.0f}"), unsafe_allow_html=True)
            
        # --- Middle Row: Distance KPIs ---
        col4, col5 = st.columns(2)
        with col4:
            st.markdown(create_kpi_card("Avg Distance to Food Facility", f"{avg_dist_food:.1f} KM"), unsafe_allow_html=True)
        with col5:
            st.markdown(create_kpi_card("Avg Distance to Plastic RRF", f"{avg_dist_plastic:.1f} KM"), unsafe_allow_html=True)
            
        st.markdown("---")
        st.subheader("Locations of Segregation Centres & Processing Facilities")
        
        map_df = df.dropna(subset=['latitude', 'longitude'])
        if not map_df.empty:
            # 1. Prepare your existing segregation centers
            map_df = map_df.copy()
            map_df['Facility Type'] = 'Segregation Centre'
            map_df['Display Name'] = map_df['Ward Name']
            
            # 2. Add placeholders for External Facilities (Cleaned up the brackets)
            external_facilities = pd.DataFrame([
                {"Display Name": "Mattanchery", "latitude": 9.9586622, "longitude": 76.2598884, "Facility Type": "Wkerala RRF"},
                {"Display Name": "Edathala", "latitude": 10.0786153, "longitude": 76.383978, "Facility Type": "Wkerala RRF"},
                {"Display Name": "Anjumana", "latitude": 9.998, "longitude": 76.305, "Facility Type": "Wkerala RRF"},
                {"Display Name": "Ravipuram", "latitude": 9.9559, "longitude": 76.2899, "Facility Type": "Greenworms RRF"},
                {"Display Name": "Marine Drive", "latitude": 9.9772, "longitude": 76.2773, "Facility Type": "Greenworms RRF"},
                {"Display Name": "Kaloor", "latitude": 9.9921, "longitude": 76.3019, "Facility Type": "Greenworms RRF"},
                {"Display Name": "Aluva", "latitude": 10.1004, "longitude": 76.3570, "Facility Type": "Greenworms RRF"},
                {"Display Name": "Brahmapuram", "latitude": 9.9511, "longitude": 76.2924, "Facility Type": "Food Waste Centre"},
            ])
            
            # Combine them
            combined_map_df = pd.concat([map_df[['Display Name', 'latitude', 'longitude', 'Facility Type']], external_facilities], ignore_index=True)
            
            # 3. Plot the map with distinct colors
            fig_map = px.scatter_mapbox(
                combined_map_df, lat="latitude", lon="longitude", hover_name="Display Name",
                color="Facility Type",
                color_discrete_map={
                    'Segregation Centre': '#C5E1A5', # Light green
                    'Wkerala RRF': '#8ECAE6',        # Light blue
                    'Greenworms RRF': '#457B9D',     # Dark blue
                    'Food Waste Centre': '#F4A261'   # Orange
                },
                size_max=15, zoom=10.5, height=550
            )
            try:
                import geopandas as gpd
                import json
                boundary_gdf = gpd.read_file("Kochi wards.shp") # Your shapefile
                boundary_gdf = boundary_gdf.to_crs(epsg=4326)
                geojson_boundary = json.loads(boundary_gdf.to_json())
                
                fig_map.update_layout(
                    mapbox=dict(
                        style="carto-positron",
                        layers=[dict(
                            sourcetype='geojson',
                            source=geojson_boundary,
                            type='line',
                            color='#333333', # Dark grey outline
                            line=dict(width=0.5)
                        )]
                    )
                )
            except:
                pass # If shapefile fails to load, it will just draw the points normally
            
            fig_map.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0}, 
                paper_bgcolor='#F5F5DC', plot_bgcolor='#F5F5DC',
                legend=dict(font=dict(color='black'), title_font=dict(color='black'), bgcolor='rgba(245,245,220,0.8)')
            )
            fig_map.update_traces(marker=dict(size=12))
            st.plotly_chart(fig_map, use_container_width=True, theme=None)
    else:
        st.subheader("Ward-wise Coverage Extremes & Comparisons")
        
        # Calculate Max/Min Wards
        max_cov_ward = df.loc[df['Coverage_Pct'].idxmax()]
        min_cov_ward = df.loc[df['Coverage_Pct'].idxmin()]
        max_res_ward = df.loc[df['Num of Residential units covered by HKS'].idxmax()]
        min_res_ward = df.loc[df['Num of Residential units covered by HKS'].idxmin()]

        # Ward-wise KPIs with new Custom Styling
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(create_kpi_card("Highest Household Coverage", f"{max_cov_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({max_cov_ward['Coverage_Pct']:.1f}%)</span>"), unsafe_allow_html=True)
            st.markdown(create_kpi_card("Most Res. Units Covered", f"{max_res_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({max_res_ward['Num of Residential units covered by HKS']:.0f})</span>"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Lowest Household Coverage", f"{min_cov_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({min_cov_ward['Coverage_Pct']:.1f}%)</span>"), unsafe_allow_html=True)
            st.markdown(create_kpi_card("Fewest Res. Units Covered", f"{min_res_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({min_res_ward['Num of Residential units covered by HKS']:.0f})</span>"), unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Visual Comparisons")
        
        # Replaced the redundant graph with the requested Distance Graph
        tab1, tab2 = st.tabs(["Coverage %", "Distance to Facilities"])
        
        with tab1:
            fig1 = px.bar(df, x='Ward Name', y='Coverage_Pct', color_discrete_sequence=['#C5E1A5'])
            st.plotly_chart(format_chart(fig1, "Household Coverage Percentage by Ward"), use_container_width=True, theme=None)
            
        with tab2:
            # Grouped Bar chart showing distances to both facilities per ward
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=df['Ward Name'], y=df['Distance to Food (km)'], name='Food Recycling Centre', marker_color='#F4A261'))
            fig2.add_trace(go.Bar(x=df['Ward Name'], y=df['Distance to Plastic (km)'], name='Plastic RRF', marker_color='#8ECAE6'))
            fig2.update_layout(barmode='group')
            st.plotly_chart(format_chart(fig2, "Distance to Processing Facilities by Ward (KM)"), use_container_width=True, theme=None)
            
elif selected_section == "Scoring System":
    
    # --- 1. Data Prep & Scoring Engine ---
    
    # Helper function for Min-Max Normalization (0-100)
    def normalize_score(series, is_negative=False):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val: 
            return pd.Series(100, index=series.index) # Avoid division by zero
        
        if is_negative:
            # For negative metrics (e.g., Distance), lowest value gets 100, highest gets 0
            return ((max_val - series) / (max_val - min_val)) * 100
        else:
            # For positive metrics, highest value gets 100
            return ((series - min_val) / (max_val - min_val)) * 100

    # -- Calculate Base Variables (Safeguard in case user clicks this tab first) --
    df['Weight in KG'] = pd.to_numeric(df['Weight in KG'], errors='coerce').fillna(0)
    df['Num of HKS Members'] = pd.to_numeric(df['Num of HKS Members'], errors='coerce').fillna(0)
    df['Daily Load'] = (df['Weight in KG'] / df['Num of HKS Members'] / 30).fillna(0)
    
    food_dist_col = [c for c in df.columns if 'food' in c.lower() and 'distance' in c.lower()][0]
    plastic_dist_col = [c for c in df.columns if 'plastic' in c.lower() and 'distance' in c.lower()][0]
    df['Distance to Food (km)'] = pd.to_numeric(df[food_dist_col], errors='coerce').fillna(0)
    df['Distance to Plastic (km)'] = pd.to_numeric(df[plastic_dist_col], errors='coerce').fillna(0)
    
    df['Coverage_Pct'] = (df['Num of Residential units covered by HKS'] / df['Num of Households']) * 100
    df.loc[df['Coverage_Pct'] > 100, 'Coverage_Pct'] = 100 # Cap at 100
    df['Worker Share %'] = pd.to_numeric(df['% of revenue raised from waste going to HKS workers'], errors='coerce').fillna(0) * 100
    df['Total Ward Revenue'] = df['Revenue from user fees in a month'] + df['Food Waste Revenue (When Sold as Fertilizer)'] + df['Plastic Waste Revenue ']

    # Safety Score Calculation
    safety_cols = ['Gloves', 'Footwear', 'Mask', 'Cap', 'Sanitizer', 'Uniform']
    # Count how many 'Yes' answers each ward has, divide by 6, multiply by 100
    df['Safety Score Raw'] = df[safety_cols].apply(lambda x: x.astype(str).str.strip().str.lower().eq('yes').sum(), axis=1)
    df['Safety Score'] = (df['Safety Score Raw'] / len(safety_cols)) * 100
    
    # Women %
    df['Women %'] = (df['Number of female HKS members'] / df['Num of HKS Members'] * 100).fillna(0)

    # --- 2. Calculate the 3 Pillar Scores ---
    
    # Pillar 1: Social (Assuming lower daily load and lower working hours are better for worker welfare)
    df['Score_Women'] = normalize_score(df['Women %'], is_negative=False)
    df['Score_Load'] = normalize_score(df['Daily Load'], is_negative=True)
    df['Score_Hours'] = normalize_score(df['Working hrs'], is_negative=True) 
    df['Score_Safety'] = df['Safety Score'] # Already 0-100
    df['Social Score'] = df[['Score_Women', 'Score_Load', 'Score_Hours', 'Score_Safety']].mean(axis=1)

    # Pillar 2: Economic
    df['Score_ValueCap'] = normalize_score(df['Worker Share %'], is_negative=False)
    df['Score_HourlyRate'] = normalize_score(df['Hourly rate'], is_negative=False)
    df['Score_TotalRev'] = normalize_score(df['Total Ward Revenue'], is_negative=False)
    df['Economic Score'] = df[['Score_ValueCap', 'Score_HourlyRate', 'Score_TotalRev']].mean(axis=1)

    # Pillar 3: Coverage & Logistics
    df['Score_DistPlastic'] = normalize_score(df['Distance to Plastic (km)'], is_negative=True)
    df['Score_DistFood'] = normalize_score(df['Distance to Food (km)'], is_negative=True)
    df['Score_Coverage'] = df['Coverage_Pct'] # Already 0-100
    df['Coverage Score'] = df[['Score_DistPlastic', 'Score_DistFood', 'Score_Coverage']].mean(axis=1)

    # Aggregate Total Score
    df['Total HKS Performance Score'] = df[['Social Score', 'Economic Score', 'Coverage Score']].mean(axis=1)


    # --- 3. Build the UI ---
    if st.session_state.view_mode == "Kochi":
        st.subheader("HKS Performance Index: Methodology")
        st.markdown("To objectively evaluate the decentralized waste management ecosystem, we developed a composite **HKS Performance Index (0-100)**. This normalizes disparate data points into three core pillars.")
        
        # Displaying the Methodology Table
        methodology_data = {
            "Pillar": ["Social Welfare", "Social Welfare", "Social Welfare", "Social Welfare", 
                       "Economic Viability", "Economic Viability", "Economic Viability", 
                       "Coverage & Logistics", "Coverage & Logistics", "Coverage & Logistics"],
            "Indicator": ["% Women in HKS", "Daily Individual Load (KG)", "Daily Working Hours", "Safety Equipment Score",
                          "% Value Captured by HKS", "Hourly Rate", "Total Revenue Generated",
                          "Distance to Plastic RRF", "Distance to Food Facility", "% Households Covered"],
            "Impact Direction": ["Positive", "Negative (Lower is better)", "Negative (Lower is better)", "Positive",
                                 "Positive", "Positive", "Positive",
                                 "Negative (Closer is better)", "Negative (Closer is better)", "Positive"],
            "Weighting": ["Equal (25% of Pillar)", "Equal (25% of Pillar)", "Equal (25% of Pillar)", "Equal (25% of Pillar)",
                          "Equal (33% of Pillar)", "Equal (33% of Pillar)", "Equal (33% of Pillar)",
                          "Equal (33% of Pillar)", "Equal (33% of Pillar)", "Equal (33% of Pillar)"]
        }
        st.table(pd.DataFrame(methodology_data))
        

    else:
        st.subheader("Ward-wise Spatial Scoring Map")
        
        # Dropdown to select which score to map
        score_options = ['Social Score', 'Economic Score', 'Coverage Score', 'Total HKS Performance Score']
        selected_score = st.selectbox("Select Index to Visualize:", score_options)
        
        # Two columns: Map on the left, Top 5 Leaderboard on the right
        map_col, leader_col = st.columns([2, 1])
        
        with map_col:
            try:
                import geopandas as gpd
                # --- IMPORTANT: Change this to your exact .shp file name! ---
                shapefile_path = "Kochi wards.shp" 
                
                # Load and prepare the map data
                gdf = gpd.read_file(shapefile_path)
                gdf = gdf.to_crs(epsg=4326) # Required for Plotly Mapbox
                
                # Merge the shapefile with our scored dataframe
                # Note: 'ward_name_column_in_shp' needs to match the column name in your shapefile!
                # For example, it might be 'WARD_NAME' or 'Ward_No'
                merged_gdf = gdf.merge(df, left_on='ward_lgd_n', right_on='Ward Name', how='left')
                
                # Plotly Choropleth
                fig_map = px.choropleth_mapbox(
                    merged_gdf, 
                    geojson=merged_gdf.geometry, 
                    locations=merged_gdf.index, # Plotly needs the index when using GeoPandas
                    color=selected_score,
                    hover_name='Ward Name',
                    color_continuous_scale="Viridis", # A great green/yellow/blue scale for scoring
                    range_color=[0, 100],
                    mapbox_style="carto-positron",
                    zoom=10, center={"lat": 9.9312, "lon": 76.2673},
                    opacity=0.7
                )
                fig_map.update_layout(
                    margin={"r":0,"t":0,"l":0,"b":0}, 
                    paper_bgcolor='#F5F5DC', 
                    plot_bgcolor='#F5F5DC',
                    coloraxis_colorbar=dict(
                        title=dict(font=dict(color='black')),
                        tickfont=dict(color='black')
                    )
                )
                st.plotly_chart(fig_map, use_container_width=True)
                
            except Exception as e:
                st.error(f"Map Rendering Error: Ensure `geopandas` is installed and the shapefile path is correct. Details: {e}")
                
        with leader_col:
            st.markdown(f"### Top 5 Wards")
            # Sort the dataframe by the selected score and show the top 5
            top_5 = df[['Ward Name', selected_score]].sort_values(by=selected_score, ascending=False).head(5)
            
            # Format nicely for the sidebar
            for index, row in top_5.iterrows():
                st.markdown(f"**{row['Ward Name']}**: {row[selected_score]:.1f}/100")
                st.progress(row[selected_score] / 100) # Creates a cool visual progress bar!

elif selected_section == "Value Chains":
    st.subheader("Mapping Value Addition and Capture")
    st.markdown("Understanding how raw waste transforms into a commodity across the municipal ecosystem.")
    
    tab1, tab2 = st.tabs(["Food Waste Value Chain", "Plastic Waste Value Chain"])
    
    with tab1:
        # Replace 'food_chain.png' with your actual screenshot file name
        st.image("Food.png", use_column_width=True, caption="Food Waste Value Chain")
        
    with tab2:
        # Replace 'plastic_chain.png' with your actual screenshot file name
        st.image("Plastic.png", use_column_width=True, caption="Plastic Waste Value Chain")

elif selected_section == "Waste as a Liaison":
    
    # --- Data Prep for Economics ---
    fin_cols = [
        'Revenue from user fees in a month', 
        'Food Waste Revenue (When Sold as Fertilizer)', 
        'Plastic Waste Revenue ', 
        '% of revenue raised from waste going to HKS workers',
        'Weight in KG' # Needed for new formulas
    ]
    
    for col in fin_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 1. Fix Percentage (Convert 0.46 to 46%)
    df['Worker Share %'] = df['% of revenue raised from waste going to HKS workers'] * 100

    # 2. Recalculate Corporation Expenditure based on formula
    # Formula: (2.5 * 0.28 * Weight) + (4 * 0.72 * Weight)
    df['Corp Payment to Middlemen'] = (2.5 * 0.28 * df['Weight in KG']) + (4 * 0.72 * df['Weight in KG'])

    # 3. Recalculate Value Lost by Outsourcing
    df['Value Lost by Outsourcing'] = df['Food Waste Revenue (When Sold as Fertilizer)'] + df['Plastic Waste Revenue '] + df['Corp Payment to Middlemen']

    # 4. Calculate Total Revenue per Ward
    df['Total Ward Revenue'] = df['Revenue from user fees in a month'] + df['Food Waste Revenue (When Sold as Fertilizer)'] + df['Plastic Waste Revenue ']

    # 5. Clean up Vendor Columns
    if 'Greenworms' in df.columns and 'Wkerala' in df.columns:
        df['Greenworms_bin'] = df['Greenworms'].replace({'Yes': 1, 'No': 0, '1': 1, '0': 0, True: 1, False: 0}).fillna(0).astype(int)
        df['Wkerala_bin'] = df['Wkerala'].replace({'Yes': 1, 'No': 0, '1': 1, '0': 0, True: 1, False: 0}).fillna(0).astype(int)
        
        def categorize_vendor(row):
            if row['Greenworms_bin'] == 1 and row['Wkerala_bin'] == 1: return "Both"
            elif row['Greenworms_bin'] == 1: return "Greenworms"
            elif row['Wkerala_bin'] == 1: return "Wkerala"
            else: return "None"
            
        df['Vendor_Status'] = df.apply(categorize_vendor, axis=1)
    else:
        df['Vendor_Status'] = "Data Missing"

    # Helper function to enforce black text and beige background on charts
    def format_chart(fig, title):
        fig.update_layout(
            title=dict(text=title, font=dict(color='black', size=18)),
            plot_bgcolor='#F5F5DC', paper_bgcolor='#F5F5DC', font=dict(color='black'),
            xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),
            yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),
            legend=dict(font=dict(color='black'), title_font=dict(color='black'))
        )
        return fig

    if st.session_state.view_mode == "Kochi":
        
        st.subheader("The Economics of Waste: Value Generation vs. Capture")
        
        # Create a 3:1 split layout (Main content on left, Info box on right)
        main_col, side_col = st.columns([3, 1])
        
        with side_col:
            st.markdown("""
            <div style="background-color: #FFFFFF; border: 2px solid #8ECAE6; border-radius: 12px; padding: 20px; box-shadow: 2px 4px 10px rgba(0,0,0,0.05);">
                <h3 style="margin-top:0; color:#1D3557; font-size: 18px;">Key Market Rates</h3>
                <hr style="margin: 10px 0;">
                <p style="margin-bottom: 10px; font-size: 15px;"><b>1. User Fee (Household):</b><br> ₹ 50 - ₹ 150 / month</p>
                <p style="margin-bottom: 10px; font-size: 15px;"><b>2. Sorted Plastic (Raw):</b><br> ₹ 4 / KG</p>
                <p style="margin-bottom: 10px; font-size: 15px;"><b>3. Recycled Plastic (High-Grade):</b><br> ₹ 12 / KG</p>
                <p style="margin-bottom: 0px; font-size: 15px;"><b>4. Recycled Food (Fertilizer):</b><br> ₹ 2.5 / KG</p>
            </div>
            """, unsafe_allow_html=True)
            
        with main_col:
            # --- Calculating Totals ---
            tot_user_fees = df['Revenue from user fees in a month'].sum()
            tot_food_rev = df['Food Waste Revenue (When Sold as Fertilizer)'].sum()
            tot_plastic_rev = df['Plastic Waste Revenue '].sum()
            tot_corp_exp = df['Corp Payment to Middlemen'].sum()
            tot_corp_loss = df['Value Lost by Outsourcing'].sum()
            
            # --- 5 KPIs (Kochi View) ---
            kpi_col1, kpi_col2 = st.columns(2)
            with kpi_col1:
                st.markdown(create_kpi_card("Total Household User Fees", f"₹ {format_indian_system(tot_user_fees)}"), unsafe_allow_html=True)
                st.markdown(create_kpi_card("Total Rev. from Food Waste", f"₹ {format_indian_system(tot_food_rev)}"), unsafe_allow_html=True)
                st.markdown(create_kpi_card("Total Rev. from Plastic Waste", f"₹ {format_indian_system(tot_plastic_rev)}"), unsafe_allow_html=True)
            with kpi_col2:
                st.markdown(create_kpi_card("Corp. Payment to Middlemen", f"₹ {format_indian_system(tot_corp_exp)}"), unsafe_allow_html=True)
                st.markdown(create_kpi_card("Value Lost by Outsourcing", f"₹ {format_indian_system(tot_corp_loss)}"), unsafe_allow_html=True)

        st.markdown("---")
        
        # --- Bottom Row: Charts ---
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if 'Vendor_Status' in df.columns:
                vendor_counts = df['Vendor_Status'].value_counts().reindex(["Greenworms", "Wkerala", "Both", "None"], fill_value=0).reset_index()
                vendor_counts.columns = ['Vendor', 'Number of Wards']
                
                fig_vendors = px.bar(
                    vendor_counts, x='Vendor', y='Number of Wards',
                    color='Vendor',
                    color_discrete_map={'Greenworms': '#457B9D', 'Wkerala': '#8ECAE6', 'Both': '#2A9D8F', 'None': '#E2E2D0'}
                )
                fig_vendors.update_layout(showlegend=False)
                st.plotly_chart(format_chart(fig_vendors, "Wards Assigned to Recycling Vendors"), use_container_width=True, theme=None)
                
        with chart_col2:
            # Pie Chart using the corrected 0-100 percentage
            avg_hks_share = df['Worker Share %'].mean()
            system_share = 100 - avg_hks_share if avg_hks_share <= 100 else 0
            
            fig_share = px.pie(
                names=['HKS Workers', 'System/3rd Parties'],
                values=[avg_hks_share, system_share],
                hole=0.5,
                color_discrete_sequence=['#C5E1A5', '#F4A261']
            )
            fig_share.update_traces(textinfo='percent+label', textfont_color='black')
            st.plotly_chart(format_chart(fig_share, "Average Value Capture Breakdown"), use_container_width=True, theme=None)

    else:
        st.subheader("Ward-wise Economic Extremes & Comparisons")
        
        # Calculate 4 New Extremes
        max_cap_ward = df.loc[df['Worker Share %'].idxmax()]
        min_cap_ward = df.loc[df['Worker Share %'].idxmin()]
        max_rev_ward = df.loc[df['Total Ward Revenue'].idxmax()]
        min_rev_ward = df.loc[df['Total Ward Revenue'].idxmin()]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(create_kpi_card("Highest Value Capture by HKS", f"{max_cap_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({max_cap_ward['Worker Share %']:.1f}%)</span>"), unsafe_allow_html=True)
            st.markdown(create_kpi_card("Highest Total Revenue", f"{max_rev_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>(₹ {max_rev_ward['Total Ward Revenue']:,.0f})</span>"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_kpi_card("Lowest Value Capture by HKS", f"{min_cap_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>({min_cap_ward['Worker Share %']:.1f}%)</span>"), unsafe_allow_html=True)
            st.markdown(create_kpi_card("Lowest Total Revenue", f"{min_rev_ward['Ward Name']} <br><span style='font-size:18px; color:#555;'>(₹ {min_rev_ward['Total Ward Revenue']:,.0f})</span>"), unsafe_allow_html=True)

        st.markdown("---")
        
        # Visual Tabs
        tab1, tab2, tab3 = st.tabs(["Total Revenue Collection", "Revenue Proportions (100% Stack)", "Worker Equity"])
        
        # Prepare melted DataFrame for stacked charts
        rev_df = df[['Ward Name', 'Revenue from user fees in a month', 'Food Waste Revenue (When Sold as Fertilizer)', 'Plastic Waste Revenue ']].copy()
        rev_df = rev_df.melt(id_vars=['Ward Name'], var_name='Revenue Source', value_name='Amount (₹)')
        rev_df['Revenue Source'] = rev_df['Revenue Source'].replace({
            'Revenue from user fees in a month': 'User Fees',
            'Food Waste Revenue (When Sold as Fertilizer)': 'Food Waste',
            'Plastic Waste Revenue ': 'Plastic Waste'
        })
        
        with tab1:
            # Standard Stacked Bar
            fig1 = px.bar(rev_df, x='Ward Name', y='Amount (₹)', color='Revenue Source', 
                          color_discrete_map={'User Fees': '#F4A261', 'Food Waste': '#C5E1A5', 'Plastic Waste': '#8ECAE6'})
            fig1.update_layout(barmode='stack')
            st.plotly_chart(format_chart(fig1, "Absolute Revenue Profile by Ward"), use_container_width=True, theme=None)
            
        with tab2:
            # 100% Stacked Bar (Relative Proportions)
            fig2 = px.bar(rev_df, x='Ward Name', y='Amount (₹)', color='Revenue Source', 
                          color_discrete_map={'User Fees': '#F4A261', 'Food Waste': '#C5E1A5', 'Plastic Waste': '#8ECAE6'})
            # barnorm='percent' turns it into a 100% stacked chart
            fig2.update_layout(barmode='relative', barnorm='percent', yaxis_title="% of Total Revenue")
            st.plotly_chart(format_chart(fig2, "Proportional Revenue Profile by Ward"), use_container_width=True, theme=None)
            
        with tab3:
            # Worker Equity using corrected percentage
            fig3 = px.bar(df, x='Ward Name', y='Worker Share %', color_discrete_sequence=['#C5E1A5'])
            fig3.update_layout(yaxis=dict(range=[20, 50]))
            st.plotly_chart(format_chart(fig3, "Worker Equity: % Share of Generated Value"), use_container_width=True, theme=None)
