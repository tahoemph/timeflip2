from timeflip_transformer import TimeflipTransformer
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def main():
    """Main function to run the Timeflip2 data transformation."""
    try:
        # Ensure data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        # Initialize transformer
        transformer = TimeflipTransformer('data/example.csv')
        
        # Transform the data
        transformed_df = transformer.transform()
        
        # Save the result
        transformer.save(transformed_df, 'data/transformed_output.csv')
        
    except Exception as e:
        logger.error(f"Program failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 