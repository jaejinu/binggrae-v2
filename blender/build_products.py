"""
빙그레할 틈 — 제품 3D 빌드 스크립트 (Blender 5.x)

형태만 단순화한 오리지널 모델(로고·실제 패키지 그래픽 없음)을 만들고
  - public/models/<slug>.glb   : LOOK CLOSER 인터랙티브 3D (파트 분리, explode 방향 포함)
  - public/products/<slug>.png : 사이트 전역 제품 이미지 (외곽선 렌더, 투명 배경)
  - blender/products.blend     : 편집용 원본
을 생성한다.

실행 (binggrae/ 에서):
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python blender/build_products.py
"""

import math
import os

import bmesh
import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS = os.path.join(ROOT, "public", "models")
PRODUCTS = os.path.join(ROOT, "public", "products")
os.makedirs(MODELS, exist_ok=True)
os.makedirs(PRODUCTS, exist_ok=True)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def material(name, hex_color, roughness=0.55):
    m = bpy.data.materials.new(name)
    h = hex_color.lstrip("#")
    rgb = [srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)]
    try:
        m.use_nodes = True
    except Exception:
        pass
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.25
    m.diffuse_color = (*rgb, 1)
    return m


def place(obj, coll, mat=None, smooth=True):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    if mat is not None:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    if smooth and obj.type == "MESH":
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def explode(obj, vec_yup):
    """three.js(Y-up) 기준 분해 이동량을 glTF extras로 남긴다."""
    obj["explode"] = list(vec_yup)


def catmull(points, n=6):
    """프로파일을 부드럽게 보간 (Catmull-Rom)."""
    pts = [points[0]] + points + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = (Vector(p) for p in pts[i - 1:i + 3])
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)))
    out.append(points[-1])
    return out


