"""
빙그레할 틈 — 제품 3D 빌드 스크립트 (Blender 5.x, Cycles)

형태·재질만 사실적으로 만든 오리지널 모델(로고·실제 패키지 그래픽 없음)을 생성한다.
  - public/products/<slug>.webp : Cycles 실사 렌더 (투명 배경, 제품별 HDRI 조명)
  - public/models/<slug>.glb   : LOOK CLOSER 인터랙티브 3D (절차적 질감을 텍스처로 베이킹, 파트 분리, explode extras)
  - blender/products.blend     : 편집용 원본 (절차적 재질 그대로)

실행 (binggrae/ 에서):
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python blender/build_products.py
옵션 (환경변수):
  ONLY=bravo            특정 제품만
  SKIP_GLB=1            렌더만 (베이킹/내보내기 생략)
  SAMPLES=128           렌더 샘플 수
"""

import math
import os
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS = os.path.join(ROOT, "public", "models")
PRODUCTS = os.path.join(ROOT, "public", "products")
os.makedirs(MODELS, exist_ok=True)
os.makedirs(PRODUCTS, exist_ok=True)

ONLY = os.environ.get("ONLY")
SKIP_GLB = os.environ.get("SKIP_GLB") == "1"
SAMPLES = int(os.environ.get("SAMPLES", "128"))
random.seed(7)


# ---------------------------------------------------------------------------
# material helpers
# ---------------------------------------------------------------------------

def lin(hex_color):
    h = hex_color.lstrip("#")

    def f(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return (*[f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)], 1.0)


