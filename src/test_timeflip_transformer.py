import pytest
import pandas as pd
from pathlib import Path
from timeflip_transformer import TimeflipTransformer

@pytest.fixture
def sample_timeflip_csv(tmp_path):
    """Create a sample Timeflip2 CSV file for testing."""
    csv_content = """Account:;Michael Hunter;;;;;;;
From:;01.01.2025;;To:;11.01.2025;;;;

Week #1;;;;29.12.2024;30.12.2024;31.12.2024;
Tag;Task;Time;Hour Rate;Sun;Mon;Tue;
-;Code;7.75;;;;;
;Slack;6.39;;;;;

Week #2;;;;05.01.2025;06.01.2025;07.01.2025;
Tag;Task;Time;Hour Rate;Sun;Mon;Tue;
-;Code;5.89;;;;;
;Slack;15.45;;;;;"""
    
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)
    return csv_file

def test_transformer_initialization(sample_timeflip_csv):
    """Test that the transformer initializes correctly."""
    transformer = TimeflipTransformer(sample_timeflip_csv)
    assert transformer.input_file == sample_timeflip_csv

def test_transformer_missing_file():
    """Test that the transformer raises an error for missing files."""
    with pytest.raises(FileNotFoundError):
        TimeflipTransformer("nonexistent.csv")

def test_parse_weeks(sample_timeflip_csv):
    """Test weekly data extraction."""
    transformer = TimeflipTransformer(sample_timeflip_csv)
    df = pd.read_csv(sample_timeflip_csv, sep=';', header=None)
    weeks = transformer._parse_weeks(df)
    
    print("\nWeeks data:")
    for i, week in enumerate(weeks):
        print(f"Week {i+1}:")
        print(week)
    
    assert len(weeks) == 2  # Should find two weeks
    assert any('Code' in str(row[1]) and '7.75' in str(row[2]) for _, row in weeks[0].iterrows())  # Week 1 data
    assert any('Slack' in str(row[1]) and '15.45' in str(row[2]) for _, row in weeks[1].iterrows())  # Week 2 data

def test_transform_success(sample_timeflip_csv):
    """Test successful transformation of Timeflip2 data."""
    transformer = TimeflipTransformer(sample_timeflip_csv)
    result = transformer.transform()
    
    print("\nTransformed DataFrame:")
    print(result)
    
    # Check that the result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Check column names
    assert list(result.columns) == ['Week 1', 'Week 2']
    
    # Check values with approximate equality
    assert abs(result.loc['Code', 'Week 1'] - 7.75) < 0.01
    assert abs(result.loc['Code', 'Week 2'] - 5.89) < 0.01
    assert abs(result.loc['Slack', 'Week 1'] - 6.39) < 0.01
    assert abs(result.loc['Slack', 'Week 2'] - 15.45) < 0.01

def test_save_output(sample_timeflip_csv, tmp_path):
    """Test saving the transformed data."""
    transformer = TimeflipTransformer(sample_timeflip_csv)
    result = transformer.transform()
    
    output_file = tmp_path / "output.csv"
    transformer.save(result, output_file)
    
    # Check that the file exists
    assert output_file.exists()
    
    # Read and print the saved file for debugging
    print("\nSaved file contents:")
    saved_df = pd.read_csv(output_file, index_col=0)
    print(saved_df)
    
    # Check that the content is correct
    assert list(saved_df.columns) == ['Week 1', 'Week 2']
    assert abs(float(saved_df.loc['Code', 'Week 1']) - 7.75) < 0.01
    assert abs(float(saved_df.loc['Slack', 'Week 2']) - 15.45) < 0.01 