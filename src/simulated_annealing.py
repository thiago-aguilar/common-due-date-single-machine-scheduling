import numpy as np
import pandas as pd
from .lp_problem import LpProblemEvaluator

class SimulatedAnnealing:
    neighborhood_types = {1}
    
    def __init__(self, task_df, due_date, initial_solution):
        self.task_df = task_df
        self.due_date = due_date
        self.current_solution = initial_solution
        self.current_obj

        # Initialize LpProblemEvaluator
        self.problem_evaluator = LpProblemEvaluator(task_df, due_date)

    def run(self):
        """
        Main method for simulated annealing algorithm        
        """
        # Initializations
        k = 0
        temperature = self.define_initial_temperature()
        stop = False
        current_neighborhood_type = 1

        while not (stop):
            m = 0
            iterations = self.calculate_iterations(current_temperature=temperature)

            while (m) <= iterations:
                # Evaluate new solution
                new_solution = self.get_new_solution(neighborhood_type=current_neighborhood_type)
                new_solution_obj = self.problem_evaluator.evaluate_solution(new_solution)

                # Calculate delta
                delta_e = new_solution_obj - self.current_obj

                # If improves, store solution
                if delta_e <= 0:
                    self.store_solution(new_solution, new_solution_obj)
                # If it does not improves, check acceptance criterion
                else:
                    acceptance_criterion = np.exp(-delta_e / temperature)
                    random_number = np.random.uniform(0,1)
                    if random_number < acceptance_criterion:
                        self.store_solution(new_solution, new_solution_obj)

                m += 1
            
            temperature = self.calculate_next_temperature(temperature, k)
            k += 1
            stop = self.evaluate_stop_criteria()

    def evaluate_stop_criteria(self) -> bool:
        # TODO implement
        pass

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

    def get_new_solution_type_1() -> list:
        pass

    def calculate_iterations(self, current_temperature) -> int:
        # TODO implementar M_k
        pass
            
    def calculate_next_temperature(self, current_temperature) -> float:
        # TODO implementar T_k
        pass
    
    def define_initial_temperature(self) -> float:
        # TODO implementar
        pass