class Mat:
    """Principled BSDF 기반 재질 빌더. 절차적 노드가 있으면 bake 대상으로 표시한다."""

    def __init__(self, name, color, roughness=0.5, **inputs):
        self.m = bpy.data.materials.new(name)
        try:
            self.m.use_nodes = True
        except Exception:
            pass
        self.nt = self.m.node_tree
        self.bsdf = self.nt.nodes["Principled BSDF"]
        self.set("Base Color", lin(color))
        self.set("Roughness", roughness)
        for k, v in inputs.items():
            self.set(k.replace("_", " "), v)
        self.m.diffuse_color = lin(color)
        self.m["bake"] = False
        self._coord = None

    def set(self, name, value):
        if name in self.bsdf.inputs:
            self.bsdf.inputs[name].default_value = value

    def node(self, kind, **props):
        n = self.nt.nodes.new(kind)
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def coord(self):
        if self._coord is None:
            self._coord = self.node("ShaderNodeTexCoord").outputs["Object"]
        return self._coord

    def link(self, a, b):
        self.nt.links.new(a, b)

    def color_noise(self, c1, c2, scale=6.0, detail=4.0):
        """두 색 사이를 노이즈로 섞어 얼룩/구운 색 변화를 준다."""
        self.m["bake"] = True
        noise = self.node("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = scale
        noise.inputs["Detail"].default_value = detail
        self.link(self.coord(), noise.inputs["Vector"])
        ramp = self.node("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.35
        ramp.color_ramp.elements[0].color = lin(c1)
        ramp.color_ramp.elements[1].position = 0.7
        ramp.color_ramp.elements[1].color = lin(c2)
        self.link(noise.outputs["Fac"], ramp.inputs["Fac"])
        self.link(ramp.outputs["Color"], self.bsdf.inputs["Base Color"])
        return ramp

    def bump(self, height_socket, strength=0.3, distance=0.02):
        self.m["bake"] = True
        b = self.node("ShaderNodeBump")
        b.inputs["Strength"].default_value = strength
        if "Distance" in b.inputs:
            b.inputs["Distance"].default_value = distance
        self.link(height_socket, b.inputs["Height"])
        self.link(b.outputs["Normal"], self.bsdf.inputs["Normal"])
        return b

    def noise_bump(self, scale=40.0, strength=0.15, detail=6.0):
        n = self.node("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        self.link(self.coord(), n.inputs["Vector"])
        return self.bump(n.outputs["Fac"], strength)

    def voronoi_bump(self, scale=9.0, strength=0.35):
        v = self.node("ShaderNodeTexVoronoi")
        v.inputs["Scale"].default_value = scale
        v.feature = "F1"
        self.link(self.coord(), v.inputs["Vector"])
        return self.bump(v.outputs["Distance"], strength)

    def waffle(self, scale=7.0, strength=0.6, dark="#9a5a22"):
        """45도로 교차하는 홈 → 와플콘 격자. 홈 부분은 어둡게."""
        self.m["bake"] = True
        mins = []
        for angle in (math.radians(45), math.radians(-45)):
            mapping = self.node("ShaderNodeMapping")
            mapping.inputs["Rotation"].default_value = (0, angle, 0)
            self.link(self.coord(), mapping.inputs["Vector"])
            wave = self.node("ShaderNodeTexWave", wave_type="BANDS", bands_direction="X")
            wave.inputs["Scale"].default_value = scale
            wave.inputs["Distortion"].default_value = 0.0
            self.link(mapping.outputs["Vector"], wave.inputs["Vector"])
            mins.append(wave.outputs["Fac"])
        mn = self.node("ShaderNodeMath", operation="MINIMUM")
        self.link(mins[0], mn.inputs[0])
        self.link(mins[1], mn.inputs[1])
        self.bump(mn.outputs["Value"], strength)
        ramp = self.node("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.08
        ramp.color_ramp.elements[0].color = lin(dark)
        ramp.color_ramp.elements[1].position = 0.3
        ramp.color_ramp.elements[1].color = self.bsdf.inputs["Base Color"].default_value
        self.link(mn.outputs["Value"], ramp.inputs["Fac"])
        self.link(ramp.outputs["Color"], self.bsdf.inputs["Base Color"])


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------

def place(obj, coll, mat=None, smooth=True):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    if mat is not None and obj.type in {"MESH", "CURVE"}:
        obj.data.materials.clear()
        obj.data.materials.append(mat.m if isinstance(mat, Mat) else mat)
    if smooth and obj.type == "MESH":
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def mod(obj, kind, **props):
    m = obj.modifiers.new(kind.lower(), kind)
    for k, v in props.items():
        setattr(m, k, v)
    return m


def subsurf(obj, levels=2):
    return mod(obj, "SUBSURF", levels=levels, render_levels=levels)


def explode(obj, vec_yup):
    """three.js(Y-up) 기준 분해 이동량을 glTF extras로 남긴다."""
    obj["explode"] = list(vec_yup)


def parent_keep(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def catmull(points, n=8):
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


def lathe(name, profile, coll, mat, steps=96, smooth_n=8):
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
    return place(bpy.data.objects.new(name, me), coll, mat)


def prim(op, coll, mat, name, smooth=True, **kw):
    getattr(bpy.ops.mesh, op)(**kw)
    obj = bpy.context.active_object
    obj.name = name
    return place(obj, coll, mat, smooth)


def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = name
    return o


def cloud_texture(name, size=0.4, depth=2):
    t = bpy.data.textures.new(name, "CLOUDS")
    t.noise_scale = size
    t.noise_depth = depth
    return t


def new_collection(name):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


# ---------------------------------------------------------------------------
# products (Blender Z-up, 정면 = -Y)
# ---------------------------------------------------------------------------

def add_droplets(body, coll, count=340):
    """차가운 단지 표면의 물방울 + 흘러내린 자국. 하나의 메시로 합쳐 몸통에 붙인다."""
    water = Mat("water", "#ffffff", 0.02, Transmission_Weight=1.0, IOR=1.33, Specular_IOR_Level=0.6)
    src = bmesh.new()
    src.from_mesh(body.data)
    src.faces.ensure_lookup_table()
    faces = [f for f in src.faces if -1.12 < f.calc_center_median().z < 0.5]
    weights = [f.calc_area() for f in faces]
    total = sum(weights)
    out = bmesh.new()
    for i in range(count):
        # 면적 비례로 면을 고르고, 면 안의 임의 지점에 배치
        r = random.uniform(0, total)
        acc = 0.0
        for f, w in zip(faces, weights):
            acc += w
            if acc >= r:
                break
        vs = [v.co for v in f.verts]
        a, b = random.random(), random.random()
        if a + b > 1:
            a, b = 1 - a, 1 - b
        p = vs[0] + (vs[1] - vs[0]) * a + (vs[-1] - vs[0]) * b
        n = f.normal.copy()
        if n.dot(Vector((p.x, p.y, 0))) < 0:
            n.negate()
        drip = i < 14
        size = random.uniform(0.028, 0.05) if drip else random.choice([random.uniform(0.008, 0.02), random.uniform(0.015, 0.035)])
        rot = n.to_track_quat("Z", "Y").to_matrix().to_4x4()
        stretch = random.uniform(2.2, 3.6) if drip else random.uniform(0.85, 1.25)
        m = Matrix.Translation(p + n * size * 0.1 - Vector((0, 0, size * (stretch - 1) * 0.9 if drip else 0))) @ rot @ Matrix.Diagonal((size, size * stretch, size * 0.42, 1))
        bmesh.ops.create_uvsphere(out, u_segments=10 if drip else 8, v_segments=6 if drip else 5, radius=1.0, matrix=m)
    src.free()
    me = bpy.data.meshes.new("droplets")
    out.to_mesh(me)
    out.free()
    drops = place(bpy.data.objects.new("droplets", me), coll, water)
    drops.matrix_world = body.matrix_world
    parent_keep(drops, body)
    return drops


def build_banana_milk(coll):
    plastic = Mat("bm_plastic", "#ffcc00", 0.26, Subsurface_Weight=0.05, Subsurface_Scale=0.1, Coat_Weight=0.25, Coat_Roughness=0.06)
    plastic.set("Subsurface Radius", (1.0, 0.9, 0.3))
    plastic.noise_bump(scale=3.0, strength=0.04)
    cap_m = Mat("bm_cap", "#f5f2ea", 0.38, Subsurface_Weight=0.1)
    cap_m.noise_bump(scale=60, strength=0.05)
    foil_m = Mat("bm_foil", "#eceef1", 0.32, Metallic=0.65)
    foil_m.noise_bump(scale=26, strength=0.25)

    body = lathe("body", [(0, -1.3), (0.55, -1.29), (0.86, -1.18), (0.99, -0.9), (1.04, -0.45), (0.99, 0.08), (0.8, 0.48), (0.55, 0.74), (0.45, 0.88), (0.43, 1.0)], coll, plastic)
    mod(body, "SOLIDIFY", thickness=0.02)
    subsurf(body, 1)
    # 몸통 가운데의 얕은 띠 (패키지 성형선)
    ridge = prim("primitive_torus_add", coll, plastic, "ridge", major_radius=1.035, minor_radius=0.022, major_segments=128, minor_segments=12, location=(0, 0, -0.42))
    parent_keep(ridge, body)
    add_droplets(body, coll)
    cap = lathe("cap", [(0, 1.24), (0.41, 1.24), (0.46, 1.2), (0.47, 1.0), (0.45, 0.98)], coll, cap_m, smooth_n=4)
    subsurf(cap, 1)
    foil = prim("primitive_cylinder_add", coll, foil_m, "foil", vertices=96, radius=0.45, depth=0.012, location=(0, 0, 1.25))
    mod(foil, "BEVEL", width=0.004, segments=2)
    explode(body, (0, 0, 0))
    explode(cap, (0, 0.7, 0))
    explode(foil, (0, 1.25, 0))


def build_yoplait(coll):
    cup_m = Mat("yp_cup", "#f7f4ee", 0.32, Subsurface_Weight=0.15, Subsurface_Scale=0.1, Coat_Weight=0.2)
    band_m = Mat("yp_band", "#ff8fb3", 0.45)
    band_m.color_noise("#ff6f9f", "#ff86b0", scale=2.0)
    yog_m = Mat("yp_yogurt", "#fbe4ea", 0.32, Subsurface_Weight=0.6, Subsurface_Scale=0.15)
    yog_m.noise_bump(scale=8, strength=0.12)
    lid_m = Mat("yp_lid", "#e79ab4", 0.3, Metallic=0.5)
    lid_m.noise_bump(scale=22, strength=0.4)
    spoon_m = Mat("yp_spoon", "#fbfaf7", 0.3, Coat_Weight=0.3)

    cup = lathe("cup", [(0, -1.1), (0.7, -1.1), (0.74, -1.06), (0.94, 0.9)], coll, cup_m, smooth_n=0)
    mod(cup, "SOLIDIFY", thickness=0.025)
    subsurf(cup, 1)
    rim = prim("primitive_torus_add", coll, cup_m, "rim", major_radius=0.95, minor_radius=0.045, major_segments=128, minor_segments=16, location=(0, 0, 0.9))
    parent_keep(rim, cup)
    band = prim("primitive_cone_add", coll, band_m, "band", vertices=128, radius1=0.845, radius2=0.905, depth=0.55, location=(0, 0, 0.1), end_fill_type="NOTHING")
    parent_keep(band, cup)

    bpy.ops.mesh.primitive_circle_add(vertices=96, radius=0.9, fill_type="NGON", location=(0, 0, 0.74))
    yog = place(bpy.context.active_object, coll, yog_m)
    yog.name = "yogurt"
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.poke()
    bpy.ops.mesh.subdivide(number_cuts=6)
    bpy.ops.object.mode_set(mode="OBJECT")
    tex = cloud_texture("yog_clouds", 0.35)
    mod(yog, "DISPLACE", texture=tex, strength=0.06, mid_level=0.5)
    mod(yog, "SOLIDIFY", thickness=0.05)

    bpy.ops.mesh.primitive_grid_add(x_subdivisions=48, y_subdivisions=48, size=2.0, location=(0, 0, 0))
    lid = place(bpy.context.active_object, coll, lid_m)
    lid.name = "lid"
    # 원형으로 잘라내기
    bm = bmesh.new()
    bm.from_mesh(lid.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if Vector((v.co.x, v.co.y)).length > 1.0], context="VERTS")
    bm.to_mesh(lid.data)
    bm.free()
    mod(lid, "SIMPLE_DEFORM", deform_method="BEND", angle=math.radians(55), deform_axis="Y")
    mod(lid, "SOLIDIFY", thickness=0.01)
    lid.location = (0.35, 0.05, 1.05)
    lid.rotation_euler = (0, math.radians(-18), 0)

    handle = prim("primitive_cube_add", coll, spoon_m, "spoon", size=1, location=(0, 0, 0), scale=(0.11, 0.035, 1.35))
    mod(handle, "BEVEL", width=0.02, segments=3)
    bowl = prim("primitive_uv_sphere_add", coll, spoon_m, "spoon_bowl", segments=48, ring_count=24, radius=1, location=(0, 0, 0.78), scale=(0.21, 0.06, 0.28))
    bpy.ops.object.select_all(action="DESELECT")
    handle.select_set(True)
    bpy.context.view_layer.objects.active = handle
    bpy.ops.object.modifier_apply(modifier="bevel")
    spoon = join([handle, bowl], "spoon")
    subsurf(spoon, 1)
    spoon.location = (-0.45, 0.1, 1.05)
    spoon.rotation_euler = (math.radians(8), math.radians(-24), 0)

    explode(cup, (0, 0, 0))
    explode(yog, (0, 0.55, 0))
    explode(lid, (0.2, 1.3, 0))
    explode(spoon, (-1.0, 0.5, 0))


def fish_outline():
    def bez(p0, p1, p2, p3, n=32):
        return [
            (
                (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0],
                (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1],
            )
            for t in (i / n for i in range(n))
        ]

    pts = []
    pts += bez((-1.4, 0), (-1.25, 0.82), (0.25, 1.02), (0.82, 0.34))
    pts += [(0.82 + 0.58 * k / 8, 0.34 + 0.48 * k / 8) for k in range(8)]
    pts += bez((1.4, 0.82), (1.28, 0.3), (1.28, -0.3), (1.4, -0.82))
    pts += [(1.4 - 0.58 * k / 8, -0.82 + 0.48 * k / 8) for k in range(8)]
    pts += bez((0.82, -0.34), (0.25, -1.02), (-1.25, -0.82), (-1.4, 0))
    clean = []
    for p in pts:
        if not clean or (abs(p[0] - clean[-1][0]) + abs(p[1] - clean[-1][1])) > 1e-4:
            clean.append(p)
    return clean


def fish_slab(name, coll, mat, thickness, y, sx=1.0, sz=1.0, puff=True):
    """바닥에 눕힌 도톰한 붕어 모양. 윤곽을 위로 두께만큼 밀어내고 둥글게 부풀린다."""
    bm = bmesh.new()
    verts = [bm.verts.new((x * sx, z * sz, 0)) for x, z in fish_outline()]
    face = bm.faces.new(verts)
    bmesh.ops.triangulate(bm, faces=[face])
    ext = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    moved = [v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0, 0, thickness))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = (0, 0, y - thickness / 2)
    place(obj, coll, mat)
    # 삼각형 기반 평면은 리메시로 고르게 만든 뒤 부드럽게
    mod(obj, "REMESH", mode="SMOOTH", octree_depth=7, use_smooth_shade=True)
    if puff:
        mod(obj, "CAST", cast_type="SPHERE", factor=0.5, use_x=False, use_y=False, use_z=True)
    mod(obj, "SMOOTH", factor=0.8, iterations=6)
    return obj


def build_samanco(coll):
    wafer = Mat("sm_wafer", "#c98640", 0.75)
    wafer.color_noise("#a45a1e", "#cf8a3a", scale=3.0, detail=2.0)
    wafer.voronoi_bump(scale=8.0, strength=0.6)
    cream = Mat("sm_cream", "#f6efe2", 0.45, Subsurface_Weight=0.5, Subsurface_Scale=0.1)
    cream.noise_bump(scale=14, strength=0.1)
    bean = Mat("sm_bean", "#5a2419", 0.5)
    bean.noise_bump(scale=18, strength=0.5)
    eye_m = Mat("sm_eye", "#5a3014", 0.6)

    top = fish_slab("top", coll, wafer, 0.2, 0.26)
    mid = fish_slab("cream", coll, cream, 0.28, 0.0, sx=0.94, sz=0.9, puff=False)
    red = fish_slab("bean", coll, bean, 0.14, 0.12, sx=0.62, sz=0.46)
    red.location.x -= 0.15
    bottom = fish_slab("bottom", coll, wafer, 0.2, -0.26)
    eye = prim("primitive_uv_sphere_add", coll, eye_m, "eye", segments=24, ring_count=12, radius=0.075, location=(-0.95, 0.2, 0.42), scale=(1, 1, 0.5))
    parent_keep(eye, top)
    # 아가미 곡선
    bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.025, major_segments=64, minor_segments=8, location=(-0.62, 0.0, 0.43))
    gill = place(bpy.context.active_object, coll, wafer)
    gill.name = "gill"
    bm = bmesh.new()
    bm.from_mesh(gill.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.x < 0.05], context="VERTS")
    bm.to_mesh(gill.data)
    bm.free()
    parent_keep(gill, top)
    explode(top, (0, 1.0, 0))
    explode(red, (0, 0.5, 0))
    explode(mid, (0, 0, 0))
    explode(bottom, (0, -0.9, 0))


def build_bravo(coll):
    cone_m = Mat("br_cone", "#d99a4e", 0.7)
    cone_m.waffle(scale=9.0, strength=0.7)
    sleeve_m = Mat("br_sleeve", "#1f4fd8", 0.6)
    sleeve_m.noise_bump(scale=30, strength=0.05)
    cream_m = Mat("br_cream", "#f8f2e6", 0.42, Subsurface_Weight=0.55, Subsurface_Scale=0.12)
    cream_m.noise_bump(scale=10, strength=0.08)
    choco_m = Mat("br_choco", "#4a2412", 0.16, Coat_Weight=0.5, Coat_Roughness=0.05)
    nut_m = Mat("br_nut", "#c7894a", 0.6)
    nut_m.color_noise("#a86a32", "#dca56a", scale=12)

    cone = lathe("cone", [(0.02, -1.62), (0.2, -1.2), (0.45, -0.55), (0.66, 0.05), (0.72, 0.45), (0.76, 0.5)], coll, cone_m, smooth_n=4)
    mod(cone, "SOLIDIFY", thickness=0.035)
    subsurf(cone, 1)
    sleeve = lathe("sleeve", [(0.42, -0.62), (0.7, 0.18), (0.72, 0.3)], coll, sleeve_m, smooth_n=0)
    sleeve.scale = (1.035, 1.035, 1.0)
    mod(sleeve, "SOLIDIFY", thickness=0.012)
    subsurf(sleeve, 1)

    # 소프트아이스크림: 위로 갈수록 좁아지는 나선 튜브
    curve = bpy.data.curves.new("swirl", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.21
    curve.bevel_resolution = 8
    curve.use_fill_caps = True
    spline = curve.splines.new("POLY")
    n = 220
    turns = 3.3
    spline.points.add(n - 1)
    for i, p in enumerate(spline.points):
        t = i / (n - 1)
        a = t * turns * math.tau
        r = 0.56 * (1 - t) ** 0.9 + 0.02
        p.co = (r * math.cos(a), r * math.sin(a), 0.55 + t * 0.95, 1)
        p.radius = 1.0 - 0.72 * t
    swirl_obj = bpy.data.objects.new("swirl_tmp", curve)
    coll.objects.link(swirl_obj)
    bpy.ops.object.select_all(action="DESELECT")
    swirl_obj.select_set(True)
    bpy.context.view_layer.objects.active = swirl_obj
    bpy.ops.object.convert(target="MESH")
    swirl = bpy.context.active_object
    base = prim("primitive_uv_sphere_add", coll, cream_m, "swirl_base", segments=64, ring_count=32, radius=0.66, location=(0, 0, 0.55), scale=(1, 1, 0.55))
    cream = join([swirl, base], "cream")
    place(cream, coll, cream_m)
    subsurf(cream, 1)

    # 초콜릿 코팅: 부드럽게 물결치는 가장자리 + 방울 맺힌 흘러내림 줄기
    R, CZ, SXY, SZ = 0.74, 0.72, 1.06, 1.08
    phase = [random.uniform(0, math.tau) for _ in range(3)]

    def edge_z(a):
        # 코팅 가장자리 높이(구 로컬 좌표). 낮은 주파수만 섞어 자연스럽게
        return 0.1 + 0.045 * math.sin(3 * a + phase[0]) + 0.03 * math.sin(5 * a + phase[1]) + 0.015 * math.sin(9 * a + phase[2])

    # 가장자리 곡선을 따라 매개변수로 코팅 면을 직접 생성 → 계단 없는 매끈한 물결 가장자리
    seg, rows = 160, 48
    bm = bmesh.new()
    pole = bm.verts.new((0, 0, R))
    ring_prev = None
    for j in range(1, rows + 1):
        ring = []
        for i in range(seg):
            a = i / seg * math.tau
            theta = math.acos(max(-1.0, min(1.0, edge_z(a) / R))) * j / rows
            ring.append(bm.verts.new((R * math.sin(theta) * math.cos(a), R * math.sin(theta) * math.sin(a), R * math.cos(theta))))
        for i in range(seg):
            if ring_prev is None:
                bm.faces.new((pole, ring[i], ring[(i + 1) % seg]))
            else:
                bm.faces.new((ring_prev[i], ring[i], ring[(i + 1) % seg], ring_prev[(i + 1) % seg]))
        ring_prev = ring
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("choco")
    bm.to_mesh(me)
    bm.free()
    choco = bpy.data.objects.new("choco", me)
    choco.location = (0, 0, CZ)
    place(choco, coll, choco_m)
    choco.scale = (SXY, SXY, SZ)
    mod(choco, "SOLIDIFY", thickness=0.035, offset=1.0)
    mod(choco, "DISPLACE", texture=cloud_texture("choco_clouds", 0.45), strength=0.015)
    subsurf(choco, 1)

    def smoothstep(e0, e1, x):
        t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
        return t * t * (3 - 2 * t)

    drips = []
    for k in range(8):
        a = k / 8 * math.tau + random.uniform(-0.25, 0.25)
        z0 = edge_z(a)
        rxy = math.sqrt(max(0.0, R * R - z0 * z0)) * SXY
        top = Vector((math.cos(a) * rxy, math.sin(a) * rxy, CZ + z0 * SZ + 0.06))
        length = random.uniform(0.16, 0.42)
        width = random.uniform(0.045, 0.065)
        curve = bpy.data.curves.new(f"drip_{k}", "CURVE")
        curve.dimensions = "3D"
        curve.bevel_depth = width
        curve.bevel_resolution = 6
        curve.use_fill_caps = True
        sp = curve.splines.new("POLY")
        steps = 14
        sp.points.add(steps - 1)
        for j, pt in enumerate(sp.points):
            t = j / (steps - 1)
            # 아이스크림 표면을 따라 안쪽으로 붙으며 흘러내린다
            inward = 1.0 - 0.26 * (t ** 0.7)
            pt.co = (top.x * inward, top.y * inward, top.z - length * t, 1)
            # 위는 굵게 → 가늘어졌다가 → 끝에서 살짝 맺힘
            pt.radius = 1.0 - 0.3 * t + 0.45 * smoothstep(0.78, 1.0, t) - 0.35 * smoothstep(0.96, 1.0, t)
        ob = bpy.data.objects.new(f"drip_{k}", curve)
        coll.objects.link(ob)
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.convert(target="MESH")
        drips.append(bpy.context.active_object)
    for d in drips:
        place(d, coll, choco_m)
        subsurf(d, 1)
        parent_keep(d, choco)
    for i in range(38):
        a = random.uniform(0, math.tau)
        rr = random.uniform(0.0, 0.62)
        z = 0.72 + math.sqrt(max(0.0, 0.8 ** 2 - rr ** 2)) * 1.08
        nut = prim("primitive_ico_sphere_add", coll, nut_m, f"nut_{i}", subdivisions=1, radius=random.uniform(0.035, 0.06), location=(math.cos(a) * rr, math.sin(a) * rr, z))
        nut.rotation_euler = (random.random() * 3, random.random() * 3, random.random() * 3)
        nut.scale = (1, random.uniform(0.6, 1), random.uniform(0.5, 0.9))
        parent_keep(nut, choco)

    explode(cone, (0, 0, 0))
    explode(sleeve, (0.95, -0.15, 0))
    explode(cream, (0, 1.0, 0))
    explode(choco, (0, 1.7, 0))


# ---------------------------------------------------------------------------
# "완성되는" 애니메이션 (GLB에 포함 → 사이트에서 스크롤로 재생)
# 마지막 프레임 = 완성 상태(렌더/분해의 기준 자세)
# ---------------------------------------------------------------------------

END = 64


def part(coll, name):
    for o in coll.objects:
        if o.name == name or o.name.startswith(name + "."):
            return o
    raise KeyError(name)


def key(obj, frame, loc=None, rot=None, scale=None):
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame)
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)


