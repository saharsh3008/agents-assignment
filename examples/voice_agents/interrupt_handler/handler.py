"""
Intelligent Interruption Handler for LiveKit Agents
"""

import asyncio
import logging
from enum import Enum
from typing import Set

from config import FILLER_WORDS, COMMAND_WORDS

logger = logging.getLogger(__name__)


class AgentState(Enum):
    SPEAKING = "speaking"
    SILENT = "silent"


class InterruptionHandler:
    """Manages context-aware interruption filtering"""
    
    def __init__(self):
        self.state = AgentState.SILENT
        self.filler_words = FILLER_WORDS
        self.command_words = COMMAND_WORDS
        logger.info("InterruptionHandler initialized")
    
    def set_speaking(self, is_speaking: bool):
        """Update agent speaking state"""
        new_state = AgentState.SPEAKING if is_speaking else AgentState.SILENT
        if new_state != self.state:
            logger.info(f"State: {self.state.value} -> {new_state.value}")
            self.state = new_state
    
    def is_speaking(self) -> bool:
        """Check if agent is speaking"""
        return self.state == AgentState.SPEAKING
    
    def _has_command_word(self, text: str) -> bool:
        """Check if text contains command words"""
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        # Check each word
        for word in words:
            if word in self.command_words:
                return True
        
        # Check phrases
        for cmd in self.command_words:
            if cmd in text_lower:
                return True
        
        return False
    
    def _is_only_filler(self, text: str) -> bool:
        """Check if text is only filler words"""
        text_lower = text.lower().strip()
        
        if not text_lower:
            return True
        
        # Check if entire phrase is filler
        if text_lower in self.filler_words:
            return True
        
        # Check if all words are fillers
        words = text_lower.split()
        if not words:
            return True
        
        # Count non-filler words
        non_filler = [w for w in words if w not in self.filler_words]
        return len(non_filler) == 0
    
    def should_process(self, transcription: str) -> bool:
        """
        Determine if transcription should be processed
        
        Returns:
            True: Process the input (allow interruption or respond when silent)
            False: Ignore the input (filler word while speaking)
        """
        if not transcription or not transcription.strip():
            return False
        
        # If agent is SILENT, always process (it's valid user input)
        if not self.is_speaking():
            logger.info(f"✓ Agent silent -> process: '{transcription}'")
            return True
        
        # If agent is SPEAKING, check the content
        has_command = self._has_command_word(transcription)
        only_filler = self._is_only_filler(transcription)
        
        if has_command:
            logger.info(f"✓ Command detected -> interrupt: '{transcription}'")
            return True
        
        if only_filler:
            logger.info(f"✗ Filler ignored while speaking: '{transcription}'")
            return False
        
        # Substantial content -> allow
        logger.info(f"✓ Substantial input -> process: '{transcription}'")
        return True


# Global singleton
_handler = None


def get_handler() -> InterruptionHandler:
    """Get or create handler instance"""
    global _handler
    if _handler is None:
        _handler = InterruptionHandler()
    return _handler