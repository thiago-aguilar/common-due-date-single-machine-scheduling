
class ConstructiveHeuristicFactory:
    def __init__(self,  task_df, due_date) -> None:
        """
        This class implements the constructive heurisc: 
        "Decision Theory for Earliness and Tardiness", published by V. Sridharan and Z. Zhou in 1996
        """
        self.due_date = due_date

        # Tasks information
        self.tasks = task_df['task_id']
        self.task_parameters = task_df.to_dict()
        
        # Control list 
        self.missing_tasks_to_be_scheduled = self.tasks
        
    def calculate_task_cost_and_time(self, task) -> float:
        # TODO calculate cost
        return 
        
    def run(self):
        # Initialize fobj and initial_time
        f = 0

        # Initialize output variables
        sequence_output = []
        completion_time = 0

        for _ in range(len(self.tasks)):
            
            task_cost = dict()
            task_completion_time = dict()
            arg_min = None
            t0 = completion_time

            for j in self.missing_tasks_to_be_scheduled:
                # Calculate task cost
                task_cost[j], task_completion_time[j]  = self.calculate_task_cost_and_time(j, t0)

                # if argmin is none initialize it
                if arg_min == None:
                    arg_min = j
                # if new cost is lower than current lowest update it
                else:
                    if task_cost[j] < task_cost[arg_min]:
                        arg_min = j

            # Update sequence 
            sequence_output.append(arg_min)
            self.missing_tasks_to_be_scheduled.remove(arg_min)
            
            # Update completion_time
            completion_time = task_completion_time[arg_min]

            # Add new task cost to fobj
            f = f + self.task_parameters['alpha'][arg_min] * max(0, self.due_date - completion_time) + \
                    self.task_parameters['beta'][arg_min] * max(0, completion_time - self.due_date)
            
        return sequence_output, completion_time, f


           
