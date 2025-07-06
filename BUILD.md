# Build

Save Manager for UNDERTALE and deltarune is a PyQt6 app. To run it, the following things need to be done:

- Compile the UI to .py files
- Compile the external styles

You can also compile an executable using nuitka, and a Windows Installer file using WiX.

Python 3.12 or higher is required.

## Linux

### Prerequisites

The following packages need to be installed to compile and run Save Manager for Undertale and Deltarune, per distribution.

#### Debian

```sh
sudo apt update
sudo apt upgrade
sudo apt install git  # General
sudo apt install pyqt5-dev-tools qtchooser qttools5-dev-tools  # Compile resources
sudo apt install patchelf ccache  # Compile with nuitka
```

#### RedHat

```sh
sudo dnf upgrade --refresh
sudo dnf install git  # General
sudo dnf install python3-qt5 mingw64-qt-qmake  # Compile resources
sudo dnf install patchelf ccache  # Compile with nuitka
```

#### Arch

```sh
sudo pacman -Syu
sudo pacman -S git  # General
sudo pacman -S python-pyqt5 qt5-tools  # Compile resources
sudo pacman -S patchelf ccache  # Compile with nuitka
```

### Downloading the source files

```sh
git clone https://github.com/TheCheese42/ut-dr-save-manager
```

### Compiling Data

```sh
cd ut-dr-save-manager  # cd into the cloned folder
python -m venv .venv  # At least Python 3.12
source .venv/bin/activate
pip install -r requirements.txt -r dev-requirements.txt
pyqt-utils udsm --compile-ui  # Required
source scripts/compile-styles.sh  # Optional, otherwise only the default style will be available
```

### Run

Now you can already run Save Manager for Undertale and Deltarune.

```sh
# Run from within the cloned ut-dr-save-manager/ folder
python -m ut-dr-save-manager
```

### Bundle Executable

Finally, you can also bundle everything into an executable. For that, we use [nuitka](https://nuitka.net).

```sh
# Run from within the cloned ut-dr-save-manager/ folder
pyqt-utils udsm --build-linux --build-data-dir udsm/premade_saves/=premade_saves/ --build-product-name "Save Manager for Undertale and Deltarune" --build-icon udsm/icons/icon.png
```

> Note:
> If you encounter a weird error with the line
> `FATAL: Failed unexpectedly in Scons C backend compilation.`
> You can try adding `--clang` to the `scripts/build_linux_x86_64.sh` script.
> Of course you also need to install clang using your package manager.

The resulting executable can be found at `build/Save Manager for Undertale and Deltarune.bin`.

## Windows

### Prerequisites

- Install a Python version of at least 3.12 from <https://www.python.org/downloads/>
- Install git from <https://git-scm.com/downloads/win>

### Downloading the source files

```pwsh
git clone https://github.com/TheCheese42/ut-dr-save-manager
```

### Compiling Data

```pwsh
Set-Location .\ut-dr-save-manager  # cd into the cloned folder
python -m venv .venv  # At least Python 3.12
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r dev-requirements.txt
pyqt-utils udsm --compile-ui  # Required
Set-Alias -Name lrelease -Value .\.venv\Lib\site-packages\qt6_applications\Qt\bin\lrelease.exe  # Make the lrelease.exe tool available
.\scripts\compile-styles.ps1  # Optional, otherwise only the default style will be available
```

### Run

Now you can already run Save Manager for Undertale and Deltarune.

```pwsh
# Run from within the cloned ut-dr-save-manager\ folder
python -m udsm
```

### Bundle Executable

Finally, you can also bundle everything into an executable. For that, we use [nuitka](https://nuitka.net).

```pwsh
# Run from within the cloned ut-dr-save-manager\ folder
pyqt-utils udsm --build-windows --build-data-dir .\udsm\premade_saves\=premade_saves\ --build-product-name "Save Manager for Undertale and Deltarune" --build-icon .\udsm\icons\icon.ico
```

The resulting executable can be found at `build\Save Manager for Undertale and Deltarune.exe`.

### Bundle Installer

Lastly, it's possible to create a Windows Installer file using WiX.

Install a recent [dotnet](https://dotnet.microsoft.com/en-us/download) version and run:

```pwsh
dotnet build
```
