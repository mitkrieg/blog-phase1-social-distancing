# Do we listen? A exploration of Social Distancing In NYC Parks

**Authors**: Mitch Krieger

## Overview

Using data from NYC Open Data Portal, mapped rates of Parks Patron's encounters with Social Distancing Ambassadors during the COVID-19 pandemic. Using Geopandas, folium and seaborn to generate visualizations, I then wrote a blog about my findings which can be [here found on medium](https://medium.com/swlh/do-we-listen-an-exploration-of-social-distancing-in-nyc-parks-50f9286a65b6).

## Next Steps

For further development of this project I would look into possible trends emerging from grouping the data by the different agencies Ambassadors come from, and take a closer look at smaller parks's individual data. It may also be interesting to try to create a model to predict whether a group listened or not and then extract feature importance. 

## Repository Structure

```
├── README.md           <- The top-level README for reviewers of this project
├── index.ipynb         <- Narrative documentation of project &  processes in Jupyter notebook
├── data_cleaning.py    <- .py script to clean data pulled from the csv files from NYC Open Data Portal and merging of dataframes for analysis
├── Data                <- directory of csv files of datasets used downloaded from NYC Open Data portal
├── Borough Boundaries  <- Shapefiles for NYC's 5 Boroughs
├── .gitattributes      <- git lfs file to help store large notebook 
└── images              <- directory of png verstions of visualizations
```
