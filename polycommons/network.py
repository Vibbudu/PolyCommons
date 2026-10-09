"""Complex network generation, community structures, and dynamic rewiring (social ostracism)."""

from typing import Dict, List, Optional, Set, Tuple
import networkx as nx
import numpy as np
from polycommons.config import NetworkConfig


class SocialNetwork:
    """Manages the agent interaction graph, community partitions, and dynamic rewiring."""

    def __init__(self, n_agents: int, config: NetworkConfig, seed: Optional[int] = None):
        self.n_agents = n_agents
        self.config = config
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.graph: nx.Graph = nx.Graph()
        self.community_map: Dict[int, int] = {}  # agent_id -> community_id
        self._build_graph()

    def _build_graph(self) -> None:
        """Constructs graph topology according to configuration."""
        topo = self.config.topology.lower()

        if topo == "stochastic_block":
            # Polycentric community structure
            n_comm = max(1, self.config.n_communities)
            sizes = [self.n_agents // n_comm] * n_comm
            remainder = self.n_agents - sum(sizes)
            for i in range(remainder):
                sizes[i] += 1

            p_matrix = np.full((n_comm, n_comm), self.config.p_out)
            np.fill_diagonal(p_matrix, self.config.p_in)
            
            # Seed networkx stochastic block model
            g = nx.stochastic_block_model(sizes, p_matrix.tolist(), seed=self.seed)
            self.graph = nx.Graph(g)
            
            # Map communities
            idx = 0
            for c_id, s in enumerate(sizes):
                for _ in range(s):
                    self.community_map[idx] = c_id
                    idx += 1

        elif topo == "small_world":
            k = max(2, min(self.config.k_neighbors, self.n_agents - 1))
            if k % 2 != 0:
                k += 1
            self.graph = nx.watts_strogatz_graph(
                n=self.n_agents, k=k, p=self.config.rewire_prob, seed=self.seed
            )
            # Assign communities uniformly for modular analysis
            n_comm = max(1, self.config.n_communities)
            for i in range(self.n_agents):
                self.community_map[i] = i % n_comm

        elif topo == "scale_free":
            m = max(1, min(self.config.m_attach, self.n_agents - 1))
            self.graph = nx.barabasi_albert_graph(n=self.n_agents, m=m, seed=self.seed)
            n_comm = max(1, self.config.n_communities)
            for i in range(self.n_agents):
                self.community_map[i] = i % n_comm

        else:  # Default random regular
            d = max(2, min(self.config.k_neighbors, self.n_agents - 1))
            if (self.n_agents * d) % 2 != 0:
                d = max(2, d - 1)
            self.graph = nx.random_regular_graph(d=d, n=self.n_agents, seed=self.seed)
            n_comm = max(1, self.config.n_communities)
            for i in range(self.n_agents):
                self.community_map[i] = i % n_comm

        # Ensure no self loops
        self.graph.remove_edges_from(nx.selfloop_edges(self.graph))

    def get_neighbors(self, agent_id: int) -> List[int]:
        """Returns list of neighbor agent indices."""
        return list(self.graph.neighbors(agent_id))

    def get_community(self, agent_id: int) -> int:
        """Returns community ID for a given agent."""
        return self.community_map.get(agent_id, 0)

    def rewire_ostracism(
        self,
        agent_id: int,
        target_defector_id: int,
        cooperator_ids: List[int],
        rewire_prob: float,
    ) -> bool:
        """With probability rewire_prob, severs edge with defector and connects to a cooperator."""
        if not self.graph.has_edge(agent_id, target_defector_id):
            return False

        if self.rng.random() >= rewire_prob:
            return False

        # Candidates: cooperators not already connected to agent_id and not self
        current_neighbors = set(self.graph.neighbors(agent_id))
        candidates = [
            c for c in cooperator_ids
            if c != agent_id and c not in current_neighbors
        ]

        if candidates:
            # Prefer cooperator in the same community if available (polycentric loyalty)
            same_comm = [c for c in candidates if self.get_community(c) == self.get_community(agent_id)]
            new_partner = self.rng.choice(same_comm) if same_comm else self.rng.choice(candidates)

            self.graph.remove_edge(agent_id, target_defector_id)
            self.graph.add_edge(agent_id, int(new_partner))
            return True

        return False

    def network_metrics(self) -> Dict[str, float]:
        """Calculates topological summary metrics."""
        n_nodes = self.graph.number_of_nodes()
        n_edges = self.graph.number_of_edges()
        if n_nodes == 0 or n_edges == 0:
            return {
                "avg_degree": 0.0,
                "clustering_coef": 0.0,
                "density": 0.0,
            }

        avg_degree = (2.0 * n_edges) / n_nodes
        clustering = float(nx.average_clustering(self.graph))
        density = float(nx.density(self.graph))

        return {
            "avg_degree": avg_degree,
            "clustering_coef": clustering,
            "density": density,
        }
