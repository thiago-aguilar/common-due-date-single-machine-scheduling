import pandas as pd
from .constructive_heuristic import ConstructiveHeuristicFactory
from .simulated_annealing import SimulatedAnnealing
from .fix_and_optimize import FixAndOptimize
from pyomo.opt import SolverFactory
import time
from dotenv import load_dotenv

class ProblemManager:
    def __init__(self, path_data, due_date) -> None:
        self.path_data = path_data

        self.tasks_df = self.initialize_tasks(path_data)
        self.due_date = due_date
        self.solver = SolverFactory('gurobi')

    @staticmethod
    def initialize_tasks(path_data):
        tasks_df = pd.read_csv(path_data, header=None)
        df_columns = ['p', 'alpha', 'beta']
        tasks_df.columns = df_columns
        tasks_df['task_id'] = tasks_df.index
        return tasks_df[['task_id'] + df_columns]

    def run(self):
        begin = time.time()

        # Create initial solution with constructive heuristic
        constructive_heuristic = ConstructiveHeuristicFactory(self.tasks_df, self.due_date)
        (sequence_output, completion_time, f) = constructive_heuristic.run()
        after_constructive_time = time.time()
        print(f'\nFinished constructive heuristic in {after_constructive_time-begin:.2f} secs')

        # Create SA solver with initial solution previously created
        simulated_annealing_obj = SimulatedAnnealing(task_df=self.tasks_df, due_date=self.due_date, initial_solution=sequence_output, solver=self.solver)
        SA_obj, SA_solution_df = simulated_annealing_obj.run()
        after_SA_time = time.time()
        print(f'\nFinished simulated annealing in {after_SA_time-after_constructive_time:.2f} secs')
        # # TODO remove mocked solution
        # SA_obj = 84105.0
        # SA_solution_df = pd.read_csv('temp_solution.csv', sep=';')
    
        # Run fix-and-optimize Matheuristic with MILP problem
        load_dotenv('.env')
        fix_and_optimize = FixAndOptimize(initial_solution_df=SA_solution_df, due_date=self.due_date, solver=self.solver, initial_obj=SA_obj)
        obj_function, solution = fix_and_optimize.run()
        after_FO_time = time.time()
        print(f'\nFinished fix and optimize in {after_FO_time-after_SA_time:.2f} secs')
        breakpoint()