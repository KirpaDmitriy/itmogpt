import pytest
import os
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes
import httpx
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from telegram.bot import TelegramBot, main

class TestTelegramBot:
    
    @pytest.fixture
    def mock_env(self):
        with patch.dict(os.environ, {
            'BOT_TOKEN': 'test_token_123',
            'BACKEND_URL': 'http://test-backend.com',
            'ALLOWED_USERS': 'user1,user2,TestUser'
        }):
            yield
    
    @pytest.fixture
    def bot(self, mock_env):
        with patch('telegram_bot.Application.builder') as mock_builder:
            mock_app = Mock()
            mock_builder.return_value.token.return_value.build.return_value = mock_app
            return TelegramBot()
    
    @pytest.fixture
    def mock_update(self):
        update = Mock(spec=Update)
        update.effective_user = Mock(spec=User)
        update.effective_chat = Mock(spec=Chat)
        update.effective_chat.id = 12345
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        return update
    
    @pytest.fixture
    def mock_context(self):
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = Mock()
        context.bot.send_chat_action = AsyncMock()
        return context

    def test_init_without_token(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="BOT_TOKEN environment variable is required"):
                TelegramBot()

    def test_init_without_backend_url(self):
        with patch.dict(os.environ, {'BOT_TOKEN': 'test'}, clear=True):
            with pytest.raises(ValueError, match="BACKEND_URL environment variable is required"):
                TelegramBot()

    def test_allowed_users_parsing(self, bot):
        assert 'user1' in bot.allowed_users
        assert 'user2' in bot.allowed_users
        assert 'testuser' in bot.allowed_users
        assert len(bot.allowed_users) == 3

    def test_is_user_allowed_with_username(self, bot):
        user = Mock()
        user.username = 'User1'  # разный регистр
        assert bot.is_user_allowed(user) is True

    def test_is_user_allowed_without_username(self, bot):
        user = Mock()
        user.username = None
        assert bot.is_user_allowed(user) is False

    def test_is_user_not_allowed(self, bot):
        user = Mock()
        user.username = 'hacker'
        assert bot.is_user_allowed(user) is False

    @pytest.mark.asyncio
    async def test_start_command_allowed_user(self, bot, mock_update, mock_context):
        mock_update.effective_user.username = 'user1'
        
        await bot.start_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once_with("👋 Отправьте сообщение для обработки.")

    @pytest.mark.asyncio
    async def test_start_command_not_allowed_user(self, bot, mock_update, mock_context):
        mock_update.effective_user.username = 'hacker'
        
        await bot.start_command(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once_with("❌ У вас нет доступа к этому боту.")

    @pytest.mark.asyncio
    async def test_handle_message_not_allowed_user(self, bot, mock_update, mock_context):
        mock_update.effective_user.username = 'hacker'
        mock_update.message.text = 'test message'
        
        await bot.handle_message(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once_with("❌ У вас нет доступа к этому боту.")

    @pytest.mark.asyncio
    async def test_handle_message_success(self, bot, mock_update, mock_context):
        mock_update.effective_user.username = 'user1'
        mock_update.message.text = 'test message'
        
        # Мокаем httpx клиент
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = "Bot response"
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.aenter.return_value.get = AsyncMock(return_value=mock_response)
            
            await bot.handle_message(mock_update, mock_context)
            
            mock_context.bot.send_chat_action.assert_called_once_with(
                chat_id=12345, 
                action="typing"
            )

    @pytest.mark.asyncio
    async def test_handle_message_http_error(self, bot, mock_update, mock_context):
        mock_update.effective_user.username = 'user1'
        mock_update.message.text = 'test message'
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.aenter.return_value.get = AsyncMock(
                side_effect=httpx.HTTPError("Connection failed")
            )
            
            await bot.handle_message(mock_update, mock_context)
            
            calls = mock_update.message.reply_text.call_args_list
            error_calls = [call for call in calls if "❌ Ошибка" in str(call)]
            assert len(error_calls) >= 1

    @pytest.mark.asyncio 
    async def test_handle_message_json_error(self, bot, mock_update, mock_context):
        mock_update.effective_user.username = 'user1'
        mock_update.message.text = 'test message'
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.side_effect = ValueError("Invalid JSON")
            
            mock_client.return_value.aenter.return_value.get = AsyncMock(return_value=mock_response)
            
            await bot.handle_message(mock_update, mock_context)
            
            calls = mock_update.message.reply_text.call_args_list
            error_calls = [call for call in calls if "❌ Ошибка" in str(call)]
            assert len(error_calls) >= 1

    def test_setup_handlers_called(self, mock_env):
        with patch('telegram_bot.Application.builder') as mock_builder:
            mock_app = Mock()
            mock_builder.return_value.token.return_value.build.return_value = mock_app
            
            bot = TelegramBot()
            
            assert mock_app.add_handler.call_count == 2

    def test_run_method(self, bot):
        bot.application.run_polling = Mock()
        
        bot.run()
        
        bot.application.run_polling.assert_called_once_with(drop_pending_updates=True)


class TestMain:
    @patch('telegram_bot.TelegramBot')
    def test_main_function(self, mock_bot_class):
        from telegram_bot import main
        
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        main()
        
        mock_bot_class.assert_called_once()
        mock_bot.run.assert_called_once()


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
