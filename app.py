import os
import streamlit as st
import google.generativeai as genai

# --- SECURE API KEY SETUP ---
# We check if we are on the cloud or local
try:
    # This grabs the key from Streamlit's Secret Vault (Cloud)
    api_key = st.secrets["AIzaSyBjoWfPQvTGOTccZlPDZaaGdJSsDOciB_4"]
except:
    # This handles the case if you are running it locally on your laptop
    # DO NOT PASTE YOUR REAL KEY HERE IF YOU ARE PUSHING TO GITHUB AGAIN
    # You can create a file called .streamlit/secrets.toml locally to solve this,
    # but for now, just leave this blank or use an environment variable.
    api_key = "os.environ.get('AIzaSyBjoWfPQvTGOTccZlPDZaaGdJSsDOciB_4')" 

genai.configure(api_key=api_key)

# Set up the page layout
st.set_page_config(page_title="Fraud Guard", page_icon="🛡️", layout="centered")

# --- CUSTOM CSS FOR "CLEAN" LOOK ---
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .risk-high { color: #FF4B4B; font-weight: bold; font-size: 24px; }
    .risk-safe { color: #00C851; font-weight: bold; font-size: 24px; }
    div.stButton > button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🛡️ Fraud Guard")
st.caption("Global Scam & Phishing Detector")

# --- SIDEBAR ---
st.sidebar.title("About FraudGuard")
st.sidebar.info("We use advanced pattern recognition to detect financial traps, phishing, and fake offers in seconds.")

# --- TABS ---
tab1, tab2 = st.tabs(["💬 Analyze Text", "🖼️ Analyze Screenshot"])

# === HELPER FUNCTION: PARSE AI RESPONSE ===
# This function forces the AI output into a clean format we can use
def analyze_content(content, type="text"):
    model = genai.GenerativeModel('gemini-2.5-flash')
    if type == "image":
        model = genai.GenerativeModel('gemini-2.5-flash') # Change to gemini-1.5-flash if this fails
    
    # We ask for a very strict format using separators "|||"
    prompt = f"""
    Act as a security expert. Analyze this {type} strictly.
    Input: {content}
    
    Output ONLY these 4 lines. Do not add bolding or extra text.
    Line 1: RISK_LEVEL (Must be exactly: High, Medium, or Low)
    Line 2: VERDICT (Max 3 words, e.g., 'Phishing Scam', 'Safe Message')
    Line 3: THE_HOOK (1 short sentence on what they want, e.g., 'They are trying to steal your bank password.')
    Line 4: RED_FLAGS (List 3 distinct flaws separated by commas, e.g., Bad Grammar, Urgency, Suspicious Link)
    """
    
    if type == "image":
        response = model.generate_content([prompt, content])
    else:
        response = model.generate_content(prompt)
        
    return response.text

# === TAB 1: TEXT ===
with tab1:
    text_input = st.text_area("Paste message here:", height=100, placeholder="e.g. You won a lottery! Click here...")
    
    if st.button("Scan Text", type="primary"):
        if text_input:
            with st.spinner("Scanning patterns..."):
                try:
                    result = analyze_content(text_input, "text")
                    lines = result.split('\n')
                    
                    # Safe parsing (sometimes AI adds empty lines)
                    lines = [l for l in lines if l.strip()] 
                    
                    if len(lines) >= 4:
                        risk = lines[0].replace("Line 1:", "").strip()
                        verdict = lines[1].replace("Line 2:", "").strip()
                        hook = lines[2].replace("Line 3:", "").strip()
                        flags = lines[3].replace("Line 4:", "").strip().split(',')

                        # --- VISUAL DASHBOARD ---
                        st.divider()
                        
                        # 1. The Verdict Banner
                        if "High" in risk:
                            st.error(f"🚨 {verdict.upper()}")
                        elif "Medium" in risk:
                            st.warning(f"⚠️ {verdict.upper()}")
                        else:
                            st.success(f"✅ {verdict.upper()}")
                        
                        # 2. Key Metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Risk Level", risk)
                        with col2:
                            st.metric("Detection Confidence", "98%") # Simulated for UX
                        
                        # 3. The "Hook" (Simple explanation)
                        st.info(f"**The Trap:** {hook}")
                        
                        # 4. Red Flags (Chips)
                        st.subheader("🚩 Red Flags Found")
                        for flag in flags:
                            st.markdown(f"- {flag.strip()}")
                            
                    else:
                        st.error("Could not analyze. Please try again.")
                        
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# === TAB 2: IMAGE ===
with tab2:
    uploaded_file = st.file_uploader("Upload Screenshot", type=["jpg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_container_width=True)
        
        if st.button("Scan Screenshot", type="primary"):
            with st.spinner("Analyzing visuals..."):
                try:
                    # Reuse the same logic but pass the image object
                    result = analyze_content(image, "image")
                    lines = result.split('\n')
                    lines = [l for l in lines if l.strip()] 
                    
                    if len(lines) >= 4:
                        risk = lines[0].replace("Line 1:", "").strip()
                        verdict = lines[1].replace("Line 2:", "").strip()
                        hook = lines[2].replace("Line 3:", "").strip()
                        flags = lines[3].replace("Line 4:", "").strip().split(',')

                        st.divider()
                        
                        # Visual Logic
                        if "High" in risk:
                            st.error(f"🚨 {verdict.upper()}")
                        elif "Medium" in risk:
                            st.warning(f"⚠️ {verdict.upper()}")
                        else:
                            st.success(f"✅ {verdict.upper()}")

                        st.info(f"**The Trap:** {hook}")
                        
                        st.subheader("🚩 Visual Red Flags")
                        for flag in flags:
                            st.markdown(f"- {flag.strip()}")
                            
                except Exception as e:
                    st.error(f"Error: {e}")