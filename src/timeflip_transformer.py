import pandas as pd
from pathlib import Path
from typing import Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeflipTransformer:
    """Transforms Timeflip2 CSV export data into a week-based column format."""

    def __init__(self, input_file: Union[str, Path]):
        self.input_file = Path(input_file)
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")

    def _transform_simple_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform simple CSV format (Task,Week,Value)."""
        try:
            # Pivot the data
            result_df = df.pivot(
                index='Task',
                columns='Week',
                values='Value'
            ).fillna(0)

            # Rename columns to match expected format
            result_df.columns = [f'Week {col}' for col in result_df.columns]
            return result_df

        except Exception as e:
            logger.error(f"Error transforming simple format: {str(e)}")
            raise

    def _parse_weeks(self, df: pd.DataFrame) -> list:
        """Extract weekly data sections from the DataFrame."""
        weeks = []
        current_week = None
        current_date = None
        skip_next_row = False  # Flag to skip the header row after Week #

        for idx, row in df.iterrows():
            if isinstance(row[0], str) and row[0].startswith('Week #'):
                if current_week is not None and current_date is not None:
                    weeks.append((current_date, pd.DataFrame(current_week)))
                current_week = []
                # Find the first non-empty date in the row (starting from index 4)
                for i in range(4, len(row)):
                    if pd.notna(row[i]):
                        current_date = row[i]
                        break
                skip_next_row = True  # Skip the next row (header)
            elif skip_next_row:
                skip_next_row = False  # Reset the flag
            elif current_week is not None:
                current_week.append(row)

        if current_week and current_date is not None:
            weeks.append((current_date, pd.DataFrame(current_week)))

        return weeks

    def _format_week_header(self, date_str: str, week_num: int) -> str:
        """Format the week header using the date if available."""
        if pd.isna(date_str):
            return f"Week {week_num}"
        try:
            # Parse the date string (assuming DD.MM.YYYY format)
            from datetime import datetime
            date = datetime.strptime(date_str, "%d.%m.%Y")
            return date.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return f"Week {week_num}"

    def _clean_task_name(self, row) -> str:
        """Clean task name by removing leading dash if present."""
        task_name = str(row[1]).strip()
        return task_name if pd.notna(task_name) and task_name != 'Task' else None

    def _is_task_row(self, row) -> bool:
        """Check if the row is a valid task row."""
        if not (pd.notna(row[1]) and pd.notna(row[2])):  # Task name and time must exist
            return False
            
        task_name = str(row[1]).strip()
        if task_name == 'Task':  # Skip header row
            return False
            
        # Skip summary rows
        skip_prefixes = ['Subtotal', 'Day total', 'Hours total']
        if any(task_name.startswith(prefix) for prefix in skip_prefixes):
            return False
            
        return True

    def _get_task_time(self, row) -> float:
        """Get task time by validating total against daily breakdowns."""
        try:
            # Get the total time from column 2
            total_time = float(row[2]) if pd.notna(row[2]) else 0.0
            
            # Calculate sum of daily values (columns 4-10 for Sun-Sat)
            daily_times = [float(t) if pd.notna(t) else 0.0 for t in row[4:11]]
            daily_sum = sum(daily_times)
            
            # If there's a significant difference and we have daily values, use the daily sum
            if daily_sum > 0 and abs(total_time - daily_sum) > 0.01:  # Allow for small floating point differences
                logger.warning(f"Time mismatch for task {row[1]}: total={total_time}, daily sum={daily_sum}")
                return daily_sum
                
            return total_time
        except (ValueError, TypeError):
            logger.warning(f"Invalid time value for task {row[1]}: {row[2]}")
            return 0.0

    def transform(self) -> pd.DataFrame:
        """
        Reads the CSV and transforms it to task-based weekly format.
        Handles both simple (Task,Week,Value) and complex Timeflip2 formats.
        Returns transformed DataFrame.
        """
        try:
            # First try reading as simple CSV
            try:
                df = pd.read_csv(self.input_file)
                if all(col in df.columns for col in ['Task', 'Week', 'Value']):
                    result = self._transform_simple_format(df)
                    if result.empty:
                        return pd.DataFrame(columns=['Task', 'Week 1'])
                    return result
            except Exception:
                pass

            # If that fails, try Timeflip2 format
            df = pd.read_csv(self.input_file, sep=';', header=None)

            # Extract weekly sections
            weeks = self._parse_weeks(df)

            # Process each week's data
            all_tasks = {}
            week_dates = []  # Store week dates in order

            for week_num, (date, week_df) in enumerate(weeks):
                week_dates.append(date)  # Store the date
                # Process task rows
                for idx, row in week_df.iterrows():
                    if self._is_task_row(row):
                        task_name = self._clean_task_name(row)
                        if task_name:
                            if task_name not in all_tasks:
                                # Initialize with zeros for all previous weeks
                                all_tasks[task_name] = [0.0] * week_num
                            time_value = self._get_task_time(row)
                            all_tasks[task_name].append(time_value)
                
                # Ensure all tasks have a value for this week
                for task in all_tasks:
                    if len(all_tasks[task]) <= week_num:
                        all_tasks[task].append(0.0)

            # Handle empty data
            if not all_tasks:
                logger.warning("No tasks found in the input file")
                return pd.DataFrame(columns=['Task', 'Week 1'])

            # Create result DataFrame
            result_df = pd.DataFrame.from_dict(all_tasks, orient='index')
            result_df.columns = [self._format_week_header(date, i+1) for i, date in enumerate(week_dates)]
            result_df.index.name = 'Task'

            return result_df

        except Exception as e:
            logger.error(f"Error transforming Timeflip2 data: {str(e)}")
            raise

    def save(self, df: pd.DataFrame, output_file: Union[str, Path]) -> None:
        """Saves the transformed DataFrame to a CSV file."""
        try:
            # Add total row
            df.loc['Total'] = df.sum()
            
            output_path = Path(output_file)
            df.to_csv(output_path)
            logger.info(f"Successfully saved transformed data to {output_path}")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise