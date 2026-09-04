import streamlit as st
import pandas as pd
from io import BytesIO
import re
import warnings
from datetime import datetime

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

# --- 1. محرك القراءة الشامل ---
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

# --- 2. المستشعر الزمني الذكي (Time-Context AI) ---
def extract_report_info(df):
    date_strs = set()
    for col in df.columns:
        c = str(col).lower()
        if 'total' in c or 'grand' in c: continue
        m = re.search(r'\b(\d{1,2}[\s\-]+[a-z]{3})\b', c)
        if m: date_strs.add(m.group(1).replace('-', ' ').title())
        
    if not date_strs:
        for col in df.columns:
            if str(col).strip().lower() in ['date', 'التاريخ', 'day', 'اليوم']:
                valid_dates = pd.to_datetime(df[col], errors='coerce').dropna()
                if not valid_dates.empty:
                    for d in valid_dates.dt.strftime('%d %b').unique():
                        date_strs.add(d)
                break
    
    num_days = len(date_strs)
    if num_days == 0:
        return "غير محدد (افتراضي 30 يوم)", 30
        
    try:
        parsed = sorted([pd.to_datetime(d + " 2026", format='%d %b %Y') for d in date_strs])
        start_d = parsed[0].strftime('%d %b')
        end_d = parsed[-1].strftime('%d %b')
        
        if num_days == 1:
            return f"يوم واحد ({start_d})", num_days
        elif num_days >= 28:
            return f"شهر كامل (من {start_d} إلى {end_d})", num_days
        else:
            return f"من {start_d} إلى {end_d} (المدة: {num_days} أيام)", num_days
    except:
        if num_days == 1:
            return f"يوم واحد ({list(date_strs)[0]})", num_days
        else:
            return f"المدة: {num_days} أيام", num_days

# --- 3. محرك الترجمة والذكاء الصوتي ---
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
    translated_words = [word_map.get(w, "") for w in words]
    return " ".join([w for w in translated_words if w])

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
    if norm_agent and (norm_agent == norm_fuel or norm_agent in norm_fuel or norm_fuel in norm_agent): return True
        
    trans_agent = char_transliterate_ar_to_en(agent_name)
    norm_trans = normalize_text(trans_agent)
    
    if norm_trans and (norm_trans == norm_fuel or norm_trans in norm_fuel or norm_fuel in norm_trans): return True
        
    tok_trans = set(norm_trans.split())
    tok_fuel = set(norm_fuel.split())
    if len(tok_trans.intersection(tok_fuel)) >= 2: return True
        
    if agent_username:
        clean_user = normalize_text(str(agent_username).split('-')[0])
        if clean_user and len(clean_user) >= 3 and clean_user in norm_fuel and clean_user not in ['muhammad', 'ahmed']:
            return True
            
    return False

# --- 4. الحسابات المالية ---
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

