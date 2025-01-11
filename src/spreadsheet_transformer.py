import pandas as pd
from pathlib import Path
from typing import Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpreadsheetTransformer:
    """Transforms task-based CSV data into week-based column format."""
    
    def __init__(self, input_file: Union[str, Path]):
        self.input_file = Path(input_file)
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
    
    def transform(self) -> pd.DataFrame:
        """
        Reads the input CSV and transforms it to week-based format.
        Returns transformed DataFrame.
        """
        try:
            # Read the CSV file
            df = pd.read_csv(self.input_file)
            
            # Ensure required columns exist
            required_columns = {'Task', 'Week', 'Value'}
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"Missing required columns: {missing}")
            
            # Pivot the data to create week-based columns
            transformed_df = df.pivot(
                index='Task',
                columns='Week',
                values='Value'
            ).fillna(0)
            
            # Rename columns to include "Week" prefix
            transformed_df.columns = [f'Week {col}' for col in transformed_df.columns]
            
            return transformed_df
            
        except Exception as e:
            logger.error(f"Error transforming spreadsheet: {str(e)}")
            raise
    
    def save(self, df: pd.DataFrame, output_file: Union[str, Path]) -> None:
        """Saves the transformed DataFrame to a CSV file."""
        try:
            output_path = Path(output_file)
            df.to_csv(output_path)
            logger.info(f"Successfully saved transformed data to {output_path}")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise 