import pygame
import copy

from src.entities.chess import ChessPuzzle
from src.algorithms.algorithm import ChessSolver
from src.algorithms.Astar import AStarSolver
from src.algorithms.BFS import BFSSolver
from src.algorithms.DFS import DFSSolver
from src.scenes.scene import Scene
from src.ui.element import *
import settings

ALGORITHMS: dict[str, type[ChessSolver]]= {
    "A*": AStarSolver,
    "BFS": BFSSolver,
    "DFS": DFSSolver
}

class AlgorithmHandler:
    def __init__(self, scene, start_y=None):
        self.scene = scene
        self.logic = scene.logic

        if start_y is None:
            self.start_y = scene.MARGIN + scene.SCREEN_HEIGHT // 8 + 10
        else:
            self.start_y = start_y

        self.panel_width = scene.RIGHT_PANEL_WIDTH + 1
        self.base_x = scene.SCREEN_WIDTH - self.panel_width - scene.MARGIN
        self.gap = int(scene.SCREEN_HEIGHT * 0.005)

        adaptive_font_size = round(self.panel_width*0.067+0.9226)
        self.stats_panels = {
            "A*": StatsPanel(self.base_x, 0, self.panel_width, font_size=adaptive_font_size, text_list=["A* Status"]),
            "BFS": StatsPanel(self.base_x, 0, self.panel_width, font_size=adaptive_font_size, text_list=["BFS Status"]),
            "DFS": StatsPanel(self.base_x, 0, self.panel_width, font_size=adaptive_font_size, text_list=["DFS Status"])
        }
        
        self.active_algorithm_name = None 
        self.active_data = None
        self.iterator = None
        self.solutions = {"A*": None, "BFS": None, "DFS": None}

    def start_search(self, algorithm_name):
        print(f"Starting {algorithm_name} search...")
        self.solutions[algorithm_name] = None
        self.active_algorithm_name = algorithm_name
        self.scene.game_won = False
        self.scene.is_playing_solution = False
        self.scene.playback_queue = []

        self.stats_panels[algorithm_name].update_stats(status="Starting...", nodes=0, path=[], max_node_in_memory=0, compute_time=0.0)
        
        algorithm_class = ALGORITHMS[algorithm_name]
        self.iterator = self.logic.solver_iterator(self.scene, algorithm_class)

    def update(self):
        if not self.iterator or self.scene.animating:
            return

        try:
            status, data = next(self.iterator)
            panel = self.stats_panels[self.active_algorithm_name]
            
            if status == "running":
                self.active_data = data
                if settings.SEARCH_ANIMATION: 
                    panel.update_stats(nodes=data[0], max_node_in_memory=data[1], compute_time=data[2], status="Searching...")
            
            elif status == "finished":
                self.solutions[self.active_algorithm_name] = data
                panel.update_stats(nodes=self.active_data[0], max_node_in_memory=self.active_data[1], compute_time=self.active_data[2], path=copy.deepcopy(data.get_final_path()), status="Solved!")
                self.iterator = None 
                self.active_algorithm_name = None 
            
            elif status == "failed":
                panel.update_stats(status="No Path")
                self.iterator = None
                self.active_algorithm_name = None
            
            elif status == "error":
                panel.update_stats(status="Error")
                self.iterator = None
                self.active_algorithm_name = None
                
        except StopIteration:
            self.iterator = None
            self.active_algorithm_name = None

    def draw(self, screen):
        """
        Draws panels and dynamically updates their Y positions 
        so they stack neatly.
        """
        current_y = self.start_y
        order = ["A*", "BFS", "DFS"]  
        for name in order:
            panel = self.stats_panels[name]
            panel.rect.y = current_y
            panel.draw(screen)
            current_y += panel.rect.height + self.gap

    def has_solution(self, algorithm_name):
        solver = self.solutions.get(algorithm_name)
        return solver is not None and len(solver.get_final_path()) > 0

    def get_solution_path(self, algorithm_name):
        return self.solutions[algorithm_name].get_final_path()
    
    def reset(self):
        self.iterator = None
        self.active_algorithm_name = None
        for name in self.solutions:
            self.solutions[name] = None
            self.stats_panels[name].update_stats(status="Ready", nodes=0, path=[], max_node_in_memory=0, compute_time=0.0)