# Customer Segmentation by Cohort Analysis and RFM Modelling

##### Capstone Project, Data Science Masters Program (with Simplilearn)
---

## Problem Statement

In the retail Industry, it is a critical requirement for businesses to understand the value derived from their customers. RFM is a method used for analyzing customer value.

Customer segmentation is the practice of segregating the customer base into groups of individuals based on some common characteristics such as age, gender, interests, and spending habits.

Our objective here is to perform customer segmentation using RFM analysis. The resulting segments can be ordered from most valuable (highest recency, frequency, and value) to least valuable (lowest recency, frequency, and value).



### Dataset Description
---

This is a transnational data set which contains all the transactions that occurred between 01/12/2010 and 09/12/2011 for a UK-based and registered non-store online retail. The company mainly sells unique and all-occasion gifts.


**Variables Description**


| Variable | Name | Info |
|:---|:---|:---|
| **InvoiceNo** | Invoice number| Nominal, a 6-digit integral number uniquely assigned to each transaction. If this code starts with letter 'c', it indicates a cancellation | 
| **StockCode** | Product (item) code | Nominal, a 5-digit integral number uniquely assigned to each distinct product |
| **Description** | Product (item) name| Nominal |
| **Quantity** | The quantities of each product (item) per transaction | Numeric |
| **InvoiceDate** | Invice Date and time | Numeric, the day and time when each transaction was generated |
| **UnitPrice** | Unit price | Numeric, Product price per unit in sterling |
| **CustomerID** | Customer number | Nominal, a 5-digit integral number uniquely assigned to each customer |
| **Country** | Country name | Nominal, the name of the country where each customer resides |




#### Project Plan
---

| Milestones | Week | Details |
|:---|:---|:---|
| Data Cleaning & Data Transformation | 1 | 1. Perform a preliminary data inspection and data cleaning.<br>a. Check for missing data and formulate an apt strategy to treat them.<br>b. Remove duplicate data records.<br>c. Perform descriptive analytics on the given data.<br>2. Perform cohort analysis (a cohort is a group of subjects that share a defining characteristic). Observe how a cohort behaves across time and compare it to other cohorts.<br>a. Create month cohorts and analyze active customers for each cohort.<br>b. Analyze the retention rate of customers.<br>3. Goals and Objectives<br>4. Dataset summary |
| Data Modeling: RFM analysis | 2 | 1.1. Build an RFM (Recency Frequency Monetary) model.<br>2. Calculate RFM metrics.<br>3. 3. Build RFM Segments. Give recency, frequency, and monetary scores individually by dividing them into quartiles.<br>a.Combine three ratings to get a RFM segment (as strings).<br>b. Get the RFM score by adding up the three ratings.<br>c. Analyze the RFM segments by summarizing them and comment on the findings.<br> |
| Data Modeling: Kmeans Clustering | 3 | 1. Create clusters using k-means clustering algorithm.<br>a. Prepare the data for the algorithm. If the data is asymmetrically distributed, manage the skewness with appropriate transformation. Standardize the data.<br>b. Decide the optimum number of clusters to be formed.<br>c. Analyze these clusters and comment on the results.<br> | 
| Data Visualization & Reporting | 4 | 1. Create a dashboard in tableau by choosing appropriate chart types and metrics useful for the business. The dashboard must entail the following:<br>a. Country-wise analysis to demonstrate average spend. Use a bar chart to show the monthly figures<br>b. Bar graph of top 15 products which are mostly ordered by the users to show the number of products sold.<br>c. Bar graph to show the count of orders vs. hours throughout the day<br>d. Plot the distribution of RFM values using histogram and frequency charts<br>e. Plot error (cost) vs. number of clusters selected<br>f. Visualize to compare the RFM values of the clusters using heatmap<br> |
| Presentation | 5 |1. Presentation write up and Submission |









