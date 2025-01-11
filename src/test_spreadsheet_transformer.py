import pytest
import pandas as pd
from pathlib import Path
from spreadsheet_transformer import SpreadsheetTransformer

@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    csv_content = """Task,Week,Value
Task A,1,10
Task A,2,15
Task B,1,5
Task B,2,8"""
    
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)
    return csv_file

def test_transformer_initialization(sample_csv):
    """Test that the transformer initializes correctly."""
    transformer = SpreadsheetTransformer(sample_csv)
    assert transformer.input_file == sample_csv

def test_transformer_missing_file():
    """Test that the transformer raises an error for missing files."""
    with pytest.raises(FileNotFoundError):
        SpreadsheetTransformer("nonexistent.csv")

def test_transform_success(sample_csv):
    """Test successful transformation of CSV data."""
    transformer = SpreadsheetTransformer(sample_csv)
    result = transformer.transform()
    
    # Check that the result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Check column names
    assert list(result.columns) == ['Week 1', 'Week 2']
    
    # Check values
    assert result.loc['Task A', 'Week 1'] == 10
    assert result.loc['Task A', 'Week 2'] == 15
    assert result.loc['Task B', 'Week 1'] == 5
    assert result.loc['Task B', 'Week 2'] == 8

def test_save_output(sample_csv, tmp_path):
    """Test saving the transformed data."""
    transformer = SpreadsheetTransformer(sample_csv)
    result = transformer.transform()
    
    output_file = tmp_path / "output.csv"
    transformer.save(result, output_file)
    
    # Check that the file exists
    assert output_file.exists()
    
    # Check that the content is correct
    saved_df = pd.read_csv(output_file, index_col=0)
    assert list(saved_df.columns) == ['Week 1', 'Week 2'] 