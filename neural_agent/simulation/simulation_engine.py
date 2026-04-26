"""
2D, 3D, and 4D Simulation Engine
Includes Blender integration for advanced 3D rendering
"""

import json
import math
import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, Callable
from enum import Enum
import subprocess
import os


class Dimension(Enum):
    DIM_2D = 2
    DIM_3D = 3
    DIM_4D = 4


class SimulationType(Enum):
    PHYSICS = "physics"
    PARTICLE = "particle"
    FLUID = "fluid"
    CELLULAR_AUTOMATA = "cellular_automata"
    AGENT_BASED = "agent_based"
    NEURAL_NETWORK = "neural_network"
    FINANCIAL = "financial"
    ECOSYSTEM = "ecosystem"
    TRAFFIC = "traffic"
    ROBOTICS = "robotics"


@dataclass
class Vector:
    x: float = 0
    y: float = 0
    z: float = 0
    w: float = 0
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, 
                      self.z + other.z, self.w + other.w)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y,
                      self.z - other.z, self.w - other.w)
    
    def __mul__(self, scalar: float):
        return Vector(self.x * scalar, self.y * scalar,
                      self.z * scalar, self.w * scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag
            self.z /= mag
            self.w /= mag
        return self
    
    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z + self.w * other.w
    
    def cross(self, other):
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
            0
        )


@dataclass
class Particle:
    position: Vector
    velocity: Vector = field(default_factory=Vector)
    acceleration: Vector = field(default_factory=Vector)
    mass: float = 1.0
    charge: float = 0.0
    radius: float = 1.0
    color: Tuple[int, int, int] = (255, 255, 255)
    lifetime: float = -1
    fixed: bool = False
    
    def update(self, dt: float):
        if self.fixed:
            return
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        self.acceleration = Vector()


@dataclass
class Body:
    name: str
    position: Vector
    velocity: Vector = field(default_factory=Vector)
    mass: float = 1.0
    shape: str = "sphere"
    size: float = 1.0
    color: Tuple[int, int, int] = (255, 255, 255)
    rotation: Vector = field(default_factory=Vector)
    angular_velocity: Vector = field(default_factory=Vector)


class PhysicsEngine:
    def __init__(self, gravity: Vector = None, damping: float = 0.99):
        self.gravity = gravity or Vector(0, -9.81, 0)
        self.damping = damping
        self.particle_constraints = []
        self.bodies = []
    
    def add_body(self, body: Body):
        self.bodies.append(body)
    
    def add_particle(self, particle: Particle):
        self.bodies.append(Body(
            name=f"particle_{len(self.bodies)}",
            position=particle.position,
            velocity=particle.velocity,
            mass=particle.mass,
            size=particle.radius
        ))
    
    def apply_force(self, body: Body, force: Vector):
        if body.mass > 0 and not getattr(body, 'fixed', False):
            acceleration = force * (1.0 / body.mass)
            body.velocity += acceleration
    
    def apply_gravity(self, body: Body):
        if not getattr(body, 'fixed', False):
            body.velocity += self.gravity
    
    def check_collision(self, b1: Body, b2: Body) -> bool:
        dist = (b1.position - b2.position).magnitude()
        return dist < (b1.size + b2.size)
    
    def resolve_collision(self, b1: Body, b2: Body):
        if not self.check_collision(b1, b2):
            return
        
        normal = (b2.position - b1.position)
        normal.normalize()
        
        rel_vel = b1.velocity - b2.velocity
        vel_along_normal = rel_vel.dot(normal)
        
        if vel_along_normal > 0:
            return
        
        e = 0.8
        j = -(1 + e) * vel_along_normal
        j /= (1/b1.mass + 1/b2.mass)
        
        impulse = normal * j
        b1.velocity += impulse * (1/b1.mass)
        b2.velocity -= impulse * (1/b2.mass)
        
        min_dist = b1.size + b2.size
        dist = (b1.position - b2.position).magnitude()
        overlap = min_dist - dist
        if overlap > 0:
            correction = normal * (overlap / 2)
            b1.position -= correction
            b2.position += correction
    
    def step(self, dt: float):
        for body in self.bodies:
            self.apply_gravity(body)
            body.position += body.velocity * dt
            body.velocity *= self.damping
            
            body.rotation += body.angular_velocity * dt
        
        for i, b1 in enumerate(self.bodies):
            for b2 in self.bodies[i+1:]:
                self.resolve_collision(b1, b2)