def rest(obj):
    return obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy()


def off(v, dx=0.0, dy=0.0, dz=0.0):
    return (v.x + dx, v.y + dy, v.z + dz)


def rz(r, dz):
    return (r.x, r.y, r.z + dz)


def anim_banana_milk(coll):
    body, cap, foil = part(coll, "body"), part(coll, "cap"), part(coll, "foil")
    bl, br, bs = rest(body)
    key(body, 1, scale=(0.85, 0.85, 0.7))
    key(body, 18, scale=(1.05, 1.05, 1.08))
    key(body, 28, scale=tuple(bs))
    cl, cr, _ = rest(cap)
    key(cap, 1, loc=off(cl, dz=1.1), rot=rz(cr, math.pi * 3))
    key(cap, 30, loc=off(cl, dz=0.25), rot=rz(cr, math.pi))
    key(cap, 55, loc=tuple(cl), rot=tuple(cr))
    fl, fr, _ = rest(foil)
    key(foil, 1, loc=off(fl, dz=1.8), rot=(math.radians(25), 0, 0))
    key(foil, 40, loc=off(fl, dz=0.5), rot=(math.radians(-10), 0, 0))
    key(foil, END, loc=tuple(fl), rot=tuple(fr))


def anim_yoplait(coll):
    cup, yog, lid, spoon = part(coll, "cup"), part(coll, "yogurt"), part(coll, "lid"), part(coll, "spoon")
    _, _, cs = rest(cup)
    key(cup, 1, scale=(1, 1, 0.6))
    key(cup, 18, scale=(1.04, 1.04, 1.05))
    key(cup, 26, scale=tuple(cs))
    _, _, ys = rest(yog)
    key(yog, 1, scale=(0.4, 0.4, 0.01))
    key(yog, 36, scale=tuple(ys))
    ll, lr, _ = rest(lid)
    key(lid, 1, loc=off(ll, dx=-1.2, dz=1.4), rot=(lr.x, lr.y + math.radians(60), lr.z))
    key(lid, 42, loc=tuple(ll), rot=tuple(lr))
    sl, sr, _ = rest(spoon)
    key(spoon, 1, loc=off(sl, dz=2.0))
    key(spoon, 30, loc=off(sl, dz=0.9))
    key(spoon, END, loc=tuple(sl))


