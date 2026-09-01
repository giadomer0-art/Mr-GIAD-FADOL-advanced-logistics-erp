import streamlit as st
import pandas as pd
from io import BytesIO
import re
import warnings

# محاولة استدعاء مكتبات القراءة المتقدمة
try:
    import pdfplumber
except ImportError:
    pass
try:
    import docx
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

# --- 2. محرك قراءة الملفات الذكي (Multi-Format Parser) ---
def smart_read_file(uploaded_file):
    if uploaded_file is None:
        return None
    
    file_name = uploaded_file.name.lower()
    
    try:
        if file_name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(uploaded_file)
        elif file_name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif file_name.endswith('.pdf'):
            try:
                tables = []
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_table()
                        if extracted: tables.extend(extracted)
                if tables and len(tables) > 1:
                    return pd.DataFrame(tables[1:], columns=tables[0])
                else:
                    st.warning(f"لم يتم العثور على جداول واضحة في ملف الـ PDF ({file_name}).")
                    return pd.DataFrame()
            except Exception as e:
                st.error("يرجى التأكد من تثبيت مكتبة pdfplumber في requirements.txt")
                return pd.DataFrame()
        elif file_name.endswith('.docx'):
            try:
                doc = docx.Document(uploaded_file)
                tables = []
                for table in doc.tables:
                    for row in table.rows:
                        tables.append([cell.text.strip() for cell in row.cells])
                if tables and len(tables) > 1:
                    return pd.DataFrame(tables[1:], columns=tables[0])
                else:
                    st.warning(f"لم يتم العثور على جداول في ملف الوورد ({file_name}).")
                    return pd.DataFrame()
            except Exception as e:
                st.error("يرجى التأكد من تثبيت مكتبة python-docx في requirements.txt")
                return pd.DataFrame()
        elif file_name.endswith(('.png', '.jpg', '.jpeg')):
            st.info(f"🖼️ قمت برفع صورة ({file_name}). قراءة الجداول المعقدة من الصور تتطلب ربط النظام بـ API الرؤية الذكية (Vision AI). يرجى رفع البيانات كـ Excel لضمان الدقة المالية بنسبة 100%.")
            return pd.DataFrame()
        else:
            st.error("صيغة الملف غير مدعومة.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف {file_name}: {str(e)}")
        return pd.DataFrame()

# --- 3. محرك توحيد النصوص المتقدم ---
def norm_text(text):
    if pd.isna(text): return ""
    text = str(text).lower().strip()
    text = re.sub(r'[\W_]+', ' ', text)
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    return text.strip()

