# OECD Data Dashboard

This repository provides a web-based dashboard built with Dash and Plotly to explore and visualize OECD data. The project comprises multiple Python scripts that fetch, process, and display data from the OECD's SDMX API in an interactive format, allowing users to select various datasets and visualize them using different chart types.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Scripts Overview](#scripts-overview)
6. [Contributing](#contributing)
7. [License](#license)

---

## Project Overview

The OECD Data Dashboard is a tool that leverages data from the OECD's SDMX API to provide an interactive interface for visualizing economic and statistical data. Users can choose from various datasets, apply filters, and view the data using different types of charts, including line, scatter, and bar charts. The dashboard includes support for filtering data by year range and other dimensions, and it also offers an option to add a regression line for scatter plots.

---

## Features

- **Interactive Dashboard**: Built using Dash and Plotly, offering an intuitive UI for exploring datasets.
- **Dynamic Controls**: Automatically generated dropdowns and sliders based on the selected dataset.
- **Multiple Chart Types**: Line charts, scatter plots, and bar charts with customizable options.
- **Regression Line Option**: Add a linear regression trendline to scatter plots.
- **Data Fetching and Parsing**: Uses the OECD SDMX API to fetch and parse datasets dynamically.
- **Retry Logic for API Requests**: Handles API failures with retry mechanisms and exponential backoff.

---

## Installation

To run the project, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/oecd-data-dashboard.git
   cd oecd-data-dashboard
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download Datasets**:
   The script will automatically create a folder called `01 - Datasets` and download datasets from the OECD API when you run the data-fetching scripts.

---

## Usage

1. **Run the Dashboard**:
   - Use the `plot_dashboard_oecd_data.py` script to start the Dash app:
     ```bash
     python plot_dashboard_oecd_data.py
     ```
   - Open your browser and navigate to `http://127.0.0.1:8050` to view the dashboard.

2. **Fetch and Save OECD Data**:
   - The script `fetch_oecd_data.py` downloads datasets from the OECD API and saves them as CSV files.
   - The `fetch_oecd_agencies.py` script retrieves a list of available dataflows and agency identifiers.

3. **Customize Visualizations**:
   - Use the dropdown menus and controls to customize the charts, select different datasets, and apply filters.

---

## Scripts Overview

### 1. **plot_dashboard_oecd_data.py**
   - Main script that sets up the Dash dashboard.
   - Defines the layout and callbacks to generate dynamic controls and update the graph based on user input.

### 2. **fetch_oecd_data.py**
   - Fetches and parses OECD data using the SDMX API.
   - Handles complex JSON structures to extract dimensions and observations.

### 3. **fetch_oecd_agencies.py**
   - Retrieves a list of available OECD dataflows and agency identifiers.
   - Includes retry logic for handling API failures.

### 4. **write_csv.py**
   - Saves fetched data to CSV files in the `01 - Datasets` folder.
   - Uses `tqdm` to display a progress bar while saving data row by row.

---

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgements

- **OECD SDMX API**: For providing access to a rich set of economic and statistical data.
- **Dash**: For building the interactive dashboard.
- **Plotly**: For data visualization.
- **tqdm**: For the progress bar functionality.

---

Feel free to customize this `README.md` to better fit your project structure and details.
