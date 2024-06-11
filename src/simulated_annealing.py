import numpy as np
import pandas as pd
from .lp_problem import ProblemEvaluator
import math

class SimulatedAnnealing:
    neighborhood_types = {1, 2}
    
    def __init__(self, task_df, due_date, initial_solution, solver):
        self.task_df = task_df
        self.due_date = due_date                

        # Initialize Lp ProblemEvaluator
        self.problem_evaluator = ProblemEvaluator(task_df, due_date, problem_type='LP', solver=solver)

        # Initialize SA algorithm information
        self.current_obj, self.tasks_before_dd = self.problem_evaluator.evaluate_solution(initial_solution)
        self.current_solution = initial_solution

        # Global best solution and algorithm trace
        self.global_best_obj = self.current_obj
        self.global_best_sol = self.current_solution
        self.obj_func_trace = [self.current_obj]
        self.obj_func_trace_k = [0]
        self.obj_func_trace_n = [0]
        self.neighborhood_type_trace = [None]

        # Algorithm control attributes
        self.temperature_alpha = 0.8
        self.stages_stop_criteria = 3


    def get_trace(self):
        return pd.DataFrame({
            'OBJ': self.obj_func_trace,
            'K': self.obj_func_trace_k,                
             'N':self.obj_func_trace_n, 
        })

    def run(self):
        """
        Main method for simulated annealing algorithm        
        """
        # Initializations
        k = 0
        temperature = self.define_initial_temperature()
        print(f'Initial temperature defined as {temperature}')
        stop = False
        stages_without_improvement = 0
        

        acceptance_criterion = 0
        while not (stop):
            perturbations_accepted = 0
            last_stage_obj = self.current_obj
            # Calculate perturbations beween temperature changes
            minimum_perturbations = self.calculate_minimum_perturbations(current_temperature=temperature)
            minimum_tested = self.calculate_minimum_tested_perturbations()
            n = 0
            # while perturbations_accepted < minimum_perturbations:
            while (n < minimum_tested) and (perturbations_accepted < minimum_perturbations) :
                
                if (perturbations_accepted < (minimum_perturbations / 3)):
                    neighborhood = 1
                elif (n > (minimum_tested / 2) ) or (perturbations_accepted >= (minimum_perturbations / 3)):
                    neighborhood = 2
                    

                new_solution = self.get_new_solution(neighborhood_type = neighborhood)
                new_solution_obj, new_tasks_before_due_date = self.problem_evaluator.evaluate_solution(new_solution)

                # Calculate delta
                delta_e = new_solution_obj - self.current_obj

                # If improves, store solution
                if delta_e <= 0:
                    self.store_solution(new_solution, new_solution_obj, new_tasks_before_due_date, k, n, neighborhood)
                    perturbations_accepted += 1
                # If it does not improves, check acceptance criterion
                else:
                    acceptance_criterion = np.exp(-delta_e / temperature)
                    random_number = np.random.uniform(0,1)
                    if random_number < acceptance_criterion:
                        self.store_solution(new_solution, new_solution_obj, new_tasks_before_due_date, k, n, neighborhood)
                        perturbations_accepted += 1
                
                print(f'K: {k} | N: {n} | Obj {self.current_obj} | Temperature {temperature} | perturbations_accepted {perturbations_accepted} | minimum tested: {minimum_tested} | minimum perturbations {minimum_perturbations} | neighborhood {neighborhood} | last_acceptance_criterion {acceptance_criterion} | last delta_e {delta_e}')
                n += 1
                
            temperature = self.calculate_next_temperature(temperature)
            k += 1
            

            
            # Check if did not improve
            if (last_stage_obj <= self.current_obj) and temperature < 500:
                stages_without_improvement += 1

                print(f'Simulated Annealing stopped at iteration {k} after {self.stages_stop_criteria} iterations without improvement.' )
                print(f'Best global solution {self.global_best_obj}')
                # Check if reached minimum improvements for stop criteria
                if (stages_without_improvement >= self.stages_stop_criteria) and (temperature < 500):
                    stop = True
                

            else:
                stages_without_improvement = 0

        solution_df = (
            pd.DataFrame({
                'task_id':self.global_best_sol
            })
            .merge(self.task_df, on='task_id')
        )

        return (self.global_best_obj, solution_df)

    def calculate_minimum_tested_perturbations(self):
        return 40 * len(self.current_solution)

    def store_solution(self, new_solution, new_solution_obj, tasks_before_due_date, k, n, neighborhood):

        if new_solution_obj < self.global_best_obj:
            self.global_best_obj = new_solution_obj
            self.global_best_sol = new_solution

        self.current_solution = new_solution
        self.current_obj = new_solution_obj
        self.tasks_before_dd = tasks_before_due_date
        self.obj_func_trace.append(new_solution_obj)
        self.obj_func_trace_k.append(k)
        self.obj_func_trace_n.append(n)
        self.neighborhood_type_trace.append(neighborhood)


    def get_new_solution(self, neighborhood_type) -> list:
        """
        """
        if neighborhood_type not in self.neighborhood_types:
            raise Exception(f'Error: Neighborhood type not implemented')
    
        elif neighborhood_type == 1:
            return_value = self.get_new_solution_type_1()
        elif neighborhood_type == 2:
            return_value = self.get_new_solution_type_2()
        else:
            raise Exception('Error: Neighborhood type not implemented')

        return return_value

    def get_new_solution_type_1(self) -> list:
        current_tasks_before_dd = pd.DataFrame(self.current_solution[:self.tasks_before_dd])
        current_tasks_before_dd.columns = ['task_id']
        current_tasks_before_dd = current_tasks_before_dd.merge(self.task_df[['task_id', 'alpha', 'beta']], on='task_id', how='left')
        
        current_tasks_after_dd = pd.DataFrame(self.current_solution[self.tasks_before_dd:])
        current_tasks_after_dd.columns = ['task_id']
        current_tasks_after_dd = current_tasks_after_dd.merge(self.task_df[['task_id', 'alpha', 'beta']], on='task_id', how='left')
        
        # get random task before dd, and put it after dd. Also get a random task after dd, and put it before dd
        random_row_before = current_tasks_before_dd.sample()
        random_row_after = current_tasks_after_dd.sample()

        # Delete old task after dd, and add new task brought before dd
        current_tasks_after_dd = current_tasks_after_dd.drop(random_row_after.index)
        current_tasks_after_dd = pd.concat([current_tasks_after_dd, random_row_before]).sort_values(by='alpha', ascending=False)
        
        # replace task before with task after 
        current_tasks_before_dd.iloc[random_row_before.index] = random_row_after
        
        # append both tasks and return new solution
        solution = pd.concat([current_tasks_before_dd, current_tasks_after_dd], ignore_index=True)

        return solution['task_id'].to_list()
    
    def get_new_solution_type_2(self) -> list:
        current_tasks_before_dd = pd.DataFrame(self.current_solution[:self.tasks_before_dd])
        current_tasks_before_dd.columns = ['task_id']
        current_tasks_before_dd = current_tasks_before_dd.merge(self.task_df[['task_id', 'alpha', 'beta']], on='task_id', how='left')
        
        current_tasks_after_dd = pd.DataFrame(self.current_solution[self.tasks_before_dd:])
        current_tasks_after_dd.columns = ['task_id']
        current_tasks_after_dd = current_tasks_after_dd.merge(self.task_df[['task_id', 'alpha', 'beta']], on='task_id', how='left')
        
        # get random task before dd, and put it after dd. Also get a random task after dd, and put it before dd
        random_row_before = current_tasks_before_dd.sample()
        # random_row_after = current_tasks_after_dd.sample()

        # Delete old task after dd, and add new task brought before dd
        current_tasks_after_dd = pd.concat([current_tasks_after_dd, random_row_before]).sort_values(by='alpha', ascending=False)
        
        # replace task before with task after 
        current_tasks_before_dd = current_tasks_before_dd.drop(random_row_before.index)
        
        # append both tasks and return new solution
        solution = pd.concat([current_tasks_before_dd, current_tasks_after_dd], ignore_index=True)

        return solution['task_id'].to_list()      
        

    def calculate_minimum_perturbations(self, current_temperature) -> int:
        # Utilizing 1.5n perturbations accepted 
        temp_alteration_factor = 1.5  * len(self.current_solution)
        return temp_alteration_factor
            
    def calculate_next_temperature(self, current_temperature) -> float:
        return self.temperature_alpha * current_temperature
    
    def define_initial_temperature(self) -> float:
        delta_e_array = []
        # Utilize sintetic solution as base obj 
        new_solution = self.get_new_solution(neighborhood_type = 1)
        current_obj, _ = self.problem_evaluator.evaluate_solution(new_solution)

        # Get 100 solutions in same neighborhood type ans calculate temperature
        for n_try in range(100):
            new_solution = self.get_new_solution(neighborhood_type = 1)
            new_solution_obj, _ = self.problem_evaluator.evaluate_solution(new_solution)

            # Calculate delta
            delta_e = new_solution_obj - current_obj
            delta_e_array.append(delta_e)

        # Taxa de aceitação inicial
        tau0 = 0.5
        t = np.mean(np.abs(delta_e_array)) / - math.log(tau0)
        return t
