# makepkg -dfC

pkgname_="settings-manager"
py_pkg="msm_ng"
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
  #cp ../../pyproject.toml .
  #echo 'version="0.9.1a1"' >msm_ng/__init__.py ?
  python -m build --wheel --no-isolation
}

package() {
  cd "msk-${pkgver}"
  mkdir -p "$pkgdir"/usr/{bin,share/applications,share/locale/}

  ./traductions.sh "$pkgdir/usr/share/locale"
  python -m installer --destdir="${pkgdir}" dist/*.whl --compile-bytecode 1

  install -Dm644 "${srcdir}/msk-${pkgver}/$py_pkg/msm-test.desktop" "${pkgdir}/usr/share/applications/"
  local pypkg_dir="$(python -c 'import site; print(site.getsitepackages()[0])')"
  ln -s "$pypkg_dir/$py_pkg/__main__.py" "$pkgdir"/usr/bin/msm-ng
  for plugin in "hello" "applications" "mirrors" "mhwd" "users" "system"; do
    ln -s "$pypkg_dir/$py_pkg/modules/$plugin/main.py" "$pkgdir"/usr/bin/msm-$plugin
  done

}