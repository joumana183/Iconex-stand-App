import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import pdf2image

# --- 1. الإعدادات والـ API Key ---
# ضعي الـ API Key الخاص بكِ هنا
API_KEY = "YOUR_GEMINI_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Iconex Master Pro", layout="wide", page_icon="💡")

# --- 2. إظهار اللوجو في الواجهة ---
# تأكدي أن الصورة على الديسكتوب اسمها logo.jpg أو logo.png
try:
    # جرب يفتح لوجو بامتداد jpg أو png
    try:
        icon_logo = Image.open("logo.jpg")
    except:
        icon_logo = Image.open("logo.png")
        
    col_l1, col_l2, col_l3 = st.columns([2, 2, 2])
    with col_l2:
        st.image(icon_logo, use_container_width=True)
except:
    st.warning("⚠️ يرجى التأكد من تسمية الصورة 'logo' ووضعها بجانب ملف simulator.py")

st.title("🤖 وكيل Iconex Master المطور")
st.write("التحليل الشامل للتصاميم، المقايسات (PDF)، وتعدد الخامات.")

# --- 3. الشريط الجانبي (Sidebar) ---
st.sidebar.header("📊 إعدادات الأسعار الثابتة")
sheet_w = st.sidebar.number_input("عرض اللوح (متر):", value=1.22)
sheet_h = st.sidebar.number_input("طول اللوح (متر):", value=2.44)
sheet_price = st.sidebar.number_input("سعر اللوح (MDF):", value=1200.0)
plexi_price_factor = st.sidebar.number_input("مضاعف سعر البليكسي (x):", value=2.5)
sheet_area = sheet_w * sheet_h

st.sidebar.divider()
logo_lit_p = st.sidebar.number_input("متر اللوجو المضيء:", value=800.0)
logo_unlit_p = st.sidebar.number_input("متر اللوجو غير المضيء:", value=350.0)
fixed_transport = st.sidebar.number_input("تكلفة النقل الثابتة:", value=500.0)
fixed_labor = st.sidebar.number_input("تكلفة العمالة الثابتة:", value=400.0)
waste_f = st.sidebar.slider("نسبة الهالك (%):", 0, 30, 15) / 100

# --- 4. منطقة رفع الملفات (صور و PDF) ---
st.subheader("📂 رفع التصميم أو ملف PDF")
uploaded_files = st.file_uploader("ارفع الصور أو ملفات المقايسة (PDF)", type=['jpg', 'png', 'jpeg', 'pdf'], accept_multiple_files=True)

if "extracted_data" not in st.session_state: 
    st.session_state.extracted_data = {"w": 150.0, "h": 300.0, "p": 1}

input_data_list = []
if uploaded_files:
    for uploaded_file in uploaded_files:
      if uploaded_file.type == "application/pdf":
            try:
                # هنا السيرفر سيتعامل مع الـ PDF تلقائياً بدون كتابة مسارات
                images = pdf2image.convert_from_bytes(uploaded_file.read())
                img = images[0]
                st.image(img, caption=f"PDF: {uploaded_file.name}", use_container_width=True)
                input_data_list.append(img)
            except Exception as e:
                st.error(f"خطأ في قراءة الـ PDF: {e}")
        else:
            img = Image.open(uploaded_file)
            st.image(img, caption=uploaded_file.name, use_container_width=True)
            input_data_list.append(img)

    if st.button("🔍 تحليل الملفات بالذكاء الاصطناعي"):
        if input_data_list:
            with st.spinner("جاري استخراج البيانات..."):
                try:
                    response = model.generate_content(["Extract Width (cm), Height (cm). Return ONLY: w, h", input_data_list[0]])
                    w, h = response.text.strip().split(',')
                    st.session_state.extracted_data["w"] = float(w)
                    st.session_state.extracted_data["h"] = float(h)
                    st.success("تم التحديث!")
                except:
                    st.error("يرجى مراجعة الـ API Key أو البيانات.")

# --- 5. الحسابات النهائية ---
st.subheader("📏 مدخلات المقايسة النهائية")
c1, c2, c3, c4 = st.columns(4)
width = c1.number_input("العرض (سم):", value=st.session_state.extracted_data["w"])
height = c2.number_input("الارتفاع (سم):", value=st.session_state.extracted_data["h"])
lit_m = c3.number_input("لوجو مضيء (متر):", value=1.0)
unlit_m = c4.number_input("لوجو غير مضيء (متر):", value=0.0)

material_type = st.selectbox("نوع الخامة:", ["أخشاب MDF", "أكريليك/بليكسي"])

if st.button("🖩 احسب"):
    area_m2 = (width / 100) * (height / 100)
    total_wood_m2 = area_m2 * 2.5 * (1 + waste_f)
    num_sheets = total_wood_m2 / sheet_area
    
    current_price = sheet_price if material_type == "أخشاب MDF" else sheet_price * plexi_price_factor
    final_cost = (num_sheets * current_price) + (lit_m * logo_lit_p) + (unlit_m * logo_unlit_p) + fixed_transport + fixed_labor
    
    st.divider()
    st.metric(label=f"الإجمالي ({material_type})", value=f"{final_cost:,.2f} EGP")
    st.balloons()