from src.problem_creator import ProblemManager

# Adjust instance and Due Date
path_data = 'data/sch200k1.csv'
due_date = 851

# Adjust instance name
instance_name = '200'

# Consctructive Heuristic Parameters
has_constructive_heuristic = True

# SA heuristic parameters 
temperature_alpha = 0.8
stages_stop_criteria = 3
initial_acceptance = 0.3
minimum_pct_change = 0.005 # 0.001 for 0.1%
global_minimum_it = 5

# Fix-and-Optimize parameters
window_jump = 5
window_size = 10

id = instance_name      + \
    '_Temp_' + str(temperature_alpha) + \
    '_Stop_' + str(stages_stop_criteria) + \
    '_InitAccept_' + str(initial_acceptance) + \
    '_pctchange_' + str(minimum_pct_change) + \
    '_wjump_' + str(window_jump) + \
    '_construcHeur_' + str(has_constructive_heuristic)

heuristic_parameters = {
    'temperature_alpha': temperature_alpha,
    'stages_stop_criteria': stages_stop_criteria,
    'initial_acceptance': initial_acceptance,
    'global_minimum_it': global_minimum_it,
    'minimum_pct_change': minimum_pct_change
}

fix_and_optimize_parameters = {
    'window_jump': window_jump,
    'window_size': window_size
}

problem_creator = ProblemManager(path_data, due_date, id, heuristic_parameters, fix_and_optimize_parameters, has_constructive_heuristic)
problem_creator.run()