def lathe(name, profile, coll, mat, steps=72, smooth_n=6):
    prof = catmull(profile, smooth_n) if smooth_n else profile
    bm = bmesh.new()
    verts = [bm.verts.new((max(r, 0.0), 0.0, z)) for r, z in prof]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(bm, geom=verts + edges, cent=(0, 0, 0), axis=(0, 0, 1), angle=math.radians(360), steps=steps, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    return place(obj, coll, mat)


def add(op, coll, mat, name, smooth=True, **kw):
    getattr(bpy.ops.mesh, op)(**kw)
    obj = bpy.context.active_object
    obj.name = name
    return place(obj, coll, mat, smooth)


def new_collection(name):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


# ---------------------------------------------------------------------------
# products (Blender Z-up / 정면 = -Y 방향)
# ---------------------------------------------------------------------------

def build_banana_milk(coll):
    yellow = material("bm_body", "#ffd43b", 0.45)
    cream = material("bm_cap", "#fff6e0")
    foil = material("bm_foil", "#d9d9d9", 0.3)
    body = lathe("body", [(0, -1.3), (0.62, -1.28), (0.94, -1.02), (1.04, -0.45), (0.97, 0.12), (0.74, 0.52), (0.47, 0.78), (0.42, 1.0)], coll, yellow)
    cap = add("primitive_cylinder_add", coll, cream, "cap", vertices=64, radius=0.46, depth=0.22, location=(0, 0, 1.1))
    lid = add("primitive_cylinder_add", coll, foil, "foil", vertices=64, radius=0.43, depth=0.03, location=(0, 0, 1.23))
    band = add("primitive_torus_add", coll, cream, "band", major_radius=1.03, minor_radius=0.045, major_segments=96, minor_segments=12, location=(0, 0, -0.35))
    explode(body, (0, 0, 0))
    explode(cap, (0, 0.7, 0))
    explode(lid, (0, 1.2, 0))
    explode(band, (0, -0.25, 0))


def build_yoplait(coll):
    cream = material("yp_cup", "#fff6e0")
    pink = material("yp_band", "#ff9ebd")
    yogurt = material("yp_yogurt", "#ffc2d6", 0.3)
    lidm = material("yp_lid", "#ff5f8f", 0.35)
    cup = lathe("cup", [(0, -1.1), (0.72, -1.1), (0.95, 0.9), (0.92, 0.95)], coll, cream, smooth_n=0)
    rim = add("primitive_torus_add", coll, cream, "rim", major_radius=0.95, minor_radius=0.05, major_segments=96, minor_segments=12, location=(0, 0, 0.9))
    rim.parent = cup
    band = add("primitive_cone_add", coll, pink, "band", vertices=96, radius1=0.84, radius2=0.9, depth=0.5, location=(0, 0, 0.05), end_fill_type="NOTHING")
    band.parent = cup
    yog = add("primitive_cylinder_add", coll, yogurt, "yogurt", vertices=64, radius=0.9, depth=0.08, location=(0, 0, 0.74))
    lid = add("primitive_cylinder_add", coll, lidm, "lid", vertices=64, radius=1.0, depth=0.04, location=(0.1, 0, 1.0), rotation=(0, math.radians(-12), 0))
    # 숟가락: 손잡이 + 볼을 하나로 합침
    add("primitive_cube_add", coll, cream, "spoon", size=1, location=(0, 0, 0), scale=(0.12, 0.05, 1.4))
    handle = bpy.context.active_object
    add("primitive_uv_sphere_add", coll, cream, "spoon_bowl", segments=32, ring_count=16, radius=1, location=(0, 0, 0.8), scale=(0.22, 0.08, 0.29))
    bowl = bpy.context.active_object
    bpy.ops.object.select_all(action="DESELECT")
    handle.select_set(True)
    bowl.select_set(True)
    bpy.context.view_layer.objects.active = handle
    bpy.ops.object.join()
    spoon = bpy.context.active_object
    spoon.location = (0.62, 0, 1.15)
    spoon.rotation_euler = (0, math.radians(28), 0)
    explode(cup, (0, 0, 0))
    explode(yog, (0, 0.5, 0))
    explode(lid, (0, 1.2, 0))
    explode(spoon, (1.0, 0.4, 0))


def fish_outline():
    def bez(p0, p1, p2, p3, n=28):
        pts = []
        for i in range(n):
            t = i / n
            a = (1 - t) ** 3
            b = 3 * (1 - t) ** 2 * t
            c = 3 * (1 - t) * t ** 2
            d = t ** 3
            pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
        return pts

    pts = []
    pts += bez((-1.4, 0), (-1.2, 0.8), (0.2, 1.0), (0.8, 0.35))
    pts += [(0.8, 0.35)] + [(0.8 + (1.4 - 0.8) * k / 6, 0.35 + (0.8 - 0.35) * k / 6) for k in range(1, 6)]
    pts += bez((1.4, 0.8), (1.3, 0.3), (1.3, -0.3), (1.4, -0.8))
    pts += [(1.4, -0.8)] + [(1.4 + (0.8 - 1.4) * k / 6, -0.8 + (-0.35 + 0.8) * k / 6) for k in range(1, 6)]
    pts += bez((0.8, -0.35), (0.2, -1.0), (-1.2, -0.8), (-1.4, 0))
    # 중복 점 제거
    clean = []
    for p in pts:
        if not clean or (abs(p[0] - clean[-1][0]) + abs(p[1] - clean[-1][1])) > 1e-4:
            clean.append(p)
    return clean


def fish_slab(name, coll, mat, thickness, y, sx=1.0, sz=1.0, bevel=0.05):
    """정면(-Y)을 향한 붕어 모양 판. XZ 평면 윤곽을 Y 방향으로 두께를 준다."""
    bm = bmesh.new()
    verts = [bm.verts.new((x * sx, 0, z * sz)) for x, z in fish_outline()]
    face = bm.faces.new(verts)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    moved = [v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0, thickness, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = (0, y - thickness / 2, 0)
    place(obj, coll, mat, smooth=False)
    mod = obj.modifiers.new("bevel", "BEVEL")
    mod.width = bevel
    mod.segments = 3
    mod.limit_method = "ANGLE"
    return obj


def build_samanco(coll):
    wafer = material("sm_wafer", "#d98a3d", 0.7)
    cream = material("sm_cream", "#fff6e0")
    bean = material("sm_bean", "#7a3326")
    black = material("sm_eye", "#1a1a1a", 0.2)
    top = fish_slab("top", coll, wafer, 0.16, -0.24)
    mid = fish_slab("cream", coll, cream, 0.24, 0.0, sx=0.93, sz=0.9, bevel=0.07)
    red = fish_slab("bean", coll, bean, 0.12, -0.1, sx=0.6, sz=0.45, bevel=0.03)
    red.location.x -= 0.15
    bottom = fish_slab("bottom", coll, wafer, 0.16, 0.24)
    eye = add("primitive_uv_sphere_add", coll, black, "eye", segments=16, ring_count=10, radius=0.08, location=(-0.95, -0.34, 0.18))
    eye.parent = top
    eye.matrix_parent_inverse = top.matrix_world.inverted()
    # 비늘 느낌의 작은 돌기
    for i, (x, z) in enumerate([(-0.25, 0.1), (0.0, 0.18), (0.0, -0.05), (0.25, 0.08)]):
        s = add("primitive_uv_sphere_add", coll, wafer, f"scale_{i}", segments=16, ring_count=8, radius=1, location=(x, -0.33, z), scale=(0.1, 0.03, 0.1))
        s.parent = top
        s.matrix_parent_inverse = top.matrix_world.inverted()
    explode(top, (0, 0, 1.0))
    explode(red, (0, 0, 0.5))
    explode(mid, (0, 0, 0))
    explode(bottom, (0, 0, -0.9))


def build_bravo(coll):
    wafer = material("br_cone", "#e7a95b", 0.7)
    blue = material("br_sleeve", "#3d63dd", 0.4)
    cream = material("br_cream", "#fff6e0", 0.5)
    choco = material("br_choco", "#6b3a1e", 0.35)
    sprinkle_mats = [material(f"br_sp{i}", c) for i, c in enumerate(["#e8542f", "#ffd43b", "#7ed957"])]

    cone = add("primitive_cone_add", coll, wafer, "cone", vertices=64, radius1=0.0, radius2=0.75, depth=2.2, location=(0, 0, -0.5), end_fill_type="NOTHING")
    # 와플 격자 느낌의 링
    for i in range(4):
        z = -1.2 + i * 0.35
        r = 0.75 * (z + 1.6) / 2.2
        ring = add("primitive_torus_add", coll, wafer, f"cone_ring_{i}", major_radius=r + 0.01, minor_radius=0.018, major_segments=64, minor_segments=8, location=(0, 0, z))
        ring.parent = cone
        ring.matrix_parent_inverse = cone.matrix_world.inverted()
    sleeve = add("primitive_cone_add", coll, blue, "sleeve", vertices=64, radius1=0.53, radius2=0.8, depth=0.8, location=(0, 0, -0.05), end_fill_type="NOTHING")

    swirl_parts = []
    for i in range(4):
        t = add("primitive_torus_add", coll, cream, f"swirl_{i}", major_radius=0.72 - i * 0.16, minor_radius=0.2, major_segments=64, minor_segments=16, location=(0, 0, 0.72 + i * 0.22))
        swirl_parts.append(t)
    tip = add("primitive_cone_add", coll, cream, "swirl_tip", vertices=32, radius1=0.18, radius2=0.0, depth=0.3, location=(0, 0, 1.62))
    swirl_parts.append(tip)
    bpy.ops.object.select_all(action="DESELECT")
    for p in swirl_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = swirl_parts[0]
    bpy.ops.object.join()
    swirl = bpy.context.active_object
    swirl.name = "cream"

    # 초콜릿 코팅: 구의 윗부분만 남김
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.8, location=(0, 0, 0.62))
    top = bpy.context.active_object
    top.name = "choco"
    bm = bmesh.new()
    bm.from_mesh(top.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < 0.3], context="VERTS")
    bm.to_mesh(top.data)
    bm.free()
    place(top, coll, choco)
    for i in range(14):
        a = i * 2.4
        rr = 0.25 + (i % 4) * 0.12
        z = 0.62 + math.sqrt(max(0.0, 0.8 ** 2 - rr ** 2)) + 0.01
        sp = add("primitive_cylinder_add", coll, sprinkle_mats[i % 3], f"sprinkle_{i}", vertices=8, radius=0.025, depth=0.12, location=(math.cos(a) * rr, math.sin(a) * rr, z), rotation=(math.radians(90), 0, a))
        sp.parent = top
        sp.matrix_parent_inverse = top.matrix_world.inverted()

    explode(cone, (0, 0, 0))
    explode(sleeve, (0.9, -0.1, 0))
    explode(swirl, (0, 1.0, 0))
    explode(top, (0, 1.5, 0))


