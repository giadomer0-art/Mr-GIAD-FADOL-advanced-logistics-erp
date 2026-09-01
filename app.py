import streamlit as st
import pandas as pd
from io import BytesIO
import re
import warnings

try:
    import pdfplumber
except ImportError: pass
try:
    import docx
except ImportError: pass
try:
    from PIL import Image
    import pytesseract
except ImportError: pass

warnings.filterwarnings('ignore')

st.set_page_config(page_title="شركة الحلول المتقدمة | النظام الشامل", page_icon="⚡", layout="wide")

def smart_read_file(uploaded_file):
    if uploaded_file is None: return None
    file_name = uploaded_file.name.lower()
    
    try:
        if file_name.endswith(('.xlsx', '.xls')): return pd.read_excel(uploaded_file)
        elif file_name.endswith('.csv'): return pd.read_csv(uploaded_file)
        elif file_name.endswith('.pdf'):
            try:
                tables = []
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_table()
                        if extracted: tables.extend(extracted)
                if tables and len(tables) > 1: return pd.DataFrame(tables[1:], columns=tables[0])
            except: pass
            return pd.DataFrame()
        elif file_name.endswith(('.png', '.jpg', '.jpeg')):
            try:
                img = Image.open(uploaded_file)
                extracted_text = pytesseract.image_to_string(img, lang='ara+eng')
                st.success(f"تم مسح الصورة: {file_name}")
                lines = extracted_text.split('\n')
                data = [line.split() for line in lines if line.strip()]
                if data:
                    max_cols = max(len(row) for row in data)
                    padded_data = [row + [''] * (max_cols - len(row)) for row in data]
                    return pd.DataFrame(padded_data[1:], columns=padded_data[0] if len(padded_data) > 1 else None)
            except Exception as e:
                st.error("مكتبة OCR غير مفعلة في السيرفر.")
            return pd.DataFrame()
        return pd.DataFrame()
    except:
        return pd.DataFrame()

def normalize_name(text):
    if pd.isna(text): return ""
    text = str(text).lower().strip()
    text = re.sub(r'[\W_]+', ' ', text)
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    return text.strip()

def matches_driver_name(name1, name2, aliases=[]):
    n1, n2 = normalize_name(name1), normalize_name(name2)
    if not n1 or not n2: return False
    
    if len(n1) > 3 and n1 in n2: return True
    if len(n2) > 3 and n2 in n1: return True
    
    for alias in aliases:
        a_norm = normalize_name(alias)
        if a_norm and len(a_norm) > 2:
            if a_norm in n2 or n2 in a_norm or a_norm in n1 or n1 in a_norm:
                return True
    return False

def calc_supermall_revenue(orders): return orders * 9 if orders <= 400 else (orders * 10 if orders <= 500 else (orders * 11 if orders <= 600 else orders * 12))
def calc_ninja_revenue(orders): return (6500 + ((orders - 460) * 12)) if orders >= 460 else (6500 - ((460 - orders) * 22)) if orders > 400 else orders * 10
def calc_salary_by_project(orders, client, is_freelance):
    if client == "Ninja (نينجا)": return (5000 + ((orders - 460) * 8)) if orders >= 460 else (orders * 7.0)
    if is_freelance: return (5000 + ((orders - 550) * 9)) if orders >= 550 else (orders * 7.0)
    if orders >= 550: return 2500 + 300 + ((orders - 550) * 8)
    elif 401 <= orders <= 549: return orders * 4.0
    else: return orders * 3.0

def get_smart_car_allowance(row_str, report_days):
    if not row_str: return 0
    full_allowance = 1200 if 'بدل سياره جديد' in row_str or 'بدل سيارة جديد' in row_str else (1000 if 'بدل سياره' in row_str or 'بدل سيارة' in row_str else 0)
    return full_allowance if full_allowance > 0 and report_days >= 28 else round((full_allowance / 30) * report_days, 2) if full_allowance > 0 else 0

