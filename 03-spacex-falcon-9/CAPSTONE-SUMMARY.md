# SpaceX Falcon 9 Capstone: Summary

A written summary of the capstone presentation (October 2022). The notebooks in this folder hold the code and the charts.

## Executive summary

SpaceX lists a Falcon 9 launch at about 62 million dollars, while other providers charge upward of 165 million, mostly because SpaceX reuses the first stage. If you can predict whether the first stage lands, you can estimate the cost of a launch, which helps a competitor bid against SpaceX. The goal was a machine learning pipeline that predicts a successful first-stage landing.

Questions the project set out to answer:

- Which factors decide whether the first stage lands?
- How do those features interact to affect the landing success rate?
- What operating conditions support a reliable landing program?

## Methodology

1. Collect launch data from the SpaceX REST API and from Wikipedia's Falcon 9 launch tables.
2. Wrangle the data and one-hot encode the categorical features.
3. Explore the data with SQL and with charts.
4. Build interactive views with a Folium map and a Plotly Dash dashboard.
5. Build, tune, and evaluate classification models.

## Data collection

- API: a GET request to the SpaceX API, decoded with `.json()` and flattened into a pandas DataFrame with `json_normalize()`. Missing values were checked and filled where needed.
- Web scraping: BeautifulSoup pulled the Falcon 9 launch records HTML table from Wikipedia, parsed it, and converted it to a DataFrame.

## Data wrangling

- Counted launches per launch site and the number of launches to each orbit.
- Built the training label (landing outcome) from the outcome column and exported the result to CSV.

## Exploratory data analysis

Findings from the charts:

- Flight number vs. launch site: the more flights a site has flown, the higher its success rate.
- Success rate by orbit: ES-L1, GEO, HEO, SSO, and VLEO had the highest success rates.
- Flight number vs. orbit: in LEO, success tracks the number of flights. In GTO there is no relationship between flight number and success.
- Payload vs. orbit: with heavy payloads, successful landings are more common for PO, LEO, and ISS orbits.
- Yearly trend: the success rate rose steadily from 2013 to 2020.

Findings from SQL (the data was loaded into a SQL database from inside the notebook):

- `DISTINCT` listed the unique launch sites, and a filter showed 5 records for sites starting with `CCA`.
- Total payload carried by boosters for NASA (CRS): 45,596 kg.
- Average payload carried by booster version F9 v1.1: 2,928.4 kg.
- First successful ground pad landing: 22 December 2015.
- Other queries listed boosters that landed on a drone ship with a payload between 4,000 and 6,000 kg, counted successful and failed mission outcomes, found the boosters that carried the maximum payload (subquery with `MAX()`), listed the failed drone ship landings in 2015 with booster version and launch site, and ranked landing outcomes between 2010-06-04 and 2017-03-20 by count in descending order.

## Interactive map and dashboard

Folium map:

- Marked every launch site, with color-coded marker clusters for successful (class 1) and failed (class 0) launches, which shows which sites have higher success rates.
- Measured distances from a launch site to nearby railways, highways, coastlines, and cities to see how sites are placed relative to them.

Plotly Dash dashboard:

- A pie chart of the success share achieved by each launch site, and a pie chart for the site with the highest launch success ratio.
- A scatter plot of payload mass (kg) vs. launch outcome, colored by booster version, with a range slider to filter payload.
- Per the conclusions, KSC LC-39A had the most successful launches of any site.

## Predictive analysis and results

- Loaded and transformed the data with NumPy and pandas, then split it into training and test sets.
- Trained several classifiers and tuned their hyperparameters with `GridSearchCV`, using accuracy as the metric.
- The decision tree classifier had the highest classification accuracy.
- Its confusion matrix shows it separates the two classes. The main weakness is false positives: some failed landings were predicted as successful.

## Conclusion

- Launch sites with more flights have higher success rates.
- The launch success rate increased from 2013 to 2020.
- Orbits ES-L1, GEO, HEO, SSO, and VLEO had the highest success rates.
- KSC LC-39A had the most successful launches of any site.
- The decision tree classifier was the best model for this task.