PRODUCTS_DEF = [
    ("banana-milk", build_banana_milk),
    ("yoplait", build_yoplait),
    ("samanco", build_samanco),
    ("bravo", build_bravo),
]


# ---------------------------------------------------------------------------
# scene / render setup
# ---------------------------------------------------------------------------

def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for b in list(block):
            block.remove(b)


def setup_render():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    try:
        scene.eevee.taa_render_samples = 48
    except Exception:
        pass
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1200
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"

    world = bpy.data.worlds.new("world") if not scene.world else scene.world
    scene.world = world
    try:
        world.use_nodes = True
    except Exception:
        pass
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (1, 1, 1, 1)
        bg.inputs["Strength"].default_value = 0.9

    # 외곽선 (Freestyle)
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    scene.render.line_thickness = 1.0
    fs = bpy.context.view_layer.freestyle_settings
    ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("outline")
    for attr in ("select_silhouette", "select_border", "select_external_contour"):
        if hasattr(ls, attr):
            setattr(ls, attr, True)
    for attr in ("select_crease",):
        if hasattr(ls, attr):
            setattr(ls, attr, False)
    ls.linestyle.color = (0.01, 0.01, 0.01)
    ls.linestyle.thickness = 6.0

    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.2
    sun_obj = bpy.data.objects.new("sun", sun)
    sun_obj.rotation_euler = (math.radians(45), math.radians(-15), math.radians(-35))
    scene.collection.objects.link(sun_obj)

    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam_obj = bpy.data.objects.new("cam", cam)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    return cam_obj


