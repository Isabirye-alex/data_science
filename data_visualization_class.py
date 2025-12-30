import matplotlib.pyplot as plt
import seaborn as sns


class DataVisualization:
    """
    Handles visualization of customer analytics results, including:
    - Retention heatmaps
    - Pareto (80/20) customer-revenue analysis
    """

    @staticmethod
    def plot_retention(retention_df):
        """
        Creates a retention heatmap to visualize customer retention over time.

        Parameters
        ----------
        retention_df : pandas.DataFrame
            Cohort retention matrix where rows are cohorts and columns are periods.

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure object of the retention heatmap.
        ax : matplotlib.axes.Axes
            Axes object of the heatmap.
        """

        fig, ax = plt.subplots(figsize=(12, 5))
        sns.heatmap(
            retention_df,
            annot=True,       # Show numeric values
            cmap='viridis',   # Color map
            fmt='.0%',        # Format as percentages
            ax=ax
        )
        ax.set_title('Customer Retention Heatmap Over Time')
        ax.set_xlabel('Cohort Index (Months Since First Purchase)')
        ax.set_ylabel('Cohort Month')
        fig.savefig('figures/retention_analysis.jpg',dpi=300)
        return fig, ax

    @staticmethod
    def plot_pareto(pareto_df):
        """
        Creates a Pareto curve to visualize the cumulative contribution
        of customers to total revenue.

        Parameters
        ----------
        pareto_df : pandas.DataFrame
            DataFrame containing cumulative revenue and cumulative customer percentage.

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure object of the Pareto curve.
        ax : matplotlib.axes.Axes
            Axes object of the Pareto curve.
        """

        fig, ax = plt.subplots(figsize=(20, 8))

        # Plot cumulative customer % vs cumulative revenue %
        ax.plot(
            pareto_df['CumCustomerPct'],
            pareto_df['CumRevenuePct'],
            marker='o'
        )

        # Highlight 80% revenue line
        ax.axhline(0.8, color='red', linestyle='--', label='80% Revenue')

        # Highlight the corresponding customer percentage
        x_cutoff = pareto_df[pareto_df['CumRevenuePct'] <= 0.8].shape[0] / len(pareto_df)
        ax.axvline(x_cutoff, color='blue', linestyle='--', label='Top Customers')

        ax.set_title('Pareto Analysis of Customers')
        ax.set_xlabel('Cumulative Customer Percentage')
        ax.set_ylabel('Cumulative Revenue Percentage')
        ax.set_xlim(left=0)   # x-axis starts at 0
        ax.set_ylim(bottom=0) # y-axis starts at 0
        ax.legend()
        fig.tight_layout()
        fig.savefig('figures/pareto_curve.jpg', dpi=300)

        return fig, ax
