# Customer Segmentation by Cohort Analysis and RFM Modelling

##### Capstone Project, Data Science Masters Program (with Simplilearn)
---

## Problem Statement

It is a critical requirement for business to understand the value derived from a customer. RFM is a method used for analyzing customer value.

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