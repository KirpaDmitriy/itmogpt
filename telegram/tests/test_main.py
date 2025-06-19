
import pytest
import os
from unittest.mock import Mock, AsyncMock, patch
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import bot
from bot import TelegramBot, main
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes
import httpx


class TestTelegramBot:
    
    @pytest.fixture
    def mock_env(self):
        with patch.dict(os.environ, {
            'BOT_TOKEN': 'test_token',
            'BACKEND_URL': 'http://test.com',
            'ALLOWED_USERS': 'user1,user2'
        }):
            yield
    
    @pytest.fixture
    def bot_instance(self, mock_env):
        with patch('bot.Application.builder') as mock_builder:
            mock_app = Mock()
            mock_builder.return_value.token.return_value.build.return_value = mock_app
            return TelegramBot()
    
    def test_is_user_allowed(self, bot_instance):
        user = Mock()
        user.username = 'user1'
        assert bot_instance.is_user_allowed(user) is True
        
        user.username = 'hacker'
        assert bot_instance.is_user_allowed(user) is False
    
    @pytest.mark.asyncio
    async def test_start_command_allowed(self, bot_instance):
        update = Mock()
        update.effective_user.username = 'user1'
        update.message.reply_text = AsyncMock()
        
        await bot_instance.start_command(update, None)
        
        update.message.reply_text.assert_called_once()


def test_main():
    """Простой тест main функции"""
    with patch.dict(os.environ, {
        'BOT_TOKEN': 'test_token',
        'BACKEND_URL': 'http://test.com'
    }):
        with patch('bot.TelegramBot') as mock_bot_class:
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            main()
            
            mock_bot.run.assert_called_once()
