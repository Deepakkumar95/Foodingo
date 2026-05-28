
# src/ml_models/delivery_optimizer.py
import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class QuantumInspiredDeliveryOptimizer:
    def __init__(self, population_size: int = 50, generations: int = 100):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        self.elitism_count = 5
        
    def optimize_delivery_routes(self, deliveries: List[Dict], 
                               delivery_partners: List[Dict]) -> Dict:
        """Optimize delivery routes using quantum-inspired genetic algorithm"""
        logger.info(f"Optimizing routes for {len(deliveries)} deliveries "
                   f"with {len(delivery_partners)} partners")
        
        if not deliveries or not delivery_partners:
            return self.get_empty_solution(deliveries, delivery_partners)
        
        # Initialize population
        population = self.initialize_population(deliveries, delivery_partners)
        
        best_solution = None
        best_fitness = float('inf')
        
        # Evolve population
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            for solution in population:
                fitness = self.calculate_fitness(solution, deliveries, delivery_partners)
                fitness_scores.append((fitness, solution))
                
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_solution = solution.copy()
            
            # Selection
            selected = self.selection(population, fitness_scores)
            
            # Crossover
            offspring = self.crossover(selected)
            
            # Mutation
            mutated_offspring = self.mutation(offspring)
            
            # Create new population
            population = self.create_new_population(population, fitness_scores, mutated_offspring)
            
            # Adaptive mutation rate
            self.adapt_mutation_rate(generation)
            
            if generation % 20 == 0:
                logger.debug(f"Generation {generation}, Best fitness: {best_fitness:.2f}")
        
        logger.info(f"Optimization completed. Best fitness: {best_fitness:.2f}")
        return self.format_solution(best_solution, deliveries, delivery_partners)
    
    def initialize_population(self, deliveries: List[Dict], 
                            delivery_partners: List[Dict]) -> List[Dict]:
        """Initialize population with random solutions"""
        population = []
        
        for _ in range(self.population_size):
            solution = {}
            
            # Assign each delivery to a random partner
            for delivery in deliveries:
                partner = np.random.choice(delivery_partners)
                partner_id = partner['id']
                
                if partner_id not in solution:
                    solution[partner_id] = {
                        'delivery_partner': partner,
                        'deliveries': []
                    }
                
                solution[partner_id]['deliveries'].append(delivery)
            
            population.append(solution)
        
        return population
    
    def calculate_fitness(self, solution: Dict, deliveries: List[Dict], 
                         delivery_partners: List[Dict]) -> float:
        """Calculate fitness score for a solution"""
        total_score = 0
        
        for partner_id, route in solution.items():
            if not route['deliveries']:
                continue
                
            route_score = 0
            
            # Distance cost
            distance = self.calculate_route_distance(route['deliveries'])
            route_score += distance * 0.1  # Cost per km
            
            # Time cost
            time_estimate = self.estimate_route_time(route['deliveries'])
            route_score += time_estimate * 0.5  # Cost per minute
            
            # Delivery time window penalties
            time_penalty = self.calculate_time_window_penalties(route['deliveries'], time_estimate)
            route_score += time_penalty
            
            # Workload balancing
            max_deliveries = route['delivery_partner'].get('max_deliveries', 5)
            if len(route['deliveries']) > max_deliveries:
                route_score += (len(route['deliveries']) - max_deliveries) * 10
            
            # Partner rating factor (prefer higher rated partners)
            partner_rating = route['delivery_partner'].get('rating', 3.0)
            rating_factor = (5.0 - partner_rating) / 2.0  # Lower rating = higher cost
            route_score += rating_factor * 2
            
            total_score += route_score
        
        return total_score
    
    def calculate_route_distance(self, deliveries: List[Dict]) -> float:
        """Calculate total distance for delivery route"""
        if not deliveries:
            return 0.0
        
        total_distance = 0.0
        # Simplified distance calculation
        # In production, this would use proper routing algorithm
        for i in range(len(deliveries) - 1):
            loc1 = deliveries[i]['delivery_address']
            loc2 = deliveries[i + 1]['delivery_address']
            total_distance += self.calculate_distance(loc1, loc2)
        
        return total_distance
    
    def estimate_route_time(self, deliveries: List[Dict]) -> float:
        """Estimate total time for delivery route in minutes"""
        if not deliveries:
            return 0.0
        
        base_time_per_delivery = 10  # minutes per delivery
        travel_time = self.calculate_route_distance(deliveries) * 2  # 2 min per km
        
        return len(deliveries) * base_time_per_delivery + travel_time
    
    def calculate_time_window_penalties(self, deliveries: List[Dict], 
                                      estimated_time: float) -> float:
        """Calculate penalties for missing delivery time windows"""
        penalty = 0.0
        
        for delivery in deliveries:
            promised_time = delivery.get('promised_delivery_time')
            if promised_time:
                # Simplified penalty calculation
                # In production, this would use actual time calculations
                time_difference = abs(estimated_time - promised_time)
                if time_difference > 15:  # More than 15 minutes difference
                    penalty += (time_difference - 15) * 2  # 2 points per minute over
        
        return penalty
    
    def calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two locations in km"""
        # Simplified distance calculation using Euclidean distance
        # In production, use proper geospatial distance calculation
        lat_diff = loc1.latitude - loc2.latitude
        lon_diff = loc1.longitude - loc2.longitude
        return (lat_diff**2 + lon_diff**2)**0.5 * 111  # Approximate km per degree
    
    def selection(self, population: List[Dict], fitness_scores: List[Tuple[float, Dict]]) -> List[Dict]:
        """Select individuals for reproduction using tournament selection"""
        selected = []
        
        for _ in range(len(population)):
            # Tournament selection
            tournament_size = 3
            tournament_indices = np.random.choice(
                len(population), tournament_size, replace=False
            )
            
            # Select the best from tournament
            best_fitness = float('inf')
            best_individual = None
            
            for idx in tournament_indices:
                fitness, individual = fitness_scores[idx]
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_individual = individual
            
            selected.append(best_individual)
        
        return selected
    
    def crossover(self, selected: List[Dict]) -> List[Dict]:
        """Create offspring through crossover"""
        offspring = []
        
        for i in range(0, len(selected), 2):
            if i + 1 < len(selected):
                parent1 = selected[i]
                parent2 = selected[i + 1]
                
                # Single-point crossover
                child1, child2 = self.single_point_crossover(parent1, parent2)
                offspring.extend([child1, child2])
            else:
                offspring.append(selected[i])
        
        return offspring
    
    def single_point_crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """Perform single-point crossover between two parents"""
        # Get all delivery IDs
        all_deliveries = set()
        for route in parent1.values():
            all_deliveries.update(delivery['id'] for delivery in route['deliveries'])
        for route in parent2.values():
            all_deliveries.update(delivery['id'] for delivery in route['deliveries'])
        
        all_deliveries = list(all_deliveries)
        crossover_point = len(all_deliveries) // 2
        
        child1 = {}
        child2 = {}
        
        # First half from parent1, second half from parent2 for child1
        # Vice versa for child2
        for i, delivery_id in enumerate(all_deliveries):
            if i < crossover_point:
                # Assign from parent1 to child1, parent2 to child2
                self.assign_delivery_from_parent(delivery_id, parent1, child1)
                self.assign_delivery_from_parent(delivery_id, parent2, child2)
            else:
                # Assign from parent2 to child1, parent1 to child2
                self.assign_delivery_from_parent(delivery_id, parent2, child1)
                self.assign_delivery_from_parent(delivery_id, parent1, child2)
        
        return child1, child2
    
    def assign_delivery_from_parent(self, delivery_id: str, parent: Dict, child: Dict):
        """Assign delivery to child from parent"""
        for partner_id, route in parent.items():
            for delivery in route['deliveries']:
                if delivery['id'] == delivery_id:
                    if partner_id not in child:
                        child[partner_id] = {
                            'delivery_partner': route['delivery_partner'],
                            'deliveries': []
                        }
                    child[partner_id]['deliveries'].append(delivery)
                    return
    
    def mutation(self, offspring: List[Dict]) -> List[Dict]:
        """Apply mutation to offspring"""
        mutated_offspring = []
        
        for individual in offspring:
            if np.random.random() < self.mutation_rate:
                mutated_individual = self.apply_mutation(individual)
                mutated_offspring.append(mutated_individual)
            else:
                mutated_offspring.append(individual)
        
        return mutated_offspring
    
    def apply_mutation(self, individual: Dict) -> Dict:
        """Apply mutation to an individual"""
        mutated = individual.copy()
        
        # Randomly reassign one delivery to a different partner
        if len(mutated) > 1:
            # Find a delivery to move
            source_partner_id = np.random.choice(list(mutated.keys()))
            if mutated[source_partner_id]['deliveries']:
                delivery_to_move = np.random.choice(mutated[source_partner_id]['deliveries'])
                
                # Choose a different partner
                target_partner_id = np.random.choice([
                    pid for pid in mutated.keys() if pid != source_partner_id
                ])
                
                # Move the delivery
                mutated[source_partner_id]['deliveries'].remove(delivery_to_move)
                mutated[target_partner_id]['deliveries'].append(delivery_to_move)
        
        return mutated
    
    def create_new_population(self, old_population: List[Dict], 
                            fitness_scores: List[Tuple[float, Dict]],
                            mutated_offspring: List[Dict]) -> List[Dict]:
        """Create new population with elitism"""
        # Sort by fitness
        fitness_scores.sort(key=lambda x: x[0])
        
        new_population = []
        
        # Elitism: keep best individuals
        for i in range(self.elitism_count):
            new_population.append(fitness_scores[i][1])
        
        # Add mutated offspring
        new_population.extend(mutated_offspring)
        
        # If needed, add random individuals to maintain population size
        while len(new_population) < self.population_size:
            new_population.append(np.random.choice(old_population))
        
        return new_population[:self.population_size]
    
    def adapt_mutation_rate(self, generation: int):
        """Adaptively adjust mutation rate"""
        # Decrease mutation rate over generations
        self.mutation_rate = 0.1 * (1 - generation / self.generations)
    
    def format_solution(self, solution: Dict, deliveries: List[Dict], 
                       delivery_partners: List[Dict]) -> Dict:
        """Format the solution for output"""
        routes = []
        
        for partner_id, route_data in solution.items():
            route = {
                'delivery_partner': route_data['delivery_partner'],
                'deliveries': route_data['deliveries'],
                'estimated_distance_km': self.calculate_route_distance(route_data['deliveries']),
                'estimated_time_minutes': self.estimate_route_time(route_data['deliveries'])
            }
            routes.append(route)
        
        return {
            'routes': routes,
            'total_deliveries': len(deliveries),
            'total_partners_used': len(routes),
            'total_estimated_distance_km': sum(route['estimated_distance_km'] for route in routes),
            'total_estimated_time_minutes': sum(route['estimated_time_minutes'] for route in routes)
        }
    
    def get_empty_solution(self, deliveries: List[Dict], delivery_partners: List[Dict]) -> Dict:
        """Get empty solution when no optimization is possible"""
        return {
            'routes': [],
            'total_deliveries': len(deliveries),
            'total_partners_used': 0,
            'total_estimated_distance_km': 0,
            'total_estimated_time_minutes': 0
      }