def anim_samanco(coll):
    top, bottom, mid, bean = part(coll, "top"), part(coll, "bottom"), part(coll, "cream"), part(coll, "bean")
    tl, tr, _ = rest(top)
    key(top, 1, loc=off(tl, dz=1.4), rot=(math.radians(25), 0, 0))
    key(top, 40, loc=off(tl, dz=0.25), rot=(0, 0, 0))
    key(top, END, loc=tuple(tl), rot=tuple(tr))
    bl, _, _ = rest(bottom)
    key(bottom, 1, loc=off(bl, dz=-1.0))
    key(bottom, 30, loc=tuple(bl))
    _, _, ms = rest(mid)
    key(mid, 1, scale=(0.2, 0.2, 0.2))
    key(mid, 35, scale=tuple(ms))
    _, _, bs = rest(bean)
    key(bean, 10, scale=(0.0, 0.0, 0.0))
    key(bean, 40, scale=tuple(bs))


def anim_bravo(coll):
    cone, sleeve, cream, choco = part(coll, "cone"), part(coll, "sleeve"), part(coll, "cream"), part(coll, "choco")
    _, cr, cs = rest(cone)
    key(cone, 1, rot=rz(cr, -math.pi / 2), scale=(0.9, 0.9, 0.9))
    key(cone, 25, rot=tuple(cr), scale=tuple(cs))
    sl, _, ss = rest(sleeve)
    key(sleeve, 1, loc=off(sl, dz=-0.6), scale=(ss.x * 0.9, ss.y * 0.9, ss.z))
    key(sleeve, 25, loc=tuple(sl), scale=tuple(ss))
    # 아이스크림이 콘 위에서 빙글빙글 짜 올라가도록 원점을 바닥으로
    bpy.ops.object.select_all(action="DESELECT")
    cream.select_set(True)
    bpy.context.view_layer.objects.active = cream
    bpy.context.scene.cursor.location = (0, 0, 0.5)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    _, rr, rs = rest(cream)
    key(cream, 8, rot=rz(rr, -math.tau), scale=(0.25, 0.25, 0.02))
    key(cream, 44, rot=tuple(rr), scale=tuple(rs))
    hl, _, hs = rest(choco)
    key(choco, 1, loc=off(hl, dz=1.3), scale=(0, 0, 0))
    key(choco, 40, loc=off(hl, dz=1.3), scale=(0, 0, 0))
    key(choco, 42, loc=off(hl, dz=1.2), scale=tuple(hs))
    key(choco, 56, loc=tuple(hl), scale=(hs.x * 1.04, hs.y * 1.04, hs.z * 0.88))
    key(choco, END, loc=tuple(hl), scale=tuple(hs))