class Simulation2D:
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
        self.bodies: List[Body] = []
        self.grid: Dict[Tuple[int, int], any] = {}
        self.time = 0
        self.running = False
    
    def add_particle(self, x: float, y: float, vx: float = 0, vy: float = 0):
        p = Particle(
            position=Vector(x, y),
            velocity=Vector(vx, vy)
        )
        self.particles.append(p)
        return p
    
    def add_rect(self, x: float, y: float, w: float, h: float, vx: float = 0, vy: float = 0):
        body = Body(
            name=f"rect_{len(self.bodies)}",
            position=Vector(x + w/2, y + h/2),
            velocity=Vector(vx, vy),
            shape="rect",
            size=w/2
        )
        self.bodies.append(body)
        return body
    
    def get_grid_cell(self, x: float, y: float) -> Tuple[int, int]:
        return (int(x / 10), int(y / 10))
    
    def update_cellular_automata(self, rules: str = "conway"):
        new_grid = {}
        
        if rules == "conway":
            for (gx, gy), val in self.grid.items():
                neighbors = self.count_neighbors(gx, gy)
                if val == 1:
                    new_grid[(gx, gy)] = 1 if neighbors in [2, 3] else 0
                else:
                    new_grid[(gx, gy)] = 1 if neighbors == 3 else 0
        
        elif rules == "seeds":
            for (gx, gy), val in self.grid.items():
                neighbors = self.count_neighbors(gx, gy)
                if val == 0 and neighbors == 2:
                    new_grid[(gx, gy)] = 1
        
        self.grid = new_grid
    
    def count_neighbors(self, x: int, y: int) -> int:
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                if self.grid.get((x + dx, y + dy), 0) == 1:
                    count += 1
        return count
    
    def step(self, dt: float = 0.016):
        self.time += dt
        for p in self.particles:
            p.update(dt)
            
            if p.position.y > self.height:
                p.position.y = self.height
                p.velocity.y *= -0.8
            if p.position.y < 0:
                p.position.y = 0
                p.velocity.y *= -0.8
            if p.position.x > self.width:
                p.position.x = self.width
                p.velocity.x *= -0.8
            if p.position.x < 0:
                p.position.x = 0
                p.velocity.x *= -0.8
    
    def to_json(self) -> str:
        return json.dumps({
            "width": self.width,
            "height": self.height,
            "time": self.time,
            "particles": [
                {
                    "x": p.position.x,
                    "y": p.position.y,
                    "vx": p.velocity.x,
                    "vy": p.velocity.y
                }
                for p in self.particles
            ]
        })


class Simulation3D:
    def __init__(self, bounds: Tuple[float, float, float] = (100, 100, 100)):
        self.bounds = bounds
        self.particles: List[Particle] = []
        self.bodies: List[Body] = []
        self.time = 0
        self.physics = PhysicsEngine()
    
    def add_particle(self, x: float, y: float, z: float, 
                     vx: float = 0, vy: float = 0, vz: float = 0):
        p = Particle(
            position=Vector(x, y, z),
            velocity=Vector(vx, vy, vz)
        )
        self.particles.append(p)
        return p
    
    def add_body(self, name: str, x: float, y: float, z: float,
                 size: float = 1.0, shape: str = "sphere"):
        body = Body(
            name=name,
            position=Vector(x, y, z),
            shape=shape,
            size=size
        )
        self.bodies.append(body)
        self.physics.add_body(body)
        return body
    
    def step(self, dt: float = 0.016):
        self.time += dt
        self.physics.step(dt)
    
    def get_camera_view(self, eye: Vector, target: Vector) -> Dict:
        forward = target - eye
        forward.normalize()
        
        up = Vector(0, 1, 0)
        right = forward.cross(up)
        right.normalize()
        
        up = right.cross(forward)
        
        return {
            "eye": [eye.x, eye.y, eye.z],
            "target": [target.x, target.y, target.z],
            "up": [up.x, up.y, up.z]
        }


