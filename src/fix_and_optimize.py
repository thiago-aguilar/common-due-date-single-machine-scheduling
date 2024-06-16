import numpy as np
from .lp_problem import ProblemEvaluator
import pandas as pd

class FixAndOptimize:

    def __init__(self, initial_solution_df, due_date, solver, initial_obj):
        self.task_df = initial_solution_df.copy()
        self.current_solution_df = initial_solution_df      
        self.current_obj = initial_obj  
        self.due_date = due_date

        self.milp_problem_evaluator = ProblemEvaluator(initial_solution_df, due_date, problem_type='MILP', solver=solver)

        # Algorithm control attributes
        self.window_size = 10
        self.current_index_offset = 0
        self.solution_trace_df = self.task_df[['task_id']].rename(columns={'task_id': 'solution_0'})
        self.solution_trace_obj = [initial_obj]
        self.current_sol_trace = 1

    def run(self):
        
        # Initialize variable for stop criteria
        stop = False
        it = 0

        while not stop:

            # Fix from current index offset + window size
            window_begin = self.current_index_offset
            window_end = window_begin + self.window_size 

            # Get Free and fixed tasks DF
            self.current_solution_df['current_d'] = self.current_solution_df['p'].cumsum()
            fixed_tasks = pd.concat([
                self.current_solution_df[0:window_begin], 
                self.current_solution_df[window_end:]
            ])

            # Free all tasks
            self.milp_problem_evaluator.free_all_tasks()

            # Fix tasks of current window
            for idx, row_to_fix in fixed_tasks.iterrows():
                task_id = row_to_fix['task_id']
                task_end = row_to_fix['current_d']

                self.milp_problem_evaluator.fix_task(
                    task_id=task_id,
                    task_end=task_end
                )
            
            # Solve model for current window
            new_obj, new_offset = self.milp_problem_evaluator.solve_model()
            new_solution_df = self.milp_problem_evaluator.get_solution_df()

            # Update current solution
            if (new_obj < self.current_obj):
                self.current_solution_df = new_solution_df
                self.current_obj = new_obj

            # Update solution trace
            self.solution_trace_obj.append(self.current_obj)
            self.solution_trace_df['solution_' + str(int(self.current_sol_trace))] = list(self.current_solution_df['task_id'])
            self.current_sol_trace += 1
            
            # Update window offset
            self.current_index_offset += 5

            # Check for stop criteria
            if (self.current_index_offset) >= len(self.current_solution_df):
                stop = True
            else:
                it += 1

            len_df = len(self.current_solution_df)
            print(f'Iteration: {it} | Obj: {self.current_obj} | Index offset: {self.current_index_offset} | Lenght {len_df}')
            
        return self.current_obj, self.current_solution_df
        
        