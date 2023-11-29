from priority_queue.heap_priority_queue import HeapPriorityQueue

class LazyStudent:
    def __init__(self, args, hw, t):
        self.args = args  #dictionary with keys denoting arguments, and values denoting its study hours
        self.homeworks = hw  #set where each value is a tuple of arguments
        self.t = t  #maximum number of study hours
        self._arg_value = self._compute_values_for_args() # dict mapping each argument to its value
        self._index_to_arg = self._compute_mapping_index_to_arg() # dict mapping each argument to its index
        self._indices_of_selected_args = set()
        self._heap_of_args = HeapPriorityQueue()
        #print(self._arg_value)

    def _compute_values_for_args(self): #the value of each argument is the probability of passing the exam due to the study of it / the number of its study hours
        arg_value = dict()
        arg_failure_probability = dict()
        for argument in self.args.keys():
            arg_failure_probability[argument] = 1
            for homework in self.homeworks:
                if argument in homework:
                    arg_failure_probability[argument]*=1-1/len(homework)
            arg_value[argument]=(1-arg_failure_probability[argument])/self.args[argument]
        return arg_value
    
    def _compute_mapping_index_to_arg(self):
        index_to_arg = dict()
        i=1
        for argument in self.args.keys():
            index_to_arg[i]=argument
            i+=1
        return index_to_arg
        
    def choose_args(self):     
        # returns the number of arguments to be studied in at most t hours. The selected arguments maximize the probability of passing the exam
        n = len(self.args)+1
        matrix = [[] for i in range(n)]  # the number of selected arguments is on the rows, study hours are on the columns (starting from 0)
        for i in range(n):
            for j in range(self.t+1):
                if i==0:
                    matrix[i].append(0)
                else: 
                    matrix[i].append(None)
            matrix[i][0] = 0
        
        for i in range(1,n):
            for j in range(1,self.t+1):
                if j < self.args[self._index_to_arg[i]]:
                    matrix[i][j] = matrix[i-1][j] # argument i can't be inserted since it has too many study hours
                else: # matrix[i][j] = max(matrix[i-1][j], matrix[i-1][j-study_hours_of_arg_i] + value_of_arg_i)
                    if matrix[i-1][j] > matrix[i-1][j-self.args[self._index_to_arg[i]]]+self._arg_value[self._index_to_arg[i]]:
                        matrix[i][j] = matrix[i-1][j]
                    else:
                        matrix[i][j] = matrix[i-1][j-self.args[self._index_to_arg[i]]]+self._arg_value[self._index_to_arg[i]]
        

        # argument selection (based on the highest value they bring)
        remaining_hours = self.t
        for i in range(n-1,0,-1): # starting from the right-most element of the last row of the matrix
            if matrix[i][remaining_hours] > matrix[i-1][remaining_hours]: # check if argument i contributes to the final value of the solution
                self._indices_of_selected_args.add(i)
                remaining_hours-=self.args[self._index_to_arg[i]]
        
        # build an HeapPriorityQueue to store the arguments. 
        # Heap is better than a Balanced BST since the latter doesn't allow to have multiple elements with the same key and requires more operations for the balancing
        for arg_index in self._indices_of_selected_args:
            arg = self._index_to_arg[arg_index] # value of the item to be inserted in the heap
            study_hours = self.args[arg]
            key = self.t - study_hours # key of the item to be inserted in the heap. This key adapts the MinPriorityQueue to the problem at hand (instead of using a max-oriented priority queue)
            self._heap_of_args.add(key,arg)

        return len(self._indices_of_selected_args)


    def next_arg(self):     # returns the next argument to study in decreasing order of study hours
        key, val = self._heap_of_args.remove_min()
        return val

if __name__ == "__main__":
    args = {"A": 3, "B": 2, "C": 2, "D": 5, "E": 4}
    homeworks = [("A", "B", "E"), ("B", "C", "D"), ("D", "E")]
    t = 7
    lazy_student = LazyStudent(args, homeworks, t)
    num_args = lazy_student.choose_args()
    
    print("num_args: " + str(num_args))
    for i in range(num_args):
        print("arg chosen:" + lazy_student.next_arg())
    
    



















    