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

st.set_page_config(page_title="شركة الحلول المتقدمة | المنظومة الشاملة", page_icon="⚡", layout="wide")

# --- محرك القراءة الشامل ---
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
                lines = extracted_text.split('\n')
                data = [line.split() for line in lines if line.strip()]
                if data:
                    max_cols = max(len(row) for row in data)
                    padded_data = [row + [''] * (max_cols - len(row)) for row in data]
                    return pd.DataFrame(padded_data[1:], columns=padded_data[0] if len(padded_data) > 1 else None)
            except: pass
            return pd.DataFrame()
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- محرك الذكاء الصوتي (Phonetic AI Engine) ---
def to_phonetic(name):
    if pd.isna(name): return ""
    name = str(name).lower()
    # إبقاء الحروف الإنجليزية والعربية فقط
    name = re.sub(r'[^a-z\u0600-\u06FF]', '', name)
    
    # دمج الحروف المركبة
    name = name.replace('sh', 'ش').replace('ch', 'ش').replace('ph', 'ف').replace('gh', 'غ').replace('kh', 'خ')
    
    res = []
    # تحويل الحروف لتردد صوتي موحد
    for char in name:
        if char in 'bpب': res.append('B')
        elif char in 'tطتث': res.append('T')
        elif char in 'jgج': res.append('J')
        elif char in 'hحخه': res.append('H')
        elif char in 'dدضذ': res.append('D')
        elif char in 'rر': res.append('R')
        elif char in 'zزظ': res.append('Z')
        elif char in 'scxسص': res.append('S')
        elif char == 'ش': res.append('SH')
        elif char in 'fvف': res.append('F')
        elif char in 'kqقك': res.append('K')
        elif char in 'lل': res.append('L')
        elif char in 'mم': res.append('M')
        elif char in 'nن': res.append('N')
        elif char in 'غ': res.append('G')
    
    if not res: return ""
    # إزالة التكرار (مثال: محمممد -> محمد)
    dedup = [res[0]]
    for c in res[1:]:
        if c != dedup[-1]:
            dedup.append(c)
    return "".join(dedup)

def normalize_name(text):
    if pd.isna(text): return ""
    text = str(text).lower().strip()
    text = re.sub(r'[\W_]+', ' ', text)
    return text.strip()

def matches_driver_name(name1, name2):
    n1, n2 = normalize_name(name1), normalize_name(name2)
    if not n1 or not n2: return False
    
    # 1. التطابق النصي العادي
    if n1 == n2 or (len(n1) > 3 and n1 in n2) or (len(n2) > 3 and n2 in n1):
        return True
        
    # 2. التطابق الصوتي عبر اللغات (عربي/إنجليزي)
    p1 = to_phonetic(name1)
    p2 = to_phonetic(name2)
    
    if not p1 or not p2: return False
    if p1 == p2: return True
    if len(p1) >= 3 and p1 in p2: return True
    if len(p2) >= 3 and p2 in p1: return True
    
    # 3. التطابق الصوتي بالكلمات المتفرقة
    tok1 = set([to_phonetic(t) for t in str(name1).split() if len(to_phonetic(t)) >= 2])
    tok2 = set([to_phonetic(t) for t in str(name2).split() if len(to_phonetic(t)) >= 2])
    if tok1 and tok2:
        intersection = tok1.intersection(tok2)
        if len(intersection) >= 2: return True
        if len(intersection) == 1 and (len(tok1) == 1 or len(tok2) == 1): return True
        
    return False

# --- الحسابات المالية ---
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

