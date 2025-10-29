from typing import Tuple # Re-added for the required Tuple hint
from src.gen_hint_word import (
    generate_topic_hidden_word, 
    get_hint,
)
import asyncio

class NamesleLogic:
    def __init__(self):
        self.hidden_word = generate_topic_hidden_word()
        self.current_guess: str = ""
        self.current_hint: str = ""
        self.current_percentage: int = 0
        self.last_percentage: int = 0
        self.max_guesses: int = 6
        self.max_length: int = 50
        self.num_guesses: int = 0
        self.guesses: list[tuple[str,int]] = []
        self.streak: int = 0
        self.max_streak: int = 0
        
    def add_letter(self, letter: str) -> bool:
        valid = letter.isalpha() or letter == ' '
        if not valid or len(letter) != 1:
            print(f"[{letter}] is not a valid letter input.")
            return False
        elif len(self.current_guess) >= self.max_length:
            print(f"Limit of {self.max_length} letters reached.")
            return False
        else:
            if letter== ' ':
                self.current_guess+=' '
            else:
                self.current_guess += letter.upper()
            return True
        
    def remove_letter(self):
        if len(self.current_guess)>0:
            self.current_guess=self.current_guess[:-1]
    
    def get_current_guess(self) -> str:
        return self.current_guess
    
    def get_hidden_topic(self) -> str:
        return self.hidden_topic
    
    def get_hidden_word(self) -> str:
        return self.hidden_word
    
    def get_max_guesses(self) -> int:
        return self.max_guesses
    
    def get_num_guesses(self) -> int:
        return self.num_guesses
    
    def get_max_length(self) -> int:
        return self.max_length
    
    def submit_word(self) -> tuple[str,bool]: # hints word, percentage, win?
        
        guess = self.current_guess.upper()
        if guess == self.hidden_word:
            self.current_guess = "" 
            self.num_guesses += 1
            self.guesses.append((guess,100))
            self.streak+=1
            self.max_streak = max(self.max_streak, self.streak)
            return (self.hidden_word, True) 
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        try:
            hint, percent = loop.run_until_complete(
                get_hint(self.current_guess, self.hidden_word)
            )
        except Exception as e:
            print(f"Error in get_hint: {e}")
            hint, percent = "API_ERROR", 0.0
        percent*=100
        percent=round(percent)
        self.current_guess = "" 
        self.num_guesses += 1 
        self.guesses.append((hint,percent))
        self.last_percentage=self.current_percentage
        self.current_percentage=percent
        if self.current_percentage >= self.last_percentage:
            self.streak+=1
        else: 
            self.streak=0
        self.max_streak = max(self.max_streak, self.streak)
        self.current_hint = hint.upper()
        return (self.current_hint, False) 

