
import pytest
import os
import sys
from unittest.mock import Mock, AsyncMock, patch

# Мокаем переменные окружения ДО импорта bot.py
with patch.dict(os.environ, {
    'BOT_TOKEN': 'test_token',
    'BACKEND_URL': 'http://test.com',
    'ALLOWED_USERS': 'user1,user2'
}):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    import bot
    from bot import TelegramBot, main


def test_is_user_allowed():
    """Простой синхронный тест"""
    with patch('bot.Application.builder'):
        bot_instance = TelegramBot()
        
        user = Mock()
        user.username = 'user1'
        assert bot_instance.is_user_allowed(user) is True
        
        user.username = 'hacker'
        assert bot_instance.is_user_allowed(user) is False


def test_main():
    """Тест main функции"""
    with patch('bot.TelegramBot') as mock_bot_class:
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        main()
        
        mock_bot.run.assert_called_once()
