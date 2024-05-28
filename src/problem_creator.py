import pandas as pd
from .constructive_heuristic import ConstructiveHeuristicFactory

class ProblemManager:
    def __init__(self, path_data) -> None:
        self.path_data = path_data

        self.tasks_df = self.initialize_tasks(path_data)

    @staticmethod
    def initialize_tasks(path_data):
        tasks_df = pd.read_csv(path_data, header=None)
        df_columns = ['p', 'alpha', 'beta']
        tasks_df.columns = df_columns
        tasks_df['task_id'] = tasks_df.index
        return tasks_df[['task_id'] + df_columns]

    def run(self):
        # Create initial solution with constructive heuristic
        constructive_heuristic = ConstructiveHeuristicFactory(self.tasks_df)
        constructive_heuristic.run()
