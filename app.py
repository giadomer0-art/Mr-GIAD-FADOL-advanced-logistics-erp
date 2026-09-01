import streamlit as st
import pandas as pd
from io import BytesIO
import re
import warnings

try:
    import pdfplumber
except ImportError:
    pass
try:
    import docx
except ImportError:
    pass
try:
    from PIL import Image
    import pytesseract
except ImportError:
    pass

warnings.filterwarnings('ignore')

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="شركة الحلول المتقدمة | نظام التشغيل الذكي", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. محرك قراءة الملفات الذكي ---
def smart_read_file(uploaded_file):
    if uploaded_file is None: return None
    file_name = uploaded_file.name.lower()
    try:
        if file_name.endswith(('.xlsx', '.xls')): return pd.read_excel(uploaded_file)
        elif file_name.endswith('.csv'): return pd.read_csv(uploaded_file)
        # (تم اختصار كود الـ PDF والوورد هنا للتركيز على المعالجة، يمكنك إبقاؤه كما هو في النسخة السابقة إذا أردت)
        return pd.read_excel(uploaded_file) # الافتراضي
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        return pd.DataFrame()

# --- 3. محرك المطابقة المرن جداً (Flexible Matcher) ---
def normalize_name(text):
    if pd.isna(text): return ""
    text = str(text).lower().strip()
    text = re.sub(r'[\W_]+', ' ', text)
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    return text.strip()

def matches_driver_name(name1, name2):
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    if not n1 or not n2: return False
    # إذا كان أحد الاسمين جزءاً من الآخر (مطابقة ذكية)
    if len(n1) > 3 and n1 in n2: return True
    if len(n2) > 3 and n2 in n1: return True
    return False

# --- 4. دوال الإيرادات والرواتب ---
def calc_supermall_revenue(orders): return orders * 9 if orders <= 400 else (orders * 10 if orders <= 500 else (orders * 11 if orders <= 600 else orders * 12))
def calc_ninja_revenue(orders): return (6500 + ((orders - 460) * 12)) if orders >= 460 else (6500 - ((460 - orders) * 22)) if orders > 400 else orders * 10
def calc_kita_revenue(orders, dist): return (orders * 6.5) + (max(0, dist - orders) * 0.6) if pd.notna(orders) else 0
def calc_hungerstation_revenue(orders, status, dist, ql): return (orders * 6) + (dist * 0.90) if pd.notna(orders) else 0

def calc_salary_by_project(orders, client, is_freelance):
    if client == "Ninja (نينجا)": return (5000 + ((orders - 460) * 8)) if orders >= 460 else (orders * 7.0)
    if is_freelance: return (5000 + ((orders - 550) * 9)) if orders >= 550 else (orders * 7.0)
    if orders >= 550: return 2500 + 300 + ((orders - 550) * 8)
    elif 401 <= orders <= 549: return orders * 4.0
    else: return orders * 3.0

def get_smart_car_allowance(row_str, report_days):
    if not row_str: return 0
    full_allowance = 1200 if 'بدل سياره جديد' in row_str or 'بدل سيارة جديد' in row_str else (1000 if 'بدل سياره' in row_str or 'بدل سيارة' in row_str else 0)
    if full_allowance > 0: return full_allowance if report_days >= 28 else round((full_allowance / 30) * report_days, 2)
    return 0

# --- 5. واجهة النظام ---
st.markdown('<style>@import url("https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap"); *{font-family:"Cairo",sans-serif; direction:rtl; text-align:right;} .metric-card{background:#fff; padding:15px; border-radius:10px; box-shadow:0 4px 6px rgba(0,0,0,0.1);}</style>', unsafe_allow_html=True)
st.markdown('<h2>📊 المنظومة المالية - الإصدار المعالج (v29.1)</h2>', unsafe_allow_html=True)

with st.sidebar:
    selected_client = st.radio("اختر المشروع:", ["Supermall", "Ninja (نينجا)", "Kita (كيتا)", "HungerStation (هنقرستيشن)"])

col1, col2, col3 = st.columns(3)
perf_file = col1.file_uploader("1. تقرير الأداء", type=['xlsx', 'csv'])
agent_info_file = col2.file_uploader("2. بيانات المناديب", type=['xlsx', 'csv'])
car_fuel_file = col3.file_uploader("3. استهلاك البنزين", type=['xlsx', 'csv'])

