# -*- mode: python ; coding: utf-8 -*-
from dotenv import load_dotenv
import os
load_dotenv(encoding='utf-8')

version_number = os.getenv("VERSION")
app_name = os.getenv("APP_NAME")
robot_name = app_name + '_' + version_number


block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\user\\Desktop\\workbench\\hamburgsud2'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name=robot_name,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