def frame_camera(cam_obj, objs):
    pts = []
    for o in objs:
        if o.type == "MESH":
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (lo + hi) / 2
    size = hi - lo
    direction = Vector((0.45, -1.0, 0.42)).normalized()
    cam_obj.location = center + direction * 12
    cam_obj.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    height = size.z
    width = max(size.x, size.y)
    cam_obj.data.ortho_scale = max(height * 1.18, width * 1.18 * 1.2)


def main():
    reset_scene()
    cam = setup_render()
    colls = {}

    for slug, build in PRODUCTS_DEF:
        coll = new_collection(slug)
        colls[slug] = coll
        build(coll)

    for slug, _ in PRODUCTS_DEF:
        coll = colls[slug]
        objs = list(coll.all_objects)
        for other_slug, other in colls.items():
            other.hide_render = other_slug != slug

        # GLB (최상위 오브젝트만 선택 → 자식은 함께 포함)
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs:
            o.select_set(True)
        bpy.ops.export_scene.gltf(
            filepath=os.path.join(MODELS, f"{slug}.glb"),
            export_format="GLB",
            use_selection=True,
            export_extras=True,
            export_apply=True,
            export_yup=True,
        )

        # PNG 렌더
        frame_camera(cam, objs)
        bpy.context.scene.render.filepath = os.path.join(PRODUCTS, f"{slug}.png")
        bpy.ops.render.render(write_still=True)
        print(f"BUILT {slug}")

    # 편집용 .blend: 제품을 옆으로 나란히 배치해 저장
    for i, (slug, _) in enumerate(PRODUCTS_DEF):
        colls[slug].hide_render = False
        for o in colls[slug].objects:
            if o.parent is None:
                o.location.x += (i - 1.5) * 3.2
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", "products.blend"))
    print("DONE")


main()
