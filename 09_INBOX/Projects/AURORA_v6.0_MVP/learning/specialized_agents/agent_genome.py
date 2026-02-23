"""
Agent Genome - AURORA v6.0 MVP
DNA evolutivo dos agentes
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import logging
import copy

logger = logging.getLogger("AGENT_GENOME")


class AgentGenome:
    """
    DNA Evolutivo dos Agentes
    
    Responsabilidades:
    - Definir estrutura genética de cada agente
    - Mutação controlada de parâmetros
    - Crossover entre agentes bem-sucedidos
    - Seleção natural baseada em Sharpe
    
    Operações Genéticas:
    - mutate(): Pequenas alterações aleatórias
    - crossover(): Combina genes de dois agentes
    - select(): Escolhe melhores genomas
    """
    
    # Genes base (todos os agentes)
    BASE_GENES = {
        "confidence_threshold": {"min": 0.3, "max": 0.9, "default": 0.6},
        "position_size_factor": {"min": 0.5, "max": 2.0, "default": 1.0},
        "risk_multiplier": {"min": 0.5, "max": 1.5, "default": 1.0},
        "learning_rate": {"min": 0.0001, "max": 0.01, "default": 0.001},
        "exploration_rate": {"min": 0.01, "max": 0.3, "default": 0.1},
        "momentum_weight": {"min": 0.0, "max": 1.0, "default": 0.5},
        "mean_reversion_weight": {"min": 0.0, "max": 1.0, "default": 0.3},
        "trend_weight": {"min": 0.0, "max": 1.0, "default": 0.2}
    }
    
    # Genes específicos por tipo
    SYMBOL_GENES = {
        "XAUUSD": {
            "gold_volatility_factor": {"min": 1.0, "max": 3.0, "default": 1.5},
            "usd_correlation_weight": {"min": 0.1, "max": 0.5, "default": 0.3},
            "atr_multiplier": {"min": 1.0, "max": 4.0, "default": 2.0}
        },
        "EURUSD": {
            "liquidity_preference": {"min": 0.8, "max": 1.5, "default": 1.2},
            "mean_reversion_strength": {"min": 0.3, "max": 1.0, "default": 0.7},
            "news_sensitivity": {"min": 0.1, "max": 0.9, "default": 0.5}
        }
    }
    
    def __init__(self, symbol: str = None):
        self.symbol = symbol
        self.genes = self._create_default_genome(symbol)
        self.fitness = 0.0
        self.generation = 0
        self.mutations_count = 0
        self.created_at = datetime.now()
        
    def _create_default_genome(self, symbol: str = None) -> Dict:
        """Cria genoma padrão"""
        genome = {}
        
        # Genes base
        for gene, config in self.BASE_GENES.items():
            genome[gene] = config["default"]
        
        # Genes específicos do símbolo
        if symbol and symbol in self.SYMBOL_GENES:
            for gene, config in self.SYMBOL_GENES[symbol].items():
                genome[gene] = config["default"]
        
        return genome
    
    def mutate(self, mutation_rate: float = 0.1, mutation_strength: float = 0.2) -> 'AgentGenome':
        """
        Aplica mutação ao genoma
        
        Args:
            mutation_rate: Probabilidade de cada gene mutar
            mutation_strength: Força da mutação (0-1)
            
        Returns:
            Novo genoma mutado
        """
        mutated = AgentGenome(self.symbol)
        mutated.genes = copy.deepcopy(self.genes)
        mutated.generation = self.generation + 1
        
        all_genes = {**self.BASE_GENES}
        if self.symbol and self.symbol in self.SYMBOL_GENES:
            all_genes.update(self.SYMBOL_GENES[self.symbol])
        
        mutations = []
        
        for gene, config in all_genes.items():
            if gene in mutated.genes and np.random.random() < mutation_rate:
                old_value = mutated.genes[gene]
                
                # Mutação gaussiana
                range_size = config["max"] - config["min"]
                mutation = np.random.randn() * range_size * mutation_strength
                
                new_value = old_value + mutation
                new_value = np.clip(new_value, config["min"], config["max"])
                
                mutated.genes[gene] = new_value
                mutations.append((gene, old_value, new_value))
        
        mutated.mutations_count = len(mutations)
        
        if mutations:
            logger.debug(f"Genome mutated: {len(mutations)} genes changed")
        
        return mutated
    
    @staticmethod
    def crossover(parent1: 'AgentGenome', parent2: 'AgentGenome') -> Tuple['AgentGenome', 'AgentGenome']:
        """
        Crossover entre dois genomas (reprodução)
        
        Args:
            parent1: Primeiro pai
            parent2: Segundo pai
            
        Returns:
            Tuple de dois filhos
        """
        if parent1.symbol != parent2.symbol:
            logger.warning("Crossover between different symbols may produce unexpected results")
        
        child1 = AgentGenome(parent1.symbol)
        child2 = AgentGenome(parent2.symbol)
        
        child1.generation = max(parent1.generation, parent2.generation) + 1
        child2.generation = child1.generation
        
        # Crossover uniforme
        for gene in parent1.genes:
            if gene in parent2.genes:
                if np.random.random() < 0.5:
                    child1.genes[gene] = parent1.genes[gene]
                    child2.genes[gene] = parent2.genes[gene]
                else:
                    child1.genes[gene] = parent2.genes[gene]
                    child2.genes[gene] = parent1.genes[gene]
        
        # Fitness inicial é média dos pais
        child1.fitness = (parent1.fitness + parent2.fitness) / 2
        child2.fitness = child1.fitness
        
        logger.debug(f"Crossover produced 2 children (gen {child1.generation})")
        
        return child1, child2
    
    @staticmethod
    def select(population: List['AgentGenome'], n_survivors: int, tournament_size: int = 3) -> List['AgentGenome']:
        """
        Seleção natural - escolhe os melhores
        
        Args:
            population: Lista de genomas
            n_survivors: Número de sobreviventes
            tournament_size: Tamanho do torneio
            
        Returns:
            Lista de genomas selecionados
        """
        survivors = []
        
        for _ in range(n_survivors):
            # Tournament selection
            tournament = np.random.choice(population, size=min(tournament_size, len(population)), replace=False)
            winner = max(tournament, key=lambda g: g.fitness)
            survivors.append(copy.deepcopy(winner))
        
        logger.debug(f"Selection: {len(survivors)} survivors from {len(population)}")
        
        return survivors
    
    def update_fitness(self, sharpe: float, win_rate: float = 0.5, profit_factor: float = 1.0):
        """
        Atualiza fitness do genoma
        
        Fitness = weighted combination of metrics
        """
        self.fitness = (
            sharpe * 0.5 +
            (win_rate - 0.5) * 2 * 0.3 +
            np.log(max(profit_factor, 0.1)) * 0.2
        )
    
    def to_dict(self) -> Dict:
        """Exporta genoma para dict"""
        return {
            "symbol": self.symbol,
            "genes": self.genes,
            "fitness": self.fitness,
            "generation": self.generation,
            "mutations_count": self.mutations_count,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentGenome':
        """Importa genoma de dict"""
        genome = cls(data.get("symbol"))
        genome.genes = data.get("genes", genome.genes)
        genome.fitness = data.get("fitness", 0.0)
        genome.generation = data.get("generation", 0)
        genome.mutations_count = data.get("mutations_count", 0)
        return genome
    
    def __repr__(self):
        return f"AgentGenome({self.symbol}, gen={self.generation}, fitness={self.fitness:.3f})"


class GeneticOptimizer:
    """
    Otimizador Genético para população de agentes
    """
    
    def __init__(
        self,
        population_size: int = 20,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        elitism: int = 2
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism = elitism
        
        self.population: List[AgentGenome] = []
        self.best_genome: AgentGenome = None
        self.generation = 0
        
    def initialize_population(self, symbol: str):
        """Inicializa população aleatória"""
        self.population = []
        
        for _ in range(self.population_size):
            genome = AgentGenome(symbol)
            # Mutação inicial para diversidade
            genome = genome.mutate(mutation_rate=0.5, mutation_strength=0.5)
            self.population.append(genome)
        
        logger.info(f"Initialized population of {self.population_size} genomes for {symbol}")
    
    def evolve(self) -> AgentGenome:
        """
        Executa uma geração de evolução
        
        Returns:
            Melhor genoma da geração
        """
        # Ordenar por fitness
        self.population.sort(key=lambda g: g.fitness, reverse=True)
        
        # Elitismo - manter os melhores
        new_population = self.population[:self.elitism]
        
        # Seleção
        parents = AgentGenome.select(
            self.population,
            self.population_size - self.elitism
        )
        
        # Crossover e mutação
        while len(new_population) < self.population_size:
            if len(parents) >= 2 and np.random.random() < self.crossover_rate:
                p1, p2 = np.random.choice(parents, size=2, replace=False)
                c1, c2 = AgentGenome.crossover(p1, p2)
                new_population.extend([c1.mutate(self.mutation_rate), c2.mutate(self.mutation_rate)])
            else:
                parent = np.random.choice(parents)
                new_population.append(parent.mutate(self.mutation_rate))
        
        # Trim se passou do tamanho
        self.population = new_population[:self.population_size]
        self.generation += 1
        
        # Atualizar melhor
        self.best_genome = max(self.population, key=lambda g: g.fitness)
        
        logger.info(f"Generation {self.generation}: best fitness = {self.best_genome.fitness:.4f}")
        
        return self.best_genome

