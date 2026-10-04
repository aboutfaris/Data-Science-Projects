# SpaceX Falcon-9

SpaceX lists a Falcon 9 launch at about 62 million dollars, while other providers charge 165 million dollars or more, mostly because SpaceX reuses the first stage. This capstone predicts whether the first stage will land, which is a good proxy for the cost of a launch.

Questions the project answers:

- How do payload mass, launch site, number of flights, and orbit affect landing success?
- Does the landing success rate improve over the years?
- Which classification algorithm works best for this binary prediction?

## What you'll use

- Python 3 with Jupyter (JupyterLab or Notebook)
- pandas, NumPy, requests, BeautifulSoup (`bs4`), matplotlib, seaborn, scikit-learn
- folium and wget for the map notebook
- ipython-sql and `ibm_db_sa` with an IBM Db2 on Cloud instance for the SQL notebook
- Dash and Plotly for the dashboard (`spacex_dash_app.py`)

## Prerequisites

- An internet connection. The notebooks call the SpaceX REST API, scrape Wikipedia, and read the course datasets from IBM's cf-courses-data bucket.
- For the SQL notebook only: a Db2 on Cloud service and its service credentials.

## Steps

Run the notebooks in this order. Each one builds on the output of the one before.

### Part 1: Collect the data

1. Install the packages.

   ```bash
   pip install jupyterlab pandas numpy requests beautifulsoup4 matplotlib seaborn scikit-learn folium wget ipython-sql ibm_db_sa dash plotly
   ```

2. Start Jupyter in this folder.

   ```bash
   jupyter lab
   ```

3. Open `Data Collection API.ipynb` and run all cells. It requests past launches from `https://api.spacexdata.com/v4/launches/past`, looks up the booster, launch pad, payload, and core details for each launch, keeps only Falcon 9 launches, and fills missing payload masses with the mean.

   Expected result: the notebook writes `dataset_part_1.csv`.

4. Open `Data Collection with Web Scraping.ipynb` and run all cells. It downloads a fixed revision of the Wikipedia page "List of Falcon 9 and Falcon Heavy launches", parses the launch tables with BeautifulSoup, and builds a DataFrame with flight number, date, booster version, launch site, payload, payload mass, orbit, customer, launch outcome, and booster landing.

   Expected result: the notebook writes `spacex_web_scraped.csv`.

### Part 2: Clean and explore

5. Open `Data Wrangling.ipynb` and run all cells. It counts launches per site and per orbit, then turns the landing outcomes into a `Class` column (1 for a successful landing, 0 for a failure).

   Expected result: the notebook writes `dataset_part_2.csv`.

6. Open `EDA with SQL.ipynb`. Load the SpaceX CSV into a Db2 table with the Db2 console's Load Data tool (turn off data type detection, use the DD-MM-YYYY date format, and set the payload mass column to INTEGER). Then put your own connection details into the `%sql` cell, in this form:

   ```text
   %sql ibm_db_sa://<username>:<password>@<hostname>:<port>/<db-name>?security=SSL
   ```

   Expected result: the queries return the unique launch sites, payload totals for NASA (CRS), the first successful ground-pad landing, and the landing outcome counts by date range.

7. Open `EDA with Data Visualization.ipynb` and run all cells. It plots flight number, payload mass, and orbit against landing success with seaborn and matplotlib, and one-hot encodes the features.

   Expected result: 7 charts render, including the yearly success-rate trend, and the notebook writes `dataset_part_3.csv`.

### Part 3: Map and dashboard

8. Open `Interactive Visual Analytics with Folium.ipynb` and run all cells.

   Expected result: a map marks VAFB SLC-4E in California and the Cape Canaveral sites in Florida, groups launches into clusters (green pins for successful landings, red for failures), and draws a line from a launch site to the nearest coastline with its distance.

9. Put the course file `spacex_launch_dash.csv` in this folder, then start the dashboard.

   ```bash
   python3 spacex_dash_app.py
   ```

   Expected result: Dash serves the "SpaceX Launch Records Dashboard" at `http://127.0.0.1:8050`. Choose All Sites or one site from the dropdown to update the success pie chart, and drag the payload range slider (0 to 10,000 kg) to update the payload versus outcome scatter chart.

### Part 4: Predict

10. Open `Machine Learning Prediction.ipynb` and run all cells. It standardizes the features, splits the data into training and test sets, and tunes logistic regression, SVM, decision tree, and k-nearest neighbors with `GridSearchCV`.

    Expected result: each model prints its best parameters and test accuracy, and 4 confusion matrices render so you can compare the models.

A written summary of the capstone presentation and its results is in [CAPSTONE-SUMMARY.md](./CAPSTONE-SUMMARY.md).

## What I learned

- Pulling data from a REST API and from HTML tables, and joining both into one clean dataset.
- Using SQL, charts, and maps to find the features that matter before modeling.
- Building a small interactive dashboard with Dash callbacks.
- Tuning and comparing classifiers with cross-validated grid search.