if perf_file and agent_info_file and car_fuel_file:
    with st.spinner('⏳ جاري المطابقة الذكية للأسماء والبنزين...'):
        try:
            df_perf = smart_read_file(perf_file)
            df_agents = smart_read_file(agent_info_file)
            df_cars = smart_read_file(car_fuel_file)

            # توحيد أسماء الأعمدة الهامة بذكاء مهما كان اسمها في ملفك
            def rename_col(df, possible_names, target_name):
                for col in df.columns:
                    if str(col).strip().lower() in [p.lower() for p in possible_names]:
                        df.rename(columns={col: target_name}, inplace=True)
                        break

            rename_col(df_perf, ['اسم المندوب', 'الاسم', 'Driver Name', 'Username', 'Name'], 'اسم المندوب')
            rename_col(df_perf, ['رقم الإقامة', 'Iqama', 'رقم الاقامة', 'ID', 'National ID'], 'Iqama')
            
            rename_col(df_agents, ['اسم المندوب', 'الاسم', 'Driver Name', 'Name'], 'اسم المندوب')
            rename_col(df_agents, ['رقم الإقامة', 'Iqama', 'رقم الاقامة', 'ID'], 'Iqama')

            # تنظيف أرقام الإقامة للدمج
            if 'Iqama' in df_perf.columns: df_perf['Iqama_Clean'] = df_perf['Iqama'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            if 'Iqama' in df_agents.columns: df_agents['Iqama_Clean'] = df_agents['Iqama'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

            df_agents['agent_full_text'] = df_agents.apply(lambda r: " ".join(str(v).lower() for v in r.values).replace('ة', 'ه'), axis=1)

            # الدمج بناءً على الإقامة
            if 'Iqama_Clean' in df_perf.columns and 'Iqama_Clean' in df_agents.columns:
                df_merged = pd.merge(df_perf, df_agents, on='Iqama_Clean', how='left', suffixes=('', '_agent'))
            else:
                df_merged = df_perf.copy()

            # التأكد من وجود عمود اسم المندوب والإقامة في النتيجة النهائية
            if 'اسم المندوب' not in df_merged.columns: df_merged['اسم المندوب'] = 'غير معروف'
            if 'Iqama' not in df_merged.columns: df_merged['Iqama'] = 'غير متوفر'

            # ---------------- معالجة البنزين (المطابقة المرنة) ----------------
            rename_col(df_cars, ['السائقين المعينين للمركبة', 'اسم السائق', 'Driver', 'Name'], 'Driver_Name')
            rename_col(df_cars, ['إجمالي المبلغ المستخدم', 'القيمة', 'المبلغ', 'Amount', 'Total'], 'Fuel_Cost')

            if 'Driver_Name' in df_cars.columns and 'Fuel_Cost' in df_cars.columns:
                df_cars['Fuel_Cost'] = pd.to_numeric(df_cars['Fuel_Cost'], errors='coerce').fillna(0)
                
                # دالة استخراج البنزين لكل مندوب
                def get_agent_fuel(agent_name):
                    total_fuel = 0
                    for _, car_row in df_cars.iterrows():
                        if matches_driver_name(agent_name, str(car_row['Driver_Name'])):
                            total_fuel += car_row['Fuel_Cost']
                    return total_fuel

                df_merged['مخصص البنزين'] = df_merged['اسم المندوب'].apply(get_agent_fuel)
            else:
                df_merged['مخصص البنزين'] = 0

            # ---------------- الحسابات المالية ----------------
            rename_col(df_merged, ['Grand Total Delivered', 'الطلبات الناجحة', 'Orders', 'Total Orders'], 'الطلبات المحققة')
            df_merged['الطلبات المحققة'] = pd.to_numeric(df_merged.get('الطلبات المحققة', 0), errors='coerce').fillna(0)

            # الإيرادات
            if selected_client == "Supermall": df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'].apply(calc_supermall_revenue)
            elif selected_client == "Ninja (نينجا)": df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'].apply(calc_ninja_revenue)
            else: df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'] * 6 

            def calc_agent_dues_final(row):
                orders = row['الطلبات المحققة']
                row_str = str(row.get('agent_full_text', ''))
                is_freelance = True if selected_client == "Ninja (نينجا)" else (('فري' in row_str) or ('freelance' in row_str) or ('حر' in row_str))
                
                salary = calc_salary_by_project(orders, selected_client, is_freelance)
                car_rent = get_smart_car_allowance(row_str, 30) # افتراضي 30 يوم
                return pd.Series(['فري لانسر' if is_freelance else 'كفالة', salary, car_rent, salary + car_rent])

            df_merged[['نوع المندوب', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب']] = df_merged.apply(calc_agent_dues_final, axis=1)
            df_merged['ربح الشركة الصافي'] = df_merged['إيراد الشركة من العميل'] - df_merged['إجمالي المستحق للمندوب'] - df_merged['مخصص البنزين']
            
            df_merged.rename(columns={'Iqama': 'رقم الإقامة'}, inplace=True)

            # العرض النهائي
            display_cols = ['رقم الإقامة', 'اسم المندوب', 'نوع المندوب', 'الطلبات المحققة', 'مخصص البنزين', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب', 'إيراد الشركة من العميل', 'ربح الشركة الصافي']
            final_df = df_merged[[c for c in display_cols if c in df_merged.columns]]
            
            st.success("✅ تمت معالجة البيانات والمطابقة بنجاح!")
            st.dataframe(final_df, use_container_width=True)

            # التصدير المباشر
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, index=False, sheet_name='البيانات')
            st.download_button("📥 تصدير التقرير (Excel)", data=output.getvalue(), file_name=f"Report_{selected_client}.xlsx")

        except Exception as e:
            st.error(f"حدث خطأ: {e}")
