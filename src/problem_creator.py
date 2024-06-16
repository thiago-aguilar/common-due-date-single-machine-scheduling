import pandas as pd
from .constructive_heuristic import ConstructiveHeuristicFactory
from .simulated_annealing import SimulatedAnnealing
from .fix_and_optimize import FixAndOptimize
from pyomo.opt import SolverFactory
import time
import os
from dotenv import load_dotenv
from .utils.excel_writer import ExcelWriter

class ProblemManager:
    def __init__(self, path_data, due_date, run_id: str, heuristic_parameters: dict) -> None:
        self.path_data = path_data

        self.tasks_df = self.initialize_tasks(path_data)
        self.due_date = due_date
        self.heuristic_parameters = heuristic_parameters

        self.run_id = run_id

    @staticmethod
    def initialize_tasks(path_data):
        tasks_df = pd.read_csv(path_data, header=None)
        df_columns = ['p', 'alpha', 'beta']
        tasks_df.columns = df_columns
        tasks_df['task_id'] = tasks_df.index
        return tasks_df[['task_id'] + df_columns]

    def export_resuls(self, SA_trace, FO_trace, results):
        output_directory = 'outputs/' + self.run_id

        # new output directory (if already exists, create suffix for folder name)
        offset_idx = 0
        while not os.path.isdir(output_directory):
            output_directory = 'outputs/' + self.run_id + '_' + str(int(offset_idx))
            offset_idx += 1
        os.makedirs(output_directory)

        # Create file with both outputs in it
        output_file = output_directory + '/output.xlsx'
        excel_writer = ExcelWriter(output_path=output_directory)
        excel_writer.new_sheet(df=results, sheet_name='Final Solution')
        excel_writer.new_sheet(df=SA_trace, sheet_name='Simulated Annealing Trace')
        excel_writer.new_sheet(df=FO_trace, sheet_name='Fix and Optimize Trace')



    def run(self):
        begin = time.time()

        # Create initial solution with constructive heuristic
        constructive_heuristic = ConstructiveHeuristicFactory(self.tasks_df, self.due_date)
        (sequence_output, completion_time, f) = constructive_heuristic.run()
        after_constructive_time = time.time()
        print(f'\nFinished constructive heuristic in {after_constructive_time-begin:.2f} secs')

        # Create SA solver with initial solution previously created
        simulated_annealing_obj = SimulatedAnnealing(
            task_df=self.tasks_df, 
            due_date=self.due_date, 
            initial_solution=sequence_output, 
            heuristic_parameters=self.heuristic_parameters
        )
        SA_obj, SA_solution_df = simulated_annealing_obj.run()
        after_SA_time = time.time()
        print(f'\nFinished simulated annealing in {after_SA_time-after_constructive_time:.2f} secs')
    
        # Run fix-and-optimize Matheuristic with MILP problem
        print(f'\n\nInitializing Fix-and-Optimize algorithm\n')
        load_dotenv('.env')
        fix_and_optimize = FixAndOptimize(initial_solution_df=SA_solution_df, due_date=self.due_date, initial_obj=SA_obj)
        obj_function, solution = fix_and_optimize.run()
        after_FO_time = time.time()
        print(f'\nFinished fix and optimize in {after_FO_time-after_SA_time:.2f} secs')
        breakpoint()

        # Export results from SA and fix-and-optimize 
        print(f'\n\nFinal OBJ function is: {obj_function}')
        SA_trace = simulated_annealing_obj.get_trace()
        FO_trace = fix_and_optimize.get_trace()
        self.export_resuls(
            SA_trace=SA_trace,
            FO_trace=FO_trace,
            results=solution
        )

        
