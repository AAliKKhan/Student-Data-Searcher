import streamlit as st
import pandas as pd
import pdfplumber
from io import BytesIO

def parse_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            tables = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    # Get headers from first row
                    headers = [cell.strip() if cell else '' for cell in table[0]]
                    # Process remaining rows
                    data = []
                    for row in table[1:]:
                        clean_row = [str(cell).strip() if cell else '' for cell in row]
                        if any(clean_row):  # Skip empty rows
                            data.append(clean_row)
                    if data:
                        tables.append(pd.DataFrame(data, columns=headers))
        return pd.concat(tables) if tables else pd.DataFrame()
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")
        return pd.DataFrame()

# Main app
st.header("Developed By Ali Adnan")
st.title("Student Data Processor ")

# File upload section
st.header("📤 Upload Student Data Files")
uploaded_files = st.file_uploader(
    "Choose files (CSV, Excel, JSON, PDF)",
    type=["csv", "xlsx", "json", "pdf"],
    accept_multiple_files=True
)

# Process uploaded files
combined_df = pd.DataFrame()
if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            if file_type == "csv":
                df = pd.read_csv(uploaded_file, dtype=str)
            elif file_type == "xlsx":
                df = pd.read_excel(uploaded_file, dtype=str)
            elif file_type == "json":
                df = pd.read_json(uploaded_file, dtype=str)
            elif file_type == "pdf":
                df = parse_pdf(BytesIO(uploaded_file.read()))
            
            # Standardize column names
            df.columns = [col.strip().title() for col in df.columns]
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")

# Display example data format
st.header("📝 Expected Data Format")
example_data = {
    "Roll No": [1, 2, 3, 4],
    "Name": ["ALI", "SANA", "AHMED", "FATIMA"],
    "Father Name": ["Adnan", "Usman", "Zubair", "Kamran"],
    "D.O.B": ["9/6/2007", "15/3/2008", "22/11/2007", "5/5/2009"],
    "Gender": ["Male", "Female", "Male", "Female"],
    "Section": ["F", "A", "B", "C"]
}
example_df = pd.DataFrame(example_data)
st.table(example_df)

# Search functionality
st.header("🔍 Search Students")
search_method = st.selectbox(
    "Search by:",
    ["Roll No", "Name", "Father Name", "Gender"],
    index=0
)

search_term = st.text_input("Enter search term:").strip()

if search_term:
    if combined_df.empty:
        st.warning("⚠️ No data loaded - please upload files first")
    else:
        # Clean and prepare data for search
        combined_df = combined_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        search_col = search_method.title()
        
        try:
            # Case-insensitive search
            results = combined_df[
                combined_df[search_col].astype(str).str.lower() == search_term.lower()
            ]
            
            if not results.empty:
                st.success(f"✅ Found {len(results)} matching records:")
                st.dataframe(results.reset_index(drop=True))
            else:
                st.warning("⛔ No matching records found")
        except KeyError:
            st.error(f"❌ Column '{search_col}' not found in uploaded data")