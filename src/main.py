from timeflip_transformer import TimeflipTransformer
import logging
from pathlib import Path
import argparse

logger = logging.getLogger(__name__)

def main():
    """Main function to run the Timeflip2 data transformation."""
    parser = argparse.ArgumentParser(description='Transform Timeflip2 CSV data.')
    parser.add_argument('input_file', help='Path to input CSV file')
    parser.add_argument('--output', '-o', default='data/transformed_output.csv',
                       help='Path to output CSV file (default: data/transformed_output.csv)')
    args = parser.parse_args()

    try:
        # Ensure data directory exists for default output
        if args.output.startswith('data/'):
            data_dir = Path('data')
            data_dir.mkdir(exist_ok=True)

        # Initialize transformer
        transformer = TimeflipTransformer(args.input_file)

        # Transform the data
        transformed_df = transformer.transform()

        # Save the result
        transformer.save(transformed_df, args.output)

    except Exception as e:
        logger.error(f"Program failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()