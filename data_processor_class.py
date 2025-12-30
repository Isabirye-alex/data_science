import pandas as pd


class DataProcessor:
    """
    Handles all data cleaning and feature engineering operations
    required before customer-level analytics.

    Responsibilities:
    - Data type standardization
    - Missing value handling
    - Revenue computation
    - Cancellation flagging
    - Time-based feature creation
    """

    def __init__(self, dataset):
        """
        Initializes the DataProcessor and immediately cleans the dataset.

        Parameters
        ----------
        dataset : pandas.DataFrame
            Raw transactional dataset.
        """
        # Work on a copy to avoid mutating the original dataset
        self.df = dataset.copy()

        # Automatically clean data upon instantiation
        self.clean_data()

    # DATA CLEANING
    def clean_data(self):
        """
        Cleans and standardizes the raw dataset by:
        - Converting date columns to datetime
        - Handling missing customer IDs
        - Standardizing string fields
        - Identifying cancelled invoices
        - Computing transaction revenue

        Returns
        -------
        pandas.DataFrame
            Cleaned transactional dataset.
        """

        # Convert invoice date to datetime format
        self.df['InvoiceDate'] = pd.to_datetime(
            self.df['InvoiceDate'],
            format='%m/%d/%Y %H:%M',
            errors='coerce'
        )

        # Convert CustomerID to numeric to identify missing values
        self.df['CustomerID'] = pd.to_numeric(
            self.df['CustomerID'],
            errors='coerce'
        )

        # Drop rows with missing CustomerID
        self.df = self.df.dropna(subset=['CustomerID'])

        # Standardize CustomerID as string
        self.df['CustomerID'] = self.df['CustomerID'].astype(int).astype(str)

        # Clean and standardize product descriptions
        self.df['Description'] = (
            self.df['Description']
            .str.strip()
            .str.lower()
        )

        # Identify cancelled invoices (Invoice numbers starting with 'C')
        self.df['CancelledInvoice'] = self.df['InvoiceNo'].str.startswith('C')

        # Remove invalid stock codes containing only letters
        self.df = self.df[
            ~self.df['StockCode'].str.match('^[A-Za-z]+$')
        ]

        # Compute total revenue per transaction
        self.df['TotalRevenue'] = self.df['Quantity'] * self.df['UnitPrice']

        # Standardize country names
        self.df['Country'] = (
            self.df['Country']
            .str.title()
            .str.strip()
        )

        # Convert categorical columns to 'category' dtype to reduce memory usage
        categorical_columns = ['Description', 'StockCode', 'InvoiceNo', 'Country']
        for col in categorical_columns:
            self.df[col] = self.df[col].astype('category')

        return self.df

    # TIME FEATURE ENGINEERING
    def add_time_feature(self):
        """
        Extracts year and month from the InvoiceDate column
        and creates a YearMonth timestamp for cohort analysis.

        Returns
        -------
        pandas.DataFrame
            Dataset with YearMonth feature added.
        """

        self.df['YearMonth'] = (
            self.df['InvoiceDate']
            .dt.to_period('M')
        )

        return self.df
