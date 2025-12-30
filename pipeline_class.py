# -*- coding: utf-8 -*-
"""
Created on Mon Dec 29 15:50:24 2025

@author: AX

DataPipeline class: orchestrates the full data processing, analysis, 
and visualization workflow for customer analytics.
"""

import pandas as pd
from data_processor_class import DataProcessor
from customer_behavior_class import CustomerIntelligence
from data_visualization_class import DataVisualization


class DataPipeline:
    """
    A class to execute the full customer analytics pipeline:
    - Data cleaning and preprocessing
    - Feature engineering (time features)
    - Customer RFM and segmentation analysis
    - Cohort retention analysis
    - Customer lifetime value (CLV) calculation
    - Pareto analysis (80/20 customer revenue)
    - Data visualizations
    """

    def __init__(self, path):
        """
        Constructor: loads the dataset from a CSV file.

        Parameters
        
        path : str
            Path to the CSV dataset file.
        """
        self.df = pd.read_csv(path)

    def run(self):
        """
        Executes the full data analytics pipeline step by step.

        Returns
        
        None
        """
        # Step 1: Clean the dataset using the DataProcessor class
        self.df = DataProcessor(self.df)

        # Step 2: Add additional time-based features (e.g., YearMonth)
        cleaned_dataset = DataProcessor.add_time_feature(self.df)

        # Step 3: Initialize the CustomerIntelligence class with cleaned data
        customer_intelligence = CustomerIntelligence(cleaned_dataset)

        # Step 4: Build the RFM table (Recency, Frequency, Monetary) and segmentation
        customer_rfm = customer_intelligence.build_rfm()

        # Step 5: Perform cohort analysis to compute customer retention over time
        customer_retention_df = customer_intelligence.cohort_logic()

        # Step 6: Calculate Customer Lifetime Value (CLV) table
        clv_table = customer_intelligence.build_clv_table()

        # Step 7: Perform Pareto analysis (identify top 20% customers contributing 80% revenue)
        pareto_df = customer_intelligence.pareto_analysis()

        # Step 8: Initialize DataVisualization class for plotting
        data_visualizer = DataVisualization()

        # Step 9: Plot Pareto curve and get the figure/axes objects
        pareto_curve = data_visualizer.plot_pareto(pareto_df)

        # Step 11: Plot customer retention heatmap and get figure/axes objects
        retention_heatmap = data_visualizer.plot_retention(customer_retention_df)

        # Step 12: Group customers by segment and calculate segment metrics
        grouped_df = customer_intelligence.group_by_segment()

        # Step 13: Perform Pareto analysis by country
        customers_by_country = customer_intelligence.pareto_analysis_by_country()
        customers_df = customers_by_country['customers_by_country']
        customer_grouping = customers_by_country['customer_grouping']
        # Step 14: Print the top countries by number of customers and revenue
        return {
        'cleaned_dataset': cleaned_dataset,
        'rfm_table': customer_rfm,
        'retention_df': customer_retention_df,
        'clv_table': clv_table,
        'pareto_df': pareto_df,
        'grouped_df': grouped_df,
        'country_df': customers_df,
        'customer_grouping': customer_grouping
        }
