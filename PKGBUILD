# Maintainer: dielectric-coder
pkgname=flatcam
pkgver=8.5
pkgrel=1
pkgdesc='2D Computer-Aided Manufacturing application for PCB fabrication on CNC routers'
arch=('x86_64')
url='https://github.com/dielectric-coder/FlatCAM'
license=('MIT')
depends=(
    'python'
    'python-pyqt5'
    'geos'
    'libspatialindex'
    'qt5-base'
    'freetype2'
    'libpng'
)
makedepends=(
    'python-pip'
    'python-setuptools'
)
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/FlatCAM-$pkgver"

    # Install application files
    install -dm755 "$pkgdir/opt/flatcam"
    cp -a \
        FlatCAM.py FlatCAMApp.py FlatCAMObj.py FlatCAMDraw.py \
        FlatCAMGUI.py FlatCAMProcess.py FlatCAMPool.py FlatCAMWorkerStack.py \
        FlatCAMWorker.py FlatCAMShell.py FlatCAMTool.py FlatCAMCommon.py \
        GUIElements.py ObjectUI.py ObjectCollection.py PlotCanvas.py \
        VisPyCanvas.py VisPyVisuals.py VisPyPatches.py VisPyTesselators.py \
        DblSidedTool.py MeasurementTool.py \
        camlib.py svgparse.py termwidget.py \
        "$pkgdir/opt/flatcam/"

    cp -a share tclCommands descartes "$pkgdir/opt/flatcam/"
    cp -a requirements.txt "$pkgdir/opt/flatcam/"

    # Install Python dependencies into a contained lib directory
    pip install --no-warn-script-location --no-compile \
        --target="$pkgdir/opt/flatcam/lib" \
        -r requirements.txt

    # Remove PyQt5 from lib/ — we use the system package
    rm -rf "$pkgdir/opt/flatcam/lib/PyQt5"*

    # Fix any references to $pkgdir in installed files
    find "$pkgdir/opt/flatcam/lib" -name '*.pth' -delete 2>/dev/null || true

    # Launcher script
    install -Dm755 /dev/stdin "$pkgdir/usr/bin/flatcam" <<'EOF'
#!/bin/bash
export PYTHONPATH="/opt/flatcam/lib${PYTHONPATH:+:$PYTHONPATH}"
cd /opt/flatcam
exec python /opt/flatcam/FlatCAM.py "$@"
EOF

    # Desktop entry
    install -Dm644 /dev/stdin "$pkgdir/usr/share/applications/flatcam.desktop" <<EOF
[Desktop Entry]
Name=FlatCAM
Comment=2D CAM for PCB fabrication on CNC routers
Exec=flatcam
Icon=/opt/flatcam/share/flatcam_icon128.png
Terminal=false
Type=Application
Categories=Engineering;Electronics;Science;
EOF

    # License
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
