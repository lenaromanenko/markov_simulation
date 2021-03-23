## Markov Simulation

This project simulates a customer behavior in a supermarket based on Markov Chain. The project has been developed in collaboration with 
<a href="https://github.com/ai-aksoyoglu">@ai-aksoyoglu</a>, <a href="https://github.com/AlphanAksoyoglu">@AlphanAksoyoglu</a> and <a href="https://github.com/pavrmk">@pavrmk</a> and involves the following steps:

### 1. Exploring the data (includes pandas wrangling)
See the notebook in [/data_exploration](https://github.com/lenaromanenko/markov_simulation/tree/main/data_exploration) 
### 2. Calculating transition probabilities (a 5x5 matrix)
See the notebooks in [/transition_probas](https://github.com/lenaromanenko/markov_simulation/tree/main/transition_probas) 
<img src= "https://github.com/lenaromanenko/markov_simulation/blob/main/images/readme_file_images/weekly_markov_matrix.png"/>
### 3. Creating a customer class and implementing MCMC for one customer
See the notebook in [/mcmc_for_one_customer](https://github.com/lenaromanenko/markov_simulation/tree/main/mcmc_for_one_customer)
### 4. Creating a supermarket class that simulates multiple customers and adding it together with the customer class to a module
See the final module [supermarket_simulation.py](https://github.com/lenaromanenko/markov_simulation/blob/main/supermarket_simulation.py) 
### 5. Filling the shelves of a supermarket image and visualizing the supermarket
See the notebook in [/supermarket_visualization](https://github.com/lenaromanenko/markov_simulation/tree/main/supermarket_visualization)
<img src= "https://github.com/lenaromanenko/markov_simulation/blob/main/images/readme_file_images/supermarket_before_after.png"/>
