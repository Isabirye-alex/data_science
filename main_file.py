# Import the DataPipeline class from the pipeline_class module
from pipeline_class import DataPipeline

# Import matplotlib.pyplot for controlling plot display
import matplotlib.pyplot as plt

# Step 1: Initialize the data pipeline with the CSV dataset
# 'online_retail.csv' should be the path to your raw dataset
pipeline = DataPipeline('online_retail.csv')

# Step 2: Run the full data processing and analysis pipeline
# This will:
#   - Clean the data
#   - Add time-based features
#   - Perform RFM segmentation
#   - Compute cohort retention
#   - Calculate CLV
#   - Generate Pareto analysis
#   - Create retention heatmaps and Pareto plots
pipeline.run()
