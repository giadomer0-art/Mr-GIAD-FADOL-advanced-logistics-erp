import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="شركة الحلول المتقدمة | نظام التشغيل", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. قاعدة بيانات المناديب الثابتة للنظام (قابل للتحديث مستقبلاً) ---
MASTER_DRIVERS_DATA = [
    {"ID": "96134", "Username": "elsiddiq-4466", "Iqama": "2550694711", "اسم المندوب": "الصديق الامين عباس قدوره"},
    {"ID": "96124", "Username": "ahmed-0071", "Iqama": "2497147245", "اسم المندوب": "احمد عبدالحميد ابراهيم سليمان"},
    {"ID": "96122", "Username": "muhammad-6696", "Iqama": "2560541662", "اسم المندوب": "MUHAMMAD IQBAL"},
    {"ID": "96120", "Username": "md-1669", "Iqama": "2614977490", "اسم المندوب": "مد جوني"},
    {"ID": "96117", "Username": "nahid-2691", "Iqama": "2572574180", "اسم المندوب": "نهاد مولا"}
]
df_master_db = pd.DataFrame(MASTER_DRIVERS_DATA)
# تحويل المعرفات لنصوص لتجنب مشاكل الربط
for col in ['ID', 'Username', 'Iqama']:
    df_master_db[col] = df_master_db[col].astype(str).str.strip()

