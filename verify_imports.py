import sys
import os
import importlib.util

print("Python version:", sys.version)
print("\nPython path:")
for p in sys.path:
    print(f"- {p}")

print("\nChecking imports...")

try:
    import numpy
    print("✓ numpy version:", numpy.__version__)

    import PIL
    print("✓ Pillow version:", PIL.__version__)

    import moviepy
    print("✓ moviepy version:", moviepy.__version__)
    print("moviepy location:", moviepy.__file__)

    # Print out the contents of the moviepy package directory
    moviepy_dir = os.path.dirname(moviepy.__file__)
    print("\nMoviepy directory contents:", os.listdir(moviepy_dir))

    # Specifically check for editor.py
    editor_path = os.path.join(moviepy_dir, 'editor.py')
    if os.path.exists(editor_path):
        print("✓ editor.py found at:", editor_path)
    else:
        print("✗ editor.py not found")

    # Try importing specific components
    from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip
    print("✓ moviepy.editor imports successful")

    print("\nAll imports successful!")
except Exception as e:
    print("\nError during import verification:", str(e))
    sys.exit(1)