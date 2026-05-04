import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================
# KONFIGURASI HALAMAN
# ============================================
st.set_page_config(
    page_title="Tax Compliance Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS - CLEAN WHITE THEME
# ============================================
st.markdown("""
<style>
    /* HIDE DEFAULT STREAMLIT ELEMENTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* MAIN BACKGROUND - PUTIH BERSIH */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #f5f5f5 !important;
        border-right: 1px solid #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #1a1a1a !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #800020 !important;
    }
    
    /* HEADINGS */
    h1 {
        color: #1a1a1a !important;
        font-size: 28px !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px !important;
    }
    
    h2, h3, h4 {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    
    /* KPI CARDS */
    .kpi-container {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .kpi-card {
        background-color: #f8f8f8;
        border-top: 3px solid #800020;
        border-radius: 8px;
        padding: 20px;
        flex: 1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s;
    }
    
    .kpi-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .kpi-label {
        color: #666666 !important;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        color: #1a1a1a !important;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .kpi-sub {
        color: #999999 !important;
        font-size: 11px;
    }
    
    /* RISK CARDS */
    .risk-critical {
        background-color: #fff5f5;
        border-left: 3px solid #800020;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    
    .risk-high {
        background-color: #fff8f0;
        border-left: 3px solid #DAA520;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    
    .risk-medium {
        background-color: #fffdf5;
        border-left: 3px solid #c5a059;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    
    .risk-low {
        background-color: #f0f7f0;
        border-left: 3px solid #2e7d32;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    
    .risk-label {
        color: #666666 !important;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .risk-value {
        color: #1a1a1a !important;
        font-size: 20px;
        font-weight: 600;
    }
    
    /* ALERT BOX */
    .alert-box {
        background-color: #f8f8f8;
        border-left: 3px solid #800020;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    
    .alert-title {
        color: #800020 !important;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    
    .alert-message {
        color: #1a1a1a !important;
        font-size: 13px;
        font-weight: 500;
    }
    
    .alert-sub {
        color: #999999 !important;
        font-size: 11px;
        margin-top: 4px;
    }
    
    /* DIVIDER */
    hr {
        border-color: #e0e0e0;
        margin: 25px 0;
    }
    
    /* BUTTON */
    .stButton button {
        background-color: #800020;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        background-color: #a00028;
    }
    
    /* SELECTBOX & MULTISELECT */
    .stSelectbox label, .stMultiSelect label {
        color: #800020 !important;
        font-weight: 500 !important;
    }
    
    /* DATAFRAME */
    .stDataFrame {
        background-color: #ffffff;
    }
    
    /* METRIC CUSTOM */
    [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #666666 !important;
    }
    
    /* TEXT */
    p, div, span {
        color: #1a1a1a !important;
    }
    
    /* SIDEBAR TEXT */
    .sidebar-text {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    df = pd.read_csv('tax_compliance.csv')
    
    # Konversi ke datetime
    df['due_payment'] = pd.to_datetime(df['due_payment'])
    df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')
    df['due_report'] = pd.to_datetime(df['due_report'])
    df['report_date'] = pd.to_datetime(df['report_date'], errors='coerce')
    
    # Payment status
    def get_payment_status(row):
        if pd.isna(row['payment_date']):
            return 'Not Yet Paid'
        elif row['payment_date'] <= row['due_payment']:
            return 'On Time'
        else:
            return 'Late'
    df['payment_status'] = df.apply(get_payment_status, axis=1)
    
    # Report status
    def get_report_status(row):
        if pd.isna(row['report_date']):
            return 'Not Yet Reported'
        elif row['report_date'] <= row['due_report']:
            return 'On Time'
        else:
            return 'Late'
    df['report_status'] = df.apply(get_report_status, axis=1)
    
    # Delay days
    df['delay_payment_days'] = df.apply(
        lambda row: max(0, (row['payment_date'] - row['due_payment']).days) 
        if pd.notna(row['payment_date']) else np.nan, axis=1
    )
    df['delay_report_days'] = df.apply(
        lambda row: max(0, (row['report_date'] - row['due_report']).days) 
        if pd.notna(row['report_date']) else np.nan, axis=1
    )
    
    # Compliance flag
    def get_compliance_flag(row):
        payment_ok = row['payment_status'] == 'On Time'
        report_ok = row['report_status'] == 'On Time'
        
        if payment_ok and report_ok:
            return 'Compliant'
        elif row['payment_status'] == 'Not Yet Paid' or row['report_status'] == 'Not Yet Reported':
            return 'Outstanding'
        else:
            return 'Late'
    df['compliance_flag'] = df.apply(get_compliance_flag, axis=1)
    
    # RISK SCORE (0-100)
    def calculate_risk_score(row):
        score = 0
        
        if pd.notna(row['delay_payment_days']):
            if row['delay_payment_days'] <= 0:
                score += 0
            elif row['delay_payment_days'] <= 5:
                score += 20
            elif row['delay_payment_days'] <= 15:
                score += 40
            else:
                score += 60
        elif row['payment_status'] == 'Not Yet Paid':
            score += 50
        
        if pd.notna(row['delay_report_days']):
            if row['delay_report_days'] <= 0:
                score += 0
            elif row['delay_report_days'] <= 5:
                score += 15
            elif row['delay_report_days'] <= 15:
                score += 30
            else:
                score += 40
        elif row['report_status'] == 'Not Yet Reported':
            score += 40
        
        tax_weight = min(np.log10(row['tax_amount'] / 1e6) * 5, 20)
        score += tax_weight if tax_weight > 0 else 0
        
        return min(100, score)
    
    df['risk_score'] = df.apply(calculate_risk_score, axis=1)
    
    # Risk category
    def get_risk_category(score):
        if score >= 70:
            return 'Critical'
        elif score >= 50:
            return 'High'
        elif score >= 30:
            return 'Medium'
        else:
            return 'Low'
    
    df['risk_category'] = df['risk_score'].apply(get_risk_category)
    
    # Month extraction
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['month_short'] = df['tax_period'].str[:3]
    df['month_num'] = df['month_short'].map({m: i for i, m in enumerate(month_order, 1)})
    
    return df

df = load_data()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("### Tax Intelligence")
    st.markdown("Executive Dashboard")
    st.markdown("---")
    
    st.markdown("#### Data Filters")
    
    all_tax_types = ['All'] + sorted(df['tax_type'].unique().tolist())
    selected_tax_type = st.selectbox("Tax Type", all_tax_types)
    
    periods = sorted(df['tax_period'].unique(), 
                     key=lambda x: (x.split('-')[1], ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].index(x[:3])))
    selected_periods = st.multiselect("Period", periods, default=periods)
    
    st.markdown("---")
    
    st.markdown("#### Risk Summary")
    critical_count = len(df[df['risk_category'] == 'Critical'])
    high_count = len(df[df['risk_category'] == 'High'])
    
    if critical_count > 0:
        st.markdown(f"""
        <div class='risk-critical'>
            <div class='risk-label'>CRITICAL RISK</div>
            <div class='risk-value'>{critical_count} cases</div>
        </div>
        """, unsafe_allow_html=True)
    
    if high_count > 0:
        st.markdown(f"""
        <div class='risk-high'>
            <div class='risk-label'>HIGH RISK</div>
            <div class='risk-value'>{high_count} cases</div>
        </div>
        """, unsafe_allow_html=True)

# Apply filters
filtered_df = df.copy()
if selected_tax_type != 'All':
    filtered_df = filtered_df[filtered_df['tax_type'] == selected_tax_type]
filtered_df = filtered_df[filtered_df['tax_period'].isin(selected_periods)]

# ============================================
# MAIN CONTENT
# ============================================

# Header
st.markdown("# Tax Compliance Intelligence System")
st.markdown("##### Real-time monitoring & predictive risk analytics")
st.markdown("---")

# ============================================
# KPI CARDS
# ============================================

total_records = len(filtered_df)
compliant = len(filtered_df[filtered_df['compliance_flag'] == 'Compliant'])
compliance_rate = (compliant / total_records * 100) if total_records > 0 else 0
total_tax = filtered_df['tax_amount'].sum()
late_cases = len(filtered_df[filtered_df['compliance_flag'] == 'Late'])
outstanding = len(filtered_df[filtered_df['compliance_flag'] == 'Outstanding'])
avg_risk = filtered_df['risk_score'].mean() if len(filtered_df) > 0 else 0

st.markdown(f"""
<div class='kpi-container'>
    <div class='kpi-card'>
        <div class='kpi-label'>COMPLIANCE RATE</div>
        <div class='kpi-value'>{compliance_rate:.1f}%</div>
        <div class='kpi-sub'>{compliant} of {total_records} records</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-label'>TOTAL TAX LIABILITY</div>
        <div class='kpi-value'>Rp {total_tax/1e9:.2f}B</div>
        <div class='kpi-sub'>Rp {total_tax/1e6:.0f} million</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-label'>LATE CASES</div>
        <div class='kpi-value'>{late_cases}</div>
        <div class='kpi-sub'>{late_cases/total_records*100:.1f}% of total</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-label'>OUTSTANDING</div>
        <div class='kpi-value'>{outstanding}</div>
        <div class='kpi-sub'>pending action</div>
    </div>
    <div class='kpi-card'>
        <div class='kpi-label'>AVG RISK SCORE</div>
        <div class='kpi-value'>{avg_risk:.0f}<span style='font-size:14px'>/100</span></div>
        <div class='kpi-sub'>enterprise risk index</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================
# CHARTS
# ============================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Compliance Trend")
    
    monthly_compliance = filtered_df.groupby(['month_num', 'tax_period']).apply(
        lambda x: (len(x[x['compliance_flag'] == 'Compliant']) / len(x) * 100) if len(x) > 0 else 0
    ).reset_index(name='compliance_rate')
    monthly_compliance = monthly_compliance.sort_values('month_num')
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly_compliance['tax_period'],
        y=monthly_compliance['compliance_rate'],
        mode='lines+markers',
        name='Compliance Rate',
        line=dict(color='#800020', width=3),
        marker=dict(size=8, color='#c5a059'),
        fill='tozeroy',
        fillcolor='rgba(128, 0, 32, 0.05)'
    ))
    fig_trend.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font_color='#333333',
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0', title='Tax Period'),
        yaxis=dict(showgrid=True, gridcolor='#e0e0e0', title='Compliance Rate (%)', range=[0, 105]),
        height=380,
        margin=dict(l=40, r=40, t=30, b=30),
        hovermode='x unified'
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.markdown("#### Risk Distribution")
    
    risk_counts = filtered_df['risk_category'].value_counts()
    risk_order = ['Critical', 'High', 'Medium', 'Low']
    risk_counts = risk_counts.reindex(risk_order, fill_value=0)
    
    colors = ['#800020', '#DAA520', '#c5a059', '#2e7d32']
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textfont=dict(color='#333333', size=12),
        hole=0.4,
        showlegend=False
    )])
    fig_pie.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        height=380,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ============================================
# BREAKDOWN BY TAX TYPE
# ============================================

st.markdown("#### Tax Type Performance Matrix")

col_b1, col_b2 = st.columns(2)

with col_b1:
    tax_late = filtered_df.groupby('tax_type').apply(
        lambda x: len(x[x['compliance_flag'] == 'Late']) / len(x) * 100 if len(x) > 0 else 0
    ).reset_index(name='late_pct')
    
    fig_bar = px.bar(
        tax_late,
        x='tax_type',
        y='late_pct',
        color='late_pct',
        color_continuous_scale=['#c5a059', '#DAA520', '#800020'],
        text=tax_late['late_pct'].apply(lambda x: f'{x:.1f}%')
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font_color='#333333',
        xaxis_title='',
        yaxis_title='Late Cases (%)',
        height=350,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_b2:
    tax_delays = filtered_df.groupby('tax_type').agg({
        'delay_payment_days': 'mean',
        'delay_report_days': 'mean'
    }).reset_index()
    
    fig_group = go.Figure()
    fig_group.add_trace(go.Bar(
        name='Payment Delay',
        x=tax_delays['tax_type'],
        y=tax_delays['delay_payment_days'],
        marker_color='#800020'
    ))
    fig_group.add_trace(go.Bar(
        name='Report Delay',
        x=tax_delays['tax_type'],
        y=tax_delays['delay_report_days'],
        marker_color='#c5a059'
    ))
    fig_group.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font_color='#333333',
        xaxis_title='',
        yaxis_title='Average Delay (Days)',
        barmode='group',
        height=350,
        legend=dict(font_color='#333333')
    )
    st.plotly_chart(fig_group, use_container_width=True)

