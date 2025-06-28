if (Get-Command "deactivate" -ErrorAction SilentlyContinue) {
    deactivate
}
New-Item -Fo -ItemType Directory style_clones
Set-Location style_clones
git clone https://github.com/Alexhuszagh/BreezeStyleSheets
Set-Location BreezeStyleSheets
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install PySide6
python configure.py --styles=all --extensions=all --qt-framework pyqt6 --resource breeze.qrc --compiled-resource "breeze_pyqt6.py"
New-Item -Fo -ItemType Directory ../../udsm/styles/Breeze
Copy-Item -Fo LICENSE.md ../../udsm/styles/Breeze/
Copy-Item -R -Fo dist/* ../../udsm/styles/Breeze/
Copy-Item -Fo resources/breeze_pyqt6.py ../../udsm/styles/Breeze/
Remove-Item -Recurse -Force ../../udsm/styles/Breeze/*-alt
deactivate
Set-Location ../../
Remove-Item -Recurse -Force style_clones
if (Test-Path .venv/Scripts/Activate.ps1 -PathType Leaf) {
    . .venv/Scripts/Activate.ps1
}
