

import matplotlib.pyplot as plt
import seaborn as sns


class DataVisualization:
    @staticmethod
    def plot_retention(retention_df):
        plt.figure(figsize=(15,8))
        sns.heatmap(retention_df, annot=True, cmap='viridis', fmt='.0%')
        plt.title('Customer retention heatmap over time')
        plt.show()

    @staticmethod
    def plot_pareto(pareto_df):
        plt.figure(figsize=(10,5))
        plt.plot(pareto_df['CumCustomerPct'], pareto_df['CumRevenuePct'])
        plt.axhline(0.8, linestyle='--')
        plt.axvline(pareto_df[pareto_df['CumRevenuePct'] <= 0.8].shape[0]/len(pareto_df), linestyle='--')
        plt.title('Pareto Analysis')
        plt.xlabel('Cumulative Customer Percentage')
        plt.ylabel('Cumulative Revenue Percentage')
        plt.show()

