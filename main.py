from src.problem_creator import ProblemManager


path_data = 'data/sch100k1.csv'

problem_creator = ProblemManager(path_data)
problem_creator.run()