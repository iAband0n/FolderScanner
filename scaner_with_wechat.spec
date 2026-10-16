# -*- mode: python ; coding: utf-8 -*-

import os

datas = [('icon.ico', '.')]
if os.path.exists('geek.exe'):
    datas.append(('geek.exe', '.'))


a = Analysis(
    ['scaner_with_wechat.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['unittest', 'distutils', 'pydoc', 'doctest', 'lib2to3', 'idlelib', 'test'],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    name='scaner_with_wechat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
