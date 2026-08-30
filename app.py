import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. إعدادات الصفحة والواجهة ---
st.set_page_config(
    page_title="لوحة تشغيل الحلول المتقدمة", 
    page_icon="🚚", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. إدخال تنسيقات CSS احترافية (Custom CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    /* تطبيق خط القاهرة والاتجاه */
    html, body, [class*="css"], div, span, p {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* خلفية الصفحة العامة */
    .stApp {
        background-color: #f4f6f9;
    }
    
    /* الهيدر الرئيسي */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 25px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }
    .main-header h1 { color: #FFFFFF !important; font-weight: 800; font-size: 2.2rem; margin: 0; }
    .main-header p { color: #E0E7FF !important; font-size: 1.1rem; margin-top: 5px; }

    /* بطاقات المؤشرات الماليّة (Custom Metrics) */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-right: 6px solid #3B82F6;
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover { transform: translateY(-3px); }
    .metric-title { color: #6B7280; font-size: 0.95rem; font-weight: 600; }
    .metric-value { color: #1F2937; font-size: 1.8rem; font-weight: 800; margin-top: 5px; }
    
    /* الألوان للبطاقات المتنوعة */
    .card-blue { border-right-color: #2563EB; }
    .card-green { border-right-color: #059669; }
    .card-red { border-right-color: #DC2626; }
    .card-purple { border-right-color: #7C3AED; }

    /* تحسين شكل صناديق رفع الملفات */
    .stFileUploader {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        border: 1px dashed #CBD5E1;
    }
    
    /* أزرار التحميل والتفاعل */
    .stButton>button, .stDownloadButton>button {
        width: 100%;
        background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 12px 20px !important;
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3) !important;
    }
    
    /* القائمة الجانبية (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-left: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. الهيدر الرئيسي ---
st.markdown("""
    <div class="main-header">
        <h1>🚚 لوحة إدارة الرواتب وأرباح التشغيل</h1>
        <p>شركة الحلول المتقدمة للخدمات اللوجستية | Advanced Logistics Solutions</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. القائمة الجانبية لإعداد المشروع ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1554/1554284.png", width=80)
    st.title("⚙️ خيارات العميل")
    selected_client = st.radio(
        "اختر العميل المراد حسابه:", 
        ["Supermall", "Ninja (نينجا)", "Kita (كيتا)", "HungerStation (هنقرستيشن)"],
        index=0
    )
    st.divider()
    st.caption("برنامج معالجة البيانات التلقائي v2.0")

# ----------------- 5. دوال إيرادات الشركة -----------------
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

# ----------------- 6. دوال الرواتب والبدلات -----------------
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

# ----------------- 7. منطقة رفع الملفات المنسقة -----------------
st.subheader(f"📂 رفع ملفات مشروع: {selected_client}")

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

# ----------------- 8. معالجة البيانات وتصميم اللوحة -----------------
if perf_file and agent_info_file and car_fuel_file:
    try:
        df_perf = pd.read_excel(perf_file)
        df_agents = pd.read_excel(agent_info_file)
        df_cars = pd.read_excel(car_fuel_file)
        
        for df in [df_perf, df_agents, df_cars]:
            if 'Iqama' in df.columns: df.rename(columns={'Iqama': 'رقم الإقامة'}, inplace=True)
            elif 'رقم الاقامة' in df.columns: df.rename(columns={'رقم الاقامة': 'رقم الإقامة'}, inplace=True)
                
        df_merged = pd.merge(df_perf, df_agents, on='رقم الإقامة', how='left')
        df_merged = pd.merge(df_merged, df_cars, on='رقم الإقامة', how='left')
        
        orders_col = 'Grand Total Delivered' if 'Grand Total Delivered' in df_merged.columns else 'الطلبات الناجحة'
        df_merged['الطلبات الناجحة'] = df_merged[orders_col].fillna(0)
        if 'أيام العمل' not in df_merged.columns: df_merged['أيام العمل'] = 30
        
        dist_col = 'المسافة' if 'المسافة' in df_merged.columns else ('Distance' if 'Distance' in df_merged.columns else 'المسافة الإضافية')
        if dist_col not in df_merged.columns: df_merged[dist_col] = 0
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

        # --- 9. عرض بطاقات الأداء المنسقة (Custom Cards) ---
        st.write("---")
        st.markdown("### 📊 الملخص المالي والتشغيلي")
        
        rev_val = df_merged['إيراد الشركة من العميل'].sum()
        cost_val = df_merged['إجمالي المستحق للمندوب'].sum()
        profit_val = df_merged['ربح الشركة الصافي'].sum()
        orders_val = df_merged['الطلبات الناجحة'].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.markdown(f"""
                <div class="metric-card card-blue">
                    <div class="metric-title">إيرادات الشركة (SAR)</div>
                    <div class="metric-value">{rev_val:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with m2:
            st.markdown(f"""
                <div class="metric-card card-red">
                    <div class="metric-title">تكاليف المناديب (SAR)</div>
                    <div class="metric-value">{cost_val:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with m3:
            st.markdown(f"""
                <div class="metric-card card-green">
                    <div class="metric-title">الربح الصافي للشركة (SAR)</div>
                    <div class="metric-value">{profit_val:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with m4:
            st.markdown(f"""
                <div class="metric-card card-purple">
                    <div class="metric-title">إجمالي الطلبات التراكمي</div>
                    <div class="metric-value">{orders_val:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.write("")

        # --- 10. عرض الجدول التفصيلي برسم عصري ---
        st.markdown("### 📋 كشف تفاصيل الأداء والرواتب")
        
        display_cols = ['رقم الإقامة', 'اسم المندوب', 'نوع المندوب', 'الطلبات الناجحة']
        if selected_client in ["Kita (كيتا)", "HungerStation (هنقرستيشن)"]: 
            display_cols.append(dist_col)
        if selected_client == "HungerStation (هنقرستيشن)": 
            display_cols.extend([status_col, level_col])
            
        display_cols.extend(['راتب الإنتاجية', 'بدل السيارة', 'مخصص البنزين', 'إجمالي المستحق للمندوب', 'إيراد الشركة من العميل', 'ربح الشركة الصافي'])
        
        final_df = df_merged[[c for c in display_cols if c in df_merged.columns]]
        st.dataframe(final_df, use_container_width=True)

        # --- 11. زر التحميل المنظّم ---
        def convert_df(df_to_save):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_to_save.to_excel(writer, index=False, sheet_name='الرواتب والأرباح')
            return output.getvalue()

        st.download_button(
            "📥 تحميل كشف الرواتب والأرباح النهائي (Excel)", 
            data=convert_df(final_df), 
            file_name=f"Advanced_Logistics_{selected_client}.xlsx"
        )

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة البيانات: {e}")