def create_modern_excel(df, client_name):
    output = BytesIO()
    workbook = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(workbook, index=False, sheet_name='البيانات')
    
    wb = workbook.book
    ws = workbook.sheets['البيانات']
    header_fmt = wb.add_format({'bold': True, 'bg_color': '#1E293B', 'font_color': 'white'})
    red_fmt = wb.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    green_fmt = wb.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    
    for col_num, value in enumerate(df.columns):
        ws.write(0, col_num, value, header_fmt)
        ws.set_column(col_num, col_num, 15)
        
    if 'ربح الشركة الصافي' in df.columns:
        idx = df.columns.get_loc('ربح الشركة الصافي')
        col_let = chr(65 + idx) if idx < 26 else chr(64 + idx//26) + chr(65 + idx%26)
        ws.conditional_format(f'{col_let}2:{col_let}{len(df)+1}', {'type': 'cell', 'criteria': '<', 'value': 0, 'format': red_fmt})
        ws.conditional_format(f'{col_let}2:{col_let}{len(df)+1}', {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': green_fmt})

    ws_dash = wb.add_worksheet('الداشبورد')
    ws_dash.merge_range('B2:E3', f'تقرير {client_name}', wb.add_format({'bold': True, 'font_size': 16}))
    
    chart = wb.add_chart({'type': 'column'})
    if len(df) > 0 and 'اسم المندوب' in df.columns:
        name_idx = chr(65 + df.columns.get_loc('اسم المندوب'))
        order_idx = chr(65 + df.columns.get_loc('الطلبات المحققة'))
        chart.add_series({'categories': f'=البيانات!${name_idx}$2:${name_idx}${len(df)+1}', 'values': f'=البيانات!${order_idx}$2:${order_idx}${len(df)+1}'})
        ws_dash.insert_chart('B6', chart)
        
    workbook.close()
    return output.getvalue()

st.markdown('<style>*{direction:rtl; text-align:right;}</style>', unsafe_allow_html=True)
st.title("📊 المنظومة المالية الشاملة (v30.0 - ديناميكي بالكامل)")
st.info("💡 لربط تقارير الأداء التي تحتوي على (يوزر نيم إنجليزي) بأسماء المناديب العربية، أضف عموداً في ملف 'بيانات المناديب' باسم (المرادفات) أو (Username) وضع فيه اليوزر الإنجليزي للمندوب.")

selected_client = st.sidebar.radio("اختر المشروع:", ["Supermall", "Ninja", "Kita", "HungerStation"])

col1, col2, col3 = st.columns(3)
allowed_types = ['xlsx', 'csv', 'png', 'jpg', 'jpeg', 'pdf', 'docx']
perf_file = col1.file_uploader("1. تقرير الأداء", type=allowed_types)
agent_info_file = col2.file_uploader("2. بيانات المناديب", type=allowed_types)
car_fuel_file = col3.file_uploader("3. استهلاك البنزين", type=allowed_types)

if perf_file and agent_info_file and car_fuel_file:
    with st.spinner('⏳ جاري التحليل...'):
        df_perf = smart_read_file(perf_file)
        df_agents = smart_read_file(agent_info_file)
        df_cars = smart_read_file(car_fuel_file)

        def rename_col(df, possible_names, target_name):
            for col in df.columns:
                if str(col).strip().lower() in [p.lower() for p in possible_names]:
                    df.rename(columns={col: target_name}, inplace=True)
                    break

        rename_col(df_perf, ['اسم المندوب', 'الاسم', 'Username', 'Name'], 'اسم المندوب')
        rename_col(df_perf, ['رقم الإقامة', 'Iqama', 'ID'], 'Iqama')
        rename_col(df_agents, ['اسم المندوب', 'الاسم', 'Name'], 'اسم المندوب')
        rename_col(df_agents, ['رقم الإقامة', 'Iqama', 'ID'], 'Iqama')

        if 'Iqama' in df_perf.columns: df_perf['Iqama_Clean'] = df_perf['Iqama'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        if 'Iqama' in df_agents.columns: df_agents['Iqama_Clean'] = df_agents['Iqama'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

        # بناء قاموس المرادفات الديناميكي من ملف المندوبين
        dynamic_aliases = []
        if 'اسم المندوب' in df_agents.columns:
            for _, row in df_agents.iterrows():
                name = str(row['اسم المندوب']).strip()
                aliases = []
                for col in df_agents.columns:
                    col_str = str(col).lower()
                    if 'user' in col_str or 'يوزر' in col_str or 'alias' in col_str or 'مرادف' in col_str:
                        val = str(row[col]).strip()
                        if val and val != 'nan':
                            aliases.extend([a.strip() for a in val.split(',')])
                if name:
                    dynamic_aliases.append({'اسم المندوب': name, 'Aliases': aliases})

        df_agents['agent_full_text'] = df_agents.apply(lambda r: " ".join(str(v).lower() for v in r.values), axis=1)

        if 'Iqama_Clean' in df_perf.columns and 'Iqama_Clean' in df_agents.columns:
            df_merged = pd.merge(df_perf, df_agents, on='Iqama_Clean', how='left', suffixes=('', '_agent'))
        else:
            df_merged = df_perf.copy()

        if 'اسم المندوب' not in df_merged.columns: df_merged['اسم المندوب'] = 'غير معروف'
        
        # استبدال اليوزر الإنجليزي بالاسم العربي بناءً على القاموس الديناميكي
        def get_real_name(username):
            for item in dynamic_aliases:
                if matches_driver_name(username, item['اسم المندوب'], item['Aliases']):
                    return item['اسم المندوب']
            return username
            
        df_merged['اسم المندوب'] = df_merged['اسم المندوب'].apply(get_real_name)

        rename_col(df_cars, ['السائقين المعينين للمركبة', 'اسم السائق', 'Driver'], 'Driver_Name')
        rename_col(df_cars, ['إجمالي المبلغ المستخدم', 'القيمة', 'Total', 'Amount'], 'Fuel_Cost')

        if 'Driver_Name' in df_cars.columns and 'Fuel_Cost' in df_cars.columns:
            df_cars['Fuel_Cost'] = pd.to_numeric(df_cars['Fuel_Cost'], errors='coerce').fillna(0)
            def get_fuel(agent_name):
                aliases = []
                for item in dynamic_aliases:
                    if agent_name == item['اسم المندوب']:
                        aliases = item['Aliases']
                        break
                return sum(row['Fuel_Cost'] for _, row in df_cars.iterrows() if matches_driver_name(agent_name, str(row['Driver_Name']), aliases))
            df_merged['مخصص البنزين'] = df_merged['اسم المندوب'].apply(get_fuel)
        else:
            df_merged['مخصص البنزين'] = 0

        rename_col(df_merged, ['Grand Total Delivered', 'الطلبات الناجحة', 'Orders'], 'الطلبات المحققة')
        df_merged['الطلبات المحققة'] = pd.to_numeric(df_merged.get('الطلبات المحققة', 0), errors='coerce').fillna(0)

        df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'].apply(calc_supermall_revenue) if selected_client == "Supermall" else (df_merged['الطلبات المحققة'].apply(calc_ninja_revenue) if selected_client == "Ninja" else df_merged['الطلبات المحققة'] * 6)

        def calc_dues(row):
            row_str = str(row.get('agent_full_text', ''))
            is_free = True if selected_client == "Ninja" else ('فري' in row_str or 'حر' in row_str)
            sal = calc_salary_by_project(row['الطلبات المحققة'], selected_client, is_free)
            car = get_smart_car_allowance(row_str, 30)
            return pd.Series(['فري' if is_free else 'كفالة', sal, car, sal + car])

        df_merged[['نوع المندوب', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق']] = df_merged.apply(calc_dues, axis=1)
        df_merged['ربح الشركة الصافي'] = df_merged['إيراد الشركة من العميل'] - df_merged['إجمالي المستحق'] - df_merged['مخصص البنزين']

        display_cols = ['رقم الإقامة', 'اسم المندوب', 'نوع المندوب', 'الطلبات المحققة', 'مخصص البنزين', 'إجمالي المستحق', 'إيراد الشركة من العميل', 'ربح الشركة الصافي']
        final_df = df_merged[[c for c in display_cols if c in df_merged.columns]]
        
        st.dataframe(final_df, use_container_width=True)
        st.download_button("📥 تصدير الداشبورد المالي", data=create_modern_excel(final_df, selected_client), file_name=f"Dashboard_{selected_client}.xlsx")