# --- 5. إنشاء الداشبورد המطور ---
def create_modern_excel(df, client_name, date_context_str, report_days):
    output = BytesIO()
    workbook = pd.ExcelWriter(output, engine='xlsxwriter')
    wb = workbook.book
    
    ws_data = wb.add_worksheet('البيانات التفصيلية')
    
    title_fmt = wb.add_format({'bold': True, 'font_size': 14, 'font_color': '#0F172A', 'align': 'right', 'valign': 'vcenter'})
    meta_fmt = wb.add_format({'bold': True, 'font_size': 11, 'font_color': '#0284C7', 'bg_color': '#E0F2FE', 'align': 'right', 'valign': 'vcenter', 'border': 1})
    header_fmt = wb.add_format({'bold': True, 'bg_color': '#1E293B', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'border': 1})
    data_fmt = wb.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
    total_fmt = wb.add_format({'bold': True, 'bg_color': '#0284C7', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'border': 1})
    red_fmt = wb.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'align': 'center', 'border': 1})
    green_fmt = wb.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100', 'align': 'center', 'border': 1})
    
    ws_data.write('A1', f"📊 التقرير المالي والتشغيلي الموحد - مشروع: {client_name}", title_fmt)
    ws_data.write('A2', f"📅 فترة التقرير: {date_context_str} | عدد الأيام المحسوبة: {report_days} يوم", meta_fmt)
    
    start_row = 3
    for col_num, value in enumerate(df.columns):
        ws_data.write(start_row, col_num, value, header_fmt)
        ws_data.set_column(col_num, col_num, 18)
        
    for row_num, row_values in enumerate(df.values):
        is_last_row = (row_num == len(df) - 1)
        fmt = total_fmt if is_last_row else data_fmt
        for col_num, val in enumerate(row_values):
            ws_data.write(start_row + 1 + row_num, col_num, val, fmt)

    max_data_row = start_row + len(df) 
    if 'ربح الشركة الصافي' in df.columns:
        idx = df.columns.get_loc('ربح الشركة الصافي')
        col_let = chr(65 + idx) if idx < 26 else chr(64 + idx//26) + chr(65 + idx%26)
        ws_data.conditional_format(f'{col_let}5:{col_let}{max_data_row}', {'type': 'cell', 'criteria': '<', 'value': 0, 'format': red_fmt})
        ws_data.conditional_format(f'{col_let}5:{col_let}{max_data_row}', {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': green_fmt})

    ws_dash = wb.add_worksheet('📊 لوحة القيادة (Dashboard)')
    ws_dash.merge_range('B2:F3', f'التقرير المالي والتشغيلي - مشروع {client_name}', wb.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'}))
    ws_dash.merge_range('B4:F4', f'📅 فترة التقرير المكتشفة: {date_context_str} | إجمالي الأيام: {report_days} يوم', wb.add_format({'bold': True, 'font_size': 11, 'align': 'center', 'font_color': '#0369A1', 'bg_color': '#F0F9FF', 'border': 1}))
    
    chart = wb.add_chart({'type': 'column'})
    if len(df) > 1 and 'اسم المندوب' in df.columns:
        name_idx = chr(65 + df.columns.get_loc('اسم المندوب'))
        order_idx = chr(65 + df.columns.get_loc('الطلبات المحققة'))
        chart.add_series({'name': 'الطلبات المحققة', 'categories': f'=البيانات التفصيلية!${name_idx}$5:${name_idx}${max_data_row}', 'values': f'=البيانات التفصيلية!${order_idx}$5:${order_idx}${max_data_row}'})
        ws_dash.insert_chart('B7', chart)
        
    workbook.close()
    return output.getvalue()

# --- 6. الواجهة الرئيسية ---
st.markdown("""
    <style>
        *{direction:rtl; text-align:right;} 
        .time-badge {background:#E0F2FE; color:#0284C7; padding:10px 18px; border-radius:10px; font-weight:bold; display:inline-block; margin-bottom:15px; border:1px solid #BAE6FD; font-size: 1.05rem;}
        /* تصميم زر الواتساب */
        .whatsapp-btn {
            display: inline-block;
            background-color: #25D366;
            color: white;
            padding: 12px 20px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            width: 100%;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: background-color 0.3s ease;
        }
        .whatsapp-btn:hover {
            background-color: #128C7E;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 المنظومة المالية الشاملة لشركة الحلول المتقدمة للخدمات اللوجستية")
st.info("💡 تطوير وأعمال: د. جياد عمر محمد فضل | v40.0 (تم إضافة زر التواصل المباشر عبر الواتساب)")

# --- الشريط الجانبي (Sidebar) وإضافة زر الواتساب ---
with st.sidebar:
    selected_client = st.radio("اختر المشروع:", ["Supermall", "Ninja", "Kita", "HungerStation"])
    st.markdown("---")
    # زر الواتساب المباشر
    st.markdown("""
        <a href="https://wa.me/message/TVFRW7TRANRQL1" target="_blank" class="whatsapp-btn">
            💬 تحديث عقود الشركات المشغلة
        </a>
    """, unsafe_allow_html=True)


col1, col2, col3 = st.columns(3)
allowed_types = ['xlsx', 'csv', 'png', 'jpg', 'jpeg', 'pdf', 'docx']
perf_file = col1.file_uploader("1. تقرير الأداء", type=allowed_types)
agent_info_file = col2.file_uploader("2. بيانات المناديب", type=allowed_types)
car_fuel_file = col3.file_uploader("3. استهلاك البنزين", type=allowed_types)

if perf_file and car_fuel_file:
    with st.spinner('⏳ جاري المسح وحساب الإجماليات...'):
        df_perf = smart_read_file(perf_file)
        df_agents = smart_read_file(agent_info_file) if agent_info_file else pd.DataFrame()
        df_cars = smart_read_file(car_fuel_file)

        date_context_str, report_days = extract_report_info(df_perf)
        st.markdown(f'<div class="time-badge">📅 <b>فترة التقرير المكتشفة:</b> {date_context_str} | <b>عدد الأيام:</b> {report_days} يوم</div>', unsafe_allow_html=True)

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

            if matched_agent is not None and pd.notna(matched_agent.get('master_name')) and str(matched_agent.get('master_name')).strip() != '':
                row_data['اسم المندوب'] = str(matched_agent.get('master_name')).strip()
            elif p_name and p_name.lower() != 'nan':
                row_data['اسم المندوب'] = p_name
            elif p_user and p_user.lower() != 'nan':
                row_data['اسم المندوب'] = p_user
            else:
                row_data['اسم المندوب'] = f"مندوب {p_id}" if p_id else "مندوب جديد"

            if matched_agent is not None and pd.notna(matched_agent.get('master_iqama')) and str(matched_agent.get('master_iqama')).strip() != '':
                row_data['رقم الإقامة'] = str(matched_agent.get('master_iqama')).replace('.0', '').strip()
            elif p_iqama and p_iqama.lower() != 'nan':
                row_data['رقم الإقامة'] = p_iqama
            else:
                row_data['رقم الإقامة'] = p_id if p_id else "1000000000"

            row_data['agent_full_text'] = f"{row_data['اسم المندوب']} {p_name} {p_user} {p_id}"
            processed_rows.append(row_data)

        df_merged = pd.DataFrame(processed_rows)

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

        rename_col(df_merged, ['Grand Total Delivered', 'الطلبات الناجحة', 'Orders'], 'الطلبات المحققة')
        df_merged['الطلبات المحققة'] = pd.to_numeric(df_merged.get('الطلبات المحققة', 0), errors='coerce').fillna(0)
        df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'].apply(calc_supermall_revenue) if selected_client == "Supermall" else (df_merged['الطلبات المحققة'].apply(calc_ninja_revenue) if selected_client == "Ninja" else df_merged['الطلبات المحققة'] * 6)

        def calc_dues(row):
            row_str = str(row.get('agent_full_text', ''))
            is_free = True if selected_client == "Ninja" else ('فري' in row_str or 'حر' in row_str)
            sal = calc_salary_by_project(row['الطلبات المحققة'], selected_client, is_free)
            car = get_smart_car_allowance(row_str, report_days)
            return pd.Series(['فري لانسر' if is_free else 'كفالة', sal, car, sal + car])

        df_merged[['نوع المندوب', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب']] = df_merged.apply(calc_dues, axis=1)
        df_merged['ربح الشركة الصافي'] = df_merged['إيراد الشركة من العميل'] - df_merged['إجمالي المستحق للمندوب'] - df_merged['مخصص البنزين']

        display_cols = ['رقم الإقامة', 'اسم المندوب', 'نوع المندوب', 'الطلبات المحققة', 'مخصص البنزين', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب', 'إيراد الشركة من العميل', 'ربح الشركة الصافي']
        final_df = df_merged[[c for c in display_cols if c in df_merged.columns]]
        
        # --- إضافة صف المجاميع أسفل الجدول ---
        total_row = {col: '-' for col in final_df.columns}
        total_row['اسم المندوب'] = 'الإجمالي الكلي (المجموع)'
        
        numeric_cols = ['الطلبات المحققة', 'مخصص البنزين', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب', 'إيراد الشركة من العميل', 'ربح الشركة الصافي']
        for col in numeric_cols:
            if col in final_df.columns:
                total_row[col] = final_df[col].sum()
                
        final_df = pd.concat([final_df, pd.DataFrame([total_row])], ignore_index=True)

        st.dataframe(final_df, use_container_width=True)
        st.download_button("📥 تصدير الداشبورد المالي (Excel)", data=create_modern_excel(final_df, selected_client, date_context_str, report_days), file_name=f"Dashboard_{selected_client}.xlsx")
