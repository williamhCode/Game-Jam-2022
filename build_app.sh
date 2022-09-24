IMPORTS='OpenGL.GL.shaders'
pyi-makespec --onefile --windowed --hidden-import="$IMPORTS" mini_game.py

DATAS="a.datas += Tree('./engine', prefix='engine')"

ed mini_game.spec << EOF
23i
$DATAS
.
w
q
EOF

pyinstaller mini_game.spec
