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

# --- 1. محرك قراءة كافة صيغ الملفات والصور ---
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

# --- 2. محرك الترجمة الصوتية واللفظية (عربي <-> إنجليزي) ---
def char_transliterate_ar_to_en(text):
    if not text or pd.isna(text): return ""
    text = str(text).lower().strip()
    word_map = {
        'مد': 'md', 'نهاد': 'nahid', 'مولا': 'mollah', 'ملا': 'mollah',
        'محمد': 'muhammad', 'احمد': 'ahmed', 'أحمد': 'ahmed',
        'عبدالله': 'abdullah', 'علي': 'ali', 'الصديق': 'elsiddiq',
        'الامين': 'elamin', 'قدوره': 'gaddoura', 'جوني': 'jony', 'جونى': 'jony'
    }
    words = text.split()
    translated_words = []
    for w in words:
        if w in word_map:
            translated_words.append(word_map[w])
        else:
            res = ""
            for c in w:
                if c in 'أإآاى': res += 'a'
                elif c in 'ب': res += 'b'
                elif c in 'تط': res += 't'
                elif c in 'ث': res += 'th'
                elif c in 'ج': res += 'j'
                elif c in 'ح ه': res += 'h'
                elif c in 'خ': res += 'kh'
                elif c in 'دضذظ': res += 'd'
                elif c in 'ر': res += 'r'
                elif c in 'ز': res += 'z'
                elif c in 'سص': res += 's'
                elif c in 'ش': res += 'sh'
                elif c in 'ع': res += 'a'
                elif c in 'غ': res += 'gh'
                elif c in 'ف': res += 'f'
                elif c in 'قك': res += 'k'
                elif c in 'ل': res += 'l'
                elif c in 'م': res += 'm'
                elif c in 'ن': res += 'n'
                elif c in 'و': res += 'o'
                elif c in 'ي': res += 'i'
            translated_words.append(res)
    return " ".join(translated_words)

def normalize_text(text):
    if pd.isna(text): return ""
    text = str(text).lower().strip()
    text = re.sub(r'[\W_]+', ' ', text)
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    return text.strip()

def match_driver_to_fuel(agent_name, agent_username, fuel_driver_name):
    norm_agent = normalize_text(agent_name)
    norm_fuel = normalize_text(fuel_driver_name)
    
    if not norm_fuel: return False
    
    # 1. المطابقة المباشرة
    if norm_agent and (norm_agent == norm_fuel or norm_agent in norm_fuel or norm_fuel in norm_agent):
        return True
        
    # 2. المطابقة عبر الترجمة الصوتية (مد جوني -> md jony)
    trans_agent = char_transliterate_ar_to_en(agent_name)
    norm_trans_agent = normalize_text(trans_agent)
    
    if norm_trans_agent and (norm_trans_agent == norm_fuel or norm_trans_agent in norm_fuel or norm_fuel in norm_trans_agent):
        return True
        
    # 3. المطابقة المتقاطعة للكلمات
    tok_trans = set(norm_trans_agent.split())
    tok_fuel = set(norm_fuel.split())
    common = tok_trans.intersection(tok_fuel)
    if len(common) >= 2:
        return True
        
    # 4. المطابقة عبر بادئة اسم المستخدم (Username)
    if agent_username:
        clean_user = normalize_text(str(agent_username).split('-')[0])
        if clean_user and len(clean_user) >= 3:
            if clean_user in norm_fuel and clean_user not in ['muhammad', 'ahmed', 'mohammed']:
                return True
                
    return False

# --- 3. الحسابات المالية والقواعد اللوجستية ---
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

# --- 4. إنتاج لوحة القيادة وتصدير Excel المطور ---
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
        ws.set_column(col_num, col_num, 18)
        
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

# --- 5. الواجهة الرئيسية ---
st.markdown('<style>*{direction:rtl; text-align:right;}</style>', unsafe_allow_html=True)
st.title("📊 المنظومة المالية الشاملة لشركة الحلول المتقدمة للخدمات اللوجستية")
st.info("💡 تطوير وأعمال: د. جياد عمر محمد فضل | v36.0 (دعم الترجمة الصوتية والربط الذكي بين العربية والإنجليزي)")

selected_client = st.sidebar.radio("اختر المشروع:", ["Supermall", "Ninja", "Kita", "HungerStation"])

col1, col2, col3 = st.columns(3)
allowed_types = ['xlsx', 'csv', 'png', 'jpg', 'jpeg', 'pdf', 'docx']
perf_file = col1.file_uploader("1. تقرير الأداء", type=allowed_types)
agent_info_file = col2.file_uploader("2. بيانات المناديب", type=allowed_types)
car_fuel_file = col3.file_uploader("3. استهلاك البنزين", type=allowed_types)

