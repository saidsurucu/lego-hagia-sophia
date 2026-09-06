"""Render actual cached official LDraw meshes with Blender (no add-on required).

blender --background --python scripts/render_model.py -- MODEL.ldr OUTPUT.png
Optional third argument: 'hero', 'rear', 'east', 'west' or 'top'; fourth: 'draft', 'final' (default), or '4k'.
"""
from pathlib import Path
import sys
import math
import time
import bpy
from mathutils import Matrix, Vector

CACHE = Path(__file__).resolve().parents[1] / 'assets' / 'ldraw'
# Official library LDConfig.ldr values, retrieved 2026-09-06.
COLORS = {
    0: '1B2A34', 1: '1E5AA8', 2: '00852B', 4: 'B40000',
    7: '8A928D', 8: '545955', 14: 'FAC80A', 15: 'F4F4F4',
    19: 'D7BA8C', 22: '671F81', 25: 'D67923', 28: '897D62',
    70: '5F3109', 71: '969696', 72: '646464', 73: '7396C8',
    84: 'AA7D55', 85: '441A91', 86: '7B5D41', 92: 'BB805A',
    272: '19325A', 288: '00451A', 308: '352100', 320: '720012',
    297: 'AA7F2E', 378: '708E7C', 379: '70819A', 484: '91501C',
}
materials = {}
geometry = {}

def material(color):
    if color in materials:
        return materials[color]
    rgb = COLORS.get(color)
    if rgb is None:
        raise ValueError(f'Add exact LDraw color {color} to renderer palette')
    mat = bpy.data.materials.new(f'LDraw {color}')
    srgb = tuple(int(rgb[i:i+2], 16) / 255 for i in (0, 2, 4))
    linear = tuple(c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in srgb)
    mat.diffuse_color = (*linear, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*linear, 1)
    bsdf.inputs['Roughness'].default_value = .27
    if color == 297:  # LDraw Pearl Gold: pearlescent molded plastic
        bsdf.inputs['Metallic'].default_value = .35
        bsdf.inputs['Roughness'].default_value = .30
    materials[color] = mat
    return mat

def find(name):
    name = name.replace('\\', '/').lower()
    for kind in ('parts', 'p'):
        path = CACHE / kind / name
        if path.exists():
            return path
    raise FileNotFoundError(f'{name}: run scripts/fetch_parts.py --model MODEL.ldr first')

def transform(fields):
    nums = list(map(float, fields[2:14]))
    return Matrix(((nums[3], nums[4], nums[5], nums[0]),
                   (nums[6], nums[7], nums[8], nums[1]),
                   (nums[9], nums[10], nums[11], nums[2]),
                   (0, 0, 0, 1)))

def parse(path, matrix, inherited, vertices, faces, colors):
    # LDraw BFC determines the local face winding. Blender renders both sides;
    # preserving winding also keeps lighting reliable for reflected references.
    ccw = True
    invert_next = False
    for line in path.read_text(errors='replace').splitlines():
        f = line.strip().split()
        if not f:
            continue
        if f[0] == '0':
            if 'BFC' in f:
                if 'CCW' in f:
                    ccw = True
                elif 'CW' in f:
                    ccw = False
                if 'INVERTNEXT' in f:
                    invert_next = True
            continue
        if f[0] == '1':
            child_matrix = matrix @ transform(f)
            start = len(faces)
            col = int(f[1])
            parse(find(' '.join(f[14:])), child_matrix,
                  inherited if col == 16 else col, vertices, faces, colors)
            if invert_next:
                for index in range(start, len(faces)):
                    faces[index] = tuple(reversed(faces[index]))
            invert_next = False
        elif f[0] in ('3', '4'):
            count = int(f[0])
            first = len(vertices)
            for k in range(count):
                p = matrix @ Vector(tuple(map(float, f[2+3*k:5+3*k])))
                vertices.append((p.x / 20, p.z / 20, -p.y / 20))
            face = tuple(range(first, first + count))
            # Coordinate conversion has determinant +1; only source winding flips.
            if (not ccw) != (matrix.to_3x3().determinant() < 0):
                face = tuple(reversed(face))
            faces.append(face)
            colors.append(inherited if int(f[1]) == 16 else int(f[1]))

def mesh_for(name, color):
    key = (name, color)
    if key in geometry:
        return geometry[key]
    vertices, faces, colors = [], [], []
    parse(find(name), Matrix.Identity(4), color, vertices, faces, colors)
    mesh = bpy.data.meshes.new(f'{name}-{color}')
    mesh.from_pydata(vertices, [], faces)
    slots = list(dict.fromkeys(colors))
    for col in slots:
        mesh.materials.append(material(col))
    index = {col: i for i, col in enumerate(slots)}
    for polygon, col in zip(mesh.polygons, colors):
        polygon.material_index = index[col]
    mesh.update()
    geometry[key] = mesh
    return mesh

