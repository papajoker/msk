# makepkg -dfC

pkgname_="settings-manager"
py_pkg="msm_test"
pkgname="${pkgname_}-ng"
pkgver="0.9.1"
pkgrel=1

pkgdesc="Linux System Settings Tool: Next Generation"
license=('MIT License')

arch=('any')
url="https://github.com/papajoker/msk"
source=("https://github.com/papajoker/msk/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=("SKIP")

depends=(
  'inxi'
  'pyside6'
)
makedepends=("git" "python-build" "python-installer")

build() {
  cd "msk-${pkgver}"
  touch "$py_pkg/modules/__init__.py"
  touch "$py_pkg/modules/_plugin/__init__.py"
  python -m build --wheel --no-isolation
}

package() {
  cd "msk-${pkgver}"
  python -m installer --destdir="${pkgdir}" dist/*.whl --compile-bytecode 1

  local pypkg_dir="$(python -c 'import site; print(site.getsitepackages()[0])')/$py_pkg"
  mkdir -p "$pkgdir"/usr/{bin,share/applications}
  install -Dm644 "${srcdir}/msk-${pkgver}/$py_pkg/msm-test.desktop" "${pkgdir}/usr/share/applications/"
  install -Dm755 "${srcdir}/msk-${pkgver}/${py_pkg}/run.sh" "${pkgdir}/usr/bin/msm-test"
}

