"""Hồi quy q/Q: form nhận ký tự, vẫn giữ Tab/Backspace/Enter và thoát ngoài form."""
from unittest.mock import Mock

import pygame
import pytest

from main import Game
from scenes.login_scene import LoginScene


def key(code: int, text: str = ''):
    return pygame.event.Event(pygame.KEYDOWN, key=code, unicode=text)


@pytest.mark.parametrize('mode', ['login', 'register'])
def test_q_focus_and_editing(mode):
    pygame.init()
    scene = LoginScene()
    scene.switch_mode(mode)
    user = scene.input_login_user if mode == 'login' else scene.input_reg_user
    password = scene.input_login_pass if mode == 'login' else scene.input_reg_pass
    user.active = True
    password.active = False
    for text in 'qQ':
        assert scene.handle_event(key(pygame.K_q, text)) is None
    assert user.text == 'qQ'
    scene.handle_event(key(pygame.K_TAB))
    assert password.active and not user.active
    for text in 'qQx':
        scene.handle_event(key(ord(text.lower()), text))
    scene.handle_event(key(pygame.K_BACKSPACE))
    assert password.text == 'qQ'
    submit = Mock(return_value={'action': 'test_submit'})
    if mode == 'login':
        scene.do_login = submit
    else:
        scene.do_register = submit
    assert scene.handle_event(key(pygame.K_RETURN)) == {'action': 'test_submit'}
    submit.assert_called_once()


def test_game_routes_q_to_login_but_quits_on_map():
    game = Game.__new__(Game)
    game.scene = 'login'
    game.running = True
    game.transition_alpha = 0
    game.login_scene = Mock()
    game.login_scene.handle_event.return_value = None
    for text in 'qQ':
        game.handle_event(key(pygame.K_q, text))
        assert game.running
    assert game.login_scene.handle_event.call_count == 2
    game.scene = 'map'
    game.handle_event(key(pygame.K_q, 'q'))
    assert not game.running


def test_q_without_form_focus_still_quits():
    pygame.init()
    scene = LoginScene()
    scene.input_login_user.active = scene.input_login_pass.active = False
    assert scene.handle_event(key(pygame.K_q, 'Q')) == {'action': 'quit'}


def test_web_textinput_preserves_case_without_duplicate_keydown(monkeypatch):
    import scenes.login_scene as module
    monkeypatch.setattr(module.sys, 'platform', 'emscripten')
    pygame.init()
    scene = LoginScene()
    scene.handle_event(key(pygame.K_q, 'q'))
    assert scene.input_login_user.text == ''
    scene.handle_event(pygame.event.Event(pygame.TEXTINPUT, text='qQĐ'))
    assert scene.input_login_user.text == 'qQĐ'
    scene.handle_event(key(pygame.K_BACKSPACE))
    assert scene.input_login_user.text == 'qQ'