import numpy as np
from .lp_problem import ProblemEvaluator
import pandas as pd

class FixAndOptimize:

    def __init__(self, initial_solution_df, due_date, solver):
        self.task_df = initial_solution_df.copy()
        self.current_solution_df = initial_solution_df        
        self.due_date = due_date

        self.milp_problem_evaluator = ProblemEvaluator(initial_solution_df, due_date, problem_type='MILP', solver=solver)

        # Algorithm control attributes
        self.window_size = 10
        self.current_index_offset = 0

    def run(self):
        
        # Initialize variable for stop criteria
        stop = False
        
        while not stop:

            # Fix from current index offset + window size
            window_begin = self.current_index_offset
            window_end = window_begin + self.window_size 

            # Get Free and fixed tasks DF
            free_tasks = self.current_solution_df[window_begin : window_end]    
            fixed_tasks = pd.concat([
                self.current_solution_df[0:window_begin], 
                self.current_solution_df[window_end:]
            ])

            self.milp_problem_evaluator.free_all_tasks()

            fixed_tasks['current_d'] = fixed_tasks['p'].cumsum()
            for idx, row_to_fix in fixed_tasks.iterrows():
                task_id = row_to_fix['task_id']
                task_end = row_to_fix['current_d']

                self.milp_problem_evaluator.fix_task(
                    task_id=task_id,
                    task_end=task_end
                )
            
            new_obj = self.milp_problem_evaluator.solve_model()
