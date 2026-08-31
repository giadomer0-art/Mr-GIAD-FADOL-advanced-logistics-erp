import streamlit as st
import pandas as pd
from io import BytesIO
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="شركة الحلول المتقدمة | نظام التشغيل", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. قاعدة بيانات الربط الثابتة للنظام ---
MASTER_DRIVERS_DATA = [
    {"ID": "96134", "Username": "elsiddiq-4466", "Iqama": "2550694711", "اسم المندوب": "الصديق الامين عباس قدوره", "Aliases": ["elsiddiq", "صديق", "الصديق الأمين", "elsiddiq-4466"]},
    {"ID": "96124", "Username": "ahmed-0071", "Iqama": "2497147245", "اسم المندوب": "احمد عبدالحميد ابراهيم سليمان", "Aliases": ["ahmed", "أحمد", "احمد عبد الحميد", "ahmed-0071"]},
    {"ID": "96122", "Username": "muhammad-6696", "Iqama": "2560541662", "اسم المندوب": "MUHAMMAD IQBAL", "Aliases": ["muhammad iqbal", "محمد إقبال", "محمد اقبال", "muhammad-6696"]},
    {"ID": "96120", "Username": "md-1669", "Iqama": "2614977490", "اسم المندوب": "مد جوني", "Aliases": ["md jony", "md johnny", "md-1669", "md joni"]},
    {"ID": "96117", "Username": "nahid-2691", "Iqama": "2572574180", "اسم المندوب": "نهاد مولا", "Aliases": ["nahid mollah", "nahid", "نهادمولا", "nahid-2691"]}
]

df_master_db = pd.DataFrame(MASTER_DRIVERS_DATA)
for col in ['ID', 'Username', 'Iqama']:
    df_master_db[col] = df_master_db[col].astype(str).str.strip().str.replace('.0', '', regex=False)

