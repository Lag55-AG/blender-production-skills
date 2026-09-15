# Blender Production Skills

A production-grade Blender skills suite for Codex, covering native modeling, Geometry Nodes, simulation, rigging, materials, lighting, topology, scene validation, and reference reconstruction workflows.

## Features

- Uses `blender-production-router` as the sole entry point for production workflow and state scheduling.
- Prioritizes appropriate native Blender systems: Boolean, Array, Curve, Modifier, Constraint, Shader, and Physics.
- Uses Geometry Nodes only when fields, scattering, instancing, procedural topology, or node-based simulations offer a clear advantage.
- Supports direct topology, Boolean cuts, stair arrays, curve paths, cloth, rigid bodies, fluids, water, metal, wood, and NPR rendering pipelines.
- Provides read-only retrieval, interface inspection, and Blender 5.2 runtime probing for local asset libraries.
- Establishes routes, relationship construction, phases, scoring, and technical validation artifacts for non-trivial tasks.

## Showcases

Below are some scenes and renders created or explored using this suite.

<table>
  <tr>
    <td width="50%"><img src="assets/showcases/corridor-doorway.jpg" alt="Corridor and Door"><br><sub>Corridor and Door</sub></td>
    <td width="50%"><img src="assets/showcases/moonlit-bridge-viewport.jpg" alt="Moonlit Wooden Bridge Blender Viewport"><br><sub>Moonlit Wooden Bridge Blender Viewport</sub></td>
  </tr>
  <tr>
    <td><img src="assets/showcases/water-chamber.jpg" alt="Underwater Circular Space"><br><sub>Underwater Circular Space</sub></td>
    <td><img src="assets/showcases/indoor-pool.jpg" alt="Indoor Pool"><br><sub>Indoor Pool</sub></td>
  </tr>
  <tr>
    <td><img src="assets/showcases/flooded-subway-passage.jpg" alt="Flooded Underground Passage"><br><sub>Flooded Underground Passage</sub></td>
    <td><img src="assets/showcases/subway-platform.jpg" alt="Subway Platform"><br><sub>Subway Platform</sub></td>
  </tr>
  <tr>
    <td><img src="assets/showcases/fisheye-elevator.jpg" alt="Fisheye Elevator Space"><br><sub>Fisheye Elevator Space</sub></td>
    <td><img src="assets/showcases/flooded-industrial-hall.jpg" alt="Flooded Industrial Space"><br><sub>Flooded Industrial Space</sub></td>
  </tr>
  <tr>
    <td><img src="assets/showcases/station-corridor.jpg" alt="Subway Corridor"><br><sub>Subway Corridor</sub></td>
    <td><img src="assets/showcases/tiled-pool.jpg" alt="Tiled Pool"><br><sub>Tiled Pool</sub></td>
  </tr>
</table>

## Structure

`blender-production-router` is the top-level entry point; other directories are domain-specific Specialist Skills:

- `blender-direct-surface-modeling`: Vertices/Edges/Faces, BMesh, Boolean, Remesh, Sculpt, and Retopology.
- `blender-procedural-systems`: Array, Curve, Instances, Scattering, and Procedural Systems.
- `blender-geometry-nodes-studio`: Geometry Nodes Graphs, Fields, Instances, and Simulation Zones.
- `blender-simulation-effects`: Cloth, Soft Body, Rigid Body, Fluid, Water, Particles, and Fracture.
- `blender-material-surfacing`: PBR Materials, Metal, Wood, Water, and Surface Variation.
- `blender-geometry-validation`: Topology, Connectivity, Collision, Performance, and Scene Protection Checks.

## Usage

Place this repository into the Codex Skills directory, for example:

```text
C:\Users\Administrator\.codex\skills\blender-production-suite
```

The default target is Blender 5.2 LTS and the official Blender MCP. Third-party local assets are only considered candidates if they exist, are readable, and pass runtime checks; they will not be automatically installed or modified.

## Note

- This repository does not include original source files, caches, render results, or user projects for third-party assets.
- Standard hard-surface cuts remain native Booleans; standard regular stairs remain Arrays. Geometry Nodes will not be abused just to use nodes.
- Reference and usability data may change with Blender versions and local asset libraries and should be re-probed in the target environment.

## Personal Profile

**CORVUS / Xiaohongshu: liu_jian**

![CORVUS Xiaohongshu Profile](assets/corvus-xiaohongshu-profile.png)
