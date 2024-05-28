from src.problem_creator import ProblemManager


path_data = 'data/sch100k1.csv'
due_date = 454

problem_creator = ProblemManager(path_data, due_date)
problem_creator.run()