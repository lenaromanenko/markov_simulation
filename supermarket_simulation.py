import pandas as pd
import numpy as np

def construct_freq_df(df_copy):
    '''
    Construct a dataframe such that indices are seperated by delta 1 min from the Market Data
    and put it in a format that markov matrices can be obtained by the pd.crosstab() method
    '''
    
    #This is here in case user passes the actual dataframe, we do not want to modify the actual dataframe
    df = df_copy.copy()
    
    #Blank dataframe placeholder
    frames = pd.DataFrame()
    
    #Set the index to timestamp and convert it to pd timestamp
    #The datatype of the timestamp column should be string 
    
    df.set_index('timestamp', inplace=True)
    df.index = pd.to_datetime(df.index)
    
    #We need to get customer behaviour from entry to checkout for each unique customerr
    for customer in df['customer_no'].unique():
        
        #get customer
        temp_df = df[df['customer_no'] == customer]
        
        #expand timestamp index such that delta T is 1 min, and forward fill isles
        temp_df = temp_df.asfreq('T',method='ffill')
        
        #insert 'entry' 1 min before first isle 
        #re sort index so that times make sense
        #(WE MIGHT NEED TO SKIP THIS NOT SURE IF ENTRY STATE IS REQUIRED)
        temp_df.loc[temp_df.index[0] - pd.to_timedelta('1min')] = [customer,'entry']
        temp_df.sort_index(inplace=True)
        
        #after is simply a shift(-1) of current location
        #checkout location does not have an after, so drop the NA's here
        temp_df['after'] = temp_df['location'].shift(-1)
        temp_df.dropna(inplace=True)
        
        #join the frequency table for each customer
        frames = pd.concat([frames, temp_df], axis=0)
    
    #return the frequency frame 
    return frames

def generate_markov_matrix(df_copy):
    '''
    Generate the Markov Matrix for a Market Data dataframe, structured by constuct_freq_df() function
    NOTE: Columns indicate current state, rows indicate after state, probabilities are read current -> after probability
    sum of columns should add to 1
    '''
    df = df_copy.copy()
    
    return pd.crosstab(df['after'], df['location'], normalize=1)
    
class CustomerOld:
    
    def __init__(self, idn, state, transition_mat):
        self.id = idn
        self.state = state
        self.transition_mat = transition_mat

    def __repr__(self):
        """
        Returns a csv string for that customer.
        """
        return f'{self.id};{self.state}'

    def is_active(self):
        """
        Returns True if the customer has not reached the checkout
        for the second time yet, False otherwise.
        """
        if self.state != 'checkout':
             return True 
        if self.state == 'checkout':
            return False 

    def next_state(self):
        """
        Propagates the customer to the next state
        using a weighted random choice from the transition probabilities
        conditional on the current state.
        Returns nothing.
        """
        # Below are just dummy probas for testing purposes
        #self.state = np.random.choice(['Spices', 'Drinks', 'Fruits', 'Dairy', 'Checkout'], p=[0.2, 0.2, 0.1, 0.2, 0.3])

        dairy_array = self.transition_mat[0,:]
        drinks_array = self.transition_mat[1,:]
        entry_array = self.transition_mat[2,:]
        fruit_array = self.transition_mat[3,:]
        spices_array = self.transition_mat[4,:]

        if self.state == 'dairy':    
            self.state = np.random.choice(['checkout', 'dairy', 'drinks', 'fruit', 'spices'], p=dairy_array)
        if self.state == 'drinks':   
            self.state = np.random.choice(['checkout', 'dairy', 'drinks', 'fruit', 'spices'], p=drinks_array)
        if self.state == 'entry':   
            self.state = np.random.choice(['checkout', 'dairy', 'drinks', 'fruit', 'spices'], p=entry_array)
        if self.state == 'fruit':      
            self.state = np.random.choice(['checkout', 'dairy', 'drinks', 'fruit', 'spices'], p=fruit_array)
        if self.state == 'spices':          
            self.state = np.random.choice(['checkout', 'dairy', 'drinks', 'fruit', 'spices'], p=spices_array)

class Customer:
    
    def __init__(self, idn, state, transition_mat):
        self.id = idn
        self.state = state
        self.transition_mat = transition_mat

        self.tr_array_dict = {
        'dairy' : self.transition_mat[0,:],
        'drinks' : self.transition_mat[1,:],
        'entry' : self.transition_mat[2,:],
        'fruit' : self.transition_mat[3,:],
        'spices' : self.transition_mat[4,:]
        }

    def __repr__(self):
        """
        Returns a csv string for that customer.
        """
        return f'{self.id};{self.state}'

    def is_active(self):
        """
        Returns True if the customer has not reached the checkout
        for the second time yet, False otherwise.
        """
        if self.state != 'checkout':
             return True 
        if self.state == 'checkout':
            return False 

    def next_state(self):
        """
        Propagates the customer to the next state
        using a weighted random choice from the transition probabilities
        conditional on the current state.
        Returns nothing.
        """
  
        self.state = np.random.choice(['checkout', 'dairy', 'drinks', 'fruit', 'spices'], p=self.tr_array_dict[f'{self.state}'])
       
