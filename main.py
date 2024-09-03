import json
import random
import asyncio
import time
from flask import Flask
from threading import Thread
from highrise import *
from highrise.models import *
from asyncio import run as arun
from highrise.__main__ import *
from importlib import import_module


class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.word_guessed = False
        self.words = self.load_words()
        self.current_word = None
        self.masked_word = ""
        self.guesses = 0
        self.user_scores = self.load_scores()
        self.start_time = None

    def load_words(self):
        with open('words.json', 'r') as f:
            return json.load(f)

    def load_scores(self):
        try:
            with open('user_scores.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_words(self):
        with open('words.json', 'w') as f:
            json.dump(self.words, f, indent=4)

    def save_scores(self):
        with open('user_scores.json', 'w') as f:
            json.dump(self.user_scores, f, indent=4)

    def debug_print(self, message: str) -> None:
        print(message)

    async def start_game(self):
        self.word_guessed = False
        self.start_time = time.time()
        available_words = [word for word in self.words if not word.get('asked', False)]
        if not available_words:
            await self.highrise.chat("No more words left to guess!")
            return

        selected_word = random.choice(available_words)
        self.current_word = selected_word['word']
        self.masked_word = '_' * len(self.current_word)
        self.guesses = 0

        # Mark the selected word as asked
        for word in self.words:
            if word['word'] == self.current_word:
                word['asked'] = True
                break

        self.save_words()  # Save the updated words list
        definition = next(word['definition'] for word in self.words if word['word'] == self.current_word)
        await self.highrise.chat(f"Definition: {definition}")
        self.debug_print(f"Current word to guess: {self.current_word}")
        await self.highrise.chat(f"\n{self.masked_word} | {self.guesses}/{len(self.current_word)}")
        await self.reveal_letters()

    async def on_chat(self, user: User, message: str) -> None:
        if message.lower().startswith("list"):
            print("List command received!")
            await self.handle_list_command(user)
            return

        if self.word_guessed:
            return  # Ignore messages if the word has already been guessed

        if not self.current_word:
            return  # No game is currently active

        # Only check for the correct answer
        if message.lower() == self.current_word:
            self.word_guessed = True
            elapsed_time = time.time() - self.start_time

            if user.username not in self.user_scores:
                self.user_scores[user.username] = {'score': 0, 'total_time': 0}

            self.user_scores[user.username]['score'] += 1
            self.user_scores[user.username]['total_time'] += elapsed_time

            await self.highrise.chat(f"Congrats {user.username} 🎉! You got a point! The word was '{self.current_word}'!")

            # No removal of word from list, only updating the 'asked' status
            self.save_scores()
            await self.highrise.chat("Get ready!")
            await asyncio.sleep(5)
            await self.start_game()

    async def reveal_letters(self):
        max_reveals = len(self.current_word) - 2  # Don't reveal the last two letters
        await asyncio.sleep(10)

        if self.word_guessed:
            return

        # Reveal the first letter initially
        first_letter = self.current_word[0]
        self.masked_word = first_letter + self.masked_word[1:]
        self.guesses += 1
        await self.highrise.chat(f"\n{self.masked_word} | {self.guesses}/{len(self.current_word)}")

        # Keep revealing letters until the word is fully revealed or the word is guessed
        while self.guesses < max_reveals and "_" in self.masked_word:
            await asyncio.sleep(10)
            if self.word_guessed:
                return

            # Reveal a random unrevealed letter
            unrevealed_positions = [i for i, char in enumerate(self.current_word) if self.masked_word[i] == '_']
            if unrevealed_positions:
                random_position = random.choice(unrevealed_positions)
                self.masked_word = self.masked_word[:random_position] + self.current_word[random_position] + self.masked_word[random_position+1:]
                self.guesses += 1
                await self.highrise.chat(f"{self.masked_word} | {self.guesses}/{len(self.current_word)}")

        # If the word is still not guessed and the last two letters are left unrevealed
        if not self.word_guessed:
            await asyncio.sleep(10)
            await asyncio.sleep(10)  # Wait before finalizing
            await self.highrise.chat(f"Sorry, the word was '{self.current_word}'.")
            # No removal of word from list, only updating the 'asked' status
            self.save_scores()
            await self.highrise.chat("Get ready!")
            await asyncio.sleep(5)
            await self.start_game()

    async def handle_list_command(self, user: User):
        print("Handling list command...")
        sorted_scores = sorted(self.user_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        top_5 = sorted_scores[:5]
        user_rank = next((i + 1 for i, (username, score) in enumerate(sorted_scores) if username == user.username), None)
        
        message = "Top 5 users:\n"
        for rank, (username, score) in enumerate(top_5, start=1):
            message += f"{rank}. {username} - {score['score']} points\n"

        if user_rank:
            if user_rank <= 5:
                message += f"\n{user.username}, you are ranked {user_rank}."
            else:
                message += f"\n{user.username}, you are ranked {user_rank}."
        else:
            message += f"\n{user.username}, you are not ranked yet."

        await self.highrise.chat(message)

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        await self.highrise.tg.create_task(self.highrise.teleport(
            session_metadata.user_id, Position(10.5, 2.0, 9.5, "FrontLeft")))
        await self.highrise.chat("Word bot is online! Let's start playing!")
        await asyncio.sleep(5)
        await self.start_game()


class WebServer():
    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route('/')
        def index() -> str:
            return "Alive"

    def run(self) -> None:
        self.app.run(host='0.0.0.0', port=8080)

    def keep_alive(self):
        t = Thread(target=self.run)
        t.start()


class RunBot():
    room_id = "66cf436f37f8a33c1e82a8dd"
    bot_token = "1fa37219da599c8778ea5fcdb15941b789ad8ac3cafa765216848c903f9966d5"
    bot_file = "main"
    bot_class = "Bot"

    def __init__(self) -> None:
        self.definitions = [
            BotDefinition(
                getattr(import_module(self.bot_file), self.bot_class)(),
                self.room_id, self.bot_token)
        ]

    def run_loop(self) -> None:
        while True:
            try:
                arun(main(self.definitions))
            except Exception as e:
                import traceback
                print("Caught an exception:")
                traceback.print_exc()
                time.sleep(1)
                continue


if __name__ == "__main__":
    WebServer().keep_alive()
    RunBot().run_loop()