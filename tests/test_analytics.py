import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from handlers import cmd_today, cmd_last

class TestAnalytics:
    @pytest.fixture
    def mock_update(self):
        update = AsyncMock()
        update.effective_user.id = 111  # allowed user
        return update

    @pytest.fixture
    def mock_context(self):
        return AsyncMock()

    @patch("handlers.sheet")
    async def test_today_empty_sheet(self, mock_sheet, mock_update, mock_context):
        mock_sheet.get_all_values.return_value = []
        await cmd_today(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once_with("No expenses found.")

    @patch("handlers.sheet")
    async def test_today_multiple_categories(self, mock_sheet, mock_update, mock_context):
        today_str = datetime.now().strftime("%d-%m-%Y")
        mock_sheet.get_all_values.return_value = [
            ["Date", "Description", "Category", "Amount", "Account"],
            [f"{today_str} 10:00", "lunch", "Food", "390", "Cash"],
            [f"{today_str} 11:00", "uber", "Transport", "250", "Cash"],
            [f"{today_str} 12:00", "light", "Bills", "636", "BOB"],
        ]
        await cmd_today(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "📅 Today" in call_args
        assert "🍔 Food            ₹390 (31%)" in call_args
        assert "🚕 Transport       ₹250 (20%)" in call_args
        assert "💡 Bills           ₹636 (50%)" in call_args
        assert "💰 Total            ₹1276" in call_args
        assert "📝 Transactions     3" in call_args

    @patch("handlers.sheet")
    async def test_today_single_category(self, mock_sheet, mock_update, mock_context):
        today_str = datetime.now().strftime("%d-%m-%Y")
        mock_sheet.get_all_values.return_value = [
            [f"{today_str} 10:00", "lunch", "Food", "390", "Cash"],
            [f"{today_str} 11:00", "dinner", "Food", "200", "Cash"],
        ]
        await cmd_today(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "🍔 Food            ₹590 (100%)" in call_args
        assert "💰 Total            ₹590" in call_args
        assert "📝 Transactions     2" in call_args

    @patch("handlers.sheet")
    async def test_last_empty_sheet(self, mock_sheet, mock_update, mock_context):
        mock_sheet.get_all_values.return_value = [
            ["Date", "Description", "Category", "Amount", "Account"]
        ]
        await cmd_last(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once_with("No expenses found.")

    @patch("handlers.sheet")
    async def test_last_3_entries(self, mock_sheet, mock_update, mock_context):
        mock_sheet.get_all_values.return_value = [
            ["Date", "Description", "Category", "Amount", "Account"],
            ["1", "Chai", "Food", "20", "Cash"],
            ["2", "Uber", "Transport", "137", "BOB"],
            ["3", "Electricity", "Bills", "636", "BOB"]
        ]
        await cmd_last(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "🕒 Last 3 Expenses" in call_args
        assert "💡 Electricity • ₹636 • BOB" in call_args
        assert "🍔 Chai • ₹20 • Cash" in call_args
        # Electricity is newest (last in list), so it should appear before Chai (which is first)
        assert call_args.index("Electricity") < call_args.index("Chai")

    @patch("handlers.sheet")
    async def test_last_5_entries(self, mock_sheet, mock_update, mock_context):
        mock_sheet.get_all_values.return_value = [
            ["Date", "Description", "Category", "Amount", "Account"],
            ["1", "A", "Food", "10", "Cash"],
            ["2", "B", "Food", "10", "Cash"],
            ["3", "C", "Food", "10", "Cash"],
            ["4", "D", "Food", "10", "Cash"],
            ["5", "E", "Food", "10", "Cash"]
        ]
        await cmd_last(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "🕒 Last 5 Expenses" in call_args
        assert call_args.count("₹10 • Cash") == 5

    @patch("handlers.sheet")
    async def test_last_more_than_5_entries(self, mock_sheet, mock_update, mock_context):
        mock_sheet.get_all_values.return_value = [
            ["Date", "Description", "Category", "Amount", "Account"],
            ["1", "DropMe", "Food", "10", "Cash"],
            ["2", "DropMeToo", "Food", "10", "Cash"],
            ["3", "A", "Food", "10", "Cash"],
            ["4", "B", "Food", "10", "Cash"],
            ["5", "C", "Food", "10", "Cash"],
            ["6", "D", "Food", "10", "Cash"],
            ["7", "E", "Food", "10", "Cash"]
        ]
        await cmd_last(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "🕒 Last 5 Expenses" in call_args
        assert "DropMe" not in call_args
        assert "DropMeToo" not in call_args
        assert "E" in call_args
        assert "A" in call_args

    async def test_help_formatting(self, mock_update, mock_context):
        from handlers import cmd_help
        await cmd_help(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "👋 Expense Tracker" in call_args
        assert "📅 /today" in call_args

    async def test_undo_empty(self, mock_update, mock_context):
        from handlers import cmd_undo, _last_expense
        _last_expense.clear()
        await cmd_undo(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once_with("No recent expense found.")

    @patch("handlers.sheet")
    async def test_undo_success(self, mock_sheet, mock_update, mock_context):
        from handlers import cmd_undo, _last_expense
        import time
        _last_expense[mock_update.effective_user.id] = {"row_index": 5, "timestamp": time.time() - 10}
        await cmd_undo(mock_update, mock_context)
        mock_sheet.delete_rows.assert_called_once_with(5)
        mock_update.message.reply_text.assert_called_once_with("↩️ Last expense removed.")
        assert mock_update.effective_user.id not in _last_expense

    @patch("handlers.sheet")
    async def test_undo_expired(self, mock_sheet, mock_update, mock_context):
        from handlers import cmd_undo, _last_expense
        import time
        _last_expense[mock_update.effective_user.id] = {"row_index": 5, "timestamp": time.time() - 40}
        await cmd_undo(mock_update, mock_context)
        mock_sheet.delete_rows.assert_not_called()
        mock_update.message.reply_text.assert_called_once_with("Undo window expired.")
        assert mock_update.effective_user.id not in _last_expense

    @patch("handlers.sheet")
    async def test_success_message_formatting(self, mock_sheet, mock_update, mock_context):
        from handlers import handle_message
        today_str = datetime.now().strftime("%d-%m-%Y")
        mock_sheet.get_all_values.return_value = [
            ["Date", "Description", "Category", "Amount", "Account"],
            [f"{today_str} 10:00", "lunch", "Food", "390", "Cash"],
        ]
        mock_update.message.text = "chai 20 cash"
        await handle_message(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "✅ Expense Logged" in call_args
        assert "🍔 chai" in call_args
        assert "₹20 • Cash" in call_args
        assert "📅 Today's Total : ₹410" in call_args
        assert "📝 Transactions  : 2" in call_args
