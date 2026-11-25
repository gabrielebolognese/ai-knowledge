"""Check that your environment is ready for the AI Knowledge course.

Run it from the folder where you put the course code, with your virtual environment active:

    python code/setup/verify_setup.py

Every line names one tool and its version. The last line says "All checks passed." when
everything the projects need is installed. "CUDA GPU : False" is normal on a CPU install.
"""
import importlib
import platform
import sys

problems = []


def version_of(module_name, label):
    """Import a package and print its version, or record a problem."""
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        print(f"{label:<13}: MISSING  -> python -m pip install -r code/requirements.txt")
        problems.append(label)
        return None
    print(f"{label:<13}: {getattr(module, '__version__', 'installed')}")
    return module


major, minor = sys.version_info[:2]
print(f"{'Python':<13}: {platform.python_version()} {platform.platform()}")
if (major, minor) < (3, 11):
    print("               Python 3.11 or newer is needed (3.14 recommended).")
    problems.append("Python version")
if sys.maxsize <= 2**32:
    print("               This is a 32-bit Python; PyTorch needs 64-bit.")
    problems.append("64-bit Python")

version_of("numpy", "numpy")
version_of("matplotlib", "matplotlib")
version_of("PIL", "pillow")
version_of("tqdm", "tqdm")
version_of("chess", "python-chess")
torch = version_of("torch", "torch")
version_of("torchvision", "torchvision")

if torch is not None:
    cuda = torch.cuda.is_available()
    name = f"  ({torch.cuda.get_device_name(0)})" if cuda else "  (normal on a CPU install)"
    print(f"{'CUDA GPU':<13}: {cuda}{name}")
    mps = getattr(torch.backends, "mps", None)
    print(f"{'Apple MPS':<13}: {bool(mps and mps.is_available())}")
    x = torch.rand(5, 3)
    print(f"{'tensor OK':<13}: {tuple(x.shape)}")

in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
print(f"{'venv active':<13}: {in_venv}  ({sys.prefix})")

if problems:
    print("Not ready yet. Fix: " + ", ".join(problems))
    sys.exit(1)
print("All checks passed.")