class Simulation4D:
    def __init__(self, bounds: Tuple[float, float, float, float] = (50, 50, 50, 50)):
        self.bounds = bounds
        self.particles: List[Particle] = []
        self.hyperparticles: List[Dict] = []
        self.time = 0
        self.w_position = 0
    
    def add_hyperparticle(self, x: float, y: float, z: float, w: float = 0):
        hp = {
            "position": Vector(x, y, z, w),
            "velocity": Vector(0, 0, 0, 0),
            "projection_3d": Vector(x, y, z),
            "projection_2d": Vector(x, y)
        }
        self.hyperparticles.append(hp)
        return hp
    
    def project_to_3d(self, w_plane: float = 0) -> List[Vector]:
        projected = []
        for hp in self.hyperparticles:
            p = hp["position"]
            scale = 1.0 / (1.0 + (p.w - w_plane) / 10)
            projected.append(Vector(p.x * scale, p.y * scale, p.z * scale))
        return projected
    
    def project_to_2d(self) -> List[Vector]:
        projected = []
        for hp in self.hyperparticles:
            p = hp["position"]
            projected.append(Vector(p.x, p.y))
        return projected
    
    def rotate_4d(self, angle_xy: float = 0, angle_xz: float = 0, 
                   angle_xw: float = 0, angle_yz: float = 0,
                   angle_yw: float = 0, angle_zw: float = 0):
        import numpy as np
        
        for hp in self.hyperparticles:
            p = hp["position"]
            x, y, z, w = p.x, p.y, p.z, p.w
            
            if angle_xy != 0:
                c, s = np.cos(angle_xy), np.sin(angle_xy)
                p.x, p.y = x * c - y * s, x * s + y * c
            if angle_xz != 0:
                c, s = np.cos(angle_xz), np.sin(angle_xz)
                p.x, p.z = p.x * c - z * s, p.x * s + z * c
            if angle_xw != 0:
                c, s = np.cos(angle_xw), np.sin(angle_xw)
                p.x, p.w = p.x * c - w * s, p.x * s + w * c
            if angle_yz != 0:
                c, s = np.cos(angle_yz), np.sin(angle_yz)
                p.y, p.z = y * c - z * s, y * s + z * c
            if angle_yw != 0:
                c, s = np.cos(angle_yw), np.sin(angle_yw)
                p.y, p.w = p.y * c - w * s, p.y * s + w * c
            if angle_zw != 0:
                c, s = np.cos(angle_zw), np.sin(angle_zw)
                p.z, p.w = z * c - w * s, z * s + w * c
    
    def step(self, dt: float = 0.016):
        self.time += dt
        
        for hp in self.hyperparticles:
            hp["position"] += hp["velocity"] * dt


class BlenderInterface:
    def __init__(self, blender_path: str = "blender"):
        self.blender_path = blender_path
        self.script_template = """
import bpy
import math
import json

def clear_scene():
    bpy.data.objects.data

def create_{shape}_mesh(name, vertices, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def set_material(obj, color, metallic=0, roughness=0.5):
    mat = bpy.data.materials.new(name="Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    obj.data.materials.append(mat)

def add_light(type, location, energy=100):
    bpy.ops.object.light_add(type=type, location=location)
    light = bpy.context.active_object
    light.data.energy = energy
    return light

def render(output_path):
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.render.render(write_still=True)

{content}

render("/{output}")
"""
    
    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                [self.blender_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def run_blender_script(self, script: str, output_path: str = "/tmp/blender_output.png"):
        script_content = self.script_template.format(
            content=script,
            output=output_path
        )
        
        try:
            result = subprocess.run(
                [self.blender_path, "--background", "--python-expr", script_content],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {"success": True, "output": result.stdout, "error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Blender script timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_scene_from_simulation(self, sim: Simulation3D, output_path: str):
        script_lines = [
            "clear_scene()",
            "add_light('SUN', (5, 5, 10), 200)",
            "bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0))",
            "bpy.context.active_object.name = 'background'"
        ]
        
        for i, body in enumerate(sim.bodies):
            pos = body.position
            size = body.size
            color = tuple(c/255 for c in body.color)
            
            script_lines.append(f"""
bpy.ops.mesh.primitive_{body.shape}_add(
    location=({pos.x}, {pos.y}, {pos.z}),
    scale=({size}, {size}, {size})
)
obj = bpy.context.active_object
obj.name = '{body.name}'
""")
        
        return self.run_blender_script("\n".join(script_lines), output_path)
    
    def create_simulation_video(self, sim: Simulation3D, frames: int, 
                                output_path: str, fps: int = 30):
        script_lines = [
            "clear_scene()",
            "add_light('SUN', (5, 5, 10), 200)",
        ]
        
        for i, body in enumerate(sim.bodies):
            script_lines.append(f"""
bpy.ops.mesh.primitive_{body.shape}_add(location=({body.position.x}, {body.position.y}, {body.position.z}))
bpy.context.active_object.name = '{body.name}'
""")
        
        script_lines.append(f"""
scene = bpy.context.scene
scene.frame_start = 0
scene.frame_end = {frames}
scene.render.fps = {fps}

def animate():
    for frame in range({frames}):
        scene.frame_set(frame)
""")
        
        return self.run_blender_script("\n".join(script_lines), output_path)


class RenderingEngine:
    def __init__(self, dimension: Dimension = Dimension.DIM_2D):
        self.dimension = dimension
        self.renderer = "html"
        self.frame_count = 0
    
    def render_particles_2d(self, particles: List[Particle]) -> str:
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">']
        svg.append('<rect width="100%" height="100%" fill="#1a1a2e"/>')
        
        for p in particles:
            color = f'rgb({p.color[0]},{p.color[1]},{p.color[2]})'
            svg.append(f'<circle cx="{p.position.x}" cy="{p.position.y}" '
                      f'r="{p.radius}" fill="{color}"/>')
        
        svg.append('</svg>')
        return '\n'.join(svg)
    
    def render_particles_3d(self, bodies: List[Body], camera: Dict) -> str:
        return json.dumps({
            "type": "3d_scene",
            "camera": camera,
            "bodies": [
                {
                    "name": b.name,
                    "position": [b.position.x, b.position.y, b.position.z],
                    "size": b.size,
                    "color": list(b.color)
                }
                for b in bodies
            ]
        })
    
    def render_to_html(self, sim: Simulation2D) -> str:
        return f'''
<!DOCTYPE html>
<html>
<head>
    <title>2D Simulation</title>
    <style>
        body {{ margin: 0; background: #1a1a2e; }}
        canvas {{ display: block; }}
    </style>
</head>
<body>
    <canvas id="canvas" width="{sim.width}" height="{sim.height}"></canvas>
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        const particles = {json.dumps([
            {"x": p.position.x, "y": p.position.y, "r": p.radius, "c": list(p.color)}
            for p in sim.particles
        ])};
        
        function animate() {{
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            for (const p of particles) {{
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgb(${{p.c[0]}},${{p.c[1]}},${{p.c[2]}})`;
                ctx.fill();
                
                p.y += 0.5;
                if (p.y > {sim.height}) p.y = 0;
            }}
            
            requestAnimationFrame(animate);
        }}
        animate();
    </script>
</body>
</html>
'''
    
    def render_to_html_3d(self, sim: Simulation3D) -> str:
        bodies_json = json.dumps([
            {
                "name": b.name,
                "pos": [b.position.x, b.position.y, b.position.z],
                "size": b.size,
                "color": list(b.color),
                "shape": b.shape
            }
            for b in sim.bodies
        ])
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <title>3D Simulation</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #1a1a2e; }}
    </style>
</head>
<body>
    <script>
        const bodies = {bodies_json};
        
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(50, 50, 50);
        camera.lookAt(0, 0, 0);
        
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        
        bodies.forEach(b => {{
            const mat = new THREE.MeshBasicMaterial({{ color: new THREE.Color(...b.color.map(c => c/255)) }});
            const mesh = new THREE.Mesh(geometry, mat);
            mesh.position.set(...b.pos);
            mesh.scale.setScalar(b.size);
            mesh.name = b.name;
            scene.add(mesh);
        }});
        
        const light = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(light);
        
        function animate() {{
            requestAnimationFrame(animate);
            scene.children.forEach(c => {{
                if (c.name && c.name.startsWith('body_')) {{
                    c.rotation.x += 0.01;
                    c.rotation.y += 0.01;
                }}
            }});
            renderer.render(scene, camera);
        }}
        animate();
    </script>
</body>
</html>
'''
    
    def render_to_html_4d(self, sim: Simulation4D, w_slice: float = 0) -> str:
        hp_json = json.dumps([
            {"pos": [hp["position"].x, hp["position"].y, hp["position"].z, hp["position"].w]}
            for hp in sim.hyperparticles
        ])
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <title>4D Simulation Projection</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #1a1a2e; }}
        #info {{ position: absolute; top: 10px; left: 10px; color: white; font-family: monospace; }}
    </style>
</head>
<body>
    <div id="info">W-Slice: <span id="wVal">0</span> | 4D Points: {len(sim.hyperparticles)}</div>
    <script>
        const hyperparticles = {hp_json};
        
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(30, 30, 30);
        camera.lookAt(0, 0, 0);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        let wSlice = 0;
        let dots = [];
        
        function project4Dto3D(point, wSlice) {{
            const scale = 1.0 / (1.0 + (point[3] - wSlice) / 20);
            return [point[0] * scale, point[1] * scale, point[2] * scale];
        }}
        
        function updateScene() {{
            dots.forEach(d => scene.remove(d));
            dots = [];
            
            hyperparticles.forEach(hp => {{
                const p3d = project4Dto3D(hp.pos, wSlice);
                const geo = new THREE.SphereGeometry(0.5);
                const mat = new THREE.MeshBasicMaterial({{ color: 0x00ffff }});
                const mesh = new THREE.Mesh(geo, mat);
                mesh.position.set(...p3d);
                scene.add(mesh);
                dots.push(mesh);
            }});
        }}
        
        updateScene();
        
        let rotation = 0;
        function animate() {{
            requestAnimationFrame(animate);
            rotation += 0.005;
            camera.position.x = 30 * Math.cos(rotation);
            camera.position.z = 30 * Math.sin(rotation);
            camera.lookAt(0, 0, 0);
            renderer.render(scene, camera);
        }}
        animate();
        
        document.addEventListener('wheel', e => {{
            wSlice += e.deltaY * 0.01;
            document.getElementById('wVal').textContent = wSlice.toFixed(2);
            updateScene();
        }});
    </script>
</body>
</html>
'''


class MultiAgentSimulation:
    def __init__(self, dimension: Dimension, num_agents: int = 50):
        self.dimension = dimension
        self.agents: List[Dict] = []
        self.num_agents = num_agents
        self.time = 0
        self.rules: List[Callable] = []
        
        self._init_agents()
    
    def _init_agents(self):
        bounds = [100, 100, 100, 100][:self.dimension.value]
        
        for i in range(self.num_agents):
            agent = {
                "id": i,
                "position": Vector(*[random.uniform(-b/2, b/2) for b in bounds]),
                "velocity": Vector(*[random.uniform(-1, 1) for _ in range(self.dimension.value)]),
                "energy": random.uniform(50, 100),
                "age": 0,
                "genes": [random.uniform(0, 1) for _ in range(5)]
            }
            self.agents.append(agent)
    
    def add_rule(self, rule: Callable):
        self.rules.append(rule)
    
    def rule_cohesion(self, agent: Dict, neighbor_range: float = 10):
        avg_pos = Vector()
        count = 0
        
        for other in self.agents:
            if other["id"] == agent["id"]:
                continue
            dist = (agent["position"] - other["position"]).magnitude()
            if dist < neighbor_range:
                avg_pos += other["position"]
                count += 1
        
        if count > 0:
            avg_pos = avg_pos * (1.0 / count)
            cohesion = avg_pos - agent["position"]
            cohesion.normalize()
            return cohesion
        return Vector()
    
    def rule_separation(self, agent: Dict, neighbor_range: float = 5):
        steer = Vector()
        count = 0
        
        for other in self.agents:
            if other["id"] == agent["id"]:
                continue
            dist = (agent["position"] - other["position"]).magnitude()
            if dist < neighbor_range and dist > 0:
                diff = agent["position"] - other["position"]
                diff = diff * (1.0 / dist)
                steer += diff
                count += 1
        
        if count > 0:
            steer = steer * (1.0 / count)
            steer.normalize()
            return steer
        return Vector()
    
    def rule_alignment(self, agent: Dict, neighbor_range: float = 10):
        avg_vel = Vector()
        count = 0
        
        for other in self.agents:
            if other["id"] == agent["id"]:
                continue
            dist = (agent["position"] - other["position"]).magnitude()
            if dist < neighbor_range:
                avg_vel += other["velocity"]
                count += 1
        
        if count > 0:
            avg_vel = avg_vel * (1.0 / count)
            avg_vel.normalize()
            return avg_vel - agent["velocity"]
        return Vector()
    
    def step(self, dt: float = 0.1):
        self.time += dt
        
        for agent in self.agents:
            cohesion = self.rule_cohesion(agent)
            separation = self.rule_separation(agent)
            alignment = self.rule_alignment(agent)
            
            agent["velocity"] += cohesion * 0.01
            agent["velocity"] += separation * 0.05
            agent["velocity"] += alignment * 0.05
            
            agent["velocity"].normalize()
            agent["velocity"] *= 2
            
            agent["position"] += agent["velocity"] * dt
            agent["age"] += dt
            agent["energy"] -= 0.1
        
        self.agents = [a for a in self.agents if a["energy"] > 0]
        
        if len(self.agents) < self.num_agents // 2:
            self._init_agents()


class FluidSimulation:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid_size = 50
        self.density = [[0] * (width // self.grid_size) for _ in range(height // self.grid_size)]
        self.velocity_x = [[0] * (width // self.grid_size) for _ in range(height // self.grid_size)]
        self.velocity_y = [[0] * (width // self.grid_size) for _ in range(height // self.grid_size)]
    
    def add_drop(self, x: float, y: float, amount: float = 10):
        gx = int(x / self.grid_size)
        gy = int(y / self.grid_size)
        
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= gx + i < len(self.density[0]) and 0 <= gy + j < len(self.density):
                    dist = math.sqrt(i**2 + j**2)
                    if dist < 2:
                        self.density[gy + j][gx + i] += amount * (1 - dist/2)
    
    def step(self):
        nx, ny = len(self.density[0]), len(self.density)
        
        new_density = [[0] * nx for _ in range(ny)]
        new_vx = [[0] * nx for _ in range(ny)]
        new_vy = [[0] * nx for _ in range(ny)]
        
        for i in range(nx):
            for j in range(ny):
                total = self.density[j][i]
                if total > 0:
                    new_density[j][i] = total * 0.99
                    new_vx[j][i] = self.velocity_x[j][i] * 0.98
                    new_vy[j][i] = self.velocity_y[j][i] * 0.98
        
        self.density = new_density
        self.velocity_x = new_vx
        self.velocity_y = new_vy
    
    def to_html(self) -> str:
        return f'''
<!DOCTYPE html>
<html>
<body>
<canvas id="canvas" width="{self.width}" height="{self.height}"></canvas>
<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const density = {json.dumps(self.density)};
const gridSize = {self.grid_size};

canvas.onclick = (e) => {{
    const x = e.clientX;
    const y = e.clientY;
    addDrop(x, y);
}};

function addDrop(x, y) {{
    const gx = Math.floor(x / gridSize);
    const gy = Math.floor(y / gridSize);
    for (let di = -2; di <= 2; di++) {{
        for (let dj = -2; dj <= 2; dj++) {{
            if (density[gy + dj] && density[gy + dj][gx + di] !== undefined) {{
                const dist = Math.sqrt(di*di + dj*dj);
                if (dist < 2) density[gy + dj][gx + di] += 10 * (1 - dist/2);
            }}
        }}
    }}
}}

function animate() {{
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    for (let j = 0; j < density.length; j++) {{
        for (let i = 0; i < density[j].length; i++) {{
            const d = density[j][i];
            if (d > 0.1) {{
                ctx.fillStyle = `rgba(0, 150, 255, ${{Math.min(d/10, 1)}})`;
                ctx.fillRect(i * gridSize, j * gridSize, gridSize, gridSize);
            }}
        }}
    }}
    
    for (let j = density.length - 1; j > 0; j--) {{
        for (let i = 0; i < density[j].length; i++) {{
            density[j][i] = density[j][i] * 0.99;
            if (j < density.length - 1) {{
                density[j + 1][i] += density[j][i] * 0.5;
                density[j][i] *= 0.5;
            }}
        }}
    }}
    
    requestAnimationFrame(animate);
}}
animate();
</script>
</body>
</html>
'''


class SimulationManager:
    def __init__(self):
        self.simulations: Dict[str, Any] = {}
        self.blender = BlenderInterface()
        self.renderers: Dict[str, RenderingEngine] = {
            "2d": RenderingEngine(Dimension.DIM_2D),
            "3d": RenderingEngine(Dimension.DIM_3D),
            "4d": RenderingEngine(Dimension.DIM_4D)
        }
    
    def create_simulation(self, name: str, dimension: Dimension, sim_type: SimulationType = None):
        if dimension == Dimension.DIM_2D:
            self.simulations[name] = Simulation2D()
        elif dimension == Dimension.DIM_3D:
            self.simulations[name] = Simulation3D()
        elif dimension == Dimension.DIM_4D:
            self.simulations[name] = Simulation4D()
        
        return self.simulations[name]
    
    def get_simulation(self, name: str):
        return self.simulations.get(name)
    
    def list_simulations(self) -> List[str]:
        return list(self.simulations.keys())
    
    def step_all(self, dt: float = 0.016):
        for sim in self.simulations.values():
            sim.step(dt)
    
    def render(self, name: str, format: str = "html") -> str:
        sim = self.simulations.get(name)
        if not sim:
            return ""
        
        if isinstance(sim, Simulation2D):
            return self.renderers["2d"].render_to_html(sim)
        elif isinstance(sim, Simulation3D):
            if format == "html":
                return self.renderers["3d"].render_to_html_3d(sim)
            else:
                return sim.get_camera_view(Vector(50, 50, 50), Vector(0, 0, 0))
        elif isinstance(sim, Simulation4D):
            return self.renderers["4d"].render_to_html_4d(sim)
        
        return ""
    
    def export_blender(self, name: str, output_path: str = "/tmp/simulation.png"):
        if not self.blender.is_available():
            return {"success": False, "error": "Blender not available"}
        
        sim = self.simulations.get(name)
        if not sim or not isinstance(sim, Simulation3D):
            return {"success": False, "error": "Requires 3D simulation"}
        
        return self.blender.create_scene_from_simulation(sim, output_path)


if __name__ == "__main__":
    manager = SimulationManager()
    
    sim_2d = manager.create_simulation("particles_2d", Dimension.DIM_2D)
    for _ in range(50):
        sim_2d.add_particle(random.uniform(0, 800), random.uniform(0, 600),
                           random.uniform(-2, 2), random.uniform(-2, 2))
    
    sim_3d = manager.create_simulation("particles_3d", Dimension.DIM_3D)
    for i in range(20):
        sim_3d.add_body(f"body_{i}", random.uniform(-50, 50), 
                       random.uniform(-50, 50), random.uniform(-50, 50),
                       size=random.uniform(1, 5))
    
    sim_4d = manager.create_simulation("particles_4d", Dimension.DIM_4D)
    for _ in range(30):
        sim_4d.add_hyperparticle(random.uniform(-30, 30), random.uniform(-30, 30),
                                random.uniform(-30, 30), random.uniform(-10, 10))
    
    print(f"Created {len(manager.list_simulations())} simulations:")
    for name in manager.list_simulations():
        print(f"  - {name}")
    
    print(f"\nBlender available: {manager.blender.is_available()}")
    
    html_4d = manager.render("particles_4d")
    print(f"\n4D simulation HTML generated ({len(html_4d)} bytes)")