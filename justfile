# install dependencies into .venv using uv
sync:
    uv sync --all-packages --locked --all-extras --dev

# clean build artifacts
clean:
    rm -vrf build dist `find . -name '*.egg-info'` `find src -name '__pycache__'` `find chemistry_raptor_gui -name '__pycache__'`

# run the GUI frontend
[group('run')]
gui:
    uv run chemistry_raptor

# builds all packages as .whl
[group('build')]
wheel:
    uv build --all-packages --clear

pyinstaller_shared_args := '--name RAPTOR --windowed --add-data "chemistry_raptor_gui/src/chemistry_raptor_gui/ui/assets:assets" chemistry_raptor_gui/src/chemistry_raptor_gui/__main__.py'

# alias to linux_archive and linux_standalone
[group('build linux')]
linux: linux_archive linux_standalone

# builds a .tar.xz file that includes all dependencies to run the gui on linux
[group('build linux')]
linux_archive:
    rm -rvf ./dist/RAPTOR/ ./dist/RAPTOR.tar.xz
    uv run pyinstaller {{ pyinstaller_shared_args }}
    cd dist && tar czf RAPTOR.tar.xz ./RAPTOR/

# builds a standalone binary to run the gui on linux
[group('build linux')]
linux_standalone:
    rm -rvf ./dist/RAPTOR ./dist/RAPTOR_linux_standalone.bin
    uv run pyinstaller --onefile {{ pyinstaller_shared_args }}
    mv ./dist/RAPTOR ./dist/RAPTOR_linux_standalone.bin

# alias to macos_dmg and macos_standalone
[group('build macos')]
macos: macos_dmg macos_standalone

# builds a macos disk image
[group('build macos')]
macos_dmg:
    rm -rvf ./dist/RAPTOR ./dist/RAPTOP.app
    uv run pyinstaller --onedir {{ pyinstaller_shared_args }}
    cd dist && create-dmg --volname "RAPTOR" --window-pos 200 120 --window-size 800 450 --icon-size 100 --app-drop-link 600 185 RAPTOR.dmg ./RAPTOR.app

# builds a standalone binary to run the gui on macos
[group('build macos')]
macos_standalone:
    rm -rvf ./dist/RAPTOR ./dist/RAPTOR_macos_standalone.bin
    pyinstaller --onefile {{ pyinstaller_shared_args }}
    mv ./dist/RAPTOR ./dist/RAPTOR_macos_standalone.bin