# --- 3. التصميم الاحترافي (UI Customization) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
    
    html, body, [class*="css"], div, span, p, label {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background-color: #F8FAFC;
        background-image: linear-gradient(rgba(248, 250, 252, 0.93), rgba(248, 250, 252, 0.93)), 
                          url('https://raw.githubusercontent.com/giadomer0-art/Mr-GIAD-FADOL-advanced-logistics-erp/main/1.jpeg');
        background-repeat: no-repeat;
        background-position: center center;
        background-attachment: fixed;
        background-size: 550px;
    }

    .main-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: "";
        position: absolute;
        top: 0; right: 0; width: 8px; height: 100%;
        background: linear-gradient(180deg, #38BDF8 0%, #EF4444 100%);
    }
    .main-header h1 { color: #FFFFFF !important; font-weight: 900; font-size: 2.4rem; margin: 0; }
    .main-header p { color: #94A3B8 !important; font-size: 1.15rem; margin-top: 8px; font-weight: 600; }

    .metric-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-title { color: #64748B; font-size: 1rem; font-weight: 700; }
    .metric-value { color: #0F172A; font-size: 2.1rem; font-weight: 900; margin-top: 8px; }
    
    .card-revenue { border-top: 4px solid #38BDF8; }
    .card-cost { border-top: 4px solid #EF4444; }
    .card-profit { border-top: 4px solid #10B981; }
    .card-orders { border-top: 4px solid #1E293B; }

    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 16px;
        padding: 10px;
        border: 2px dashed #CBD5E1;
    }
    
    .stDownloadButton>button {
        width: 100%;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 16px 24px !important;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3) !important;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-left: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. الهيدر الرئيسي ---
st.markdown("""
    <div class="main-header">
        <h1>📊 المنظومة المالية والتشغيلية الشاملة</h1>
        <p>شركة الحلول المتقدمة للخدمات اللوجستية | Advanced Logistics Solutions</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. القائمة الجانبية ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/giadomer0-art/Mr-GIAD-FADOL-advanced-logistics-erp/main/1.jpeg", width=160)
    st.markdown("## ⚙️ إدارة المشاريع")
    selected_client = st.radio(
        "اختر العميل المراد حسابه:", 
        ["Supermall", "Ninja (نينجا)", "Kita (كيتا)", "HungerStation (هنقرستيشن)"],
        index=0
    )
    st.divider()
    st.caption("نظام الحسابات اللوجستية الموحد v4.0")

# ----------------- 6. دوال الإيرادات -----------------
def calc_supermall_revenue(orders):
    if orders <= 400: return orders * 9
    elif orders <= 500: return orders * 10
    elif orders <= 600: return orders * 11
    else: return orders * 12

def calc_ninja_revenue(orders):
    target, base = 460, 6500
    if orders >= target: return base + ((orders - target) * 12)
    else:
        missing = target - orders
        drop_pct = (missing / target) * 100
        if drop_pct <= 10.0: return base - (missing * 22)
        elif drop_pct <= 20.0: return base - (missing * 22.5)
        elif drop_pct <= 30.0: return base - (missing * 23)
        else: return orders * 10

def calc_kita_revenue(orders, total_distance):
    if pd.isna(orders) or orders == 0: return 0
    extra_distance = max(0, total_distance - orders) 
    return (orders * 6.5) + (extra_distance * 0.6)

def calc_hungerstation_revenue(orders, driver_status, extra_distance, quality_level):
    if pd.isna(orders) or orders == 0: return 0
    status = str(driver_status).strip()
    is_high_perf = ('عالي' in status) or ('High' in status)
    base_fee = 8 if is_high_perf else 6
    km_rate = 1.15 if is_high_perf else 0.90
    
    bonus_map = {'A': 2.75, 'B': 2.25, 'C': 1.75, 'D': 1.25, 'E': 0.75, 'F': 0}
    bonus_per_order = bonus_map.get(str(quality_level).strip().upper(), 0)
    extra_dist_val = extra_distance if pd.notna(extra_distance) else 0
    
    return (orders * base_fee) + (extra_dist_val * km_rate) + (orders * bonus_per_order)

# ----------------- 7. دوال الرواتب والبدلات -----------------
def calc_kafala_salary(orders):
    if orders >= 550: return 2500 + 300 + ((orders - 550) * 8)
    elif 401 <= orders <= 549: return orders * 4
    else: return orders * 3

def calc_freelancer_salary(orders, client):
    if client == "Ninja (نينجا)":
        return (5000 + ((orders - 460) * 8)) if orders >= 460 else (orders * 7)
    else:
        return (5000 + ((orders - 550) * 9)) if orders >= 550 else (orders * 7)

def calc_car_rent(owns_car, model_year):
    if str(owns_car).strip() == 'نعم':
        return 1200 if pd.notna(model_year) and int(model_year) >= 2015 else 1000
    return 0

# ----------------- 8. دالة التعرف الذكي على المندوب -----------------
def enrich_with_master_db(df):
    # توحيد نوع البيانات في الشيت المرفوع للربط
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # محاولة الربط بواسطة (الإقامة أولاً، ثم الرقم الوظيفي، ثم اسم المستخدم)
    match_col = None
    for c in ['Iqama', 'رقم الإقامة', 'رقم الاقامة']:
        if c in df.columns:
            match_col = (c, 'Iqama')
            break
    if not match_col:
        for c in ['ID', 'الرقم الوظيفي', 'رقم المندوب']:
            if c in df.columns:
                match_col = (c, 'ID')
                break
    if not match_col:
        for c in ['Username', 'اسم المستخدم', 'يوزر المندوب']:
            if c in df.columns:
                match_col = (c, 'Username')
                break
                
    if match_col:
        df = pd.merge(df, df_master_db, left_on=match_col[0], right_on=match_col[1], how='left', suffixes=('', '_db'))
        if 'اسم المندوب_db' in df.columns:
            df['اسم المندوب'] = df['اسم المندوب_db'].combine_first(df.get('اسم المندوب', pd.Series()))
            df.drop(columns=['اسم المندوب_db'], inplace=True, errors='ignore')
    return df

# ----------------- 9. منطقة رفع الملفات -----------------
st.markdown(f"### 📂 مركز رفع بيانات مشروع: `{selected_client}`")

col1, col2, col3 = st.columns(3)
with col1: 
    st.markdown("**1. تقرير الأداء الشهري**")
    perf_file = st.file_uploader("اختر ملف الإنتاجية", type=['xlsx'], key="u1")
with col2: 
    st.markdown("**2. بيانات المناديب**")
    agent_info_file = st.file_uploader("اختر ملف المناديب", type=['xlsx'], key="u2")
with col3: 
    st.markdown("**3. السيارات والبنزين**")
    car_fuel_file = st.file_uploader("اختر ملف السيارات", type=['xlsx'], key="u3")

# ----------------- 10. المعالجة وعرض النتائج -----------------
if perf_file and agent_info_file and car_fuel_file:
    try:
        df_perf = pd.read_excel(perf_file)
        df_agents = pd.read_excel(agent_info_file)
        df_cars = pd.read_excel(car_fuel_file)
        
        # إثراء تقرير الإنتاجية بقاعدة البيانات الداخلية الذكية
        df_perf = enrich_with_master_db(df_perf)
        df_agents = enrich_with_master_db(df_agents)
        df_cars = enrich_with_master_db(df_cars)

        # توحيد عمود الإقامة للدمج
        for df in [df_perf, df_agents, df_cars]:
            if 'Iqama' in df.columns: df.rename(columns={'Iqama': 'رقم الإقامة'}, inplace=True)
            elif 'رقم الاقامة' in df.columns: df.rename(columns={'رقم الاقامة': 'رقم الإقامة'}, inplace=True)
                
        df_merged = pd.merge(df_perf, df_agents, on='رقم الإقامة', how='left', suffixes=('', '_agent'))
        df_merged = pd.merge(df_merged, df_cars, on='رقم الإقامة', how='left', suffixes=('', '_car'))
        
        if 'اسم المندوب_agent' in df_merged.columns:
            df_merged['اسم المندوب'] = df_merged['اسم المندوب'].combine_first(df_merged['اسم المندوب_agent'])

        orders_col = 'Grand Total Delivered' if 'Grand Total Delivered' in df_merged.columns else 'الطلبات الناجحة'
        df_merged['الطلبات الناجحة'] = pd.to_numeric(df_merged[orders_col], errors='coerce').fillna(0)
        
        if 'أيام العمل' not in df_merged.columns: df_merged['أيام العمل'] = 30
        else: df_merged['أيام العمل'] = pd.to_numeric(df_merged['أيام العمل'], errors='coerce').fillna(30)
        
        dist_col = 'المسافة' if 'المسافة' in df_merged.columns else ('Distance' if 'Distance' in df_merged.columns else 'المسافة الإضافية')
        if dist_col not in df_merged.columns: df_merged[dist_col] = 0
        else: df_merged[dist_col] = pd.to_numeric(df_merged[dist_col], errors='coerce').fillna(0)

        status_col = 'حالة السائق' if 'حالة السائق' in df_merged.columns else 'Driver Status'
        if status_col not in df_merged.columns: df_merged[status_col] = 'أساسي'
        
        level_col = 'المستوى' if 'المستوى' in df_merged.columns else 'Quality Level'
        if level_col not in df_merged.columns: df_merged[level_col] = 'F'
        
        # حساب الإيرادات
        if selected_client == "Supermall":
            df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات الناجحة'].apply(calc_supermall_revenue)
        elif selected_client == "Ninja (نينجا)":
            df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات الناجحة'].apply(calc_ninja_revenue)
        elif selected_client == "Kita (كيتا)":
            df_merged['إيراد الشركة من العميل'] = df_merged.apply(lambda r: calc_kita_revenue(r['الطلبات الناجحة'], r[dist_col]), axis=1)
        elif selected_client == "HungerStation (هنقرستيشن)":
            df_merged['إيراد الشركة من العميل'] = df_merged.apply(
                lambda r: calc_hungerstation_revenue(r['الطلبات الناجحة'], r[status_col], r[dist_col], r[level_col]), axis=1
            )

        # حساب المستحقات
        def calc_agent_dues(row):
            agent_type = str(row.get('نوع المندوب', 'كفالة')).strip()
            orders = row['الطلبات الناجحة']
            if agent_type == 'فري لانسر':
                salary = calc_freelancer_salary(orders, selected_client)
                return pd.Series([salary, 0, 0, salary])
            else:
                salary = calc_kafala_salary(orders)
                car_rent = calc_car_rent(row.get('يمتلك سيارة', 'لا'), row.get('موديل السيارة', 2000))
                fuel = (row['أيام العمل'] * 40) if pd.notna(row['أيام العمل']) else 0
                return pd.Series([salary, car_rent, fuel, salary + car_rent + fuel])

        df_merged[['راتب الإنتاجية', 'بدل السيارة', 'مخصص البنزين', 'إجمالي المستحق للمندوب']] = df_merged.apply(calc_agent_dues, axis=1)
        df_merged['ربح الشركة الصافي'] = df_merged['إيراد الشركة من العميل'] - df_merged['إجمالي المستحق للمندوب']

        # --- 11. بطاقات الأداء المنسقة ---
        st.write("---")
        st.markdown("### 📈 المؤشرات المالية والإنتاجية")
        
        rev_val = df_merged['إيراد الشركة من العميل'].sum()
        cost_val = df_merged['إجمالي المستحق للمندوب'].sum()
        profit_val = df_merged['ربح الشركة الصافي'].sum()
        orders_val = df_merged['الطلبات الناجحة'].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.markdown(f"""
                <div class="metric-card card-revenue">
                    <div class="metric-title">إيرادات الشركة الإجمالية</div>
                    <div class="metric-value">{rev_val:,.2f} <span style="font-size: 1rem; color: #64748B;">SAR</span></div>
                </div>
            """, unsafe_allow_html=True)
            
        with m2:
            st.markdown(f"""
                <div class="metric-card card-cost">
                    <div class="metric-title">إجمالي رواتب ومستحقات المناديب</div>
                    <div class="metric-value">{cost_val:,.2f} <span style="font-size: 1rem; color: #64748B;">SAR</span></div>
                </div>
            """, unsafe_allow_html=True)
            
        with m3:
            st.markdown(f"""
                <div class="metric-card card-profit">
                    <div class="metric-title">الربح الصافي للشركة</div>
                    <div class="metric-value">{profit_val:,.2f} <span style="font-size: 1rem; color: #64748B;">SAR</span></div>
                </div>
            """, unsafe_allow_html=True)
            
        with m4:
            st.markdown(f"""
                <div class="metric-card card-orders">
                    <div class="metric-title">إجمالي شحنات المشروع</div>
                    <div class="metric-value">{orders_val:,.0f} <span style="font-size: 1rem; color: #64748B;">شحنة</span></div>
                </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.write("")

        # --- 12. جدول البيانات ---
        st.markdown("### 📋 البيان التفصيلي لمستحقات المناديب والأرباح")
        
        display_cols = ['ID', 'Username', 'رقم الإقامة', 'اسم المندوب', 'نوع المندوب', 'الطلبات الناجحة']
        if selected_client in ["Kita (كيتا)", "HungerStation (هنقرستيشن)"]: 
            display_cols.append(dist_col)
        if selected_client == "HungerStation (هنقرستيشن)": 
            display_cols.extend([status_col, level_col])
            
        display_cols.extend(['راتب الإنتاجية', 'بدل السيارة', 'مخصص البنزين', 'إجمالي المستحق للمندوب', 'إيراد الشركة من العميل', 'ربح الشركة الصافي'])
        
        final_df = df_merged[[c for c in display_cols if c in df_merged.columns]]
        st.dataframe(final_df, use_container_width=True)

        # --- 13. زر التصدير ---
        def convert_df(df_to_save):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_to_save.to_excel(writer, index=False, sheet_name='الرواتب والأرباح')
            return output.getvalue()

        st.download_button(
            "📥 تصدير مسير الرواتب والأرباح إلى ملف Excel", 
            data=convert_df(final_df), 
            file_name=f"Advanced_Logistics_{selected_client}.xlsx"
        )

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة البيانات: {e}")