# --- 3. التنسيق والواجهة ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
    html, body, [class*="css"], div, span, p, label { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; }
    .stApp { background-color: #F8FAFC; background-image: linear-gradient(rgba(248, 250, 252, 0.93), rgba(248, 250, 252, 0.93)), url('https://raw.githubusercontent.com/giadomer0-art/Mr-GIAD-FADOL-advanced-logistics-erp/main/1.jpeg'); background-repeat: no-repeat; background-position: center center; background-attachment: fixed; background-size: 550px; }
    .main-header { background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 30px; border-radius: 20px; color: white; box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.2); border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 25px; position: relative; overflow: hidden; }
    .main-header::before { content: ""; position: absolute; top: 0; right: 0; width: 8px; height: 100%; background: linear-gradient(180deg, #38BDF8 0%, #EF4444 100%); }
    .main-header h1 { color: #FFFFFF !important; font-weight: 900; font-size: 2.3rem; margin: 0; }
    .main-header p { color: #94A3B8 !important; font-size: 1.1rem; margin-top: 8px; font-weight: 600; }
    .info-summary-box { background: #FFFFFF; border-radius: 14px; padding: 18px 25px; margin-bottom: 25px; border-right: 6px solid #38BDF8; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .info-summary-box h4 { margin: 0 0 8px 0; color: #1E293B; font-weight: 800; font-size: 1.2rem; }
    .info-summary-box p { margin: 3px 0; color: #475569; font-weight: 600; font-size: 1rem; }
    .metric-card { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px); border-radius: 16px; padding: 22px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border: 1px solid #E2E8F0; transition: all 0.3s ease; }
    .metric-card:hover { transform: translateY(-4px); }
    .metric-title { color: #64748B; font-size: 0.95rem; font-weight: 700; }
    .metric-value { color: #0F172A; font-size: 2rem; font-weight: 900; margin-top: 6px; }
    .card-revenue { border-top: 4px solid #38BDF8; } .card-cost { border-top: 4px solid #EF4444; } .card-profit { border-top: 4px solid #10B981; } .card-orders { border-top: 4px solid #1E293B; }
    [data-testid="stFileUploader"] { background: rgba(255, 255, 255, 0.85); border-radius: 16px; padding: 10px; border: 2px dashed #CBD5E1; }
    .stDownloadButton>button { width: 100%; background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important; color: white !important; font-weight: 800 !important; font-size: 1.2rem !important; border-radius: 14px !important; border: none !important; padding: 16px 24px !important; box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3) !important; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.95); border-left: 1px solid #E2E8F0; }
    </style>
""", unsafe_allow_html=True)

# --- 4. الهيدر والقائمة ---
st.markdown('<div class="main-header"><h1>📊 المنظومة المالية والتشغيلية الشاملة</h1><p>شركة الحلول المتقدمة للخدمات اللوجستية | Advanced Logistics Solutions</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://raw.githubusercontent.com/giadomer0-art/Mr-GIAD-FADOL-advanced-logistics-erp/main/1.jpeg", width=160)
    st.markdown("## ⚙️ إدارة المشاريع")
    selected_client = st.radio("اختر العميل المراد حسابه:", ["Supermall", "Ninja (نينجا)", "Kita (كيتا)", "HungerStation (هنقرستيشن)"], index=0)
    st.divider()
    st.caption("نظام الحسابات اللوجستية الموحد v22.0")

# ----------------- 5. دوال الإيرادات للشركة -----------------
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

# ----------------- 6. دالة الرواتب الموحدة لجميع المشاريع (كفالة و فري لانسر) -----------------
def calc_salary_by_project(orders, client, is_freelance):
    if client == "Ninja (نينجا)":
        return (5000 + ((orders - 460) * 8)) if orders >= 460 else (orders * 7.0)

    if is_freelance:
        # نظام الفري لانسر يطبق على أي تطبيق في حال تم كتابة (حر)
        return (5000 + ((orders - 550) * 9)) if orders >= 550 else (orders * 7.0)
            
    # نظام الكفالة الموحد
    if orders >= 550:
        return 2500 + 300 + ((orders - 550) * 8)
    elif 401 <= orders <= 549:
        return orders * 4.0
    else:
        return orders * 3.0

# ----------------- 7. دالة بدل السيارة الذكية (قراءة الملاحظات والتقسيم التلقائي للأيام) -----------------
def get_smart_car_allowance(row, report_days):
    # دمج كامل بيانات المندوب في سطر نصي واحد للبحث عن الكلمات الدلالية
    row_str = " ".join(str(v).lower() for v in row.values).replace('ة', 'ه')
    full_allowance = 0
    
    if 'بدل سياره جديد' in row_str:
        full_allowance = 1200
    elif 'بدل سياره قديم' in row_str:
        full_allowance = 1000
    elif 'بدل سياره' in row_str:
        full_allowance = 1000  # الوضع الافتراضي عند كتابة (بدل سيارة) بدون تحديد
    else:
        # للرجوع للأنظمة القديمة في حال تم استخدامها
        owns = str(row.get('يمتلك سيارة', '')).strip()
        if owns == 'نعم':
            mod_yr = pd.to_numeric(row.get('موديل السيارة', 0), errors='coerce')
            full_allowance = 1200 if mod_yr >= 2015 else 1000
            
    # التقسيم التلقائي على أيام التقرير المرفوع
    if full_allowance > 0:
        if report_days >= 28:
            return full_allowance
        elif report_days > 0:
            return round((full_allowance / 30) * report_days, 2)
            
    return 0

# ----------------- 8. محرك المطابقة المطور -----------------
def normalize_name(text):
    if pd.isna(text): return ""
    text = str(text).lower().strip()
    text = re.sub(r'[\W_]+', ' ', text)
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    return text.strip()

def matches_driver_name(name_agent, name_fuel, aliases=[]):
    n_ag = normalize_name(name_agent)
    n_fu = normalize_name(name_fuel)
    if not n_ag or not n_fu: return False
    
    if len(n_ag) > 2 and n_ag in n_fu: return True
    if len(n_fu) > 2 and n_fu in n_ag: return True
    
    for alias in aliases:
        a_norm = normalize_name(alias)
        if a_norm and len(a_norm) > 2:
            if a_norm in n_fu or n_fu in a_norm:
                return True
    return False

# ----------------- 9. منطقة رفع الملفات -----------------
st.markdown(f"### 📂 مركز رفع بيانات مشروع: `{selected_client}`")
col1, col2, col3 = st.columns(3)
with col1: perf_file = st.file_uploader("1. تقرير الأداء الشهري", type=['xlsx'], key="u1")
with col2: agent_info_file = st.file_uploader("2. بيانات المناديب", type=['xlsx'], key="u3")
with col3: car_fuel_file = st.file_uploader("3. استهلاك البنزين والسيارات", type=['xlsx'], key="u2")

# ----------------- 10. المعالجة وعرض النتائج -----------------
if perf_file and agent_info_file and car_fuel_file:
    try:
        df_perf = pd.read_excel(perf_file)
        df_agents = pd.read_excel(agent_info_file)
        df_cars = pd.read_excel(car_fuel_file)

        for col in ['ID', 'Username', 'Iqama']:
            if col in df_perf.columns: df_perf[col] = df_perf[col].astype(str).str.strip().str.replace('.0', '', regex=False)

        df_perf = pd.merge(df_perf, df_master_db, on='ID', how='left', suffixes=('', '_db'))
        if 'Iqama_db' in df_perf.columns: df_perf['Iqama'] = df_perf['Iqama'].replace('nan', None).combine_first(df_perf['Iqama_db'])
        if 'اسم المندوب_db' in df_perf.columns: df_perf['اسم المندوب'] = df_perf.get('اسم المندوب', pd.Series()).combine_first(df_perf['اسم المندوب_db'])

        for col in df_agents.columns:
            c_clean = str(col).strip()
            if c_clean in ['رقم الإقامة', 'Iqama', 'رقم الاقامة']: df_agents.rename(columns={col: 'Iqama'}, inplace=True)
            elif c_clean in ['نوع المندوب', 'نوع العقد', 'النوع', 'ملاحظات']: df_agents.rename(columns={col: 'نوع المندوب'}, inplace=True)
        if 'Iqama' in df_agents.columns: df_agents['Iqama'] = df_agents['Iqama'].astype(str).str.strip().str.replace('.0', '', regex=False)

        df_merged = pd.merge(df_perf, df_agents, on='Iqama', how='left', suffixes=('', '_agents'))

        driver_col_fuel = 'السائقين المعينين للمركبة' if 'السائقين المعينين للمركبة' in df_cars.columns else ('اسم السائق' if 'اسم السائق' in df_cars.columns else None)
        cost_col_fuel = 'إجمالي المبلغ المستخدم' if 'إجمالي المبلغ المستخدم' in df_cars.columns else ('القيمة' if 'القيمة' in df_cars.columns else None)
        liters_col_fuel = 'عدد اللترات' if 'عدد اللترات' in df_cars.columns else ('اللترات' if 'اللترات' in df_cars.columns else None)

        if driver_col_fuel and cost_col_fuel:
            df_cars_clean = df_cars.copy()
            df_cars_clean[cost_col_fuel] = pd.to_numeric(df_cars_clean[cost_col_fuel], errors='coerce').fillna(0)
            if liters_col_fuel: df_cars_clean[liters_col_fuel] = pd.to_numeric(df_cars_clean[liters_col_fuel], errors='coerce').fillna(0)

            def extract_fuel_precise(row):
                agent_name = row.get('اسم المندوب', '')
                username = row.get('Username', '')
                aliases = []
                for _, master_row in df_master_db.iterrows():
                    if matches_driver_name(agent_name, master_row['اسم المندوب']) or username == master_row['Username']:
                        aliases = master_row.get('Aliases', [])
                        break

                total_cost = 0; total_liters = 0
                for _, car_row in df_cars_clean.iterrows():
                    fuel_driver_name = str(car_row[driver_col_fuel])
                    if matches_driver_name(agent_name, fuel_driver_name, aliases) or matches_driver_name(username, fuel_driver_name, aliases):
                        total_cost += car_row[cost_col_fuel]
                        if liters_col_fuel: total_liters += car_row[liters_col_fuel]
                return pd.Series([total_cost, round(total_liters, 1)])

            df_merged[['مخصص البنزين', 'كمية البنزين (لتر)']] = df_merged.apply(extract_fuel_precise, axis=1)
        else:
            df_merged['مخصص البنزين'] = 0; df_merged['كمية البنزين (لتر)'] = 0

        # احتساب عدد أيام التقرير المرفوع لقسمة البدل عليها
        date_cols = [c for c in df_perf.columns if 'Delivered' in c and c != 'Grand Total Delivered']
        dates_found = [c.replace(' Delivered', '').strip() for c in date_cols]
        report_days = len(dates_found) if len(dates_found) > 0 else 30

        hours_col = 'Grand Total Hours' if 'Grand Total Hours' in df_merged.columns else 'إجمالي ساعات العمل'
        df_merged['إجمالي ساعات العمل'] = pd.to_numeric(df_merged[hours_col], errors='coerce').fillna(0).round(2) if hours_col in df_merged.columns else 0

        def check_attendance(row):
            tot_h = row.get('إجمالي ساعات العمل', 0); tot_o = pd.to_numeric(row.get('Grand Total Delivered', 0), errors='coerce') or 0
            if tot_h == 0 and tot_o == 0: return "غائب ❌"
            elif tot_h < 8: return "تأخير / غير مكتمل ⚠️"
            return "منتظم ✅"
        df_merged['حالة الحضور والتأخير'] = df_merged.apply(check_attendance, axis=1)

        orders_col = 'Grand Total Delivered' if 'Grand Total Delivered' in df_merged.columns else 'الطلبات الناجحة'
        df_merged['الطلبات المحققة'] = pd.to_numeric(df_merged[orders_col], errors='coerce').fillna(0)

        # حساب الإيرادات
        if selected_client == "Supermall": df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'].apply(calc_supermall_revenue)
        elif selected_client == "Ninja (نينجا)": df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'].apply(calc_ninja_revenue)
        elif selected_client == "Kita (كيتا)": df_merged['إيراد الشركة من العميل'] = df_merged.apply(lambda r: calc_kita_revenue(r['الطلبات المحققة'], r.get('Distance', 0)), axis=1)
        elif selected_client == "HungerStation (هنقرستيشن)": df_merged['إيراد الشركة من العميل'] = df_merged.apply(lambda r: calc_hungerstation_revenue(r['الطلبات المحققة'], r.get('Driver Status', 'أساسي'), r.get('Distance', 0), r.get('Quality Level', 'F')), axis=1)

        # دالة المستحقات الذكية لـ (الفري لانسر والسيارات)
        def calc_agent_dues_final(row):
            orders = row['الطلبات المحققة']
            
            # فحص كلمة حر أو فري لانسر في أي مكان ببيانات المندوب
            row_str = " ".join(str(v).lower() for v in row.values)
            if selected_client == "Ninja (نينجا)":
                is_freelance = True
            else:
                is_freelance = ('فري' in row_str) or ('freelance' in row_str) or ('حر' in row_str)
            
            salary = calc_salary_by_project(orders, selected_client, is_freelance)
            
            # احتساب بدل السيارة والمخصصات
            car_rent = get_smart_car_allowance(row, report_days)
            fuel = row['مخصص البنزين']

            # إذا كان فري لانسر لا يضاف له بنزين الشركة (لكن إذا منُح بدل سيارة استثنائياً سيضاف له)
            if is_freelance:
                return pd.Series([salary, car_rent, salary + car_rent])
            else:
                return pd.Series([salary, car_rent, salary + car_rent + fuel])

        df_merged[['راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب']] = df_merged.apply(calc_agent_dues_final, axis=1)
        df_merged['ربح الشركة الصافي'] = df_merged['إيراد الشركة من العميل'] - df_merged['إجمالي المستحق للمندوب']
        df_merged.rename(columns={'Iqama': 'رقم الإقامة'}, inplace=True)

        # --- 11. واجهة العرض ---
        st.write("---")
        st.markdown(f"""
            <div class="info-summary-box">
                <h4>📌 معلومات التقرير والتشغيل العامة</h4>
                <p>📍 <b>المدينة:</b> المدينة المنورة (MEDMS01)</p>
                <p>📅 <b>عدد أيام التقرير للتقسيم المالي:</b> {report_days} يوم.</p>
                <p>⚠️ <b>ملاحظة:</b> النظام يقرأ الآن الكلمات الدلالية (حر، بدل سيارة جديد/قديم) تلقائياً ويطبق الرواتب والتقسيم الزمني بمرونة تامة.</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📈 المؤشرات المالية والإنتاجية")
        rev_val = df_merged['إيراد الشركة من العميل'].sum()
        cost_val = df_merged['إجمالي المستحق للمندوب'].sum()
        profit_val = df_merged['ربح الشركة الصافي'].sum()
        orders_val = df_merged['الطلبات المحققة'].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f'<div class="metric-card card-revenue"><div class="metric-title">إيرادات الشركة الإجمالية</div><div class="metric-value">{rev_val:,.2f} <span style="font-size: 1rem; color: #64748B;">SAR</span></div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card card-cost"><div class="metric-title">إجمالي رواتب ومستحقات المناديب</div><div class="metric-value">{cost_val:,.2f} <span style="font-size: 1rem; color: #64748B;">SAR</span></div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card card-profit"><div class="metric-title">الربح الصافي للشركة</div><div class="metric-value">{profit_val:,.2f} <span style="font-size: 1rem; color: #64748B;">SAR</span></div></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="metric-card card-orders"><div class="metric-title">إجمالي الشحنات المحققة</div><div class="metric-value">{orders_val:,.0f} <span style="font-size: 1rem; color: #64748B;">شحنة</span></div></div>', unsafe_allow_html=True)

        st.write("")
        st.markdown("### 📋 البيان التفصيلي المطور لمستحقات المناديب والأرباح")
        display_cols = ['ID', 'Username', 'رقم الإقامة', 'اسم المندوب', 'نوع المندوب', 'حالة الحضور والتأخير', 'إجمالي ساعات العمل', 'الطلبات المحققة', 'كمية البنزين (لتر)', 'مخصص البنزين', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب', 'إيراد الشركة من العميل', 'ربح الشركة الصافي']
        final_df = df_merged.loc[:, ~df_merged.columns.duplicated()][[c for c in display_cols if c in df_merged.columns]]
        st.dataframe(final_df, use_container_width=True)

        def convert_df(df_to_save):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_to_save.to_excel(writer, index=False, sheet_name='الرواتب والأرباح')
            return output.getvalue()

        st.download_button("📥 تصدير مسير الرواتب والأرباح إلى ملف Excel", data=convert_df(final_df), file_name=f"Advanced_Logistics_{selected_client}.xlsx")

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة البيانات: {e}")
