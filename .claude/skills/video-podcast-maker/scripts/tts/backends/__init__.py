"""TTS backend registry."""
import json
import os
import sys


def user_prefs_get(*keys):
    """Read nested key from user_prefs.json. Returns None if missing/unreadable."""
    # __file__ = scripts/tts/backends/__init__.py → skill root is four levels up
    skill_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    prefs_path = os.path.join(skill_dir, 'user_prefs.json')
    if not os.path.exists(prefs_path):
        return None
    try:
        with open(prefs_path) as f:
            obj = json.load(f)
        for k in keys:
            if not isinstance(obj, dict):
                return None
            obj = obj.get(k)
        return obj
    except (json.JSONDecodeError, OSError):
        return None


def resolve_backend():
    """Resolve TTS backend with precedence: env TTS_BACKEND > user_prefs.json > 'edge'.

    Returns (name, source) where source is 'env', 'user_prefs', or 'default'.
    """
    env = os.environ.get('TTS_BACKEND')
    if env:
        return env, 'env'
    pref = user_prefs_get('global', 'tts', 'backend')
    if pref:
        return pref, 'user_prefs'
    return 'edge', 'default'


def resolve_speech_rate():
    """Resolve TTS speech rate with precedence: env TTS_RATE > user_prefs.json > '+5%'.

    Returns (rate, source) where source is 'env', 'user_prefs', or 'default'.
    """
    env = os.environ.get('TTS_RATE')
    if env:
        return env, 'env'
    pref = user_prefs_get('global', 'tts', 'rate')
    if pref:
        return pref, 'user_prefs'
    return '+5%', 'default'


def _resolve_voice(backend_name, env_var, default):
    """Resolve voice with precedence: env var > user_prefs.json > hardcoded default."""
    env_val = os.environ.get(env_var)
    pref_val = user_prefs_get('global', 'tts', 'voices', backend_name)
    voice = env_val or pref_val or default
    source = 'env' if env_val else 'user_prefs' if pref_val else 'default'
    print(f"  Voice ({backend_name}): {voice} [from {source}]")
    return voice


BACKENDS = {
    'azure': {
        'module': '.azure',
        'env': ['AZURE_SPEECH_KEY'],
        'import': ('azure.cognitiveservices.speech', 'azure-cognitiveservices-speech',
                    'pip install azure-cognitiveservices-speech'),
        'max_chars': 400,
    },
    'cosyvoice': {
        'module': '.cosyvoice',
        'env': ['DASHSCOPE_API_KEY'],
        'import': ('dashscope', 'dashscope', 'pip install dashscope'),
        'max_chars': 400,
    },
    'edge': {
        'module': '.edge',
        'env': [],
        'import': ('edge_tts', 'edge-tts', 'pip install edge-tts'),
        'max_chars': 400,
    },
    'doubao': {
        'module': '.doubao',
        'env': ['VOLCENGINE_APPID', 'VOLCENGINE_ACCESS_TOKEN'],
        'import': ('requests', 'requests', 'pip install requests'),
        'max_chars': 280,
    },
    'elevenlabs': {
        'module': '.elevenlabs',
        'env': ['ELEVENLABS_API_KEY'],
        'import': ('requests', 'requests', 'pip install requests'),
        'max_chars': 400,
    },
    'openai': {
        'module': '.openai_tts',
        'env': ['OPENAI_API_KEY'],
        'import': ('requests', 'requests', 'pip install requests'),
        'max_chars': 400,
    },
    'google': {
        'module': '.google_tts',
        'env': ['GOOGLE_TTS_API_KEY'],
        'import': ('requests', 'requests', 'pip install requests'),
        'max_chars': 400,
    },
}


def init_backend(name):
    """Validate dependencies and env vars for a backend. Returns config dict."""
    if name not in BACKENDS:
        print(f"Error: Unknown backend '{name}'. Use: {', '.join(BACKENDS.keys())}", file=sys.stderr)
        sys.exit(1)

    info = BACKENDS[name]

    # Check Python module
    mod_name, pkg_name, install_cmd = info['import']
    try:
        __import__(mod_name)
    except ImportError:
        print(f"Error: '{pkg_name}' not installed. Run: {install_cmd}", file=sys.stderr)
        sys.exit(1)

    # Check env vars
    for var in info['env']:
        if not os.environ.get(var):
            print(f"Error: {var} not set", file=sys.stderr)
            sys.exit(1)

    return _build_config(name)


def get_synthesize_func(name):
    """Import and return the synthesize function for a backend."""
    from importlib import import_module
    mod = import_module(BACKENDS[name]['module'], package='tts.backends')
    return mod.synthesize


def get_max_chars(name):
    """Return max chunk size for a backend."""
    return BACKENDS[name]['max_chars']


def _build_config(name):
    """Build backend-specific config dict from environment variables."""
    config = {}
    if name == 'azure':
        config['key'] = os.environ['AZURE_SPEECH_KEY']
        config['region'] = os.environ.get('AZURE_SPEECH_REGION', 'eastasia')
        # Default to standard XiaoxiaoNeural — Multilingual variant ignores SAPI phoneme tags for zh-CN
        config['voice'] = _resolve_voice('azure', 'AZURE_TTS_VOICE', 'zh-CN-XiaoxiaoNeural')
    elif name == 'edge':
        config['voice'] = _resolve_voice('edge', 'EDGE_TTS_VOICE', 'zh-CN-XiaoxiaoNeural')
    elif name == 'doubao':
        config['appid'] = os.environ['VOLCENGINE_APPID']
        config['token'] = os.environ['VOLCENGINE_ACCESS_TOKEN']
        config['cluster'] = os.environ.get('VOLCENGINE_CLUSTER', 'volcano_tts')
        config['voice'] = _resolve_voice('doubao', 'VOLCENGINE_VOICE_TYPE', 'BV001_streaming')
        config['endpoint'] = os.environ.get('VOLCENGINE_TTS_ENDPOINT', 'https://openspeech.bytedance.com/api/v1/tts')
    elif name == 'elevenlabs':
        config['key'] = os.environ['ELEVENLABS_API_KEY']
        config['voice'] = _resolve_voice('elevenlabs', 'ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')
        config['model'] = os.environ.get('ELEVENLABS_MODEL', 'eleven_multilingual_v2')
    elif name == 'openai':
        config['key'] = os.environ['OPENAI_API_KEY']
        config['voice'] = _resolve_voice('openai', 'OPENAI_TTS_VOICE', 'alloy')
        config['model'] = os.environ.get('OPENAI_TTS_MODEL', 'tts-1-hd')
    elif name == 'google':
        config['key'] = os.environ['GOOGLE_TTS_API_KEY']
        config['voice'] = _resolve_voice('google', 'GOOGLE_TTS_VOICE', 'en-US-Neural2-F')
        config['language'] = os.environ.get('GOOGLE_TTS_LANGUAGE', 'en-US')
    return config