# --- 4. دالة إنشاء الإكسل العصري والمودرن (Beautiful Excel with Charts) ---
def create_modern_excel(df, client_name):
    output = BytesIO()
    # استخدام XlsxWriter كمحرك لصناعة الرسوم والتنسيقات العصرية
    workbook = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # 1. إدراج ورقة البيانات التفصيلية
    df.to_excel(workbook, index=False, sheet_name='البيانات التفصيلية')
    
    workbook_obj = workbook.book
    worksheet_data = workbook.sheets['البيانات التفصيلية']
    
    # التنسيقات العصرية (Modern Formats)
    header_format = workbook_obj.add_format({'bold': True, 'bg_color': '#1E293B', 'font_color': 'white', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
    money_format = workbook_obj.add_format({'num_format': '#,##0.00 "SAR"', 'align': 'center'})
    red_format = workbook_obj.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    green_format = workbook_obj.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    
    # تنسيق رأس الجدول
    for col_num, value in enumerate(df.columns.values):
        worksheet_data.write(0, col_num, value, header_format)
        worksheet_data.set_column(col_num, col_num, 18) # توسيع الأعمدة
    
    # التنسيق الشرطي (الأرباح بالأخضر والخسائر بالأحمر)
    if 'ربح الشركة الصافي' in df.columns:
        profit_col_idx = df.columns.get_loc('ربح الشركة الصافي')
        col_letter = chr(65 + profit_col_idx) if profit_col_idx < 26 else chr(64 + profit_col_idx // 26) + chr(65 + profit_col_idx % 26)
        worksheet_data.conditional_format(f'{col_letter}2:{col_letter}{len(df)+1}', {'type': 'cell', 'criteria': '<', 'value': 0, 'format': red_format})
        worksheet_data.conditional_format(f'{col_letter}2:{col_letter}{len(df)+1}', {'type': 'cell', 'criteria': '>=', 'value': 0, 'format': green_format})

    # 2. إدراج ورقة لوحة القيادة (Dashboard) مع الرسوم البيانية
    worksheet_dash = workbook_obj.add_worksheet('📊 لوحة القيادة (Dashboard)')
    
    # نصوص لوحة القيادة
    title_format = workbook_obj.add_format({'bold': True, 'font_size': 20, 'font_color': '#0F172A', 'align': 'center'})
    worksheet_dash.merge_range('B2:H3', f'التقرير المالي والتشغيلي لشركة الحلول المتقدمة - مشروع: {client_name}', title_format)
    
    total_rev = df['إيراد الشركة من العميل'].sum() if 'إيراد الشركة من العميل' in df.columns else 0
    total_cost = df['إجمالي المستحق للمندوب'].sum() if 'إجمالي المستحق للمندوب' in df.columns else 0
    total_profit = df['ربح الشركة الصافي'].sum() if 'ربح الشركة الصافي' in df.columns else 0
    
    summary_format = workbook_obj.add_format({'bold': True, 'bg_color': '#F8FAFC', 'border': 1, 'align': 'center'})
    worksheet_dash.write('C6', 'إجمالي الإيرادات:', header_format)
    worksheet_dash.write('D6', total_rev, money_format)
    worksheet_dash.write('C7', 'إجمالي رواتب المناديب:', header_format)
    worksheet_dash.write('D7', total_cost, money_format)
    worksheet_dash.write('C8', 'الربح الصافي للشركة:', header_format)
    worksheet_dash.write('D8', total_profit, money_format)

    # إضافة رسم بياني دائري (Pie Chart) يوضح توزيع الأموال
    pie_chart = workbook_obj.add_chart({'type': 'pie'})
    pie_chart.add_series({
        'name': 'توزيع المبالغ',
        'categories': ['📊 لوحة القيادة (Dashboard)', 6, 2, 7, 2],
        'values':     ['📊 لوحة القيادة (Dashboard)', 6, 3, 7, 3],
        'points': [{'fill': {'color': '#10B981'}}, {'fill': {'color': '#EF4444'}}],
    })
    pie_chart.set_title({'name': 'نسبة الأرباح مقابل المصروفات'})
    worksheet_dash.insert_chart('F6', pie_chart, {'x_offset': 25, 'y_offset': 10})

    # رسم بياني عمودي لأفضل المناديب إنتاجية (Bar Chart)
    if len(df) > 0 and 'اسم المندوب' in df.columns and 'الطلبات المحققة' in df.columns:
        bar_chart = workbook_obj.add_chart({'type': 'column'})
        max_row = len(df) + 1
        name_col_idx = chr(65 + df.columns.get_loc('اسم المندوب'))
        order_col_idx = chr(65 + df.columns.get_loc('الطلبات المحققة'))
        
        bar_chart.add_series({
            'name':       'الشحنات المحققة',
            'categories': f'=\'البيانات التفصيلية\'!${name_col_idx}$2:${name_col_idx}${max_row}',
            'values':     f'=\'البيانات التفصيلية\'!${order_col_idx}$2:${order_col_idx}${max_row}',
            'fill':       {'color': '#38BDF8'},
        })
        bar_chart.set_title({'name': 'إنتاجية المناديب'})
        bar_chart.set_x_axis({'name': 'اسم المندوب'})
        bar_chart.set_y_axis({'name': 'عدد الشحنات'})
        worksheet_dash.insert_chart('B20', bar_chart, {'x_scale': 1.5, 'y_scale': 1.2})

    workbook.close()
    return output.getvalue()

# --- 5. واجهة النظام العصرية ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
    html, body, [class*="css"], div, span, p, label { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; }
    .stApp { background-color: #F8FAFC; background-image: linear-gradient(rgba(248, 250, 252, 0.93), rgba(248, 250, 252, 0.93)), url('https://raw.githubusercontent.com/giadomer0-art/Mr-GIAD-FADOL-advanced-logistics-erp/main/1.jpeg'); background-repeat: no-repeat; background-position: center center; background-attachment: fixed; background-size: 550px; }
    .main-header { background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 30px; border-radius: 20px; color: white; box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.2); margin-bottom: 25px; position: relative; overflow: hidden; }
    .main-header::before { content: ""; position: absolute; top: 0; right: 0; width: 8px; height: 100%; background: linear-gradient(180deg, #38BDF8 0%, #EF4444 100%); }
    .main-header h1 { color: #FFFFFF !important; font-weight: 900; font-size: 2.3rem; margin: 0; }
    .metric-card { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px); border-radius: 16px; padding: 22px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border: 1px solid #E2E8F0; transition: all 0.3s ease; }
    .metric-card:hover { transform: translateY(-4px); }
    .metric-title { color: #64748B; font-size: 0.95rem; font-weight: 700; }
    .metric-value { color: #0F172A; font-size: 2rem; font-weight: 900; margin-top: 6px; }
    .card-revenue { border-top: 4px solid #38BDF8; } .card-cost { border-top: 4px solid #EF4444; } .card-profit { border-top: 4px solid #10B981; } .card-orders { border-top: 4px solid #1E293B; }
    .stDownloadButton>button { width: 100%; background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important; color: white !important; font-weight: 800 !important; font-size: 1.2rem !important; border-radius: 14px !important; border: none !important; padding: 16px 24px !important; box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3) !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>📊 المنظومة المالية والتشغيلية الشاملة</h1><p>شركة الحلول المتقدمة للخدمات اللوجستية | Advanced Logistics Solutions</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://raw.githubusercontent.com/giadomer0-art/Mr-GIAD-FADOL-advanced-logistics-erp/main/1.jpeg", width=160)
    st.markdown("## ⚙️ إعدادات النظام")
    selected_client = st.radio("اختر العميل المراد حسابه:", ["Supermall", "Ninja (نينجا)", "Kita (كيتا)", "HungerStation (هنقرستيشن)"], index=0)
    st.divider()
    st.caption("نظام الحسابات الذكي الموحد v28.0 (Multi-Format & Dashboards)")

# ----------------- 6. دوال العمليات المالية -----------------
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

# ----------------- 7. منطقة الرفع الذكية (تقبل كل الصيغ) -----------------
st.markdown(f"### 📂 مركز التحليل الذكي لمشروع: `{selected_client}`")
st.info("💡 يمكنك الآن رفع ملفات بصيغ: (Excel, CSV, PDF, Word, أو صور). سيقوم الذكاء باستخراج الجداول منها.")

col1, col2, col3 = st.columns(3)
# تحديث نوع الملفات المسموحة في أداة الرفع
allowed_types = ['xlsx', 'xls', 'csv', 'pdf', 'docx', 'png', 'jpg', 'jpeg']
with col1: perf_file = st.file_uploader("1. تقرير الأداء", type=allowed_types, key="u1")
with col2: agent_info_file = st.file_uploader("2. بيانات المناديب", type=allowed_types, key="u3")
with col3: car_fuel_file = st.file_uploader("3. استهلاك البنزين", type=allowed_types, key="u2")

if perf_file and agent_info_file and car_fuel_file:
    with st.spinner('⏳ جاري التحليل واستخراج البيانات بذكاء...'):
        try:
            # استخدام محرك القراءة الذكي
            df_perf = smart_read_file(perf_file)
            df_agents = smart_read_file(agent_info_file)
            df_cars = smart_read_file(car_fuel_file)

            if df_perf.empty or df_agents.empty:
                st.warning("تعذر قراءة الجداول من الملفات المرفوعة. يرجى التأكد من محتواها أو استخدام صيغة Excel.")
            else:
                # تنظيف الأعمدة والدمج
                for col in df_agents.columns:
                    if str(col).strip() in ['رقم الإقامة', 'Iqama', 'رقم الاقامة']: df_agents.rename(columns={col: 'Iqama'}, inplace=True)
                
                if 'Iqama' in df_perf.columns: df_perf['Iqama_Clean'] = df_perf['Iqama'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                if 'Iqama' in df_agents.columns: df_agents['Iqama_Clean'] = df_agents['Iqama'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

                df_agents['agent_full_text'] = df_agents.apply(lambda r: " ".join(str(v).lower() for v in r.values).replace('ة', 'ه'), axis=1)

                if 'Iqama_Clean' in df_perf.columns and 'Iqama_Clean' in df_agents.columns:
                    df_merged = pd.merge(df_perf, df_agents, on='Iqama_Clean', how='left', suffixes=('', '_agent'))
                else:
                    df_merged = df_perf.copy()

                # معالجة البنزين
                driver_col_fuel = 'السائقين المعينين للمركبة' if 'السائقين المعينين للمركبة' in df_cars.columns else ('اسم السائق' if 'اسم السائق' in df_cars.columns else None)
                cost_col_fuel = 'إجمالي المبلغ المستخدم' if 'إجمالي المبلغ المستخدم' in df_cars.columns else ('القيمة' if 'القيمة' in df_cars.columns else None)
                liters_col_fuel = 'عدد اللترات' if 'عدد اللترات' in df_cars.columns else None

                if driver_col_fuel and cost_col_fuel:
                    df_cars[cost_col_fuel] = pd.to_numeric(df_cars[cost_col_fuel], errors='coerce').fillna(0)
                    df_cars['Clean_Fuel_Name'] = df_cars[driver_col_fuel].apply(norm_text)
                    fuel_agg = df_cars.groupby('Clean_Fuel_Name', as_index=False).agg({cost_col_fuel: 'sum'})
                    
                    name_col = 'اسم المندوب' if 'اسم المندوب' in df_merged.columns else ('Username' if 'Username' in df_merged.columns else None)
                    if name_col:
                        df_merged['Clean_Agent_Name'] = df_merged[name_col].apply(norm_text)
                        df_merged = pd.merge(df_merged, fuel_agg, left_on='Clean_Agent_Name', right_on='Clean_Fuel_Name', how='left')
                        df_merged['مخصص البنزين'] = df_merged[cost_col_fuel].fillna(0)
                else:
                    df_merged['مخصص البنزين'] = 0

                date_cols = [c for c in df_perf.columns if 'Delivered' in c and c != 'Grand Total Delivered']
                report_days = len(date_cols) if len(date_cols) > 0 else 30

                orders_col = 'Grand Total Delivered' if 'Grand Total Delivered' in df_merged.columns else 'الطلبات الناجحة'
                df_merged['الطلبات المحققة'] = pd.to_numeric(df_merged[orders_col], errors='coerce').fillna(0)

                # الإيرادات
                if selected_client == "Supermall": df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'].apply(calc_supermall_revenue)
                elif selected_client == "Ninja (نينجا)": df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'].apply(calc_ninja_revenue)
                else: df_merged['إيراد الشركة من العميل'] = df_merged['الطلبات المحققة'] * 6 # Default fallback

                def calc_agent_dues_final(row):
                    orders = row['الطلبات المحققة']
                    row_str = str(row.get('agent_full_text', ''))
                    is_freelance = True if selected_client == "Ninja (نينجا)" else (('فري' in row_str) or ('freelance' in row_str) or ('حر' in row_str))
                    
                    salary = calc_salary_by_project(orders, selected_client, is_freelance)
                    car_rent = get_smart_car_allowance(row_str, report_days)
                    return pd.Series(['فري لانسر' if is_freelance else 'كفالة', salary, car_rent, salary + car_rent])

                df_merged[['نوع المندوب', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب']] = df_merged.apply(calc_agent_dues_final, axis=1)
                df_merged['ربح الشركة الصافي'] = df_merged['إيراد الشركة من العميل'] - df_merged['إجمالي المستحق للمندوب'] - df_merged['مخصص البنزين']
                
                if 'Iqama' in df_merged.columns: df_merged.rename(columns={'Iqama': 'رقم الإقامة'}, inplace=True)

                # --- 8. واجهة العرض والتصدير المودرن ---
                rev_val = df_merged['إيراد الشركة من العميل'].sum()
                cost_val = df_merged['إجمالي المستحق للمندوب'].sum()
                profit_val = df_merged['ربح الشركة الصافي'].sum()
                orders_val = df_merged['الطلبات المحققة'].sum()
                
                st.write("---")
                m1, m2, m3, m4 = st.columns(4)
                with m1: st.markdown(f'<div class="metric-card card-revenue"><div class="metric-title">إيرادات الشركة</div><div class="metric-value">{rev_val:,.2f} <span style="font-size: 1rem;">SAR</span></div></div>', unsafe_allow_html=True)
                with m2: st.markdown(f'<div class="metric-card card-cost"><div class="metric-title">رواتب المناديب</div><div class="metric-value">{cost_val:,.2f} <span style="font-size: 1rem;">SAR</span></div></div>', unsafe_allow_html=True)
                with m3: st.markdown(f'<div class="metric-card card-profit"><div class="metric-title">الربح الصافي</div><div class="metric-value">{profit_val:,.2f} <span style="font-size: 1rem;">SAR</span></div></div>', unsafe_allow_html=True)
                with m4: st.markdown(f'<div class="metric-card card-orders"><div class="metric-title">الشحنات المحققة</div><div class="metric-value">{orders_val:,.0f} <span style="font-size: 1rem;">شحنة</span></div></div>', unsafe_allow_html=True)

                display_cols = ['رقم الإقامة', 'اسم المندوب', 'نوع المندوب', 'الطلبات المحققة', 'مخصص البنزين', 'راتب الإنتاجية', 'بدل السيارة', 'إجمالي المستحق للمندوب', 'إيراد الشركة من العميل', 'ربح الشركة الصافي']
                final_df = df_merged[[c for c in display_cols if c in df_merged.columns]]
                st.write("")
                st.dataframe(final_df, use_container_width=True)

                # زر التصدير العبقري 
                st.download_button(
                    "📥 تصدير الداشبورد المالي (Excel بتصميم عصري ورسوم بيانية)", 
                    data=create_modern_excel(final_df, selected_client), 
                    file_name=f"Advanced_Logistics_Dashboard_{selected_client}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة البيانات: {e}")
