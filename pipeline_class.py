# -*- coding: utf-8 -*-
"""
Created on Mon Dec 29 15:50:24 2025

@author: AX
"""
import pandas as pd
from data_processor_class import DataProcessor
from customer_behavior_class import CustomerIntelligence
from data_visualization_class import DataVisualization

class DataPipeline:
    def __init__(self, path):
        self.df = pd.read_csv(path)
    
    def run(self):
        self.df = DataProcessor(self.df)
        
        cleaned_dataset = DataProcessor.add_time_feature(self.df)
        
        customer_intelligence = CustomerIntelligence(cleaned_dataset)
        
        customer_rfm = customer_intelligence.build_rfm()
                
        customer_retention_df = customer_intelligence.cohort_logic()
        
        clv_table = customer_intelligence.build_clv_table()
        
        pareto_df = customer_intelligence.pareto_analysis()
        
        data_visualizer = DataVisualization()
        
        pareto_curve = data_visualizer.plot_pareto(pareto_df)
        
        pareto_df[pareto_df['CumRevenuePct'] <=0.8].shape[0]/len(pareto_df)
        
        retention_heatmap = data_visualizer.plot_retention(customer_retention_df)
        
        grouped_df = customer_intelligence.group_by_segment()
        
        customers_by_country = customer_intelligence.pareto_analysis_by_country()
        print(customers_by_country.head())