st.markdown("---")

# ============================================
# EARLY WARNING SYSTEM
# ============================================

st.markdown("#### Early Warning System")

# Top high risk items
high_risk_items = filtered_df[filtered_df['risk_category'].isin(['Critical', 'High'])].nlargest(5, 'risk_score')

if len(high_risk_items) > 0:
    st.markdown(f"""
    <div class='alert-box'>
        <div class='alert-title'>Immediate Attention Required</div>
    """, unsafe_allow_html=True)
    for _, row in high_risk_items.iterrows():
        st.markdown(f"""
        <div class='alert-message'>
            • {row['tax_period']} - {row['tax_type']} | Risk Score: {row['risk_score']:.0f}/100
            <div class='alert-sub'>Payment: {row['payment_status']} | Report: {row['report_status']}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Executive insights
col_i1, col_i2, col_i3 = st.columns(3)

# Worst tax type
worst_tax = tax_late.loc[tax_late['late_pct'].idxmax()] if len(tax_late) > 0 else None
if worst_tax is not None:
    with col_i1:
        st.markdown(f"""
        <div class='alert-box'>
            <div class='alert-title'>Problematic Tax Type</div>
            <div class='alert-message'>{worst_tax['tax_type']}</div>
            <div class='alert-sub'>{worst_tax['late_pct']:.1f}% late rate</div>
        </div>
        """, unsafe_allow_html=True)

# Worst month
monthly_late = filtered_df.groupby('tax_period').apply(
    lambda x: len(x[x['compliance_flag'] == 'Late']) / len(x) * 100 if len(x) > 0 else 0
)
if len(monthly_late) > 0 and monthly_late.max() > 0:
    worst_month = monthly_late.idxmax()
    with col_i2:
        st.markdown(f"""
        <div class='alert-box'>
            <div class='alert-title'>Critical Period</div>
            <div class='alert-message'>{worst_month}</div>
            <div class='alert-sub'>{monthly_late.max():.1f}% delinquency rate</div>
        </div>
        """, unsafe_allow_html=True)

# Outstanding exposure
outstanding_amount = filtered_df[filtered_df['compliance_flag'] == 'Outstanding']['tax_amount'].sum()
if outstanding_amount > 0:
    with col_i3:
        st.markdown(f"""
        <div class='alert-box'>
            <div class='alert-title'>Outstanding Exposure</div>
            <div class='alert-message'>Rp {outstanding_amount/1e6:.1f} Million</div>
            <div class='alert-sub'>uncollected tax liability</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============================================
# DETAIL TABLE
# ============================================

st.markdown("#### Transaction Risk Register")

table_df = filtered_df[[
    'tax_period', 'tax_type', 'due_payment', 'payment_date',
    'due_report', 'report_date', 'tax_amount',
    'payment_status', 'report_status', 'risk_score', 'risk_category'
]].copy()

table_df['due_payment'] = table_df['due_payment'].dt.strftime('%Y-%m-%d')
table_df['payment_date'] = table_df['payment_date'].dt.strftime('%Y-%m-%d')
table_df['due_report'] = table_df['due_report'].dt.strftime('%Y-%m-%d')
table_df['report_date'] = table_df['report_date'].dt.strftime('%Y-%m-%d')
table_df['tax_amount'] = table_df['tax_amount'].apply(lambda x: f"Rp {x:,.0f}")
table_df['risk_score'] = table_df['risk_score'].round(0).astype(int)

st.dataframe(table_df, use_container_width=True, height=400)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f2:
    st.markdown("<p style='text-align: center; color: #999999; font-size: 11px;'>Tax Compliance Intelligence System | Powered by Streamlit</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #999999; font-size: 10px;'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)