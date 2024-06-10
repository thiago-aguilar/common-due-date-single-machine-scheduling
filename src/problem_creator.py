import pandas as pd
from .constructive_heuristic import ConstructiveHeuristicFactory
from .simulated_annealing import SimulatedAnnealing

class ProblemManager:
    def __init__(self, path_data, due_date) -> None:
        self.path_data = path_data

        self.tasks_df = self.initialize_tasks(path_data)
        self.due_date = due_date

    @staticmethod
    def initialize_tasks(path_data):
        tasks_df = pd.read_csv(path_data, header=None)
        df_columns = ['p', 'alpha', 'beta']
        tasks_df.columns = df_columns
        tasks_df['task_id'] = tasks_df.index
        return tasks_df[['task_id'] + df_columns]

    def run(self):
        # Create initial solution with constructive heuristic
        constructive_heuristic = ConstructiveHeuristicFactory(self.tasks_df, self.due_date)
        (sequence_output, completion_time, f) = constructive_heuristic.run()

        # Create SA solver with initial solution previously created
        simulated_annealing_obj = SimulatedAnnealing(task_df=self.tasks_df, due_date=self.due_date, initial_solution=sequence_output)
        simulated_annealing_obj.run()
        breakpoint()
