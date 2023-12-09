import asyncio
import unittest
from main import message_ai

class TestMessageAI(unittest.TestCase):
    def test_message_ai(self):
        message = "Hello, AI!"
        result = asyncio.run(message_ai(message))
        self.assertEqual(result, "Hello, AI!")

    def test_message_ai_with_event(self):
        message = '{"event": "meeting"}'
        result = asyncio.run(message_ai(message))
        self.assertEqual(result, "Event processed: meeting")

    def test_message_ai_with_task(self):
        message = '{"task": "cleaning"}'
        result = asyncio.run(message_ai(message))
        self.assertEqual(result, "Task processed: cleaning")

if __name__ == '__main__':
    unittest.main()