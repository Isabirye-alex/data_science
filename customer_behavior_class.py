import pandas as pd

class CustomerIntelligence:
    """
    This class handles all customer-level analytics including:
    - RFM modeling and segmentation
    - Cohort-based retention analysis
    - Customer Lifetime Value (CLV) computation
    - Pareto (80/20) revenue analysis
    - Customer segmentation and country-level analysis
    """

    def __init__(self, cleaned_dataset):
        """
        Initializes the CustomerIntelligence object.

        Parameters
        ----------
        cleaned_dataset : pandas.DataFrame
            Preprocessed transactional dataset with time features,
            revenue columns, and cleaned customer information.
        """
        self.df = cleaned_dataset

        # Containers for derived analytical tables
        self.rfm = None
        self.clv_table = None
        self.retention = None
        self.customer_revenue = None
        self.grouped_df = None
        self.customer_country = None

    # RFM ANALYSIS
    def build_rfm(self):
        """
        Builds the RFM (Recency, Frequency, Monetary) table and assigns
        customer segments based on RFM scores.

        Returns
        -------
        pandas.DataFrame
            RFM table with scores and customer segments.
        """

        # Snapshot date (one day after last invoice date)
        snapshot_date = self.df['InvoiceDate'].max() + pd.Timedelta(days=1)

        # Compute Recency and Monetary value
        rfm = self.df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
            'TotalRevenue': 'sum'
        }).reset_index()

        # Compute Frequency (unique non-cancelled invoices)
        frequency_df = (
            self.df[self.df['CancelledInvoice'] == False]
            .groupby('CustomerID')['InvoiceNo']
            .nunique()
            .reset_index()
        )

        # Merge frequency with recency and monetary
        rfm = pd.merge(rfm, frequency_df, on='CustomerID')
        rfm.columns = ['CustomerID', 'Recency', 'Monetary', 'Frequency']

        # Remove customers with zero or negative monetary value
        rfm = rfm[rfm['Monetary'] > 0]

        # Assign RFM scores using quantiles
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

        # Segment mapping rules based on R and F scores
        segs = {
            r'[1-2][1-2]': 'Lost',
            r'[1-2][3-4]': 'At risk',
            r'[1-2]5': "Can't lose",
            r'3[1-2]': 'About to sleep',
            r'33': 'Need attention',
            r'41': 'Promising',
            r'[3-4][4-5]': 'Loyal customer',
            r'51': 'New customers',
            r'[4-5][2-3]': 'Potential Loyalist',
            r'5[4-5]': 'Champion',
        }

        # Build RFM score and assign segments
        rfm['RFM_Score'] = (
            rfm['R_Score'].astype(str) +
            rfm['F_Score'].astype(str) +
            rfm['M_Score'].astype(str)
        )

        rfm['Segments'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str)
        rfm['Segments'] = rfm['Segments'].replace(segs, regex=True)

        self.rfm = rfm
        return rfm

    # COHORT ANALYSIS
    def cohort_logic(self):
        """
        Performs cohort-based retention analysis using customer
        first purchase month.

        Returns
        -------
        pandas.DataFrame
            Cohort retention matrix.
        """

        # Identify first purchase month per customer
        self.df['CohortMonth'] = self.df.groupby('CustomerID')['YearMonth'].transform('min')

        # Extract year and month components
        invoice_year = self.df['YearMonth'].dt.year
        invoice_month = self.df['YearMonth'].dt.month
        cohort_year = self.df['CohortMonth'].dt.year
        cohort_month = self.df['CohortMonth'].dt.month

        # Compute cohort index (number of months since first purchase)
        years_diff = invoice_year - cohort_year
        months_diff = invoice_month - cohort_month
        self.df['CohortIndex'] = (years_diff * 12) + (months_diff + 1)

        # Build cohort table
        cohort_data = (
            self.df
            .groupby(['CohortMonth', 'CohortIndex'])['CustomerID']
            .nunique()
            .unstack(1)
        )

        # Calculate retention rates
        cohort_sizes = cohort_data.iloc[:, 0]
        retention = cohort_data.divide(cohort_sizes, axis=0)

        self.retention = retention
        return retention

    # CUSTOMER LIFETIME VALUE (CLV)
    def build_clv_table(self):
        """
        Computes Customer Lifetime Value (CLV) using:
        CLV = Average Order Value × Purchase Frequency × Customer Lifespan

        Returns
        -------
        pandas.DataFrame
            CLV table per customer.
        """

        # Average Order Value
        aov = (
            self.df.groupby('CustomerID')['TotalRevenue'].sum() /
            self.df.groupby('CustomerID')['InvoiceNo'].nunique()
        )

        # Purchase frequency (non-cancelled orders)
        purchase_frequency = (
            self.df[self.df['CancelledInvoice'] == False]
            .groupby('CustomerID')['InvoiceNo']
            .nunique()
            .astype('Int64')
        )

        # Customer lifespan in months
        lifespan = (
            (self.df.groupby('CustomerID')['InvoiceDate'].max() -
             self.df.groupby('CustomerID')['InvoiceDate'].min())
            .dt.days.add(1) / 30
        )

        # Build CLV table
        clv_table = pd.DataFrame({
            'AOV': aov,
            'PurchaseFrequency': purchase_frequency,
            'Lifespan': lifespan
        })

        clv_table['CLV'] = aov * purchase_frequency * lifespan
        clv_table = clv_table[clv_table['CLV'] > 0]

        self.clv_table = clv_table
        return clv_table

    # PARETO ANALYSIS
    def pareto_analysis(self):
        """
        Performs Pareto (80/20) analysis on customer revenue.

        Returns
        -------
        pandas.DataFrame
            Customer revenue distribution with cumulative percentages.
        """

        customer_revenue = (
            self.df.groupby('CustomerID')['TotalRevenue']
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        customer_revenue = customer_revenue[customer_revenue['TotalRevenue'] > 0]

        # Cumulative metrics
        customer_revenue['CumRevenue'] = customer_revenue['TotalRevenue'].cumsum()
        customer_revenue['CumRevenuePct'] = (
            customer_revenue['CumRevenue'] / customer_revenue['TotalRevenue'].sum()
        )
        customer_revenue['CumCustomerPct'] = (
            (customer_revenue.index + 1) / len(customer_revenue)
        )

        self.customer_revenue = customer_revenue
        return customer_revenue

    # SEGMENT-LEVEL AGGREGATION
    def group_by_segment(self):
        """
        Aggregates customer count and revenue by RFM segment.

        Returns
        -------
        pandas.DataFrame
            Segment-level revenue and customer distribution.
        """

        grouped_df = (
            self.rfm.groupby('Segments')['Monetary']
            .sum()
            .reset_index(name='TotalRevenue')
            .rename(columns={'Segments':'Segment', 'Monetary': 'TotalRevenue'})
        )

        total_customers_per_segment = (
            self.rfm.groupby('Segments')['CustomerID']
            .count()
            .reset_index(name='TotalCustomers')
            .rename(columns={'Segments': 'Segment'})
        )

        grouped_df = pd.merge(grouped_df, total_customers_per_segment, on='Segment')
        grouped_df = grouped_df.sort_values(by='TotalRevenue', ascending=False)

        total_customers = self.rfm.shape[0]
        grouped_df['CustomerPct(%)'] = grouped_df['TotalCustomers'] / total_customers
        grouped_df['RevenuePct(%)'] = (
            grouped_df['TotalRevenue'] / grouped_df['TotalRevenue'].sum()
        )

        self.grouped_df = grouped_df
        return grouped_df

    # COUNTRY-LEVEL ANALYSIS
    def pareto_analysis_by_country(self):
        """
        Performs customer count and revenue analysis by country.

        Returns
        -------
        pandas.DataFrame
            Country-level customer and revenue distribution.
        """

        customers_by_country = (
            self.df.groupby('Country', observed=False)
            .agg({'CustomerID': 'count'})
            .reset_index()
            .rename(columns={'CustomerID': 'TotalCustomers'})
            .sort_values(by='TotalCustomers', ascending=False)
        )

        revenue_per_country = (
            self.df[self.df['CancelledInvoice'] == False]
            .groupby('Country', observed=False)['TotalRevenue']
            .sum()
            .reset_index()
        )

        customers_by_country = pd.merge(
            customers_by_country,
            revenue_per_country,
            on='Country'
        )

        customers_by_country['CustomerPercent(%)'] = (
            customers_by_country['TotalCustomers'] /
            customers_by_country['TotalCustomers'].sum()
        ) * 100

        customers_by_country['RevenuePercent(%)'] = (
            customers_by_country['TotalRevenue'] /
            customers_by_country['TotalRevenue'].sum()
        ) * 100

        self.customer_country = customers_by_country
        return customers_by_country
