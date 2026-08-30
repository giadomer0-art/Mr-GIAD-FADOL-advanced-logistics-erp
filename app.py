import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="نظام التشغيل والأرباح", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.title("🏢 النظام الشامل لإدارة الرواتب وأرباح التشغيل")
st.caption("شركة الحلول المتقدمة | عقود (Supermall, Ninja, Kita, HungerStation)")

# --- تحديد العميل ---
st.subheader("⚙️ إعدادات المشروع")
selected_client = st.radio(
    "اختر المشروع (العميل) المراد حساب رواتبه وأرباحه:", 
    ["Supermall", "Ninja (نينجا)", "Kita (كيتا)", "HungerStation (هنقرستيشن)"]
)

# ----------------- دوال إيرادات الشركة -----------------
def calc_supermall_revenue(orders):
    if orders <= 400: return orders * 9
    elif orders <= 500: return orders * 10
    elif orders <= 600: return orders * 11
    else: return orders * 12

def calc_ninja_revenue(orders):
    target = 460
    base = 6500
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
    
    # تحديد السعر الأساسي وسعر الكيلومتر بناءً على حالة السائق (سيارات فقط)
    is_high_perf = str(driver_status).strip() == 'عالي'
    base_fee = 8 if is_high_perf else 6
    km_rate = 1.15 if is_high_perf else 0.90
    
    # تحديد مكافأة الجودة حسب المستوى
    bonus_map = {'A': 2.75, 'B': 2.25, 'C': 1.75, 'D': 1.25, 'E': 0.75, 'F': 0}
    level = str(quality_level).strip().upper()
    bonus_per_order = bonus_map.get(level, 0)
    
    return (orders * base_fee) + (extra_distance * km_rate) + (orders * bonus_per_order)

# ----------------- دوال رواتب المناديب الداخلية -----------------
def calc_kafala_salary(orders):
    if orders >= 550: return 2500 + 300 + ((orders - 550) * 8)
    elif 401 <= orders <= 549: return orders * 4
    else: return orders * 3

def calc_freelancer_salary(orders, client):
    # سياسة نينجا للفري لانسر
    if client == "Ninja (نينجا)":
        if orders >= 460: return 5000 + ((orders - 460) * 8)
        else: return orders * 7
    # سياسة موحدة لبقية المشاريع
    else:
        if orders >= 550: return 5000 + ((orders - 550) * 9)
        else: return orders * 7

def calc_car_rent(owns_car, model_year):
    if str(owns_car).strip() == 'نعم':
        return 1200 if pd.notna(model_year) and int(model_year) >= 2015 else 1000
    return 0

# ----------------- واجهة الرفع والمعالجة -----------------
st.write("---")
st.subheader("📂 مركز رفع البيانات")

if selected_client == "Kita (كيتا)":
    st.info("💡 تأكد أن تقرير الأداء يحتوي على عمود: 'المسافة' أو 'Distance'.")
elif selected_client == "HungerStation (هنقرستيشن)":
    st.info("💡 لـ هنقرستيشن: يفضل أن يحتوي تقرير الأداء على أعمدة: 'حالة السائق' (عالي/أساسي) ، 'المستوى' (A,B,C..)، و 'المسافة الإضافية'.")

col1, col2, col3 = st.columns(3)
with col1: perf_file = st.file_uploader(f"1. تقرير أداء {selected_client}", type=['xlsx'])
with col2: agent_info_file = st.file_uploader("2. بيانات المناديب (كفالة/فري لانسر)", type=['xlsx'])
with col3: car_fuel_file = st.file_uploader("3. بيانات السيارات والبنزين", type=['xlsx'])

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
        
        # أعمدة كيتا وهنقرستيشن
        dist_col = 'المسافة' if 'المسافة' in df_merged.columns else ('Distance' if 'Distance' in df_merged.columns else 'المسافة الإضافية')
        if dist_col not in df_merged.columns: df_merged[dist_col] = 0
        
        status_col = 'حالة السائق' if 'حالة السائق' in df_merged.columns else 'Driver Status'
        if status_col not in df_merged.columns: df_merged[status_col] = 'أساسي'
        
        level_col = 'المستوى' if 'المستوى' in df_merged.columns else 'Quality Level'
        if level_col not in df_merged.columns: df_merged[level_col] = 'F'
        
        # حساب إيرادات الشركة
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

        # حساب رواتب المناديب
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

        # ----------------- عرض النتائج -----------------
        st.write("---")
        st.subheader(f"💰 لوحة الأرباح والتشغيل الشاملة - {selected_client}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إيرادات الشركة (قبل الصرف)", f"{df_merged['إيراد الشركة من العميل'].sum():,.2f} ريال")
        c2.metric("إجمالي تكاليف المناديب", f"{df_merged['إجمالي المستحق للمندوب'].sum():,.2f} ريال", delta="-تكلفة", delta_color="inverse")
        c3.metric("الربح الصافي للشركة", f"{df_merged['ربح الشركة الصافي'].sum():,.2f} ريال")
        c4.metric("إجمالي الطلبات", f"{df_merged['الطلبات الناجحة'].sum():,.0f} طلب")
        
        display_cols = ['رقم الإقامة', 'اسم المندوب', 'نوع المندوب', 'الطلبات الناجحة']
        if selected_client in ["Kita (كيتا)", "HungerStation (هنقرستيشن)"]: 
            display_cols.append(dist_col)
        if selected_client == "HungerStation (هنقرستيشن)": 
            display_cols.extend([status_col, level_col])
            
        display_cols.extend(['إجمالي المستحق للمندوب', 'إيراد الشركة من العميل', 'ربح الشركة الصافي'])
        
        final_df = df_merged[[c for c in display_cols if c in df_merged.columns]]
        st.dataframe(final_df, use_container_width=True)

        def convert_df(df_to_save):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_to_save.to_excel(writer, index=False, sheet_name='الرواتب والأرباح')
            return output.getvalue()

        st.download_button("📥 تحميل التقرير الشامل (Excel)", data=convert_df(final_df), file_name=f"Payroll_Profit_{selected_client}.xlsx")

    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {e}")
