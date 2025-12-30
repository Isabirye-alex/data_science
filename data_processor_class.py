
import pandas as pd


class DataProcessor:

    # Constructor class to be called immediatey whenever an instance of the data processor class is called
    def __init__(self, dataset):
        self.df = dataset.copy()
        self.clean_data()

    # Function to clean the dataset
    def clean_data(self):
        # Convert date time column to datetime object
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'], format='%m/%d/%Y %H:%M', errors='coerce')
        # First convert customer id to numeric to create NA for null values for easy dropping
        self.df['CustomerID'] = pd.to_numeric(self.df['CustomerID'], errors='coerce')
        # Drop null rows with reference to customer id
        self.df = self.df.dropna(subset=['CustomerID'])
        # Standardize strings and types
        self.df['CustomerID'] = self.df['CustomerID'].astype(int).astype(str)
        self.df['Description'] = self.df['Description'].str.strip().str.lower()
        # Identify cancelled invoices
        self.df['CancelledInvoice'] = self.df['InvoiceNo'].str.startswith('C')
        # Filter out invalid stock codes
        self.df = self.df[~self.df['StockCode'].str.match('^[A-za-z]+$')]
        # Add total revenue column to each row
        self.df['TotalRevenue'] = self.df['Quantity'] * self.df['UnitPrice']
        self.df['Country'] = self.df['Country'].str.title().str.strip()
        #self.df['Country']= self.df['Country'] !='Unspecified'
        #Convert categorical columns to category to minimize memory usage
        categorical_columns = ['Description', 'StockCode','InvoiceNo','Country']
        for c in categorical_columns:
            self.df[c] = self.df[c].astype('category')
        return self.df

    # Extract year and month from the datetime column
    def add_time_feature(self):
        self.df['YearMonth'] = self.df['InvoiceDate'].dt.to_period('M').dt.to_timestamp()

        return self.df
     