# --- إنشاء الداشبورد ---
def create_modern_excel(df, client_name):
    output = BytesIO()
    workbook = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(workbook, index=False, sheet_name='البيانات')
    
    wb = workbook.book
    ws = workbook.sheets['البيانات']
    header_fmt = wb.add_format({'bold': True, 'bg_color': '#1E293B', 'font_color': 'white', 'align': 'center'})
    red_fmt = wb.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    green_fmt = wb.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    
    for col_num, value in enumerate(df.columns):
        ws.write(0, col_num, value, header_fmt)
        ws.set_column(col_num, col_num, 16)
        
    if 'ربح الشركة الصافي' in df.columns:
        idx = df.columns.get_loc('ربح الشركة الصافي')
        col_let = chr(65 + idx) if idx < 26 else chr(64 + idx//26) + chr(65 + idx%26)
        ws.conditional_format(f'{col_let}2:{col_let}{len(df)+1}', {'type': 'cell', 'criteria': '<', 'value': 0, 'format': red_fmt})
        ws.conditional_format(f'{col_let}2:{col_let}{len(df)+1}', {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': green_fmt})

    ws_dash = wb.add_worksheet('الداشبورد')
    ws_dash.merge_range('B2:E3', f'التقرير المالي - {client_name}', wb.add_format({'bold': True, 'font_size': 16, 'align': 'center'}))
    
    chart = wb.add_chart({'type': 'column'})
    if len(df) > 0 and 'اسم المندوب' in df.columns:
        name_idx = chr(65 + df.columns.get_loc('اسم المندوب'))
        order_idx = chr(65 + df.columns.get_loc('الطلبات المحققة'))
        chart.add_series({'name': 'الطلبات المحققة', 'categories': f'=البيانات!${name_idx}$2:${name_idx}${len(df)+1}', 'values': f'=البيانات!${order_idx}$2:${order_idx}${len(df)+1}'})
        ws_dash.insert_chart('B6', chart)
        
    workbook.close()
    return output.getvalue()

# --- الواجهة الرئيسية (بالهوية الجديدة) ---
st.markdown('<style>*{direction:rtl; text-align:right;}</style>', unsafe_allow_html=True)
st.title("📊 المنظومة المالية الشاملة لشركة الحلول المتقدمة للخدمات اللوجستية")
st.info("💡 تطوير وأعمال: د. جياد عمر محمد فضل | v35.0 (مزود بمحرك الذكاء الصوتي)")

selected_client = st.sidebar.radio("اختر المشروع:", ["Supermall", "Ninja", "Kita", "HungerStation"])

col1, col2, col3 = st.columns(3)
allowed_types = ['xlsx', 'csv', 'png', 'jpg', 'jpeg', 'pdf', 'docx']
perf_file = col1.file_uploader("1. تقرير الأداء", type=allowed_types)
agent_info_file = col2.file_uploader("2. بيانات المناديب", type=allowed_types)
car_fuel_file = col3.file_uploader("3. استهلاك البنزين", type=allowed_types)

if perf_file and agent_info_file and car_fuel_file:
    with st.spinner('⏳ جاري المسح الشامل والمطابقة بالذكاء الصوتي (Phonetic AI)...'):
        df_perf = smart_read_file(perf_file)
        df_agents = smart_read_file(agent_info_file)
        df_cars = smart_read_file(car_fuel_file)

        def rename_col(df, possible_names, target_name):
            for col in df.columns:
                if str(col).strip().lower() in [p.lower() for p in possible_names]:
                    df.rename(columns={col: target_name}, inplace=True)
                    break

        rename_col(df_perf, ['رقم الإقامة', 'Iqama'], 'perf_iqama')
        rename_col(df_perf, ['اسم المندوب', 'الاسم', 'Name'], 'perf_name')
        rename_col(df_perf, ['Username', 'يوزر'], 'perf_user')
        rename_col(df_perf, ['ID', 'رقم'], 'perf_id')
        
        rename_col(df_agents, ['رقم الإقامة', 'Iqama', 'رقم الهوية', 'رقم الاقامة'], 'master_iqama')
        rename_col(df_agents, ['اسم المندوب', 'الاسم', 'Name'], 'master_name')

        processed_rows = []
        for _, p_row in df_perf.iterrows():
            matched_agent = None
            
            p_iqama = str(p_row.get('perf_iqama', '')).replace('.0', '').strip().lower()
            p_name = str(p_row.get('perf_name', '')).strip().lower()
            p_user = str(p_row.get('perf_user', '')).strip().lower()
            p_id = str(p_row.get('perf_id', '')).replace('.0', '').strip().lower()
            
            search_keys = [k for k in [p_iqama, p_name, p_user, p_id] if k and k != 'nan' and len(k) > 2]
            
            for _, a_row in df_agents.iterrows():
                a_full_text = " ".join([str(v).lower() for v in a_row.values if pd.notna(v)])
                found = False
                for key in search_keys:
                    if key in a_full_text or matches_driver_name(key, a_full_text):
                        found = True
                        break
                if found:
                    matched_agent = a_row
                    break
                    
            row_data = p_row.to_dict()
            for k in list(row_data.keys()):
                if 'إقامة' in str(k) or 'اقامة' in str(k) or 'اسم المندوب' in str(k):
                    del row_data[k]

            if matched_agent is not None:
                raw_iqama = str(matched_agent.get('master_iqama', ''))
                raw_name = str(matched_agent.get('master_name', ''))
                row_data['agent_full_text'] = " ".join([str(v).lower() for v in matched_agent.values if pd.notna(v)])
            else:
                raw_iqama = p_iqama
                fallback_name = p_name if p_name and p_name != 'nan' else p_user
                raw_name = fallback_name
                row_data['agent_full_text'] = p_name + " " + p_user

            # تصفية الإقامة (أرقام فقط)
            clean_iqama = re.sub(r'\D', '', raw_iqama)
            if len(clean_iqama) >= 8:
                row_data['رقم الإقامة'] = clean_iqama
            else:
                found_iqama = re.search(r'\b[12]\d{9}\b', row_data['agent_full_text'])
                row_data['رقم الإقامة'] = found_iqama.group(0) if found_iqama else 'غير مسجل'

            # تصفية الاسم وإظهاره بشكل أنيق ومفهوم
            if re.search(r'[\u0600-\u06FF]', raw_name):
                row_data['اسم المندوب'] = raw_name.title()
            else:
                clean_name = re.sub(r'[^a-zA-Z\u0600-\u06FF\s]', ' ', str(raw_name)).strip().title()
                row_data['اسم المندوب'] = clean_name if clean_name else 'غير مسجل'

            processed_rows.append(row_data)

        df_merged = pd.DataFrame(processed_rows)

        # --- معالجة البنزين بالذكاء الصوتي ---
        rename_col(df_cars, ['السائقين المعينين للمركبة', 'اسم السائق', 'Driver'], 'Driver_Name')
        rename_col(df_cars, ['إجمالي المبلغ المستخدم', 'القيمة', 'Total', 'Amount'], 'Fuel_Cost')

        if 'Driver_Name' in df_cars.columns and 'Fuel_Cost' in df_cars.columns:
            df_cars['Fuel_Cost'] = pd.to_numeric(df_cars['Fuel_Cost'], errors='coerce').fillna(0)
            
            def get_fuel(agent_name, agent_full_text):
                total_fuel = 0
                for _, car_row in df_cars.iterrows():
                    car_driver = str(car_row['Driver_Name']).strip().lower()
                    if matches_driver_name(agent_name, car_driver) or (car_driver and matches_driver_name(car_driver, agent_full_text)):
                        total_fuel += car_row['Fuel_Cost']
                return total_fuel
                
            df_merged['مخصص البنزين'] = df_merged.apply(lambda r: get_fuel(r['اسم المندوب'], r.get('agent_full_text', '')), axis=1)
        else:
            df_merged['مخصص البنزين'] = 0

        # --- الحسابات النهائية ---
        rename_col(df_merged, ['Grand Total Delivered', 'الطلبات الناجحة', 'Orders'], 'الطلبات المحققة')
        df_merged['الطلبات المحققة'] = pd.to_numeric(df_merged.get('الطلبات المحققة', 0), errors='coerce').fillna(0)

        df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'].apply(calc_supermall_revenue) if selected_client == "Supermall" else (df_merged['الطلبات المحققة'].apply(calc_ninja_revenue) if selected_client == "Ninja" else df_merged['الطلبات المحققة'] * 6)

        def calc_dues(row):
            row_str = str(row.get('agent_full_text', ''))
            is_free = True if selected_client == "Ninja" else ('فري' in row_str or 'حر' in row_str)
            sal = calc_salary_by_project(row['الطلبات المحققة'], selected_client, is_free)
            car = get_smart_car_allowance(row_str, 30)
            return pd.Series(['فري لانسر' if is_free else 'كفالة', sal, car, sal + car])

        df_merged[['نوع المندوب', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب']] = df_merged.apply(calc_dues, axis=1)
        df_merged['ربح الشركة الصافي'] = df_merged['إيراد الشركة من العميل'] - df_merged['إجمالي المستحق للمندوب'] - df_merged['مخصص البنزين']

        display_cols = ['رقم الإقامة', 'اسم المندوب', 'نوع المندوب', 'الطلبات المحققة', 'مخصص البنزين', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب', 'إيراد الشركة من العميل', 'ربح الشركة الصافي']
        final_df = df_merged[[c for c in display_cols if c in df_merged.columns]]
        
        st.success("✅ تمت المعالجة بنجاح! محرك الذكاء الصوتي قام بمطابقة الأسماء العربية والإنجليزية بسلاسة.")
        st.dataframe(final_df, use_container_width=True)
        st.download_button("📥 تصدير الداشبورد المالي (Excel)", data=create_modern_excel(final_df, selected_client), file_name=f"Dashboard_{selected_client}.xlsx")
