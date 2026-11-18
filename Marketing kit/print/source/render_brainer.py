# Renders the Brainer at print size from the game kit's brainer2.py, on a transparent film with no floor shadow.
# usage: blender -b --python render_brainer.py -- <brainer2.py> <outdir> <size px> <stages, comma separated>
import bpy, sys, os, runpy

argv = sys.argv[sys.argv.index('--') + 1:]
KIT, OUTDIR, SIZE, WANT = argv[0], argv[1], int(argv[2]), [int(s) for s in argv[3].split(',')]
os.makedirs(OUTDIR, exist_ok=True)
sys.argv = ['blender', '--', OUTDIR, 'none']   # an unknown mode: the kit builds nothing on load
K = runpy.run_path(KIT, run_name='brainer2_kit')
for s in WANT:
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    name, ex, pose = K['STAGES'][s - 1]
    K['build'](s, 'G', style='carved_dense', face=f'face_pixel_{ex}.png', pose=pose)
    K['studio']((SIZE, SIZE), (1.6, -8.4, 2.4), (0, 0, 1.45), lens=90)   # tighter than the kit's stages shot: the robot fills the frame
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.is_shadow_catcher: o.hide_render = True
    K['scene'].cycles.samples = 160
    K['render'](os.path.join(OUTDIR, f'stage-{s}.png'))
