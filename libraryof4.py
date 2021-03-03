import pandas as pd

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
    