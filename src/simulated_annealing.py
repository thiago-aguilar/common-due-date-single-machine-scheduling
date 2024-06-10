import numpy as np
import pandas as pd
from .lp_problem import ProblemEvaluator

class SimulatedAnnealing:
    neighborhood_types = {1}
    
    def __init__(self, task_df, due_date, initial_solution):
        self.task_df = task_df
        self.due_date = due_date                

        # Initialize Lp ProblemEvaluator
        self.problem_evaluator = ProblemEvaluator(task_df, due_date, problem_type='LP')

        # Initialize SA algorithm information
        self.current_obj = self.problem_evaluator.evaluate_solution(initial_solution)
        self.current_solution = initial_solution
        self.temperature_alpha = 0.9
        self.stages_stop_criteria = 3


    def run(self):
        """
        Main method for simulated annealing algorithm        
        """
        # Initializations
        k = 0
        temperature = self.define_initial_temperature()
        stop = False
        stages_without_improvement = 0

        while not (stop):
            perturbations_accepted = 0
            last_stage_obj = self.current_obj

            # Calculate perturbations beween temperature changes
            minimum_perturbations = self.calculate_minimum_perturbations(current_temperature=temperature)

            while perturbations_accepted < minimum_perturbations:
                
                # Evaluate new solution of neighborhood type 1
                new_solution = self.get_new_solution(neighborhood_type = 1)
                new_solution_obj = self.problem_evaluator.evaluate_solution(new_solution)

                # Calculate delta
                delta_e = new_solution_obj - self.current_obj

                # If improves, store solution
                if delta_e <= 0:
                    self.store_solution(new_solution, new_solution_obj)
                    perturbations_accepted += 1
                # If it does not improves, check acceptance criterion
                else:
                    acceptance_criterion = np.exp(-delta_e / temperature)
                    random_number = np.random.uniform(0,1)
                    if random_number < acceptance_criterion:
                        self.store_solution(new_solution, new_solution_obj)
                        perturbations_accepted += 1
                
            temperature = self.calculate_next_temperature(temperature)
            k += 1
            
            # Check if did not improve
            if last_stage_obj <= self.current_solution:
                stages_without_improvement += 1

                print(f'Simulated Annealing stopped at iteration {k} after {self.stages_stop_criteria} iterations without improvement.' )
                # Check if reached minimum improvements for stop criteria
                if stages_without_improvement == self.stages_stop_criteria:
                    stop = True
            
            else:
                stages_without_improvement = 0

    def store_solution(self, new_solution, new_solution_obj):
        self.current_solution = new_solution
        self.current_obj = new_solution_obj

    def get_new_solution(self, neighborhood_type) -> list:
        """
        """
        if neighborhood_type not in self.neighborhood_types:
            raise Exception(f'Error: Neighborhood type not implemented')
    
        elif neighborhood_type == 1:
            self.get_new_solution_type_1()
        else:
            raise Exception('Error: Neighborhood type not implemented')

    def get_new_solution_type_1(self) -> list:
        pass

    def calculate_minimum_perturbations(self, current_temperature) -> int:
        # Utilizing 12n perturbations accepted 
        temp_alteration_factor = 12  * len(self.current_solution)
        return temp_alteration_factor
            
    def calculate_next_temperature(self, current_temperature) -> float:
        return self.temperature_alpha * current_temperature
    
    def define_initial_temperature(self) -> float:
        # TODO implementar
        pass