ANIMATE = {"banana-milk": anim_banana_milk, "yoplait": anim_yoplait, "samanco": anim_samanco, "bravo": anim_bravo}


PRODUCTS_DEF = [
    ("banana-milk", build_banana_milk),
    ("yoplait", build_yoplait),
    ("samanco", build_samanco),
    ("bravo", build_bravo),
]


# ---------------------------------------------------------------------------
# scene / render
# ---------------------------------------------------------------------------

def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.curves, bpy.data.textures):
        for b in list(block):
            block.remove(b)


def setup_render():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        scene.cycles.device = "GPU"
    except Exception as e:
        print("GPU unavailable, using CPU:", e)
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1200
    scene.render.film_transparent = True
    # 물방울 같은 투명 재질이 투명 배경을 굴절해 검게 찍히지 않도록
    try:
        scene.cycles.film_transparent_glass = True
        scene.cycles.film_transparent_roughness = 0.1
    except AttributeError:
        pass
    scene.render.image_settings.file_format = "WEBP"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.quality = 90
    # 제품 색이 바래지 않도록 Khronos PBR Neutral (없으면 Standard)
    for vt in ("Khronos PBR Neutral", "Standard"):
        try:
            scene.view_settings.view_transform = vt
            break
        except TypeError:
            continue

    # 내장 스튜디오 HDRI로 반사/환경광
    world = bpy.data.worlds.new("world")
    scene.world = world
    try:
        world.use_nodes = True
    except Exception:
        pass
    nt = world.node_tree
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.name = "env_mapping"
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.name = "env"
    hdri_dir = bpy.utils.system_resource("DATAFILES", path="studiolights/world")
    env.image = bpy.data.images.load(os.path.join(hdri_dir, "studio.exr"))
    bg = nt.nodes["Background"]
    bg.inputs["Strength"].default_value = 0.8
    nt.links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])

    def area(name, loc, energy, size, color=(1, 1, 1), shadow=True):
        light = bpy.data.lights.new(name, "AREA")
        light.energy = energy
        light.size = size
        light.color = color
        light.use_shadow = shadow
        obj = bpy.data.objects.new(name, light)
        obj.location = loc
        direction = -Vector(loc).normalized()
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        scene.collection.objects.link(obj)

    area("key", (-2.2, -3.2, 7.0), 1100, 6.0)
    area("fill", (4.5, -3.5, 3.5), 320, 5.0, (1.0, 0.96, 0.9), shadow=False)
    area("rim", (0.6, 3.0, 6.5), 650, 3.0, shadow=False)

    # 접지 그림자만 남기는 바닥
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "shadow_catcher"
    floor.is_shadow_catcher = True
    # 렌더 PNG는 제품만 깔끔하게 오려낸다 (그림자는 사이트 CSS에서). 필요하면 True로.
    floor.hide_render = os.environ.get("FLOOR_SHADOW") != "1"

    cam = bpy.data.cameras.new("cam")
    cam.lens = 70
    cam_obj = bpy.data.objects.new("cam", cam)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    return cam_obj, floor


