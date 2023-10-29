import streamlit as st
import pandas as pd
import base64
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
from io import BytesIO

# Globla varialbes

FORBIDDEN_WORDS = ['Read topic', 'inContact', 'Contact', 'Portal', 'Log in', 'Sales', 'Home', 'Learning Center', 'TOP TOPICS']
example_data = {
    'target_page': ['https://example.com/fruits/', 'https://example.com/vegetables/'],
    'keyword': ['orange, apple', 'tomato']
}
example_df = pd.DataFrame(example_data)

def calculate_cost_from_uploaded_file(uploaded_file):
    COST_PER_QUERY = 0.004740499
    FREE_KEYWORDS_LIMIT = 5
    
    if uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1]
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_extension == "xlsx":
            df = pd.read_excel(uploaded_file)


    
    keywords = df['keyword'].str.split(',').explode().str.strip()
    
    total_keywords = len(keywords)
    
    if total_keywords <= FREE_KEYWORDS_LIMIT:
        total_cost = 0
    else:
        total_cost = (total_keywords - FREE_KEYWORDS_LIMIT) * COST_PER_QUERY
    
    return total_keywords, total_cost

def process_uploaded_file(uploaded_file):
    link = None
    uploaded_file.seek(0)
    if uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1]
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_extension == "xlsx":
            df = pd.read_excel(uploaded_file)

    first_row = df.iloc[0]
    domain = urlparse(first_row['target_page']).netloc

    results_df = pd.DataFrame()

    for index, row in df.iterrows():
        keywords = [k.strip() for k in row['keyword'].split(',')]
        url_to_keyword = {}

        for keyword in keywords:
            try:
                query = f"site:{domain} {keyword} -inurl:{row['target_page']}"
                results = search(query, st.session_state['api_key'], st.session_state['cse_id'])
                link_list = [result['link'] for result in results.get('items', []) if 'link' in result]

                if not link_list:
                    print(f"No linking opportunities found for keyword: {keyword}")
                    st.info(f"No linking opportunities found for keyword: {keyword}") 
                    continue

                for link in link_list:
                    if link and link not in url_to_keyword:
                        if has_link_to_target(link, row['target_page']):
                            continue
                        text = get_page_text(link)
                        context, context_url = find_keyword_in_text(link, text, keyword)
                        if any(word in context for word in FORBIDDEN_WORDS) or context_url == '':
                            continue
                        url_to_keyword[link] = keyword
                        new_row = pd.DataFrame({
                            'keyword': [keyword],
                            'URL': [link],
                            'context': [context],
                            'context_url': [context_url],
                            'target_page': [row['target_page']]
                        })
                        results_df = pd.concat([results_df, new_row], ignore_index=True)
                        print(f"Successful request for keyword: {keyword}, URL: {link}")
            except Exception as e:
                st.error("An unexpected error occurred: " + str(e))
    return results_df

