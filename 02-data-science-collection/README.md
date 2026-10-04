# Data Science Collection

Data science practice projects from my data analytics learning path: collecting data from APIs and web pages, cleaning it, exploring it with SQL, charts, and maps, and building simple prediction models. The main project is the SpaceX Falcon 9 landing prediction capstone in `SpaceX Project/`.

## What you'll use

- Python 3 with Jupyter (JupyterLab or Notebook)
- pandas, NumPy, requests, BeautifulSoup (`bs4`), matplotlib, seaborn, scikit-learn
- folium and wget for the map notebook
- ipython-sql and `ibm_db_sa` with an IBM Db2 on Cloud instance for the SQL notebook
- yfinance and Plotly for the stock notebooks
- Dash and Plotly for the two dashboards (`SpaceX Project/spacex_dash_app.py` and `Airline Analysis.py`)

## Prerequisites

- An internet connection. The notebooks call the SpaceX REST API, scrape web pages, pull stock data, and read course datasets from IBM's cf-courses-data bucket.
- For the SQL notebook only: a Db2 on Cloud service and its service credentials.

## Steps

### Part 1: Set up

1. Install the packages.

   ```bash
   pip install jupyterlab pandas numpy requests beautifulsoup4 matplotlib seaborn scikit-learn folium wget ipython-sql ibm_db_sa yfinance plotly dash
   ```

2. Start Jupyter in this folder.

   ```bash
   jupyter lab
   ```

### Part 2: SpaceX Falcon 9 landing prediction (`SpaceX Project/`)

Run these in order. Each notebook builds on the output of the one before.

3. Open `Data Collection API.ipynb` and run all cells. It requests past launches from `https://api.spacexdata.com/v4/launches/past`, looks up the booster, launch pad, payload, and core details, keeps only Falcon 9 launches, and fills missing payload masses with the mean.

   Expected result: the notebook writes `dataset_part_1.csv`.

4. Open `Data Collection with Web Scraping.ipynb` and run all cells. It parses the launch tables on a fixed revision of the Wikipedia page "List of Falcon 9 and Falcon Heavy launches" with BeautifulSoup.

   Expected result: the notebook writes `spacex_web_scraped.csv` with flight number, date, booster version, launch site, payload, payload mass, orbit, customer, launch outcome, and booster landing.

5. Open `Data Wrangling.ipynb` and run all cells. It counts launches per site and per orbit and turns the landing outcomes into a `Class` column (1 for a successful landing, 0 for a failure).

   Expected result: the notebook writes `dataset_part_2.csv`.

6. Open `EDA with SQL.ipynb`. Load the SpaceX CSV into a Db2 table with the Db2 console's Load Data tool (turn off data type detection, use the DD-MM-YYYY date format, and set the payload mass column to INTEGER). Then put your own connection details into the `%sql` cell, in this form:

   ```text
   %sql ibm_db_sa://<username>:<password>@<hostname>:<port>/<db-name>?security=SSL
   ```

   Expected result: the queries return the unique launch sites, payload totals for NASA (CRS), the first successful ground-pad landing, and landing outcome counts by date range.

7. Open `EDA with Data Visualization.ipynb` and run all cells. It plots flight number, payload mass, and orbit against landing success and one-hot encodes the features.

   Expected result: 7 charts render, including the yearly success-rate trend, and the notebook writes `dataset_part_3.csv`.

8. Open `Interactive Visual Analytics with Folium.ipynb` and run all cells.

   Expected result: a map marks VAFB SLC-4E in California and the Cape Canaveral sites in Florida, groups launches into clusters (green pins for successful landings, red for failures), and draws a line from a launch site to the nearest coastline with its distance.

9. Put the course file `spacex_launch_dash.csv` in `SpaceX Project/`, then start the dashboard.

   ```bash
   cd "SpaceX Project"
   python3 spacex_dash_app.py
   ```

   Expected result: Dash serves the "SpaceX Launch Records Dashboard" at `http://127.0.0.1:8050`. The site dropdown updates the success pie chart, and the payload range slider (0 to 10,000 kg) updates the payload versus outcome scatter chart.

10. Open `Machine Learning Prediction.ipynb` and run all cells. It standardizes the features, splits training and test sets, and tunes logistic regression, SVM, decision tree, and k-nearest neighbors with `GridSearchCV`.

    Expected result: each model prints its best parameters and test accuracy, and 4 confusion matrices render.

### Part 3: Other practice projects

11. Run `Tesla Stock.ipynb` and `Tesla Stock Scraping.ipynb`. They pull TSLA price history with yfinance, scrape Tesla revenue with requests and BeautifulSoup, and chart both with Plotly.

    Expected result: each notebook shows a 2-panel chart of share price and revenue over time.

12. Run `Netflix V Amazon Stock.ipynb`. It reads course-hosted stock price pages for Netflix and Amazon with requests, BeautifulSoup, and `pandas.read_html` and turns them into DataFrames to compare. The file `Netflix V Amazon` (no extension) is a second version of the same notebook; open it in Jupyter the same way.

13. Run `Real Estate House Sales King County.ipynb` (a second version is in `SpaceX Project/House Sales in King County, USA.ipynb`). It explores King County, Washington home prices with seaborn and fits linear, polynomial, and ridge regression models with scikit-learn.

    Expected result: 2 charts render and each model prints its R² score.

14. Start the airline dashboard.

    ```bash
    python3 "Airline Analysis.py"
    ```

    Expected result: the "US Domestic Airline Flights Performance" page opens at `http://127.0.0.1:8050`. Pick a report type (Yearly Airline Performance Report or Yearly Airline Delay Report) and a year from 2005 to 2020 to draw the charts.

## What I learned

- Collecting data from REST APIs, HTML tables, and stock data libraries, and turning it into clean CSVs.
- Exploring data with SQL, seaborn charts, and Folium maps before modeling.
- Building interactive dashboards with Dash callbacks.
- Training, tuning, and comparing classification and regression models in scikit-learn.

## Next steps / cleanup

- The polished version of the SpaceX capstone, with its slide deck, is in [SpaceX Falcon-9](../03-spacex-falcon-9/).
- Delete or pause your Db2 on Cloud instance when you finish the SQL notebook.
