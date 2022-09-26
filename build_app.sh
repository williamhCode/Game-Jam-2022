IMPORTS='OpenGL.GL.shaders'
pyi-makespec --onefile --windowed --hidden-import="$IMPORTS" main.py

DATAS1="a.datas += Tree('./engine', prefix='engine')"
DATAS2="a.datas += Tree('./src', prefix='src')"

ed main.spec << EOF
23i
$DATAS1
$DATAS2
.
w
q
EOF

pyinstaller main.spec
