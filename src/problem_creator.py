import pandas as pd
from .constructive_heuristic import ConstructiveHeuristicFactory
from .simulated_annealing import SimulatedAnnealing
from .fix_and_optimize import FixAndOptimize
from pyomo.opt import SolverFactory
import time
import os
from dotenv import load_dotenv
from .utils.excel_writer import ExcelWriter
import csv

class ProblemManager:
    def __init__(self, 
                 path_data, 
                 due_date, 
                 run_id: str, 
                 heuristic_parameters: dict,
                 fix_and_optimize_parameters: dict, 
                 has_constructive_heuristic: bool
        ) -> None:
        self.path_data = path_data

        self.tasks_df = self.initialize_tasks(path_data)
        self.due_date = due_date
        self.heuristic_parameters = heuristic_parameters
        self.fix_and_optimize_parameters = fix_and_optimize_parameters

        self.run_id = run_id
        self.has_constructive_heuristic = has_constructive_heuristic

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
        while os.path.isdir(output_directory): 
            output_directory = 'outputs/' + self.run_id + '_' + str(int(offset_idx))
            offset_idx += 1
        os.makedirs(output_directory)

        # Create file with both outputs in it
        output_file = output_directory + '/output.xlsx'
        excel_writer = ExcelWriter(output_path=output_file)
        excel_writer.new_sheet(df=results, sheet_name='Final Solution')
        excel_writer.new_sheet(df=SA_trace, sheet_name='Simulated Annealing Trace')
        excel_writer.new_sheet(df=FO_trace, sheet_name='Fix and Optimize Trace')
        excel_writer.export_results()



    def run(self):
        begin = time.time()

        # Create initial solution with constructive heuristic
        if self.has_constructive_heuristic:
            constructive_heuristic = ConstructiveHeuristicFactory(self.tasks_df, self.due_date)
            (sequence_output, completion_time, f) = constructive_heuristic.run()
            after_constructive_time = time.time()
            print(f'\nFinished constructive heuristic in {after_constructive_time-begin:.2f} secs')
        else:
            after_constructive_time = time.time()
            sequence_output = self.generate_random_solution()

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
        fix_and_optimize = FixAndOptimize(
            initial_solution_df=SA_solution_df, 
            due_date=self.due_date, 
            initial_obj=SA_obj,
            parameters=self.fix_and_optimize_parameters    
        )
        obj_function, solution = fix_and_optimize.run()
        after_FO_time = time.time()
        print(f'\nFinished fix and optimize in {after_FO_time-after_SA_time:.2f} secs')

        # Export results from SA and fix-and-optimize 
        print(f'\n\nFinal OBJ function is: {obj_function}')
        SA_trace = simulated_annealing_obj.get_trace()
        FO_trace = fix_and_optimize.get_trace()
        self.export_resuls(
            SA_trace=SA_trace,
            FO_trace=FO_trace,
            results=solution
        )
        breakpoint()

        # Export csv
        list_tasks = solution['task_id'].to_list()
        with open('AguilarMourao.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(list_tasks)

        
    def generate_random_solution(self):
        task_df = self.tasks_df
        df_return = pd.DataFrame()
        while len(task_df) > 0:
            # Seleciona uma linha aleatória
            sample = task_df.sample()
            
            # Concatena a linha selecionada ao df_return
            df_return = pd.concat([df_return, sample])
            
            # Remove a linha selecionada do task_df
            task_df = task_df.drop(sample.index)

        return df_return['task_id'].to_list()