def has_link_to_target(search_result_url, target_page):
    response = requests.get(search_result_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for a_tag in soup.body.find_all('a', href=True):
        if target_page in a_tag['href']:
            return True
    return False

def get_page_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    domain = urlparse(url).netloc

    if soup.body:
        for tag in soup.body(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            tag.decompose()

    return soup.body.get_text() if soup.body else ''

def find_keyword_in_text(url, text, keyword):
    pattern = r'((?:\b\w+\b\s){0,5}\b' + re.escape(keyword) + r'\b\s(?:\b\w+\b\s){0,5})'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        context = match.group()
        encoded_context = quote(context)
        return context, url + '#:~:text=' + encoded_context
    return '', ''

def search(query,api_key,cse_id):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}"
    response = requests.get(url)
    data = json.loads(response.text)
    return data

def display_sidebar_instructions():
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = ''
    if 'cse_id' not in st.session_state:
        st.session_state['cse_id'] = ''

    api_key = st.sidebar.text_input("Enter your API Key", value=st.session_state['api_key'], type="password")
    st.sidebar.markdown(
        "Get Google Custom Search JSON API [here](https://developers.google.com/custom-search/v1/overview).",
        unsafe_allow_html=True,
    )
    cse_id = st.sidebar.text_input("Enter your CSE ID", value=st.session_state['cse_id'], type="password")
    st.sidebar.markdown(
        "Get Custom Search Engine ID [here](https://programmablesearchengine.google.com/controlpanel/create) (Log in needed).",
        unsafe_allow_html=True,
    )
    st.session_state['api_key'] = api_key
    st.session_state['cse_id'] = cse_id

    if st.sidebar.button('Submit'):
        if st.session_state['api_key'] and st.session_state['cse_id']:
            st.sidebar.success('Credentials received. You can now proceed with using the application.')
        else:
            st.sidebar.error('Please enter valid credentials before proceeding.')
            
    st.sidebar.title("How to Use")
    st.sidebar.markdown("1. **Upload a CSV file**")
    st.sidebar.markdown("- Ensure it has two columns: `target_page` and `keyword`.")
    st.sidebar.markdown("- `target_page`: column consists of web pages (URL) to whom we are looking for internal linking opportunites.")
    st.sidebar.markdown("- `keyword`: column consists of target keywords you want to have a link on. Each keyword should be seperated by `,` commas. (can be 1 or more keywords in one row, app will prioritise in sequence)")
    st.sidebar.markdown("2. **Processing**:")
    st.sidebar.markdown("- After uploading, the app will process the CSV. This might take up to minutes depending on the file size.")
    st.sidebar.markdown("3. **Download Results**:")
    st.sidebar.markdown("- Once done, you can download the results.")
    st.sidebar.markdown("- Choose either CSV or XLSX format.")
    st.sidebar.markdown("### Example CSV Format:")
    st.sidebar.table(example_df)

def main():   
    display_sidebar_instructions()
    st.title("LinkLoom - Internal linking tool")
    st.write("Easy way to find **internal linking opportunites** for any website.")
    with st.expander("More about the app"):
        st.write("LinkLoom is a powerful internal linking tool designed for SEO specialists and webmasters. It streamlines the process of identifying internal linking opportunities by allowing users to upload a CSV file with specified keywords and target pages. Utilizing the Google Custom Search API, LinkLoom searches for these keywords across predefined websites, extracts relevant content, and compiles a list of potential internal linking opportunities. The results can be conveniently downloaded in CSV or XLSX format for further analysis or implementation.")
    uploaded_file = uploaded_file = st.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"])

    if uploaded_file:
        total_keywords, total_cost = calculate_cost_from_uploaded_file(uploaded_file)
        st.write(f"Total Keywords: {total_keywords}")
        st.write(f"It roughtly costs you around `€{total_cost:.2f}` to execute this file (Google custom search API pricing).")
        start_processing = st.button("Start Processing")
        if start_processing:
            st.write("Processing... Please wait.")
            st.session_state.button_clicked = True
            try:
                st.session_state.processed_data = process_uploaded_file(uploaded_file)
            except ValueError as e:
                st.error(str(e))

    if 'processed_data' not in st.session_state:
        st.session_state['processed_data'] = None
    if st.button("Reset"):
        st.session_state.processed_data = None
        st.session_state.button_clicked = False
        uploaded_file = None
        st.experimental_set_query_params()

    if st.session_state['processed_data'] is not None:
        st.write("Processing complete! Here are your results:")
        output_df = st.session_state.processed_data

        if not output_df.empty:
            st.write("Download Results:")
            columns = st.columns(2)

            csv_data = output_df.to_csv(index=False)
            b64_csv = base64.b64encode(csv_data.encode()).decode()
            href_csv = f'<a href="data:text/csv;base64,{b64_csv}" download="results.csv">Export as CSV</a>'
            columns[0].markdown(href_csv, unsafe_allow_html=True)

            excel_data = BytesIO()
            with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                output_df.to_excel(writer, index=False, sheet_name='Sheet1')
            b64_xlsx = base64.b64encode(excel_data.getvalue()).decode()
            href_xlsx = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_xlsx}" download="results.xlsx">Export as XLSX</a>'
            columns[1].markdown(href_xlsx, unsafe_allow_html=True)

            st.write("Preview of Downloadable Document:")
            st.dataframe(output_df)
            
if __name__ == "__main__":
    main()
