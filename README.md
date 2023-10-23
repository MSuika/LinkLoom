
# LinkLoom

## Overview
LinkLoom is a powerful internal linking tool designed for SEO specialists and webmasters. It streamlines the process of identifying internal linking opportunities by allowing users to upload a CSV file with specified keywords and target pages. Utilizing the Google Custom Search API, LinkLoom searches for these keywords across predefined websites, extracts relevant content, and compiles a list of potential internal linking opportunities. The results can be conveniently downloaded in CSV or XLSX format for further analysis or implementation.

## Features
- **Easy CSV Upload**: Users can upload a CSV file with keywords and target URLs.
- **Google Custom Search Integration**: Performs comprehensive searches using the Google Custom Search API.
- **Content Extraction**: Gathers and filters content where specified keywords are found.
- **Result Compilation**: Allows users to download the search results and potential linking opportunities.

## Requirements
- Python 3.8 or later
- Streamlit
- Pandas
- Requests
- BeautifulSoup
- And other dependencies listed in `requirements.txt`

## Required CSV Format

Your CSV file must contain two columns:
- `target_page`: The URLs of the pages you want to find linking opportunities for.
- `keyword`: The keywords you want to use for finding linking opportunities. Multiple keywords should be separated by commas.

An example template can be found in the `Samples` folder.

## Installation
Clone the repository to your local machine:
```
git clone https://github.com/MSuika/LinkLoom-main.git
```
Navigate to the project directory and install the dependencies:
```
cd LinkLoom
pip install -r requirements.txt
```

## Usage
1. Start the Streamlit app by running the following command in the terminal:
    ```
    streamlit run main.py
    ```
2. Open the app in your web browser and follow the instructions in the sidebar:
    - Upload a CSV file with `target_page` and `keyword` columns.
    - Start proccessing
    - Review the search results and download the data in your preferred format.

## Contributing

We welcome contributions to LinkLoom. If you're interested in contributing, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## Licensing

The code in this project is licensed under the MIT license.

## Support

If you encounter any issues or require support, please raise an issue on the GitHub repository or contact the maintainer at [markassuika@gmail.com](mailto:markassuika@gmail.com).
