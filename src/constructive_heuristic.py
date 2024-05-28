import numpy as np
class ConstructiveHeuristicFactory:
    def __init__(self,  task_df, due_date) -> None:
        """
        This class implements and adaptation of the constructive heurisc: 
        "Decision Theory for Earliness and Tardiness", published by V. Sridharan and Z. Zhou in 1996
        """
        self.due_date = due_date

        # Tasks information
        self.tasks = task_df['task_id']
        self.task_parameters = task_df.to_dict()
        
        # Control list 
        self.missing_tasks_to_be_scheduled = set(self.tasks)

        # Task_df 
        self.task_df = task_df
        
    def calculate_task_cost_and_time(self, task, t0):
        """ 
        Return tuple (task_cost, task_completion_time)
        """
        C_earliest = t0 + self.task_parameters['p'][task]


        if C_earliest >= self.due_date:
            C_j_chapeu = C_earliest
        else:
            C_star = max(C_earliest, self.due_date)

            if self.task_parameters['alpha'][task] >= self.task_parameters['beta'][task]:
                C_j_chapeu = C_star
            else:

                # Sum missing tasks duration
                filter_missing_tasks = self.task_df['task_id'].isin(self.missing_tasks_to_be_scheduled)
                P = self.task_df[filter_missing_tasks]['p'].sum()

                # Sum missing tasks completion time
                R = t0 * len(self.task_df[filter_missing_tasks])

                # Calculating averages
                P_barra = P / (len(self.task_df[filter_missing_tasks]) - 1)
                R_barra = R / (len(self.task_df[filter_missing_tasks]) - 1)

                # Calculating C
                C_barra = C_star + R_barra + (P - P_barra)/2 + P_barra
                C_shifted = max(C_earliest, (C_star - (C_barra - self.due_date)))

                C_j_chapeu = C_shifted

        # Calculating C_k
        C_k = dict()
        filter_missing_tasks = self.task_df['task_id'].isin(self.missing_tasks_to_be_scheduled)
        P = self.task_df[filter_missing_tasks]['p'].sum()
        for k in self.missing_tasks_to_be_scheduled:
            elements_max = [
                self.due_date,
                t0 + self.task_parameters['p'][k],
                C_j_chapeu + (P - self.task_parameters['p'][k]) / 2 + self.task_parameters['p'][k] 
            ]
            C_k[k] = np.max(elements_max)
        
        # Calculating Kappa
        kappa = 0
        for k in self.missing_tasks_to_be_scheduled:
            current_kappa = max(0, self.task_parameters['alpha'][k] * (self.due_date - C_k[k])) + \
                            max(0, self.task_parameters['beta'][k] * (C_k[k] - self.due_date))

            kappa += current_kappa
        
        return (kappa, C_j_chapeu)

        
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


           