# 제품별 분위기 (모먼트 기획과 맞춤). HDRI는 블렌더 내장 CC0(Poly Haven).
LOOKS = {
    # 시작하기 힘든 아침 — 일출빛
    "yoplait": dict(hdri="sunrise.exr", strength=1.0, rot=40, key=(1.0, 0.9, 0.78), key_e=950, fill=(0.85, 0.92, 1.0), fill_e=300, rim_e=700),
    # 나른한 오후 — 한낮 야외
    "banana-milk": dict(hdri="courtyard.exr", strength=1.1, rot=120, key=(1.0, 0.97, 0.9), key_e=1150, fill=(0.95, 0.97, 1.0), fill_e=320, rim_e=650),
    # 기분 전환 — 산뜻한 도시
    "bravo": dict(hdri="city.exr", strength=1.15, rot=200, key=(0.95, 0.98, 1.0), key_e=1050, fill=(1.0, 0.96, 0.9), fill_e=300, rim_e=750),
    # 수고한 하루의 끝 — 따뜻한 실내 조명
    "samanco": dict(hdri="interior.exr", strength=0.9, rot=30, key=(1.0, 0.8, 0.58), key_e=900, fill=(1.0, 0.86, 0.72), fill_e=230, rim_e=520),
}


def apply_look(slug):
    look = LOOKS.get(slug)
    if not look:
        return
    world = bpy.context.scene.world
    nt = world.node_tree
    hdri_dir = bpy.utils.system_resource("DATAFILES", path="studiolights/world")
    nt.nodes["env"].image = bpy.data.images.load(os.path.join(hdri_dir, look["hdri"]), check_existing=True)
    nt.nodes["env_mapping"].inputs["Rotation"].default_value = (0, 0, math.radians(look["rot"]))
    nt.nodes["Background"].inputs["Strength"].default_value = look["strength"]
    lights = {o.name: o.data for o in bpy.context.scene.objects if o.type == "LIGHT"}
    lights["key"].color, lights["key"].energy = look["key"], look["key_e"]
    lights["fill"].color, lights["fill"].energy = look["fill"], look["fill_e"]
    lights["rim"].energy = look["rim_e"]


