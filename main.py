from src.problem_creator import ProblemManager

# Adjust instance and Due Date
path_data = 'data/sch200k1.csv'
due_date = 851

# Adjust instance name, and heuristic parameters 
instance_name = '200'
temperature_alpha = 0.8
stages_stop_criteria = 3
initial_acceptance = 0.3


id = instance_name      + \
    '_Temp_' + str(temperature_alpha) + \
    '_Stop_' + str(stages_stop_criteria) + \
    '_InitAccept_' + str(initial_acceptance)

heuristic_parameters = {
    'temperature_alpha': temperature_alpha,
    'stages_strop_criteria': stages_stop_criteria,
    'initial_acceptance': initial_acceptance
}

problem_creator = ProblemManager(path_data, due_date, id, heuristic_parameters)
problem_creator.run()