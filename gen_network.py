
import os
import random
import pygame
#from utils import QuitGame

from multiprocessing import Pool
import concurrent.futures

import sys

import numpy as np
import pickle
'''配置类'''

class NeuralNetwork:
    def __init__(self, input_size, hidden_layers, output_size):
        self.input_size = input_size
        self.hidden_layers = hidden_layers  # 隐藏层的列表，例如：[10, 20] 表示两个隐藏层，分别有 10 和 20 个神经元
        self.output_size = output_size

        # 初始化权重和偏置
        layer_sizes = [input_size] + hidden_layers + [output_size]
        self.weights = []
        self.biases = []
        for i in range(len(layer_sizes) - 1):
            self.weights.append(np.random.randn(layer_sizes[i], layer_sizes[i+1]))
            self.biases.append(np.random.randn(layer_sizes[i+1]))

    def predict(self, inputs):
        activations = inputs
        for weight, bias in zip(self.weights[:-1], self.biases[:-1]):
            activations = np.tanh(np.dot(activations, weight) + bias)
        output = np.dot(activations, self.weights[-1]) + self.biases[-1]
        return output

    def get_weights(self):
        return np.concatenate([w.flatten() for w in self.weights] + [b.flatten() for b in self.biases])

    def set_weights(self, weights):
        layer_sizes = [self.input_size] + self.hidden_layers + [self.output_size]
        offset = 0
        self.weights = []
        self.biases = []
        for i in range(len(layer_sizes) - 1):
            weight_size = layer_sizes[i] * layer_sizes[i+1]
            self.weights.append(weights[offset:offset + weight_size].reshape(layer_sizes[i], layer_sizes[i+1]))
            offset += weight_size
            bias_size = layer_sizes[i+1]
            self.biases.append(weights[offset:offset + bias_size])
            offset += bias_size

    def save_weights(self, filename):
        np.savez(filename, *self.get_weights())

    def load_weights(self, filename):
        data = np.load(filename)
        self.set_weights(data['arr_0'])

class GA:
    def __init__(self,game,population_size, mutation_rate, input_size, hidden_layers, output_size):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = [self.create_individual(input_size, hidden_layers, output_size) for _ in range(population_size)]
        self.game = game
    def create_individual(self, input_size, hidden_layers, output_size):
        nn = NeuralNetwork(input_size, hidden_layers, output_size)
        return nn

    def fitness(self, individual):
        game = self.game
        score = game.run(run_ai=True, individual=individual)
        return score

    def select(self):
        """ sorted_population = sorted(self.population, key=lambda ind: self.fitness(ind), reverse=True)
        return sorted_population[:self.population_size // 2]
        """
        """ with Pool(processes=20) as pool:  # s
            fitness_results = pool.map(self.fitness, self.population)
    
        sorted_population = [x for _, x in sorted(zip(fitness_results, self.population), key=lambda pair: pair[0], reverse=True)]
        return sorted_population[:self.population_size // 2] """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            fitness_results = list(executor.map(self.fitness, self.population))
        
        sorted_population = [x for _, x in sorted(zip(fitness_results, self.population), key=lambda pair: pair[0], reverse=True)]
        return sorted_population[:self.population_size // 2]
    def crossover(self, parent1, parent2):
        parent1_weights = parent1.get_weights()
        parent2_weights = parent2.get_weights()
        crossover_point = random.randint(0, len(parent1_weights) - 1)
        child_weights = np.concatenate((parent1_weights[:crossover_point], parent2_weights[crossover_point:]))
        child = NeuralNetwork(parent1.input_size, parent1.hidden_layers, parent1.output_size)
        child.set_weights(child_weights)
        return child

    def mutate(self, individual):
        weights = individual.get_weights()
        for i in range(len(weights)):
            if random.random() < self.mutation_rate:
                weights[i] += np.random.randn() * 0.1
        individual.set_weights(weights)
        return individual

    def run(self, generations):
        
        for generation in range(generations):
            new_population = []
            selected = self.select()
            
            print(f'Generation {generation}: Best Score {self.fitness(selected[0])}')
            self.save_weights('best.pkl',selected[0])
            
            
            elites = selected[:2]  # 保留前2个最优个体
            new_population.extend(elites)
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(selected, 2)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            self.population = new_population
            

    def save_weights(self, filename,best_individual):
        #best_individual = max(self.population, key=lambda ind: self.fitness(ind))
        weights = best_individual.get_weights()
        try:
            with open(filename, 'wb') as f:
                pickle.dump(weights, f)
        except Exception as e:
            print(f"Error saving weights: {e}")
        print(f"Weights saved to {filename}")

    def load_weights(self, filename, input_size=5, hidden_layers=[16], output_size=2):
        with open(filename, 'rb') as f:
            weights = pickle.load(f)
        individual = NeuralNetwork(input_size, hidden_layers, output_size)
        individual.set_weights(weights)
        print(f"Weights loaded from {filename}")
        return individual