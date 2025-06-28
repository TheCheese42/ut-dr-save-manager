deactivate || true
mkdir style_clones
cd style_clones
git clone https://github.com/Alexhuszagh/BreezeStyleSheets
cd BreezeStyleSheets
python -m venv .venv
source .venv/bin/activate
pip install PySide6
python configure.py --styles=all --extensions=all --qt-framework pyqt6 --resource breeze.qrc --compiled-resource "breeze_pyqt6.py"
mkdir -p ../../udsm/styles/Breeze
cp -f LICENSE.md ../../udsm/styles/Breeze/
cp -rf dist/* ../../udsm/styles/Breeze/
cp -f resources/breeze_pyqt6.py ../../udsm/styles/Breeze/
rm -rf ../../udsm/styles/Breeze/*-alt
deactivate
cd ../../
rm -rf style_clones
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi
