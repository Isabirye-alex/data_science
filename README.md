Customer Analytics Pipeline
Overview

This project provides a comprehensive pipeline for customer analytics using transactional data. It enables businesses to understand customer behavior, segment customers, and visualize key metrics for decision-making.
The pipeline includes:
Data preprocessing and cleaning
RFM (Recency, Frequency, Monetary) modeling and segmentation
Cohort-based customer retention analysis
Customer Lifetime Value (CLV) computation
Pareto (80/20) revenue analysis
Customer segmentation by country
Data visualization of retention and Pareto curves

data_science/
│
├── customer_behavior_class.py     # Customer analytics and RFM, CLV, Pareto, cohort logic
├── data_processor_class.py        # Data cleaning and time feature extraction
├── data_visualization_class.py    # Plotting retention heatmaps and Pareto curves
├── pipeline_class.py              # Pipeline class integrating preprocessing, analysis, and visualization
├── online_retail.csv              # Sample transactional dataset
├── figures/                       # Folder for saving generated plots
└── README.md
Installation
clone the repository git clone https://github.com/Isabirye-alex/data_science.git
# cd data_science

#Usage
Run the pipeline
from pipeline_class import DataPipeline
import matplotlib.pyplot as plt

# Initialize pipeline with dataset
pipeline = DataPipeline('online_retail.csv')

# Run the pipeline
pipeline.run()

# Show plots
plt.show()

Features
Data Preprocessing
Converts invoice dates to datetime objects
Cleans customer IDs and description fields
Computes total revenue and flags cancelled invoices
Converts categorical columns to minimize memory usage
Extracts YearMonth for cohort analysis
Customer Intelligence
RFM Analysis: Assigns scores and segments customers
Cohort Analysis: Retention over time per cohort
Customer Lifetime Value (CLV): Computes CLV per customer
Pareto Analysis: Identify top contributing customers
Segment Aggregation: Revenue and customer distribution per segment
Country-level Analysis: Revenue and customer distribution by country
Data Visualization
Retention heatmaps
Pareto curves
Returns figure objects for saving and customization

Notes
The pipeline works best with a transactional dataset containing columns like:
InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country.

Use .dt.to_period('M') for monthly grouping to avoid unnecessary zero timestamps.

Figures can be saved in any folder by specifying the path in fig.savefig('folder/filename.jpg').


License

This project is released under the MIT License.