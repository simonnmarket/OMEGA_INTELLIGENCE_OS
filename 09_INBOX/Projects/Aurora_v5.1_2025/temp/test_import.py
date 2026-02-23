
import sys
sys.path.insert(0, '.')

try:
    import system_core.ncnt_orchestrator_complete
    print("SUCCESS: Module imports correctly")
    sys.exit(0)
except SyntaxError as e:
    print(f"SYNTAX_ERROR: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
    sys.exit(2)
except Exception as e:
    print(f"UNKNOWN_ERROR: {e}")
    sys.exit(3)