def mesh_objects(coll):
    return [o for o in coll.all_objects if o.type == "MESH"]


def world_bbox(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        ev = o.evaluated_get(dg)
        pts += [ev.matrix_world @ Vector(c) for c in ev.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


CAM_DIR = {"samanco": (0.3, -1.0, 1.25)}


def frame(cam_obj, floor, objs, slug=""):
    lo, hi = world_bbox(objs)
    center = (lo + hi) / 2
    size = hi - lo
    floor.location.z = lo.z
    direction = Vector(CAM_DIR.get(slug, (0.38, -1.0, 0.42))).normalized()
    fov_v = 2 * math.atan(cam_obj.data.sensor_width / 2 / cam_obj.data.lens) * (1200 / 1000)
    radius = max(size.x, size.y, size.z) * 0.62
    dist = radius / math.tan(min(fov_v, 2 * math.atan(cam_obj.data.sensor_width / 2 / cam_obj.data.lens)) / 2) * 1.15
    cam_obj.location = center + direction * dist
    cam_obj.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()


# ---------------------------------------------------------------------------
# baking for glTF (절차적 재질 → 이미지 텍스처)
# ---------------------------------------------------------------------------

def bake_object(obj, size):
    mat = obj.active_material
    scene = bpy.context.scene
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.01)
    bpy.ops.object.mode_set(mode="OBJECT")

    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    images = {}
    for kind, colorspace in (("DIFFUSE", "sRGB"), ("NORMAL", "Non-Color"), ("ROUGHNESS", "Non-Color")):
        img = bpy.data.images.new(f"{obj.name}_{kind.lower()}", size, size, alpha=False)
        img.colorspace_settings.name = colorspace
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = img
        nt.nodes.active = node
        kw = {"type": kind, "margin": 8, "use_clear": True}
        if kind == "DIFFUSE":
            kw["pass_filter"] = {"COLOR"}
        bpy.ops.object.bake(**kw)
        images[kind] = (img, node)

    # 절차적 노드를 떼고 베이크 이미지로 연결 (glTF가 읽을 수 있는 형태)
    for link in list(bsdf.inputs["Base Color"].links) + list(bsdf.inputs["Normal"].links) + list(bsdf.inputs["Roughness"].links):
        nt.links.remove(link)
    nt.links.new(images["DIFFUSE"][1].outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(images["ROUGHNESS"][1].outputs["Color"], bsdf.inputs["Roughness"])
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(images["NORMAL"][1].outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])


def prepare_glb(coll):
    scene = bpy.context.scene
    scene.cycles.samples = 8
    for obj in mesh_objects(coll):
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        if obj.modifiers:
            bpy.ops.object.convert(target="MESH")
    for obj in mesh_objects(coll):
        mat = obj.active_material
        if mat is None or not mat.get("bake"):
            continue
        # 오브젝트마다 재질을 따로 두어야 각자의 UV에 맞는 텍스처가 구워진다
        own = mat.copy()
        obj.active_material = own
        if max(obj.dimensions) > 0.5:
            bake_object(obj, 1024)
        else:
            # 작은 파트(견과·눈 등)는 텍스처 없이 기본 색만
            bsdf = own.node_tree.nodes["Principled BSDF"]
            for name in ("Base Color", "Normal", "Roughness"):
                for link in list(bsdf.inputs[name].links):
                    own.node_tree.links.remove(link)
    scene.cycles.samples = SAMPLES


def export_glb(coll, slug):
    bpy.ops.object.select_all(action="DESELECT")
    for o in mesh_objects(coll):
        o.select_set(True)
    kw = dict(
        filepath=os.path.join(MODELS, f"{slug}.glb"),
        export_format="GLB",
        use_selection=True,
        export_extras=True,
        export_apply=True,
        export_yup=True,
        export_image_format="JPEG",
    )
    extra = dict(export_jpeg_quality=82, export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
                 export_animations=True, export_animation_mode="SCENE", export_frame_range=True)
    try:
        bpy.ops.export_scene.gltf(**kw, **extra)
    except TypeError:
        extra.pop("export_animation_mode")
        bpy.ops.export_scene.gltf(**kw, **extra)


def main():
    reset_scene()
    cam, floor = setup_render()
    colls = {}
    targets = [p for p in PRODUCTS_DEF if not ONLY or p[0] == ONLY]
    for slug, build in targets:
        colls[slug] = new_collection(slug)
        build(colls[slug])
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, END
    scene.render.fps = 30
    for slug, _ in targets:
        ANIMATE[slug](colls[slug])
    # 완성 상태에서 렌더·내보내기
    scene.frame_set(END)

    # 1) 실사 렌더
    for slug, _ in targets:
        for other, c in colls.items():
            c.hide_render = other != slug
        frame(cam, floor, mesh_objects(colls[slug]), slug)
        apply_look(slug)
        bpy.context.scene.render.filepath = os.path.join(PRODUCTS, f"{slug}.webp")
        bpy.ops.render.render(write_still=True)
        print(f"RENDERED {slug}")

    # 2) 편집용 .blend (절차적 재질 그대로). 애니메이션 키가 있으므로 임시 부모 empty로 나란히 배치
    if not ONLY:
        empties = []
        for i, (slug, _) in enumerate(targets):
            colls[slug].hide_render = False
            e = bpy.data.objects.new(f"{slug}_layout", None)
            colls[slug].objects.link(e)
            for o in list(colls[slug].objects):
                if o.parent is None and o is not e:
                    o.parent = e
            e.location.x = (i - 1.5) * 3.2
            empties.append(e)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender", "products.blend"))
        for e in empties:
            e.location.x = 0
            bpy.context.view_layer.update()
            for o in list(e.children):
                mw = o.matrix_world.copy()
                o.parent = None
                o.matrix_world = mw
            bpy.data.objects.remove(e)
        scene.frame_set(END)

    # 3) GLB: 모디파이어 적용 + 베이킹 + 내보내기
    if not SKIP_GLB:
        for slug, _ in targets:
            prepare_glb(colls[slug])
            export_glb(colls[slug], slug)
            print(f"EXPORTED {slug}")
    print("DONE")


main()
