"""
Configuration for intelligent interruption handling
"""

# Words to ignore when agent is speaking
FILLER_WORDS = {
    'yeah', 'yep', 'yes', 'yup', 'ya',
    'ok', 'okay', 'k', 'kay',
    'hmm', 'mhm', 'mm', 'mmm',
    'uh-huh', 'uh huh', 'uhuh',
    'right', 'sure', 'alright',
    'got it', 'gotcha',
    'i see', 'understood',
    'continue', 'go on', 'go ahead'
}

# Words that always trigger interruption
COMMAND_WORDS = {
    'wait', 'stop', 'hold', 'hold on',
    'no', 'nope', 'nah',
    'pause', 'hang on',
    'actually', 'but', 'however',
    'excuse me', 'sorry', 'pardon',
    'interrupt', 'one second'
}

# How long to wait for transcription (seconds)
TRANSCRIPTION_TIMEOUT = 1.0