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

        for idx, row in df.iterrows():
            if isinstance(row[0], str) and row[0].startswith('Week #'):
                if current_week is not None:
                    weeks.append(pd.DataFrame(current_week))
                current_week = []
            elif current_week is not None:
                current_week.append(row)

        if current_week:
            weeks.append(pd.DataFrame(current_week))

        return weeks

    def _clean_task_name(self, row) -> str:
        """Clean task name by removing leading dash if present."""
        task_name = str(row[1])
        return task_name.strip() if pd.notna(task_name) else None

    def _is_task_row(self, row) -> bool:
        """Check if the row is a valid task row."""
        return (
            pd.notna(row[1]) and  # Task name exists
            pd.notna(row[2]) and  # Time exists
            (pd.isna(row[0]) or str(row[0]).strip() in ['-', '']) and  # First column is '-' or empty
            str(row[1]).strip() != 'Task'  # Not a header row
        )

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

            for week_df in weeks:
                # Find the task rows
                for idx, row in week_df.iterrows():
                    if self._is_task_row(row):
                        task_name = self._clean_task_name(row)
                        if task_name:
                            if task_name not in all_tasks:
                                all_tasks[task_name] = []
                            try:
                                time_value = float(row[2])
                                all_tasks[task_name].append(time_value)
                            except (ValueError, TypeError):
                                logger.warning(f"Invalid time value for task {task_name}: {row[2]}")
                                all_tasks[task_name].append(0.0)

            # Handle empty data
            if not all_tasks:
                logger.warning("No tasks found in the input file")
                return pd.DataFrame(columns=['Task', 'Week 1'])

            # Ensure all tasks have the same number of weeks
            max_weeks = max(len(times) for times in all_tasks.values())
            for task in all_tasks:
                while len(all_tasks[task]) < max_weeks:
                    all_tasks[task].append(0.0)

            # Create result DataFrame
            result_df = pd.DataFrame.from_dict(all_tasks, orient='index')
            result_df.columns = [f'Week {i+1}' for i in range(len(result_df.columns))]
            result_df.index.name = 'Task'

            return result_df

        except Exception as e:
            logger.error(f"Error transforming Timeflip2 data: {str(e)}")
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