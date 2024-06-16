from src.problem_creator import ProblemManager

# Adjust instance and Due Date
path_data = 'data/sch200k1.csv'
due_date = 851

# Adjust instance name, and heuristic parameters 
instance_name = '200'
temperature_alpha = 0.8
stages_stop_criteria = 3
initial_acceptance = 0.3
minimum_pct_change = 0.005 # 0.001 for 0.1%
global_minimum_it = 5


id = instance_name      + \
    '_Temp_' + str(temperature_alpha) + \
    '_Stop_' + str(stages_stop_criteria) + \
    '_InitAccept_' + str(initial_acceptance) + \
    '_pctchange_' + str(minimum_pct_change)

heuristic_parameters = {
    'temperature_alpha': temperature_alpha,
    'stages_stop_criteria': stages_stop_criteria,
    'initial_acceptance': initial_acceptance,
    'global_minimum_it': global_minimum_it,
    'minimum_pct_change': minimum_pct_change
}

problem_creator = ProblemManager(path_data, due_date, id, heuristic_parameters)
problem_creator.run()