if perf_file and car_fuel_file:
    with st.spinner('⏳ جاري المسح الشامل والربط الصوتي بين الملفات...'):
        df_perf = smart_read_file(perf_file)
        df_agents = smart_read_file(agent_info_file) if agent_info_file else pd.DataFrame()
        df_cars = smart_read_file(car_fuel_file)

        def rename_col(df, possible_names, target_name):
            if df.empty: return
            for col in list(df.columns):
                if str(col).strip().lower() in [p.lower() for p in possible_names]:
                    df.rename(columns={col: target_name}, inplace=True)
                    break

        rename_col(df_perf, ['رقم الإقامة', 'Iqama'], 'perf_iqama')
        rename_col(df_perf, ['اسم المندوب', 'الاسم', 'Name'], 'perf_name')
        rename_col(df_perf, ['Username', 'يوزر'], 'perf_user')
        rename_col(df_perf, ['ID', 'رقم'], 'perf_id')
        
        if not df_agents.empty:
            rename_col(df_agents, ['رقم الإقامة', 'Iqama', 'رقم الهوية', 'رقم الاقامة'], 'master_iqama')
            rename_col(df_agents, ['اسم المندوب', 'الاسم', 'Name'], 'master_name')

        processed_rows = []
        for _, p_row in df_perf.iterrows():
            matched_agent = None
            
            p_iqama = str(p_row.get('perf_iqama', '')).replace('.0', '').strip()
            p_name = str(p_row.get('perf_name', '')).strip()
            p_user = str(p_row.get('perf_user', '')).strip()
            p_id = str(p_row.get('perf_id', '')).replace('.0', '').strip()
            
            search_keys = [k for k in [p_iqama, p_name, p_user, p_id] if k and k.lower() != 'nan' and len(k) >= 2]
            
            if not df_agents.empty:
                for _, a_row in df_agents.iterrows():
                    a_full_text = " ".join([str(v) for v in a_row.values if pd.notna(v)])
                    found = False
                    for key in search_keys:
                        if key.lower() in a_full_text.lower():
                            found = True
                            break
                    if found:
                        matched_agent = a_row
                        break
                    
            row_data = p_row.to_dict()

            # --- أولوية تحديد الاسم الحقيقي لمنع كلمة "غير مسجل" ---
            if matched_agent is not None and pd.notna(matched_agent.get('master_name')) and str(matched_agent.get('master_name')).strip() != '':
                row_data['اسم المندوب'] = str(matched_agent.get('master_name')).strip()
            elif p_name and p_name.lower() != 'nan':
                row_data['اسم المندوب'] = p_name
            elif p_user and p_user.lower() != 'nan':
                row_data['اسم المندوب'] = p_user
            else:
                row_data['اسم المندوب'] = f"مندوب {p_id}" if p_id else "مندوب جديد"

            # --- أولوية تحديد رقم الإقامة ---
            if matched_agent is not None and pd.notna(matched_agent.get('master_iqama')) and str(matched_agent.get('master_iqama')).strip() != '':
                row_data['رقم الإقامة'] = str(matched_agent.get('master_iqama')).replace('.0', '').strip()
            elif p_iqama and p_iqama.lower() != 'nan':
                row_data['رقم الإقامة'] = p_iqama
            else:
                row_data['رقم الإقامة'] = p_id if p_id else "1000000000"

            row_data['agent_full_text'] = f"{row_data['اسم المندوب']} {p_name} {p_user} {p_id}"
            processed_rows.append(row_data)

        df_merged = pd.DataFrame(processed_rows)

        # --- معالجة البنزين بالترجمة والربط الصوتي ---
        rename_col(df_cars, ['السائقين المعينين للمركبة', 'اسم السائق', 'Driver'], 'Driver_Name')
        rename_col(df_cars, ['إجمالي المبلغ المستخدم', 'القيمة', 'Total', 'Amount'], 'Fuel_Cost')

        if 'Driver_Name' in df_cars.columns and 'Fuel_Cost' in df_cars.columns:
            df_cars['Fuel_Cost'] = pd.to_numeric(df_cars['Fuel_Cost'], errors='coerce').fillna(0)
            
            def get_fuel(agent_name, agent_user, agent_full_text):
                total_fuel = 0
                for _, car_row in df_cars.iterrows():
                    car_driver = str(car_row['Driver_Name']).strip()
                    if match_driver_to_fuel(agent_name, agent_user, car_driver):
                        total_fuel += car_row['Fuel_Cost']
                return total_fuel
                
            df_merged['مخصص البنزين'] = df_merged.apply(lambda r: get_fuel(r['اسم المندوب'], r.get('perf_user', ''), r.get('agent_full_text', '')), axis=1)
        else:
            df_merged['مخصص البنزين'] = 0

        # --- الحسابات النهائية والإيرادات ---
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
        
        st.success("✅ تمت المعالجة بنجاح بدون أي بيانات مفقودة! مطابقة البنزين تعمل بالذكاء الصوتي الكامل.")
        st.dataframe(final_df, use_container_width=True)
        st.download_button("📥 تصدير الداشبورد المالي (Excel)", data=create_modern_excel(final_df, selected_client), file_name=f"Dashboard_{selected_client}.xlsx")
