import os
import pandas as pd
import numpy as np
from pathlib import Path


def analyze_constance_inventory(filename="myconstancedbmaster.xlsx"):
    """
    Analyzes the MyConstance inventory Excel file structure
    """
    # Construct path relative to /app/xls
    file_path = Path('xls') / filename

    print(f"Attempting to read file: {file_path}")

    try:
        # First try reading with default settings
        df = pd.read_excel(file_path)

        # Basic file info
        print("\nFile Statistics:")
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        print("\nColumns found:")
        for col in df.columns:
            print(f"- {col}")

        print("\nDetailed Column Analysis:")
        print("-" * 80)

        column_analysis = {}
        for column in df.columns:
            non_null_values = df[column].dropna()

            analysis = {
                'dtype': str(df[column].dtype),
                'non_null_count': len(non_null_values),
                'null_count': df[column].isnull().sum(),
                'unique_values': df[column].nunique(),
                'sample_values': df[column].dropna().head(3).tolist()
            }

            # Additional analysis for numeric columns
            if df[column].dtype in ['int64', 'float64']:
                analysis['min'] = df[column].min()
                analysis['max'] = df[column].max()

            # For string columns, get max length
            if df[column].dtype == 'object':
                str_lengths = df[column].astype(str).str.len()
                analysis['max_length'] = str_lengths.max()

            column_analysis[column] = analysis

            # Print analysis
            print(f"\nColumn: {column}")
            print(f"Data type: {analysis['dtype']}")
            print(f"Non-null count: {analysis['non_null_count']}")
            print(f"Null count: {analysis['null_count']}")
            print(f"Unique values: {analysis['unique_values']}")
            print(f"Sample values: {analysis['sample_values']}")
            if 'max_length' in analysis:
                print(f"Max length: {analysis['max_length']}")
            if 'min' in analysis:
                print(f"Min: {analysis['min']}")
                print(f"Max: {analysis['max']}")

        return df, column_analysis

    except FileNotFoundError:
        print(f"Error: Could not find file at {file_path}")
        print("Please ensure the file exists in the app/xls directory")
        return None, None
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        print("If this is an Excel-specific error, we might need to try different pandas read_excel parameters")
        return None, None


if __name__ == "__main__":
    df, analysis = analyze_constance_inventory()

    if df is not None:
        print("\nSuggested SQLAlchemy Models:")
        print("-" * 80)
        print("Based on the Excel structure, here's a suggested database schema:")

        print("""
from app import db
from datetime import datetime

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'

    id = db.Column(db.Integer, primary_key=True)""")

        for column, details in analysis.items():
            # Convert Excel column name to Python variable name
            column_name = column.lower().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')

            # Determine appropriate SQLAlchemy type
            if details['dtype'] == 'int64':
                col_type = 'Integer'
            elif details['dtype'] == 'float64':
                col_type = 'Float'
            elif details['dtype'] == 'datetime64[ns]':
                col_type = 'DateTime'
            else:
                if 'max_length' in details:
                    # Add some buffer to the max length
                    max_length = min(int(details['max_length'] * 1.5), 255)
                    col_type = f'String({max_length})'
                else:
                    col_type = 'String(255)'

            nullable = details['null_count'] > 0
            print(f"    {column_name} = db.Column(db.{col_type}, nullable={nullable})")