def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

def main():
    args = sys.argv[sys.argv.index('--')+1:]
    model, output = map(Path, args[:2])
    view = args[2] if len(args) > 2 else 'hero'
    quality = args[3] if len(args) > 3 else 'final'
    profiles = {'draft': (1200, 1000, 24), 'final': (1800, 1500, 48), '4k': (3840, 3200, 64)}
    if quality not in profiles:
        raise ValueError(f'Unknown quality {quality!r}; choose {list(profiles)}')
    image_width, image_height, samples = profiles[quality]
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    conv = Matrix(((.05, 0, 0, 0), (0, 0, .05, 0), (0, -.05, 0, 0), (0, 0, 0, 1)))
    count = 0
    for line in model.read_text().splitlines():
        f = line.split()
        if not f or f[0] != '1':
            continue
        name, color = ' '.join(f[14:]), int(f[1])
        obj = bpy.data.objects.new(f'{count:04d} {name}', mesh_for(name, color))
        bpy.context.collection.objects.link(obj)
        obj.matrix_world = conv @ transform(f) @ conv.inverted()
        count += 1
    bpy.context.view_layer.update()
    bounds = [o.matrix_world @ Vector(corner) for o in bpy.context.scene.objects
              if o.type == 'MESH' for corner in o.bound_box]
    min_z, max_z = min(p.z for p in bounds), max(p.z for p in bounds)
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, min_z-.045))
    floor = bpy.context.object
    floor.name = 'Studio ground'
    mat = bpy.data.materials.new('Warm paper backdrop')
    mat.diffuse_color = (.94, .93, .91, 1)
    mat.use_nodes = True
    floor_bsdf = mat.node_tree.nodes.get('Principled BSDF')
    floor_bsdf.inputs['Base Color'].default_value = (.94, .93, .91, 1)
    floor_bsdf.inputs['Roughness'].default_value = .85
    floor.data.materials.append(mat)
    center = (0, 0, (max_z + min_z) * .39)
    # Model grid: +X south, +Z east. Blender maps LDraw +Z to +Y.
    camera_positions = {
        'hero': (125, -30, 42),
        'rear': (-82, 100, 78),
        'east': (26, 125, 50),
        'west': (26, -125, 50),
        'top': (0, -1, 140),
    }
    if view not in camera_positions:
        raise ValueError(f'Unknown view {view!r}; choose {list(camera_positions)}')
    bpy.ops.object.camera_add(location=camera_positions[view])
    camera = bpy.context.object
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = {'hero': 74, 'rear': 80, 'east': 74, 'west': 74, 'top': 63}[view]
    aim(camera, center)
    scene = bpy.context.scene
    scene.camera = camera
    for name, pos, power, size in (
        ('Large softbox', (-35, -45, 95), 90000, 65),
        ('Fill softbox', (60, -5, 55), 40000, 55),
        ('Rim softbox', (0, 65, 80), 65000, 45),
    ):
        bpy.ops.object.light_add(type='AREA', location=pos)
        light = bpy.context.object
        light.name = name
        light.data.energy = power
        light.data.shape = 'DISK'
        light.data.size = size
        aim(light, center)
    # A bright neutral studio environment prevents a dark distant-ground gradient.
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get('Background')
    background.inputs['Color'].default_value = (1, .98, .95, 1)
    background.inputs['Strength'].default_value = .65
    scene.render.engine = 'CYCLES'
    # Use available Apple Metal hardware for high-resolution renders.
    if sys.platform == 'darwin' and quality == '4k':
        try:
            prefs = bpy.context.preferences.addons['cycles'].preferences
            prefs.compute_device_type = 'METAL'
            prefs.get_devices()
            has_gpu = any(device.type == 'METAL' for device in prefs.devices)
            if has_gpu:
                for device in prefs.devices:
                    device.use = device.type == 'METAL'
                scene.cycles.device = 'GPU'
                print('Cycles device: Metal GPU', flush=True)
        except (RuntimeError, TypeError) as exc:
            print(f'Metal unavailable; using CPU: {exc}', flush=True)
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = image_width
    scene.render.resolution_y = image_height
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.exposure = .15
    scene.render.image_settings.file_format = 'PNG'
    output.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output.resolve())
    print(f'Rendering {count} actual parts, {len(geometry)} mesh variants', flush=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output.with_suffix('.blend').resolve()))
    last_progress = [0.0]
    def report_render_stats(*messages):
        now = time.monotonic()
        if now-last_progress[0] >= 5:
            print('Render progress:', *messages, flush=True)
            last_progress[0] = now
    bpy.app.handlers.render_stats.append(report_render_stats)
    try:
        bpy.ops.render.render(write_still=True)
    finally:
        bpy.app.handlers.render_stats.remove(report_render_stats)

if __name__ == '__main__':
    main()
