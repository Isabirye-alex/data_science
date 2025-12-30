
import pandas as pd


# This class builds the rfm table and also performs the segmentation logic
class CustomerIntelligence:
    # Default function or method to be called whenever an instance of this class (Customer Intelligence class ) is called
    def __init__(self, cleaned_dataset):
        self.df = cleaned_dataset
        self.rfm = None
        self.clv_table = None
        self.retention = None
        self.customer_revenue = None
        self.grouped_df = None
        self.customer_country = None

    # Function to build rfm table
    def build_rfm(self):
        # Fake date to be used as the current data
        snapshot_date = self.df['InvoiceDate'].max() + pd.Timedelta(days=1)

        rfm = self.df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x : (snapshot_date - x.max()).days,
            'TotalRevenue' : 'sum'
        })
        rfm = rfm.reset_index()
        frequency_df = self.df[self.df['CancelledInvoice'] == False].groupby('CustomerID')['InvoiceNo'].nunique()
        frequency_df = frequency_df.reset_index()
        rfm = pd.merge(rfm, frequency_df, on='CustomerID')
        rfm.columns = ['CustomerID','Recency', 'Monetary', 'Frequency']
        rfm = rfm[rfm['Monetary'] > 0]
        # Assign scores 
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'),5, labels=[1,2,3,4,5])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5])
        
        segs = {
            r'[1-2][1-2]': 'Lost',
            r'[1-2][3-4]' : 'At risk',
            r'[1-2]5' : 'Can\'t lose',
            r'3[1-2]' : 'About to sleep',
            r'33' : 'Need attention',
            r'41': 'Promising',
            r'[3-4][4-5]' : 'Loyal customer',
            r'51' : 'New customers',
            r'[4-5][2-3]': 'Potential Loyalist',
            r'5[4-5]': 'Champion',
            }
        
        rfm['RFM_Score'] = rfm['R_Score'].astype(str)+rfm['F_Score'].astype(str)+rfm['M_Score'].astype(str)
        rfm['Segments'] = rfm['R_Score'].astype(str)+rfm['F_Score'].astype(str)
        rfm['Segments'] = rfm['Segments'].replace(segs, regex=True)
        self.rfm = rfm
        return rfm
    
    # Cohort analysis function
    def cohort_logic(self):
        self.df['CohortMonth'] = self.df.groupby('CustomerID')['YearMonth'].transform('min')
        invoice_year = self.df['YearMonth'].dt.year
        invoice_month = self.df['YearMonth'].dt.month
        cohort_year = self.df['CohortMonth'].dt.year
        cohort_month = self.df['CohortMonth'].dt.month

        years_dff = invoice_year - cohort_year
        months_diff = invoice_month - cohort_month

        self.df['CohortIndex'] = (years_dff * 12) + (months_diff+1)

        cohort_data = self.df.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().unstack(1)
        cohort_sizes = cohort_data.iloc[:,0]
        retention = cohort_data.divide(cohort_sizes, axis=0)
        self.retention = retention
        return self.retention

    # Clv method to calculate customer lifetime value
    def build_clv_table(self):
        # clv = AOV * Purchae Frequency * Lifespan
        aov = (self.df.groupby('CustomerID')['TotalRevenue'].sum()) / (self.df.groupby('CustomerID')['InvoiceNo'].nunique())
        # aov = aov.reset_index()
        purchase_frequency = self.df[self.df['CancelledInvoice'] == False].groupby('CustomerID')['InvoiceNo'].nunique().astype('Int64')
        # purchase_frequency = purchase_frequency.reset_index()
        lifespan = (((self.df.groupby('CustomerID')['InvoiceDate'].max())-(self.df.groupby('CustomerID')['InvoiceDate'].min())).dt.days+1)/(30)
        # lifespan = lifespan.reset_index()
        clv_table = pd.DataFrame({
            'AOV':aov,
            'PurchaseFrequency': purchase_frequency,
            'Lifespan': lifespan,
        })
        clv_table['CLV'] = aov * purchase_frequency * lifespan
        clv_table = clv_table[clv_table['CLV'] > 0]
        self.clv_table = clv_table
        return self.clv_table
    
    def pareto_analysis(self):
        customer_revenue = self.df.groupby('CustomerID')['TotalRevenue'].sum().sort_values(ascending=False).reset_index()
        customer_revenue = customer_revenue[customer_revenue['TotalRevenue'] > 0]
        customer_revenue['CumRevenue'] = customer_revenue['TotalRevenue'].cumsum()
        customer_revenue['CumRevenuePct'] =  customer_revenue['CumRevenue']/ customer_revenue['TotalRevenue'].sum()
        customer_revenue['CumCustomerPct'] = ((customer_revenue.index+1) / (len(customer_revenue)))
        self.customer_revenue = customer_revenue
        return self.customer_revenue
    
    def group_by_segment(self):
        grouped_df = self.rfm.groupby('Segments')['Monetary'].sum()
        grouped_df = grouped_df.reset_index()
        grouped_df.columns = ['Segment', 'TotalRevenue']
        total_customers_per_segment = self.rfm.groupby('Segments').agg({'CustomerID':'count'}).reset_index().rename(columns={'Segments': 'Segment', 'CustomerID': 'TotalCustomers'})
        grouped_df = pd.merge(grouped_df, total_customers_per_segment, on='Segment')
        grouped_df = grouped_df.sort_values(by='TotalRevenue', ascending=False)
        total_customers = self.rfm.shape[0]
        grouped_df['CustomerPct(%)'] = grouped_df['TotalCustomers']/total_customers
        grouped_df['RevenuePct(%)'] = grouped_df['TotalRevenue'] / grouped_df['TotalRevenue'].sum()
        self.grouped_df = grouped_df
        return grouped_df
    def pareto_analysis_by_country(self):
        customers_by_country = self.df.groupby('Country',observed=False).agg({'CustomerID': 'count'}).reset_index()
        customers_by_country.columns = ['Country', 'TotalCustomers']
        customers_by_country = customers_by_country.sort_values(by='TotalCustomers', ascending=False)
        revenue_per_country = self.df[self.df['CancelledInvoice']==False].groupby('Country', observed=False)['TotalRevenue'].sum()
        revenue_per_country = revenue_per_country.reset_index()
        customers_by_country = pd.merge(customers_by_country, revenue_per_country, on='Country')
        customers_by_country['CustomerPercent(%)'] = (customers_by_country['TotalCustomers']/ customers_by_country['TotalCustomers'].sum()) * 100
        customers_by_country['RevenuePercent(%'] = (customers_by_country['TotalRevenue']/customers_by_country['TotalRevenue'].sum()) * 100
        self.customer_country = customers_by_country
        
        return self.customer_country

