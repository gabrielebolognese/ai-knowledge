# 04 — Environment setup research (Windows, macOS, Linux)

**Purpose:** source material for the optional *Setup* track of the AI Knowledge course. Every version, URL, command and UI label below was checked against the live official page on **2026-11-24** (the run date), not recalled from memory. Where something could *not* be verified live it is marked **[UNVERIFIED]** so the lesson author can capture it from a real machine.

**Audience:** a complete beginner who has never installed Python. Windows is the primary audience, so it gets the most detail; macOS and Linux follow.

---

## 0. Verified facts snapshot (as of 2026-11-24)

| Item | Verified value | Where verified |
|---|---|---|
| Newest stable Python | **3.15.2** (released 2026-10-25; 3.15.0 on 2026-10-09) | <https://www.python.org/downloads/> |
| Latest 3.14 | **3.14.10** (2026-10-25), status *bugfix*, supported until 2030-10 | python.org downloads table |
| Latest 3.13 | 3.13.18 (source only — no Windows installer exists for it, HTTP 404) / **3.13.17** is the last one with Windows installers; status *security* | <https://www.python.org/downloads/windows/> |
| 3.10 | **End of life** (2026-10-01) — do not recommend | python.org downloads table |
| Windows installer type | **Python install manager 26.4** is now the primary route. The classic `.exe` installer is labelled *deprecated* in the docs, and the 3.14.10 installer itself shows "*This installer is being retired and will no longer be available after Python 3.15*". The `py.exe` launcher is also *deprecated* (replaced by the manager's `py`). | <https://docs.python.org/3/using/windows.html>, strings extracted from `python-3.14.10-amd64.exe` |
| Latest PyTorch | **2.15.0** (PyPI), `Requires-Python >=3.11`, wheels for **cp311–cp315** on Windows x64, Linux x86_64/aarch64 and macOS arm64 | <https://pypi.org/project/torch/>, PyPI JSON API |
| PyTorch selector options (Stable) | Compute platforms: **CUDA 13.2**, **CUDA 13.4**, **ROCm 10.0** (Linux only), **CPU** | <https://pytorch.org/get-started/locally/> (JS matrix in page source) |
| NumPy | 2.5.5, `Requires-Python >=3.12` (wheels cp312–cp315) | PyPI |
| Matplotlib | 3.11.2, `>=3.11` | PyPI |
| Jupyter | `jupyterlab` 4.6.6, `notebook` 7.6.5, `ipykernel` 7.4.0 | PyPI |
| tqdm | 4.70.1 | PyPI |
| python-chess | PyPI project **`chess`** 1.11.2 (`import chess`). The name `python-chess` on PyPI is only a shim at version 1.999 that points to `chess`. **Install `chess`.** | PyPI JSON for both names |
| scikit-learn / Pillow | 1.9.1 / 13.0.0 (both `>=3.11`) | PyPI |
| pip | 26.3 | PyPI |
| VS Code | **1.147.0** (stable) | resolved from `update.code.visualstudio.com/latest/...` redirect |
| Git for Windows | **2.56.1.windows.1** | GitHub releases redirect |
| GitHub Desktop | 3.7.0 | `central.github.com` redirect |
| Ubuntu `python3` | 26.04 "resolute" → **3.14.3**; 24.04 "noble" → 3.12.3; Debian stable → 3.13.5 | packages.ubuntu.com, packages.debian.org |
| Homebrew | `python@3.14` = 3.14.10, `python@3.15` = 3.15.2, `python@3.13` = 3.13.18 | formulae.brew.sh API |
| CUDA/driver floor | Any CUDA **13.x** toolkit needs NVIDIA driver **>= 580** | <https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html> |

### Stale-doc warnings (important for the lesson author)

PyTorch's own prose pages lag behind its data. The command table and PyPI are current; the surrounding text is not:

* The selector page's *header text* still reads "Stable (2.7.0)", and the **macOS prerequisites paragraph says "Python 3.10 – 3.14"**. The same page's banner says *"Latest Stable PyTorch requires Python 3.11 or later"* and PyPI says 2.15.0 / `>=3.11`. **Trust PyPI and the command table.** Do not tell learners to use Python 3.10 (also EOL).
* <https://developer.apple.com/metal/pytorch/> still says "Stable (PyTorch 2.11.0)" and `torchaudio`. Ignore the version number there.
* The selector no longer offers `torchaudio` in its default command — the course does not need it (no audio projects).
* The page's Windows prerequisites say "Windows 7 and greater; Windows 10 or greater recommended" and "PyTorch on Windows only supports Python 3.10-3…" — both stale. PyPI shows only 64-bit (`win_amd64`/`win_arm64`) wheels for 2.15.0 and Python >=3.11. Course minimum: **64-bit Windows 10 or 11**.

### Course-wide decisions (made by this research step)

1. **Recommended Python: 3.14.10** (`py install 3.14` on Windows). Why: it is the newest *fully matured* line — every course dependency has cp314 wheels today, it is in bugfix status until 2030, and it is what Ubuntu 26.04 ships. **3.12, 3.13 and 3.15 all work too** (verified wheels for NumPy/Matplotlib/Pillow/scikit-learn/PyTorch exist for cp312–cp315). 3.15 is only six weeks old, so beginners are steered to 3.14. **Avoid exactly 3.14.1** — `torchvision` declares `Requires-Python: !=3.14.1,>=3.10`.
2. **Windows primary route = Python install manager (MSIX from python.org), not the legacy installer.** The legacy installer (with the "Add python.exe to PATH" checkbox) is kept as a *documented fallback* because many existing tutorials show it and it still works for 3.14.
3. **Default compute for the course = CPU.** All six projects are sized so they train acceptably on a laptop CPU (or Colab). GPU is an optional "go faster" lesson.
4. **Project folder lives outside OneDrive** (e.g. `C:\dev\ai-knowledge`). A virtual environment contains tens of thousands of small files; OneDrive sync makes it slow and can corrupt it. (Practical advice, flagged as author judgement, not an official statement.)
5. **Learners always call pip as `python -m pip`.** Python's own troubleshooting table recommends this exact form when `pip` is "not found".

---

## 1. Recommended install order (one picture)

```
Terminal ─► Python 3.14 ─► VS Code ─► Python + Jupyter extensions
        ─► project folder ─► virtual environment (.venv) ─► activate
        ─► pip upgrade ─► PyTorch (CPU or CUDA) ─► NumPy, Matplotlib, Jupyter, chess, tqdm
        ─► verify script ─► (optional) Git + GitHub Desktop
Alternative with zero install: Google Colab
```

Each step below has: *what to click/type*, *what you should see*, and *the screenshot ID* from §8.

---

## 2. Windows (primary audience) — ordered, click-by-click

Supported: Windows 10 and 11, 64-bit (x64). Windows on ARM works (python.org ships ARM64 builds; PyTorch publishes `win_arm64` CPU wheels), but CUDA does not apply. Needs ~3 GB free disk (CPU) or ~6 GB (CUDA).

### 2.1 Open a terminal (SS-W01)

* **Windows 11:** press **Win**, type `terminal`, press **Enter**. This opens *Windows Terminal* with a **PowerShell** tab. (Alternative: right-click Start → **Terminal**.)
* **Windows 10:** press **Win**, type `PowerShell`, press Enter. Optionally install *Windows Terminal* from the Microsoft Store.
* Docs: <https://learn.microsoft.com/en-us/windows/terminal/install>
* Try: type `echo hello` and press Enter. Seeing `hello` proves the terminal works. Everything in this course that says "run this command" means *type it here, then press Enter*.

### 2.2 Install Python — route A (recommended): Python install manager

The current official Windows route, per <https://docs.python.org/3/using/windows.html> §4.1: *"To obtain Python from the CPython team, use the Python install manager… You can download the Python install manager from python.org/downloads or through the Microsoft Store app."* The two versions are identical.

**Route A1 — download from python.org (SS-W02, SS-W03)**

1. Open <https://www.python.org/downloads/windows/> (or <https://www.python.org/downloads/> and use the button **Download Python install manager**).
2. Click **Python install manager** (page header reads *"Latest Python install manager – Python install manager 26.4"*). It links to the release page <https://www.python.org/downloads/release/pymanager-264/>.
3. Click the **MSIX** file: <https://www.python.org/ftp/python/pymanager/python-manager-26.4.msix>. (An `.msi` variant is also offered: <https://www.python.org/ftp/python/pymanager/python-manager-26.4.msi> — for locked-down PCs; see §4.1.10 *Advanced installation* in the docs.)
4. When the download finishes, double-click the `.msix` file → click **Install** (SS-W04). Alternative from PowerShell: `Add-AppxPackage <path-to-msix>` (documented).
5. **Close the terminal and open a new one** so the new commands are visible.

**Route A2 — Microsoft Store:** open the Store, search *Python install manager*, click **Install**. Docs: *"To install through the Store, simply click 'Install'. After it has completed, open a terminal and type python to get started."* [UNVERIFIED: the exact Store listing URL — author should capture it.]

**Install the Python runtime** (the manager is only the installer; you still need a Python):

```powershell
py install 3.14
py list
python --version
```

* `py install 3.14` downloads the runtime. `py list` shows installed runtimes and which one is default; `py list --online` shows what is available. Documented in §4.1.4–4.1.5.
* If you **skip** `py install` and just type `python`, the docs say *"If no runtimes are installed at all, the current latest release will be installed automatically"* — that would be **3.15.2** today. Fine, but the course teaches `py install 3.14` to pin the tested version.
* Expected: `Python 3.14.10` (or a newer 3.14.x).
* On first install you may be asked to add `%LocalAppData%\Python\bin` to PATH. Docs: *"This is optional, if you prefer to use the py command"*. Beginners can answer **No** and use `py` — but `python` also works because the manager registers the *App execution aliases*.
* Updating later: `py install --update` (updates all manager-installed runtimes; the manager itself auto-updates).

**Why `python` and `py` both work:** the manager provides `python`, `py`, `pymanager`, `pythonw`, `pyw` and a `python3` safety-net command. `py -V:3.14 …` selects a specific version (tag must come first).

### 2.3 Install Python — route B (fallback): classic installer with the PATH checkbox (SS-W05)

Use only if route A fails (e.g. MSIX blocked by IT policy) or you want to match an older tutorial. The docs mark this installer *deprecated*; the installer window itself says it is retiring after 3.15.

1. Open <https://www.python.org/downloads/windows/>, section **Python 3.14.10**, click **Windows installer (64-bit)**. Direct link (verified, HTTP 200, ~32 MB): <https://www.python.org/ftp/python/3.14.10/python-3.14.10-amd64.exe>. ARM64: <https://www.python.org/ftp/python/3.14.10/python-3.14.10-arm64.exe>.
2. Run it. First window labels (extracted from the installer's own string table): button **Install Now** (installs for current user, *no administrator needed*), button **Customize installation**, and two check-boxes at the bottom: **"Use admin privileges when installing py.exe"** and **"Add python.exe to PATH"**.
3. **Tick "Add python.exe to PATH".** (On the *Customize → Advanced Options* page the same option is worded *"Add Python to environment variables"*.)
4. Click **Install Now**. At the end, if you see **"Disable path length limit"**, click it (this is the MAX_PATH fix, §7 FAQ-10) — it asks for administrator approval.
5. Open a **new** terminal and run `python --version`.

### 2.4 The Microsoft Store "python" trap (SS-W06)

If typing `python` opens the Microsoft Store (or prints *"Python was not found; run without arguments to install from the Microsoft Store…"*), Windows' built-in alias is intercepting it. Official fix (docs §4.1.16 *Troubleshooting*):

1. Click **Start**, search **"Manage app execution aliases"**, open it.
2. Make sure **Python (default)** is **On**; also check *Python (default windowed)* and *Python install manager*. If already on, switch it **off and on** to refresh.
3. If you used route B instead, **turn the alias off** for the entry that points to the Store.
4. Check that `py` and `pymanager` work, and that `%UserProfile%\AppData\Local\Microsoft\WindowsApps` is still on PATH.

Other documented symptoms: `py` says *"can't open file"* → the *legacy launcher* has priority: Start → **Installed apps** → uninstall **"Python launcher"**. `python` and `py` pick different versions → remove old runtimes in *Installed apps* or *Modify* them and untick the PATH options.

### 2.5 The `py` launcher

With route A, `py` is the manager's command (recommended for multi-version machines): `py` launches your default Python; `py -V:3.14 -m venv .venv` pins a version. With route B, `py.exe` is the *legacy* launcher (deprecated). Same typing, different program; the troubleshooting above covers conflicts. Docs: <https://docs.python.org/3/using/windows.html#python-install-manager>.

### 2.6 Install VS Code (SS-W07, SS-W08)

1. Open <https://code.visualstudio.com/download>.
2. Under **Windows**, click **User Installer** → **x64** (ARM64 for ARM PCs). Direct, version-pinned redirects that always resolve to the latest stable (verified → `VSCodeUserSetup-x64-1.147.0.exe`): <https://update.code.visualstudio.com/latest/win32-x64-user/stable> (ARM64: <https://update.code.visualstudio.com/latest/win32-arm64-user/stable>). The *User* installer needs no administrator rights.
3. Run it. Accept the licence. On **Select Additional Tasks** keep **Add to PATH** ticked (it is on by default) and optionally tick *Add "Open with Code" action…* (SS-W08). Docs confirm: *"verify that Add to PATH is checked on the Select Additional Tasks step"*. Setup guide: <https://code.visualstudio.com/docs/setup/windows>.
4. Click **Finish → Launch Visual Studio Code**.

### 2.7 Install the Python and Jupyter extensions (SS-W09, SS-W10)

1. In VS Code, click the **Extensions** icon (four squares) in the left bar, or press **Ctrl+Shift+X**.
2. Search **Python**; install the one published by **Microsoft** (ID `ms-python.python`; marketplace page shows ~246 million installs): <https://marketplace.visualstudio.com/items?itemName=ms-python.python>. It brings in Pylance and the Python Debugger.
3. Search **Jupyter**; install the one by **Microsoft** (ID `ms-toolsai.jupyter`): <https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter>.
4. Optional but handy: **Python Environments** (`ms-python.vscode-python-envs`): <https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs> — a UI to create/switch environments (docs: <https://code.visualstudio.com/docs/python/environments>).
5. Terminal alternative (only works because "Add to PATH" was ticked):
   ```powershell
   code --install-extension ms-python.python
   code --install-extension ms-toolsai.jupyter
   ```
Docs: <https://code.visualstudio.com/docs/python/python-quick-start>, <https://code.visualstudio.com/docs/datascience/jupyter-notebooks>.

### 2.8 Make a project folder and open it (SS-W11)

Outside OneDrive (see decision 4):

```powershell
mkdir C:\dev\ai-knowledge
cd C:\dev\ai-knowledge
code .
```

`code .` opens the folder in VS Code. If asked *"Do you trust the authors of the files in this folder?"* click **Yes, I trust the authors** (Workspace Trust) — it is the learner's own folder.

### 2.9 Create the virtual environment (venv) (SS-W12)

Analogy for the lesson: *a venv is a clean lab bench for one project, so the experiments from one project never contaminate another.*

```powershell
python -m venv .venv
```

(With the install manager: `py -V:3.14 -m venv .venv` to pin the version.) This creates the `.venv` folder. Docs: <https://docs.python.org/3/library/venv.html>, <https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/>.

**Activate it** (per shell, from the venv docs table):

| Shell | Command |
|---|---|
| **PowerShell** (default in Windows Terminal) | `.venv\Scripts\Activate.ps1` |
| **cmd.exe** | `.venv\Scripts\activate.bat` |
| PowerShell Core on any OS | `.venv/bin/Activate.ps1` |
| bash/zsh (macOS, Linux, Git Bash) | `source .venv/bin/activate` |
| fish / csh | `source .venv/bin/activate.fish` / `.csh` |

Success looks like `(.venv)` at the start of the prompt. Leave with `deactivate`.

**PowerShell execution-policy error (SS-W13).** On a fresh Windows PC, `Activate.ps1` often fails with *"…cannot be loaded because running scripts is disabled on this system"*. Official fix (Microsoft Learn, *about_Execution_Policies*): set the policy for **your user only**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Answer **Y** if asked, then run the activate command again. Docs: <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies>. `RemoteSigned` lets local scripts run and only demands signatures for scripts downloaded from the internet; `-Scope CurrentUser` needs no admin.

**Two no-fix alternatives** (both safe): (a) use `cmd` and `activate.bat`; (b) skip activation and call the venv's Python directly: `.venv\Scripts\python.exe -m pip …` (the venv docs say activation is optional).

**Tell VS Code to use it (SS-W14):** press **Ctrl+Shift+P** → type **"Python: Select Interpreter"** → choose the entry marked **`.venv`** (recommended). VS Code's *Python: Create Environment* command can also create it (it uses `uv` automatically if installed). Bottom-right of the window shows the active interpreter.

### 2.10 Upgrade pip

```powershell
python -m pip install --upgrade pip
```

(Verified current: pip 26.3.) Always `python -m pip`, never bare `pip`. Docs: <https://pip.pypa.io/en/stable/installation/>.

### 2.11 Install PyTorch (SS-W15, SS-W16)

Open <https://pytorch.org/get-started/locally/>. Click: **Stable → Windows → Pip → Python → Compute Platform**. Verified command matrix for *Stable / Pip / Python*:

| Compute Platform tile | Command (verified from the page's command table) | Download size (measured, cp314 wheel) |
|---|---|---|
| **CPU** | `pip3 install torch torchvision` — on Windows PyPI's default wheel *is* the CPU build | ~123 MB |
| **CUDA 13.2** | `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu132` | ~2.0 GB |
| **CUDA 13.4** | `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu134` | ~2 GB |
| ROCm 10.0 | **Not available on Windows** (the page says so); Linux only | — |

Course-friendly form (so the venv's own pip is used, and an explicit CPU index makes the choice obvious):

```powershell
# CPU (recommended default for the course)
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
# NVIDIA GPU (optional) — pick ONE
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu132
```

(Verified: `https://download.pytorch.org/whl/cpu`, `/cu132` and `/cu134` all serve `torch-2.15.0` wheels for cp311–cp315 on `win_amd64`.)

**CPU or CUDA?** CPU if you have no NVIDIA GPU, or are unsure. CUDA needs an **NVIDIA** GPU and driver **>= 580** (CUDA 13.x floor, NVIDIA release notes). You do **not** install the CUDA Toolkit separately — the pip wheel bundles the CUDA runtime; only the *driver* matters. Check the driver with `nvidia-smi` in a terminal. Update drivers from <https://www.nvidia.com/en-us/drivers/>. AMD/Intel GPUs on Windows: use CPU. (PyTorch's Windows ROCm is unavailable.)

**Python versions supported by this release:** 3.11, 3.12, 3.13, 3.14, 3.15 (PyPI `requires_python >=3.11`; wheels for cp311–cp315, plus free-threaded cp314t/cp315t on the CPU/CUDA indexes).

### 2.12 Install the remaining libraries (SS-W17)

Put this in `requirements.txt` (the course repo ships it) and install:

```text
numpy
matplotlib
tqdm
chess
pillow
scikit-learn
jupyterlab
ipykernel
```

```powershell
python -m pip install -r requirements.txt
```

* **NumPy** — arrays (note 2.5 needs Python >= 3.12). **Matplotlib** — plots. **tqdm** — progress bars. **chess** — the *python-chess* library (`import chess`); install `chess`, *not* `python-chess` (which is a 1.999 redirect shim). Docs: <https://python-chess.readthedocs.io/en/latest/>.
* **Jupyter:** VS Code only needs `ipykernel` (+ the Jupyter extension) to run `.ipynb` notebooks inline. `jupyterlab` additionally gives a browser-based notebook: `python -m jupyter lab`. Install docs: <https://jupyter.org/install>.
* Install docs: <https://numpy.org/install/>, <https://matplotlib.org/stable/install/index.html>.

### 2.13 Verify everything (SS-W18)

Create `verify_setup.py` in the project folder (the course repo ships it) and run it with `python verify_setup.py`:

```python
import sys, platform
print("Python      :", sys.version.split()[0], platform.platform())
import numpy, matplotlib, tqdm, chess, torch, torchvision
print("numpy       :", numpy.__version__)
print("matplotlib  :", matplotlib.__version__)
print("python-chess:", chess.__version__)
print("torch       :", torch.__version__, "| torchvision:", torchvision.__version__)
print("CUDA GPU    :", torch.cuda.is_available(),
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")
mps = getattr(torch.backends, "mps", None)
print("Apple MPS   :", bool(mps and mps.is_available()))
x = torch.rand(5, 3)
print("tensor OK   :", tuple(x.shape))
```

Expected on a CPU laptop: Python 3.14.x, `CUDA GPU : False`, `Apple MPS : False`, `tensor OK : (5, 3)`. **`False` for CUDA is normal and fine on a CPU install.** One-liners shown in the lesson: `python --version`, `python -c "import torch; print(torch.cuda.is_available())"`. The PyTorch page's own verification step is `x = torch.rand(5, 3); print(x)`.

### 2.14 Optional: Git and GitHub Desktop (SS-W19)

* **Git for Windows:** <https://git-scm.com/install/windows> (current 2.56.1; release list <https://github.com/git-for-windows/git/releases>). Accept defaults.
* **GitHub Desktop:** <https://desktop.github.com/download/> (direct redirect resolves to `GitHubDesktopSetup-x64.exe`; docs <https://docs.github.com/en/desktop/installing-and-authenticating-to-github-desktop/installing-github-desktop>). Sign in with a GitHub account; **File → Clone repository** to fetch the course companion code.
* The course is read-only; **Git is never required**. Learners can use GitHub's *Code → Download ZIP*.

### 2.15 Optional: WSL2 (advanced note only)

<https://learn.microsoft.com/en-us/windows/wsl/install> (`wsl --install`). GPU-in-WSL notes: <https://developer.nvidia.com/cuda/wsl>. Mentioned as "advanced, not required".

---

## 3. macOS — ordered steps

Apple Silicon (M1+) Macs only for PyTorch 2.15: PyPI wheels are `macosx_14_0_arm64` (**macOS 14 Sonoma or later**). **Intel Macs have no PyTorch 2.15 wheel** → send those learners to Colab (§6) [finding from PyPI file list; flag prominently in the lesson].

### 3.1 Open Terminal (SS-M01)
Press **⌘ Space**, type `Terminal`, press Return. Apple guide: <https://support.apple.com/guide/terminal/welcome/mac>.

### 3.2 Install Python — option A: python.org installer (recommended)
1. <https://www.python.org/downloads/macos/> → **Python 3.14.10** row → *macOS 64-bit universal2 installer*. Direct: <https://www.python.org/ftp/python/3.14.10/python-3.14.10-macos11.pkg> (verified present). (3.15.2: <https://www.python.org/ftp/python/3.15.2/python-3.15.2-macos11.pkg>.)
2. Double-click the `.pkg` → **Continue** through Introduction/Licence → **Agree** → **Install** (enter your Mac password) (SS-M02).
3. When the finder window opens, **double-click `Install Certificates.command`** (inside `/Applications/Python 3.14/`). The macOS docs say this "will open a temporary Terminal shell window… to download and install SSL root certificates". It prevents `SSL: CERTIFICATE_VERIFY_FAILED` later (SS-M03). Docs: <https://docs.python.org/3/using/mac.html>.
4. New Terminal tab → `python3 --version`. On macOS the command is **`python3`** and **`pip3`** (not `python`) — inside an activated venv, `python` works.

### 3.3 Install Python — option B: Homebrew
```bash
xcode-select --install          # command-line tools (Apple's dialog; click Install)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.14
python3.14 --version
```
Command verified on <https://brew.sh/>. Homebrew `python@3.14` is currently 3.14.10. Follow the "Next steps" the installer prints to add `brew` to your PATH.

### 3.4 VS Code
<https://code.visualstudio.com/download> → **Mac → Universal** (zip; direct <https://update.code.visualstudio.com/latest/darwin-universal/stable>). Unzip, drag **Visual Studio Code** to **Applications**, open it (right-click → Open if Gatekeeper asks). Optional `code` command: **⌘⇧P → "Shell Command: Install 'code' command in PATH"** (verified in <https://code.visualstudio.com/docs/setup/mac>; note it may now offer to also install the Copilot CLI — answer **No**). Install the same two extensions as §2.7 (**⌘⇧X**).

### 3.5 venv and activation
```bash
mkdir -p ~/dev/ai-knowledge && cd ~/dev/ai-knowledge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```
No execution-policy issue on macOS.

### 3.6 PyTorch + libraries
Selector: **Stable → Mac → Pip → Python → CPU**. Verified command: `pip3 install torch torchvision` (macOS wheels are one build that includes **Metal (MPS)** support; the page notes CUDA/ROCm are not available on macOS). In the venv: `python -m pip install torch torchvision`, then `python -m pip install -r requirements.txt`.

**Apple GPU (MPS):** check with `python -c "import torch; print(torch.backends.mps.is_available())"` → `True` on supported Macs. Use with `device = torch.device("mps")`. Apple's page lists *Apple silicon, macOS 14+, Python 3.10+, Xcode command-line tools* as requirements: <https://developer.apple.com/metal/pytorch/>; PyTorch doc: <https://docs.pytorch.org/docs/stable/notes/mps.html>. The course trains on CPU by default; MPS is an optional speed-up (a few operators may fall back to CPU).

### 3.7 Git (optional)
Typing `git --version` in Terminal triggers the Command Line Tools installer. GitHub Desktop: <https://desktop.github.com/download/>. Git for macOS: <https://git-scm.com/install/mac>.

---

## 4. Linux — ordered steps

PyTorch needs a distro with **glibc >= 2.28**; the selector page's minimums are Debian 10, Ubuntu 20.04 (the page itself notes 20.04 is EOL), Fedora 24, CentOS 8, Mint 20, openSUSE 15 and Arch 2020.01.22. Wheels: x86_64 and aarch64 (`manylinux_2_28`).

### 4.1 Terminal
Ubuntu: **Ctrl+Alt+T** (or Activities → *Terminal*). Fedora/others: Activities → *Terminal*/*Console*.

### 4.2 Install Python, venv and pip
**Debian / Ubuntu (apt)** — the system Python is already new on current releases (Ubuntu 26.04 → 3.14.3, Ubuntu 24.04 → 3.12.3, Debian stable → 3.13.5; all satisfy PyTorch's `>=3.11`). **The `venv` module is a separate package on Debian/Ubuntu** and `pip` too:
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 --version
```
(If `python3 -m venv` later prints *"ensurepip is not available"*, the fix is exactly `sudo apt install python3-venv`.)

**Older Ubuntu (22.04 ships Python 3.10, which is end-of-life and below PyTorch's `>=3.11`):** use the **deadsnakes** PPA (<https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa>, project <https://github.com/deadsnakes>), which lists Ubuntu 22.04, 24.04 and 26.04 and "Python 3.7+ except the version the distro ships":
```bash
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv      # or python3.14 — verify with: apt-cache policy python3.14
python3.13 -m venv .venv
```
The PPA is third-party; say so in the lesson. On 24.04 you do not need it for 3.12, and 3.12 is a fully supported course version.

**Fedora (dnf):** `sudo dnf install python3.14` (package page <https://packages.fedoraproject.org/pkgs/python3.14/python3.14/>; venv and pip are included) or the default `python3`.

**Other:** Python on Unix overview <https://docs.python.org/3/using/unix.html>.

### 4.3 VS Code
<https://code.visualstudio.com/download> → **.deb** (Debian/Ubuntu; direct <https://update.code.visualstudio.com/latest/linux-deb-x64/stable>, verified → `code_1.147.0-…_amd64.deb`) or **.rpm** (Fedora/RHEL; <https://update.code.visualstudio.com/latest/linux-rpm-x64/stable>, verified → `code-1.147.0-…el8.x86_64.rpm`). Then `sudo apt install ./code_*.deb` (or double-click in the software centre). Guide: <https://code.visualstudio.com/docs/setup/linux>. Extensions: §2.7 (**Ctrl+Shift+X**).

### 4.4 venv, activation, pip
```bash
mkdir -p ~/dev/ai-knowledge && cd ~/dev/ai-knowledge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### 4.5 PyTorch + libraries
Selector: **Stable → Linux → Pip → Python → (CUDA 13.2 | CUDA 13.4 | ROCm 10.0 | CPU)**. Verified commands:

| Tile | Command |
|---|---|
| CPU | `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu` |
| CUDA 13.2 | `pip3 install torch torchvision` *(PyPI's default Linux wheel is the CUDA 13.2 build — large, ~GBs)* |
| CUDA 13.4 | `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu134` |
| ROCm 10.0 (AMD) | `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/rocm10.0` |

**Beginner trap:** on Linux, the plain `pip install torch` pulls the large CUDA build even on machines without a GPU. The course therefore teaches the explicit `--index-url …/cpu` form unless the learner has an NVIDIA GPU. Then `python -m pip install -r requirements.txt`.

NVIDIA: driver **>= 580** (CUDA 13.x); install via your distro's driver tool or <https://www.nvidia.com/en-us/drivers/>; check with `nvidia-smi`.

**PEP 668 "externally-managed-environment" error:** modern Debian/Ubuntu/Fedora refuse `pip install` into the *system* Python (spec: <https://peps.python.org/pep-0668/>). This is why we always use a venv; inside an activated venv the error does not appear.

---

## 5. Terminal reference table (for the lesson "Your terminal" box)

| OS | Open | Prompt looks like | Python command | pip command | Activate venv |
|---|---|---|---|---|---|
| Windows 11 | Win → `terminal` | `PS C:\Users\you>` | `python` or `py` | `python -m pip` | `.venv\Scripts\Activate.ps1` (PowerShell) |
| Windows 10 | Win → `PowerShell` | `PS C:\Users\you>` | `python` or `py` | `python -m pip` | same |
| macOS | ⌘ Space → `Terminal` | `you@Mac ~ %` | `python3` (venv: `python`) | `python3 -m pip` | `source .venv/bin/activate` |
| Linux | Ctrl+Alt+T | `you@host:~$` | `python3` (venv: `python`) | `python3 -m pip` | `source .venv/bin/activate` |

---

## 6. Zero-install alternative: Google Colab (SS-C01 … SS-C03)

* Open <https://colab.research.google.com/> and sign in with a Google account. Free of charge (official FAQ: *"Colab is free of charge to use"*), runs in the browser, **PyTorch, NumPy, Matplotlib, tqdm are pre-installed**. FAQ: <https://research.google.com/colaboratory/faq.html>. Intro notebook: <https://colab.research.google.com/notebooks/intro.ipynb>.
* **File → New notebook**. To use a GPU: **Runtime → Change runtime type → Hardware accelerator** (the FAQ refers to *"Runtime Type"* / *"Hardware Accelerator"*). GPUs are *not guaranteed* on the free tier and sessions time out; files vanish when the session ends unless saved to Drive. The FAQ also mentions a "new AI-First Colab" UI — **[UNVERIFIED]** menu labels may differ slightly; capture at authoring time.
* `python-chess` is *not* pre-installed: first cell `!pip install chess`.
* Verify: `import torch; print(torch.__version__, torch.cuda.is_available())`.
* Course use: every lesson's companion notebook gets an "Open in Colab" link (a static `https://colab.research.google.com/github/gabrielebolognese/ai-knowledge/blob/main/<path>.ipynb` URL — works once the repo is pushed). Intel-Mac and locked-down school PCs are the main audience.

---

## 7. Troubleshooting FAQ (final text drafts, ready to paste)

**FAQ-1 — "I typed `python` and the Microsoft Store opened."** Windows' built-in *app execution alias* is catching the command. Start → **Manage app execution aliases** → make sure **Python (default)** is **On** (toggle off/on to refresh), or install Python with the install manager (§2.2). Then open a *new* terminal. (Source: python docs §4.1.16.)

**FAQ-2 — "`python` / `py` is not recognized."** The terminal was open *before* installing — close it and open a new one. If still failing: (route A) check `py` and `pymanager`; confirm `%UserProfile%\AppData\Local\Microsoft\WindowsApps` is on PATH; run `py install --refresh`. (Route B) re-run the installer → **Modify/Repair** and tick **Add python.exe to PATH**. To edit PATH by hand: Start → **"Edit environment variables for your account"** → **Path** → **Edit** → **New**.

**FAQ-3 — "`pip` is not recognized / pip not found."** Don't fight it: use **`python -m pip`**, which always works. (Official docs recommend exactly this.) Or you forgot to activate the venv. `python -m ensurepip --upgrade` repairs a missing pip (<https://pip.pypa.io/en/stable/installation/>).

**FAQ-4 — "Running scripts is disabled on this system" when activating the venv.** See §2.9: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, or use `cmd`/`activate.bat`, or call `.venv\Scripts\python.exe` directly.

**FAQ-5 — "Package installed but the command isn't found" (e.g. `jupyter`).** Activate the venv, or run it as a module: `python -m jupyter lab`.

**FAQ-6 — "SSL: CERTIFICATE_VERIFY_FAILED" or pip can't connect.** *macOS:* run `Install Certificates.command` (§3.2). *Anywhere:* a school/work network may use a proxy. Windows install manager respects system proxy settings (v26.4 added `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` overrides). For pip: `python -m pip install --proxy http://user:pass@host:port <pkg>` (see <https://pip.pypa.io/en/stable/user_guide/>). If a company firewall re-signs HTTPS, ask IT for the CA bundle (`--cert`) — do **not** use `--trusted-host` as a habit. Easiest bypass: use Colab (§6).

**FAQ-7 — "ERROR: No matching distribution found for torch".** Almost always the Python version: PyTorch 2.15 needs **3.11–3.15** on **64-bit** Python. Check `python --version` and `python -c "import struct; print(struct.calcsize('P')*8)"` (should print 64). Intel Macs have no wheels (use Colab). Python 3.14.1 exactly is blocked by torchvision; upgrade to 3.14.10.

**FAQ-8 — "`torch.cuda.is_available()` is `False`."** Either you installed the CPU wheel (check `python -c "import torch; print(torch.__version__)"` — a `+cpu` suffix means CPU build; reinstall with the `cu132` URL), your NVIDIA driver is older than 580 (`nvidia-smi` shows the driver version), or you have no NVIDIA GPU. None of the course's projects *require* a GPU.

**FAQ-9 — "The CUDA download is huge / my disk is full."** The CUDA wheel is ~2 GB and unpacks to ~4+ GB; the CPU wheel is ~125 MB. Use CPU unless you really want a GPU. Free space: `python -m pip cache purge`.

**FAQ-10 — "Path too long" / WinError 3 / install fails with very long folder names (Windows long paths).** Windows historically caps paths at 260 characters (MAX_PATH). Keep project paths short (`C:\dev\ai-knowledge`). To lift the limit (needs administrator + reboot): enable the **"Enable Win32 long paths"** group policy, or set registry value `LongPathsEnabled` to `1` under `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem` (documented in python docs §4.6). The classic installer offers the same via **"Disable path length limit"**. PowerShell one-liner (admin): `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force`.

**FAQ-11 — "VS Code doesn't see my packages / red squiggles under `import torch`."** The wrong interpreter is selected. **Ctrl+Shift+P → Python: Select Interpreter →** choose the `.venv` entry. Reload the window if needed.

**FAQ-12 — "Jupyter notebook asks me to pick a kernel / 'ipykernel' missing."** Click **Select Kernel** (top-right of the notebook) → **Python Environments…** → `.venv`. If VS Code offers to install `ipykernel`, click **Install**. (Or `python -m pip install ipykernel`.)

**FAQ-13 — "venv creation is very slow / fails with strange errors inside OneDrive."** Move the project out of the OneDrive/Dropbox/iCloud-synced folder (e.g. `C:\dev`). Delete the broken `.venv` folder and recreate it.

**FAQ-14 — Linux: "ensurepip is not available" or "externally-managed-environment".** `sudo apt install python3-venv`; and always install inside the venv (§4.2, §4.5).

**FAQ-15 — "I have several Pythons and the wrong one runs."** `py list` (Windows manager) shows what is installed and the default. Inside a venv, `python --version` and `python -c "import sys; print(sys.executable)"` show which is active. Remove old versions in **Settings → Apps → Installed apps**.

**FAQ-16 — "`UnicodeDecodeError` / odd characters in files on Windows (Python < 3.15)."** Pass `encoding="utf-8"` to `open(...)`. Python 3.15 made UTF-8 mode the default (PEP 686, python docs §4.7).

**FAQ-17 — Antivirus / SmartScreen warns about the installer.** Download only from <https://www.python.org/downloads/> and <https://code.visualstudio.com/download>. Python publishes sigstore signatures next to each download (see the release page).

---

## 8. SCREENSHOT LIST

**Capture-method legend**
* **PW** = capture a public web page with Playwright (headless Chromium, 1440×900, DPR 2, light colour scheme); the page URL, capture date (2026-11-24 baseline) and attribution go in the caption. Re-capturing is automatable, so these stay fresh.
* **SVG** = *annotated SVG recreation* in the site's own style, drawn by us (Windows/macOS system dialogs, installers and logged-in apps cannot be captured by a headless browser, and copying Microsoft/Apple UI imagery is a licensing risk). Faithful labels, our own colours; each carries a "simplified illustration" note and a link to the official docs page.
* **DOC** = an image from an official document, **linked or described, not re-hosted** (check each licence); used only where a recreation would be less clear.
* "Highlight" = the element to ring with the accent colour (#3340C9 per the design brief) plus a numbered badge.

| ID | Step (lesson) | Page URL / app | Element to highlight | Method |
|---|---|---|---|---|
| **SS-W01** | W 2.1 Open a terminal | Windows Start menu, search "terminal" → Windows Terminal with PowerShell tab | Search box text `terminal`; the "Terminal" result; then the `PS C:\>` prompt | SVG |
| **SS-W02** | W 2.2 Find the manager | <https://www.python.org/downloads/windows/> | Header line "Latest Python install manager – Python install manager 26.4" and its link | PW |
| **SS-W03** | W 2.2 Download MSIX | <https://www.python.org/downloads/release/pymanager-264/> | The `python-manager-26.4.msix` file row (not the `.msi`) | PW |
| **SS-W04** | W 2.2 Install MSIX | Windows App Installer dialog for `python-manager-26.4.msix` | The **Install** button [UNVERIFIED exact dialog wording — capture from a real PC] | SVG |
| **SS-W05** | W 2.3 Legacy installer | `python-3.14.10-amd64.exe` first window | The **"Add python.exe to PATH"** checkbox (tick it) and **Install Now** button; the "installer is being retired" note | SVG (labels verified from installer strings) |
| **SS-W06** | W 2.4 Store alias | Windows *Settings → Apps → Advanced app settings → App execution aliases* (open via Start → "Manage app execution aliases") | The **Python (default)** toggle set to On | SVG |
| **SS-W07** | W 2.6 Download VS Code | <https://code.visualstudio.com/download> | **Windows → User Installer → x64** button | PW |
| **SS-W08** | W 2.6 Installer tasks | VS Code setup wizard "Select Additional Tasks" | **Add to PATH** checkbox (ticked) | SVG |
| **SS-W09** | W 2.7 Python extension | <https://marketplace.visualstudio.com/items?itemName=ms-python.python> (and VS Code Extensions panel) | Publisher "Microsoft" + the **Install** button | PW (marketplace page) + SVG (in-app panel) |
| **SS-W10** | W 2.7 Jupyter extension | <https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter> | Publisher "Microsoft", extension ID `ms-toolsai.jupyter` | PW |
| **SS-W11** | W 2.8 Open folder | VS Code window with `C:\dev\ai-knowledge` open, Explorer showing the folder | **File → Open Folder** and the Workspace-Trust dialog "Yes, I trust the authors" | SVG |
| **SS-W12** | W 2.9 Create venv | Windows Terminal: `python -m venv .venv` then `.venv` folder appearing in the VS Code Explorer | The command line and the new `.venv` folder | SVG |
| **SS-W13** | W 2.9 Execution policy | PowerShell showing the red "running scripts is disabled" error, then the `Set-ExecutionPolicy … -Scope CurrentUser` fix, then `(.venv)` prompt | The red error line; the fix command; the `(.venv)` prefix | SVG |
| **SS-W14** | W 2.9 Select interpreter | VS Code Command Palette (Ctrl+Shift+P) "Python: Select Interpreter" list | The `.venv` entry marked *Recommended* | SVG |
| **SS-W15** | W 2.11 PyTorch selector (CPU) | <https://pytorch.org/get-started/locally/> with Stable / Windows / Pip / Python / **CPU** selected | The five selected tiles and the **"Run this Command"** box | PW (click the tiles via Playwright selectors, then screenshot the build matrix) |
| **SS-W16** | W 2.11 PyTorch selector (CUDA) | Same page, **CUDA 13.2** tile selected | The CUDA tile and the `--index-url …/cu132` command | PW |
| **SS-W17** | W 2.12 Install libraries | Terminal running `python -m pip install -r requirements.txt` finishing with "Successfully installed …" | The final "Successfully installed" line | SVG |
| **SS-W18** | W 2.13 Verify | Terminal output of `python verify_setup.py` | Python line, `tensor OK`, and `CUDA GPU : False` marked "fine on CPU" | SVG |
| **SS-W19** | W 2.14 Git / GitHub Desktop | <https://git-scm.com/install/windows> and <https://desktop.github.com/download/> | The **Download for Windows** buttons | PW |
| **SS-M01** | M 3.1 Terminal | macOS Spotlight (⌘ Space) → Terminal | Search field + Terminal result | SVG |
| **SS-M02** | M 3.2 pkg installer | macOS Python installer wizard "Installation Type" step | **Install** button | SVG |
| **SS-M03** | M 3.2 Certificates | Finder window `/Applications/Python 3.14/` | The **Install Certificates.command** file | SVG |
| **SS-M04** | M 3.2 Download | <https://www.python.org/downloads/macos/> | Row "Python 3.14.10" and its installer link | PW |
| **SS-M05** | M 3.3 Homebrew | <https://brew.sh/> | The install command box (copy button) | PW |
| **SS-M06** | M 3.4 VS Code (Mac) | <https://code.visualstudio.com/download> Mac section | **Universal** download button | PW |
| **SS-M07** | M 3.6 PyTorch selector (Mac) | <https://pytorch.org/get-started/locally/> Stable / Mac / Pip / Python / CPU | Selected tiles and command | PW |
| **SS-L01** | L 4.2 apt install | Terminal showing `sudo apt install -y python3 python3-venv python3-pip` | The command; final `python3 --version` line | SVG |
| **SS-L02** | L 4.3 VS Code Linux | <https://code.visualstudio.com/download> Linux section | **.deb** / **.rpm** buttons | PW |
| **SS-L03** | L 4.5 PyTorch selector (Linux) | <https://pytorch.org/get-started/locally/> Stable / Linux / Pip / Python / CPU | Compute-platform tiles incl. ROCm 10.0 and the command | PW |
| **SS-C01** | Colab landing | <https://colab.research.google.com/> | **New notebook** button | PW (public landing before login) |
| **SS-C02** | Colab runtime menu | A Colab notebook: **Runtime → Change runtime type** (Hardware accelerator list) | The accelerator drop-down [UNVERIFIED label set; needs Google login] | SVG |
| **SS-C03** | Colab verify cell | A cell running `import torch; print(torch.cuda.is_available())` with output | The cell and its output | SVG |
| **SS-G01** | Marketplace trust cue | VS Code marketplace page showing the **verified publisher** badge for Microsoft | Publisher name + verified check mark | PW |

Notes for the capture script / author:
1. The PW captures need the PyTorch selector JS to run; wait for the `#command` / "Run this Command" element, click the tiles by their visible text, then clip to the build matrix.
2. All `SVG` illustrations must say "Simplified illustration — your screen may differ slightly" and should link to the official docs page in the caption.
3. Windows UI in the user's own dev machine is Windows 11 Home 26200; real PNGs can optionally replace the SVGs later (record the Windows build in the caption). None are required for the first release.
4. Total: **19 Windows**, **7 macOS**, **3 Linux**, **3 Colab**, **1 generic** = **33 images**, of which **16 are PW (automated)** and **17 are SVG**.

---

## 9. Setup-track lesson skeleton (suggested, for the curriculum step)

1. *Before you start* — what we install and why (analogy: workshop, bench, tools). Time ~45 min first time.
2. *Open a terminal* (OS tabs).
3. *Install Python* (Windows A/B, macOS A/B, Linux) + verify.
4. *Install VS Code and two extensions.*
5. *Project folder + virtual environment* (+ execution-policy fix).
6. *Install PyTorch — choose CPU or GPU* (decision flowchart: NVIDIA GPU? driver >= 580? else CPU).
7. *Install the other libraries; run `verify_setup.py`.*
8. *Optional:* Git + GitHub Desktop; WSL.
9. *No install? Use Colab.*
10. *Troubleshooting FAQ* (§7).
Skip path: a single banner "Already have Python 3.11+? Jump to step 5."

---

## 10. Bibliography (every source consulted, with what it established)

**Python**
1. Python Software Foundation. *Download Python*. <https://www.python.org/downloads/> — current releases (3.15.2, 3.14.10), support dates, 3.10 EOL.
2. PSF. *Python Releases for Windows*. <https://www.python.org/downloads/windows/> — install manager 26.4; installer links.
3. PSF. *Python install manager 26.4*. <https://www.python.org/downloads/release/pymanager-264/> — MSIX/MSI files.
4. PSF. `python-manager-26.4.msix`. <https://www.python.org/ftp/python/pymanager/python-manager-26.4.msix>; `.msi`: <https://www.python.org/ftp/python/pymanager/python-manager-26.4.msi>.
5. PSF. *Python Releases for macOS*. <https://www.python.org/downloads/macos/>; installers <https://www.python.org/ftp/python/3.14.10/python-3.14.10-macos11.pkg>, <https://www.python.org/ftp/python/3.15.2/python-3.15.2-macos11.pkg>.
6. PSF. *Python 3.14.10 release page*. <https://www.python.org/downloads/release/python-31410/> — installer sizes; Windows installer direct link <https://www.python.org/ftp/python/3.14.10/python-3.14.10-amd64.exe>.
7. Python docs. *Using Python on Windows*. <https://docs.python.org/3/using/windows.html> — install manager, `py`, troubleshooting table, MAX_PATH, UTF-8 mode, deprecation of full installer and legacy launcher.
8. Python docs (3.14). *Using Python on Windows*. <https://docs.python.org/3.14/using/windows.html>.
9. Python docs. *Using Python on macOS*. <https://docs.python.org/3/using/mac.html> — installer steps, `Install Certificates.command`.
10. Python docs. *Using Python on Unix platforms*. <https://docs.python.org/3/using/unix.html>.
11. Python docs. *venv — Creation of virtual environments*. <https://docs.python.org/3/library/venv.html> — activation table.
12. Python Packaging User Guide. *Install packages using pip and virtual environments*. <https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/>.
13. pip documentation. *Installation*. <https://pip.pypa.io/en/stable/installation/>; *User guide*. <https://pip.pypa.io/en/stable/user_guide/>.
14. PEP 773 — *A Python installation manager for Windows*. <https://peps.python.org/pep-0773/>.
15. PEP 668 — *Marking Python base environments as "externally managed"*. <https://peps.python.org/pep-0668/>.
16. PyPI JSON API (versions, `requires_python`, wheel tags): <https://pypi.org/project/torch/>, <https://pypi.org/project/numpy/>, <https://pypi.org/project/matplotlib/>, <https://pypi.org/project/jupyterlab/>, <https://pypi.org/project/notebook/>, <https://pypi.org/project/ipykernel/>, <https://pypi.org/project/tqdm/>, <https://pypi.org/project/chess/>, <https://pypi.org/project/python-chess/>, <https://pypi.org/project/torchvision/>, <https://pypi.org/project/scikit-learn/>, <https://pypi.org/project/pillow/>, <https://pypi.org/project/pip/>.

**PyTorch and GPU**
17. PyTorch. *Get Started — Start Locally*. <https://pytorch.org/get-started/locally/> — selector matrix and commands (CUDA 13.2/13.4, ROCm 10.0, CPU).
18. PyTorch. *Previous versions*. <https://pytorch.org/get-started/previous-versions/>.
19. PyTorch wheel indexes: <https://download.pytorch.org/whl/cpu/torch/>, <https://download.pytorch.org/whl/cu132/torch/>, <https://download.pytorch.org/whl/cu134/torch/> — wheel availability and sizes (measured by HTTP HEAD).
20. NVIDIA. *CUDA Toolkit Release Notes* (minimum driver table). <https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html>.
21. NVIDIA. *Drivers*. <https://www.nvidia.com/en-us/drivers/>; *CUDA on WSL*. <https://developer.nvidia.com/cuda/wsl>.
22. Apple. *Accelerated PyTorch training on Mac*. <https://developer.apple.com/metal/pytorch/> (stale version number noted).
23. PyTorch docs. *MPS backend*. <https://docs.pytorch.org/docs/stable/notes/mps.html>.

**Editor and tools**
24. Microsoft. *Download Visual Studio Code*. <https://code.visualstudio.com/download>; direct redirects <https://update.code.visualstudio.com/latest/win32-x64-user/stable>, <https://update.code.visualstudio.com/latest/win32-arm64-user/stable>, <https://update.code.visualstudio.com/latest/darwin-universal/stable>, <https://update.code.visualstudio.com/latest/linux-deb-x64/stable>, <https://update.code.visualstudio.com/latest/linux-rpm-x64/stable>.
25. Microsoft. *VS Code on Windows*. <https://code.visualstudio.com/docs/setup/windows>; *macOS*. <https://code.visualstudio.com/docs/setup/mac>; *Linux*. <https://code.visualstudio.com/docs/setup/linux>.
26. Microsoft. *Getting started with Python in VS Code*. <https://code.visualstudio.com/docs/python/python-quick-start>; *Python environments*. <https://code.visualstudio.com/docs/python/environments>; *Jupyter Notebooks in VS Code*. <https://code.visualstudio.com/docs/datascience/jupyter-notebooks>.
27. Visual Studio Marketplace. *Python* (`ms-python.python`). <https://marketplace.visualstudio.com/items?itemName=ms-python.python>; *Jupyter* (`ms-toolsai.jupyter`). <https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter>; *Python Environments*. <https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs>.
28. Microsoft Learn. *Install Windows Terminal*. <https://learn.microsoft.com/en-us/windows/terminal/install>.
29. Microsoft Learn. *about_Execution_Policies*. <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies>.
30. Microsoft Learn. *Install WSL*. <https://learn.microsoft.com/en-us/windows/wsl/install>.
31. Apple Support. *Terminal User Guide*. <https://support.apple.com/guide/terminal/welcome/mac>.
32. Homebrew. <https://brew.sh/>; formula API <https://formulae.brew.sh/api/formula/python@3.14.json>.
33. Ubuntu packages: <https://packages.ubuntu.com/resolute/python3>, <https://packages.ubuntu.com/noble/python3>; Debian: <https://packages.debian.org/stable/python3>; Fedora: <https://packages.fedoraproject.org/pkgs/python3.14/python3.14/>.
34. deadsnakes PPA. <https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa>; <https://github.com/deadsnakes>.
35. Git. *Downloads*: <https://git-scm.com/downloads>, Windows <https://git-scm.com/install/windows>, macOS <https://git-scm.com/install/mac>, Linux <https://git-scm.com/install/linux>; Git for Windows releases <https://github.com/git-for-windows/git/releases>.
36. GitHub Desktop. <https://desktop.github.com/download/>; docs <https://docs.github.com/en/desktop/installing-and-authenticating-to-github-desktop/installing-github-desktop>.
37. Google. *Colaboratory*. <https://colab.research.google.com/>; FAQ <https://research.google.com/colaboratory/faq.html>.
38. Library homes: python-chess <https://python-chess.readthedocs.io/en/latest/>; Jupyter <https://jupyter.org/install>; NumPy <https://numpy.org/install/>; Matplotlib <https://matplotlib.org/stable/install/index.html>.

---

## 11. Verification log and honest limits

* **Method:** HTTP fetches (curl) of the live official pages and JSON APIs on 2026-11-24; every URL listed above returned HTTP 200 on that date (redirect-style `update.code.visualstudio.com` links resolved to a 200 download). Strings for the legacy Python installer were read directly from `python-3.14.10-amd64.exe` (downloaded to a scratch folder outside the repo, not executed).
* **Not verifiable without an interactive GUI (marked [UNVERIFIED] or SVG):** the Windows App Installer dialog wording, the Windows 11 *Settings* breadcrumb for App execution aliases (the python docs give the Start-search route used here), the Microsoft Store listing URL for the install manager, and Colab's menu labels (login-gated; the FAQ confirms *Runtime Type* / *Hardware Accelerator* only).
* **Things that will change:** Python point releases, VS Code (monthly), PyTorch (CUDA tiles rotate roughly twice a year), the Windows installer retirement. The lesson text should reference "the version shown on the page" and keep commands version-agnostic (`py install 3.14`), as drafted above. A link-checker run before release is recommended (the validator step covers it).
* **Not covered (out of scope):** conda/Anaconda/uv/pyenv alternatives (VS Code's Python Environments extension will use `uv` automatically if present, but the course teaches plain `venv` — the one tool in Python's standard library); TensorFlow; AMD GPUs on Windows; Docker.
