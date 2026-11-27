"""Hai pin sát nhau không được làm người chơi vào nhầm địa điểm."""
from types import SimpleNamespace
from unittest.mock import Mock
import pygame
from scenes.map_scene import MapScene


def test_nearest_pin_beats_earlier_label():
    scene=MapScene.__new__(MapScene)
    scene.settings_button=pygame.Rect(1010,34,46,46)
    scene.locations=[{'name':'Ben','x':365,'y':500,'start':1911,
                      'label_rect':pygame.Rect(370,490,150,30)},
                     {'name':'Dinh','x':380,'y':505,'start':1975}]
    scene.status=Mock(return_value='open')
    scene.in_year=Mock(return_value=False)
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(380,505)))
    assert scene.selected_location['name']=='Dinh'
    assert scene.selected_year==1975


def test_timeline_major_year_is_clickable():
    scene = MapScene.__new__(MapScene)
    scene.settings_button = pygame.Rect(1190, 28, 46, 46)
    scene.explore_button = pygame.Rect(804, 486, 424, 50)
    scene.timeline_years = (1911, 1930, 1941, 1945, 1954, 1975)
    scene.locations = []
    scene.selected_location = None
    scene.selected_year = 1914
    scene.message = ""
    # With slider_x = 190 and width = 900, 1930 maps to 190 + (1930-1914)/61 * 900 ≈ 426
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(426, 640))
    scene.handle_event(event)
    assert scene.selected_year == 1930



def test_explore_button_returns_explore_action():
    scene = MapScene.__new__(MapScene)
    scene.settings_button = pygame.Rect(1010, 34, 46, 46)
    scene.explore_button = pygame.Rect(790, 485, 250, 42)
    scene.timeline_years = (1911, 1930, 1941, 1945, 1954, 1975)
    scene.locations = []
    scene.selected_location = {"name": "A"}
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(800, 500))
    assert scene.handle_event(event) == "explore"
