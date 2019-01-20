# coding: utf-8
# semi-episodic SARSA

import gym
import numpy as np
from tqdm import trange # make your loops show a smart progress meter - just wrap any iterable loop
import random

class Linear_Reg_SARSA:
    def __init__(self,env,weights = None,max_tiles = 2048,num_tilings = 8,features_type = True,basis_type = True):
        self.env = env
        self.maxtiles = max_tiles
        self.numtilings = num_tilings
        if weights == None:
            self.weights = np.zeros(self.maxtiles)
        else:
            self.weights = weights
        self.max_position, self.max_velocity = tuple(self.env.observation_space.high)
        self.min_position, self.min_velocity = tuple(self.env.observation_space.low)
        
        # set up features function
        self.features = []
        self.features_type = features_type
        self.basis_type = basis_type
        if self.basis_type == True:
            if self.features_type == False:
                for i in range(0, self.maxtiles):
                    #k = i if i <= 2 else 2
                    self.features.append(lambda s, i= i : pow(s, i)) # trying S power j  
        else:
            for i in range(0, self.maxtiles):
                self.features.append(lambda s, i=i: np.cos(i * np.pi * s)) # trying fourier basis 



    def Linear_Reg_SARSA(self,epsilon = 0.2,gamma = 0.99,steps = 2000,episodes = 500,learning_rate = 0.001):
        '''
        SARSA algo:
        - Initialize parameters
        - for each episode
            - Initialize state S
            - choose action A using the policy
            - for each step in the episode
                - take a step with action A & get the reward R and next state S'
                - if next state S' is done and terminal
                    - update the weights without using the Q_target
                    - go to next episode
                - choose action A' for the next state S' using the policy
                - update the policy 
                    update the weights with the Q_target 
                - update the action A = A' & the state S = S'
        '''
        self.env.seed(3333)
        np.random.seed(3333)
        # Initialize Parameters
        self.env._max_episode_steps = 1000
        reward_history = []
        successes = 0
        position = []
        first_succeeded_episode = -1

        for episode in trange(episodes): # trange is the range function but with ploting option
            # Initialize state S
            episode_reward = 0
            S = self.env.reset()
            # act non-greedy or state-action have no value # exploration constant 
            if np.random.uniform(0, 1) < epsilon:
                A = np.random.choice(self.env.action_space.n)
            else:
                # TODO: take action from the policy
                A = self.take_action(S)   

            for s in range(steps):
                if (episode % 50 == 0 and episode > 0):
                    if s == 0 or s == 1999:
                        print('successful episodes: {}'.format(successes))
                    #env.render()
                
                # act non-greedy or state-action have no value # exploration constant 
                if np.random.uniform(0, 1) < epsilon:
                    A = np.random.choice(self.env.action_space.n)
            
                # take a step with action A & get the reward R and next state S'  
                S_1, R, done, info = self.env.step(A)
                if done:
                    if S_1[0] >= 0.5:
                        # On successful epsisodes, store the following parameters
                        
                        # Adjust epsilon
                        epsilon *= 0.99

                        # Store episode number if it is the first
                        if successes == 0:
                            first_succeeded_episode = episode

                        # Record successful episode
                        successes += 1
                    
                        #TODO: update your weights
                        change = learning_rate * (R - self.build_q_fun(S, A))
                        delta = self.get_linear_features(S)
                        self.weights += np.dot(delta,change)

                        episode_reward += R
                    
                    # Record history
                    reward_history.append(episode_reward)
                    position.append(S_1[0])

                    break # to terminate the episode
            
                # choose action A' for the next state S' using the policy
                #TODO: choose second action A'
                A_1 = self.take_action(S_1)
                
                # Create target Q value for training the policy
                #TODO: create the q_target value
                qdash = self.build_q_fun(S_1, A_1)
                q = self.build_q_fun(S, A)
                # Update policy
                #TODO: update policy
                q_target = R + gamma * qdash
                change = learning_rate * (q_target - q)
                delta = self.get_linear_features(S)
                self.weights += np.dot(delta,change)

                # Record history
                episode_reward += R
                
                #TODO: calculate S & A 
                S = S_1
                A = A_1          

        print('successful episodes: {:d} - {:.4f}%'.format(successes, successes/episodes*100))
        print(" The first episode that reached the solution is: ",first_succeeded_episode)

    def take_action(self,State):
        ''' take a state observation, returns the best chosen action.'''
        actions_list = [self.build_q_fun(State, action) for action in range(self.env.action_space.n)]
        return np.argmax(actions_list)

    # q(S,A,weights) = weights.T features(S,A)
    def build_q_fun(self,State, action):
        return np.dot(self.weights,self.get_linear_features(State) )

    def get_linear_features(self,state):
        if self.basis_type == True:
            if self.features_type == True:
                a_feature = []
                for i in range(0,self.maxtiles):
                    a_feature.append(pow(state, random.choice([0,1,i]) ) )
                return np.asarray(a_feature)
            else:
                return np.asarray([func(state) for func in self.features])
        else:   
            return np.asarray([func(state) for func in self.features])
    

    def get_special_activities(self,state,n=2,k = 2):
        length = (n+1)**k
        features_universal = []
        current_S_universal = []
        next_S_universal = []
        for iter_ in range(length):
            current_S_universal.append( (pos0**iter_)*(vel0**iter_) )
            next_S_universal.append( (pos1**iter_)*(vel1**iter_) )
        for i in range(length):
            features_universal.append(int(random.choice(current_S_universal)*random.choice(next_S_universal)) )
        return features_universal

    def run_optimal_policy(self,steps = 2000,episodes = 10):
        # after finishing we want to test the policy
        success_counter = 0
        for iter_ in range(episodes):
            S = self.env.reset()
            # choose action A using the policy
            A = self.take_action(S) 
            #env = wrappers.Monitor(env, './semi-sarsa', force=True)  # to take a video snapshot
            for s in range(steps):
                #self.env.render()

                # take a step with action A & get the reward R and next state S'  
                S_1, R, done, info = self.env.step(A)
                if done:
                    if S_1[0] >= 0.5:
                        success_counter += 1
                        print(" **** successful try number {}  in testing phase, Car reached the goal. **** ".format(iter_))
                    break # to terminate the episode

                # choose action A' for the next state S' using the policy
                A = self.take_action(S_1)
                S = S_1

        print(" total succeeded {} out of {}".format(success_counter,episodes))         

if __name__ == '__main__':
    env_name = 'MountainCar-v0'
    env = gym.make(env_name)
    env.seed(3333)    
    EpisodicSARSA = Linear_Reg_SARSA(env,features_type = True,basis_type = False) # for fourier basis_type = False, if feature_type is true choose small features randomly, else normal features 
    EpisodicSARSA.Linear_Reg_SARSA()
    EpisodicSARSA.run_optimal_policy() 