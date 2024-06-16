import pandas as pd
import numpy as np
from pprint import pprint
import pyomo.environ as pyo
from math import isfinite
from pyomo.opt import SolverStatus, TerminationCondition
# import highspy
from pyomo.contrib import appsi
from pyomo.contrib.iis import write_iis
from pyomo.core import ComponentUID
from pyomo.opt import SolverFactory
import itertools

class ProblemEvaluator:
    def __init__(self, task_df, due_date, solver, problem_type='LP'):
        self.task_df = task_df.set_index('task_id')
        self.due_date = due_date
        self.problem_type = problem_type

        self.create_initial_model()
        self.solver = solver

    def evaluate_solution(self, solution_to_evaluate) -> float:
        solution_df = self.fix_d_solution(solution_to_evaluate)
        
        results = self.solver.solve(self.model, tee=False)
        if str(results['Solver'].Termination_condition.value) == 'optimal':
            obj_function = pyo.value(self.model.obj)
            offset = pyo.value(self.model.offset)
            solution_df['task_deliver_time'] = solution_df['p_cumsum'] + offset
            solution_df['task_before_due_date'] = solution_df['task_deliver_time'] <= self.due_date
            tasks_before_dd = solution_df['task_before_due_date'].sum()
            return obj_function, tasks_before_dd 
        else:
            raise Exception('Error when evaluation solution')
    
    def print_d_bounds(self):
        for i in self.model.d:
            print(f"d[{i}] lower bound: {self.model.d[i].lb}, upper bound: {self.model.d[i].ub}")

    def solve_model(self):
        results = self.solver.solve(self.model, tee=True)

        if str(results['Solver'].Termination_condition.value) == 'optimal':
            obj_function = pyo.value(self.model.obj)
            offset = pyo.value(self.model.offset)
            
            return obj_function, offset
        else:
            raise Exception('Error when evaluation solution')

    def fix_d_solution(self, solution_to_evaluate):
        new_solution_df = pd.DataFrame({
            'task_id':solution_to_evaluate
        }).set_index('task_id')

        merged_df = new_solution_df.join(self.task_df[['p', 'alpha', 'beta']])
        merged_df['p_cumsum'] = merged_df['p'].cumsum()
        
        d_dict = merged_df.to_dict()['p_cumsum']
        for task_id, task_d in d_dict.items():
            self.model.d[task_id] = task_d
        return merged_df
        
        

    def create_initial_model(self):

        # INITIALIZE AND POPULATE PYOMO LP PROBLEM
        self.model = pyo.ConcreteModel()
        self.create_sets()
        self.create_decision_variables()
        self.define_parameters()
        self.define_constraints()
        self.define_obj_function()

    def create_sets(self):
        # Tasks to be scheduled 
        self.model.I = set(self.task_df.index)

        # Combinations of tasks for constraints in case is MILP
        if self.problem_type == 'MILP':
            self.model.Omega = set(itertools.permutations(self.model.I, 2))

    def create_decision_variables(self):

        if self.problem_type == 'MILP':
            self.model.d = pyo.Var(self.model.I, within=pyo.NonNegativeReals)
        elif self.problem_type == 'LP':
            self.model.d = pyo.Param(self.model.I, mutable=True, initialize=0)
            pass
        else:
            raise Exception('Unsupported problem type for variable d')

        self.model.e = pyo.Var(self.model.I, within=pyo.NonNegativeReals)

        self.model.t = pyo.Var(self.model.I, within=pyo.NonNegativeReals)

        if self.problem_type == 'MILP':
            self.model.b = pyo.Var(self.model.Omega, within=pyo.Binary)

        self.model.offset = pyo.Var(within=pyo.NonNegativeReals, bounds=(0, self.due_date))
    
    def free_all_tasks(self):
        for task_id in self.task_df.index:
            self.model.d[task_id].setlb(0)
            self.model.d[task_id].setub(np.inf)


    def fix_task(self, task_id, task_end):
        self.model.d[task_id].bounds = (task_end, task_end)

    def define_parameters(self):
        task_df_dict = self.task_df.to_dict()
        
        self.model.p = task_df_dict['p']
        self.model.due_date = self.due_date
        self.model.alpha = task_df_dict['alpha']
        self.model.beta = task_df_dict['beta']

        if self.problem_type == 'MILP':
            self.model.bigM = self.task_df['p'].sum() * 2 + 1e-5

    def define_constraints(self):

        if self.problem_type == 'LP': 
            if hasattr(self.model, 'C1'):
                self.model.del_component(self.model.C1)         
            self.model.C1 = pyo.Constraint(self.model.I, rule=self.rule_constraint_c1_LP)

            if hasattr(self.model, 'C2'):
                self.model.del_component(self.model.C2)     
            self.model.C2 = pyo.Constraint(self.model.I, rule=self.rule_constraint_c2_LP)
        
        elif self.problem_type == 'MILP':
            self.model.C1 = pyo.Constraint(self.model.I, rule=self.rule_constraint_c1_MILP)
            self.model.C2 = pyo.Constraint(self.model.I, rule=self.rule_constraint_c2_MILP)
            self.model.C3 = pyo.Constraint(self.model.Omega, rule=self.rule_constraint_c3_MILP)
            self.model.C4 = pyo.Constraint(self.model.Omega, rule=self.rule_constraint_c4_MILP)
    
    @staticmethod
    def rule_constraint_c1_LP(M, i):
        LHS = M.e[i]
        RHS = M.due_date - M.d[i] - M.offset
        return LHS >= RHS
        
    @staticmethod
    def rule_constraint_c1_MILP(M, i):
        LHS = M.e[i]
        RHS = M.due_date - M.d[i] - M.offset
        return LHS >= RHS
            
    @staticmethod
    def rule_constraint_c2_LP(M, i):
        LHS = M.t[i]
        RHS = M.d[i] - M.due_date + M.offset
        return LHS >= RHS
    
    @staticmethod
    def rule_constraint_c2_MILP(M, i):
        LHS = M.t[i]
        RHS = M.d[i] - M.due_date + M.offset
        return LHS >= RHS

    @staticmethod
    def rule_constraint_c3_MILP(M, i, j):
        LHS = M.d[i]
        RHS = (M.d[j] - M.p[j]) + M.bigM * (1 - M.b[(i,j)])
        return LHS <= RHS

    @staticmethod
    def rule_constraint_c4_MILP(M, i, j):
        LHS = M.d[i] - M.p[i]
        RHS = M.d[j] - M.bigM * M.b[(i,j)]
        return LHS >= RHS

    def define_obj_function(self):
        self.model.obj = pyo.Objective(rule=self.objective_function_rule)

    @staticmethod
    def objective_function_rule(M):
        obj = sum(M.alpha[i] * M.t[i] + M.beta[i] * M.e[i] for i in M.I)
        return obj

