import streamlit as st
import requests
import json

def process_query(nlquery):
    url = 'https://earl.skynet.coypu.org/processQuery'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'nlquery': nlquery})
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': f'Error {response.status_code}: {response.text}'}

# Streamlit UI Styling
st.set_page_config(page_title="Entity Linker UI", page_icon="🔗", layout="centered")
st.markdown("""
    <style>
        .main {background-color: #f4f4f4; padding: 20px; border-radius: 10px;}
        .stTextInput, .stButton > button {border-radius: 5px;}
        .stSubheader {color: #444; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

st.title("🔗 EARL Entity Linker UI")
st.write("Code: https://github.com/AskNowQA/EARL")
st.write("Paper: https://link.springer.com/chapter/10.1007/978-3-030-00671-6_7")
st.write("Enter a natural language query and get linked entities and relations.")

# Input field for query
nlquery = st.text_input("Enter your query:", "Who is the president of Russia?")


if st.button("Process Query"):
    result = process_query(nlquery)
    
    if 'error' in result:
        st.error(result['error'])
    else:
        st.subheader("Extracted Entities and Relations")
        
        if 'chunktext' in result:
            for item in result['chunktext']:
                st.markdown(f"""
                    <div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #fff; margin-bottom: 5px;'>
                        <strong>{item['class'].capitalize()}:</strong> {item['chunk']}
                    </div>
                """, unsafe_allow_html=True)
        
        st.subheader("Reranked Entity and Relation Links")
        
        if 'rerankedlists' in result:
            for key, values in result['rerankedlists'].items():
                st.markdown(f"<h4 style='color: #2c3e50;'>List {key}</h4>", unsafe_allow_html=True)
                for score, uri in values:
                    st.markdown(f"""
                        <div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #eef; margin-bottom: 5px;'>
                            <a href='{uri}' target='_blank' style='color: #2980b9; font-weight: bold;'>{uri}</a> (Score: {score:.4f})
                        </div>
                    """, unsafe_allow_html=True)
