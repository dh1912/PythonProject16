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