class SuperMarket:
    """manages multiple Customer instances that are currently in the market.
    """

    def __init__(self,transition_matrix):        
        
        #List contains the customer objects
        self.customers = []
     
        #Timing stuff set to some defults, open and close time get their values from the simulate() method when called
        self.open_time = pd.to_datetime('08:00',format='%H:%M')
        self.close_time = pd.to_datetime('17:00',format='%H:%M')
        self.current_time = pd.to_datetime('08:00',format='%H:%M')
        
        #Customer id counter, so that we can consistently assign ids to new customers
        self.last_id = 0
        
        #current and total state during a simulation, total state is initiated like this because it becomes the header of a dataframe
        #when returned from results() method, also it needs to be in 1x3 shapre for np.vstack() to work in update_total_state()
        self.current_state = np.array([])
        self.total_state = np.array(['timestamp','customer_id','customer_location'])

        #transition matrix is assigned when initiating the SuperMarket object
        self.transition_matrix = transition_matrix

    def __repr__(self):
        pass
    
    def write_current_state(self):
        """
        writes the current state during a simulation. Makes rows with current time, customer.id and customer.state of current customers in the market
        """
        self.current_state = np.array([[self.current_time, customer.id, customer.state] for customer in self.customers])
        
    def update_total_state(self):
        """
        updates the total state, this is constantly updated by the current state during a simulation which yields the final data from the simulation
        can be directly accessed or returned as a neat dataframe by the results() method
        """
        self.total_state = np.vstack((self.total_state,self.current_state))
        

    def next_minute(self):
        """propagates all customers to the next state. Adds one minute to current time and updates all customers in the market to their next state
        """
        self.current_time += pd.Timedelta(1,'min')
        #self.customers = [customer.next_state() for customer in self.customers]
        for customer in self.customers:
            customer.next_state()
        #return get_time()

    def add_new_customers(self, n_customers):
        """randomly creates new customers. Adds n_customer number of customers to the current list, they all start at the entry, and assigned 
        an id that is +1 of the current id. Afterwards updates the last id by the latest customer
        """
        self.customers = self.customers + [Customer(self.last_id + 1 + i, 'entry', self.transition_matrix) for i in range(n_customers)]
        self.last_id = self.customers[-1].id

    def remove_exiting_customers(self):
        """removes every customer that is not active any more. Goes through the customer list and if they are active keeps them, 
        the ones in checkout are dropped
        """
        self.customers = [customer for customer in self.customers if customer.is_active() == True]

    def count_checkout(self):
        
        """
        counts the number of customers that are at checkout at the current_state. This would be easier if current_state was a dataframe 
        but since it is a numpy matrix we return the submatrix where the 3rd row is checkout, then we "pseudo count" them by looking at the shape 
        """
        row_mask = (self.current_state[:,2] == 'checkout')
        return self.current_state[row_mask,:].shape[0]

    def simulate(self,initial_customers=20,open_time='8:00',close_time='8:10'):
        """
        Simulates the SuperMarket. Gets initial customers, opening time and closing time from the user
        """
        self.current_state = np.array([])
        self.total_state = np.array(['timestamp','customer_id','customer_location'])
        #Timing stuff
        self.open_time = pd.to_datetime(open_time,format='%H:%M')
        self.close_time = pd.to_datetime(close_time,format='%H:%M')
        self.current_time = self.open_time
        
        #We first add initial_customers of customers at the entry
        self.add_new_customers(initial_customers)
        
        #We simlate until the market closes
        while self.current_time <= self.close_time:
            
            #write the current state and update the total state
            self.write_current_state()
            self.update_total_state()

            #get the number of customers at checkout
            n_checkout = self.count_checkout()

            #remove the customers who are at checkout
            self.remove_exiting_customers()

            #advance to next minute (also updates the states of the current customers)
            self.next_minute()

            #POTENTIAL BUG: this is kind of weird, we shold not need the if statement but if it is not there it somehow adds new customers
            #needs a revisit
            if n_checkout > 0:
                self.add_new_customers(n_checkout)
    
    def results(self):
        '''
        Returns Simulation results in a DataFrame. Simply converts the total_state numpy matrix to a more friendly dataframe
        '''
        data = self.total_state[1:,1:]
        index = self.total_state[1:,0]
        columns = self.total_state[0,1:]
        return pd.DataFrame(data=data,index=index,columns=columns)
