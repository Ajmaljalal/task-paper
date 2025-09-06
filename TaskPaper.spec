# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('transparent_icon.png', '.')],
    hiddenimports=[
        'google.auth.transport.requests',
        'google.auth.transport._http_client',
        'googleapiclient.discovery',
        'googleapiclient.errors',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'openai',
        'rumps',
        'sounddevice',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TaskPaper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TaskPaper',
)

app = BUNDLE(
    coll,
    name='TaskPaper.app',
    icon=None,
    bundle_identifier='com.taskpaper.app',
    info_plist={
        'LSUIElement': True,  # Background app, no dock icon
        'CFBundleName': 'TaskPaper',
        'CFBundleDisplayName': 'TaskPaper',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024, TaskPaper',
    },
)
