import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface VoxelClusterProps {
  position: [number, number, number]
  color: string
  count?: number
  scale?: number
  seed?: number
  rotationSpeed?: number
  floatSpeed?: number
}

// Deterministic pseudo-random for stable layouts across renders
function mulberry32(seed: number) {
  return function () {
    seed |= 0
    seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/**
 * A floating cluster of voxel cubes representing one game world.
 * Cubes are arranged in a loose spherical cloud with subtle individual
 * rotation and a global slow spin.
 */
export default function VoxelCluster({
  position,
  color,
  count = 28,
  scale = 1,
  seed = 1,
  rotationSpeed = 0.06,
  floatSpeed = 0.4,
}: VoxelClusterProps) {
  const group = useRef<THREE.Group>(null)

  // Pre-compute per-voxel transforms
  const voxels = useMemo(() => {
    const rand = mulberry32(seed)
    const items: {
      pos: [number, number, number]
      size: number
      rot: [number, number, number]
      phase: number
    }[] = []
    for (let i = 0; i < count; i++) {
      // Distribute on a sphere shell with bias toward surface
      const theta = rand() * Math.PI * 2
      const phi = Math.acos(2 * rand() - 1)
      const r = (0.7 + rand() * 1.1) * scale
      const x = r * Math.sin(phi) * Math.cos(theta)
      const y = r * Math.sin(phi) * Math.sin(theta) * 0.7
      const z = r * Math.cos(phi) * 0.7
      const size = (0.18 + rand() * 0.22) * scale
      items.push({
        pos: [x, y, z],
        size,
        rot: [rand() * Math.PI, rand() * Math.PI, rand() * Math.PI],
        phase: rand() * Math.PI * 2,
      })
    }
    return items
  }, [count, scale, seed])

  const material = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color(color),
        roughness: 0.35,
        metalness: 0.25,
        emissive: new THREE.Color(color).multiplyScalar(0.35),
        emissiveIntensity: 0.6,
      }),
    [color],
  )

  const edgesMaterial = useMemo(
    () =>
      new THREE.LineBasicMaterial({
        color: new THREE.Color(color).multiplyScalar(1.4),
        transparent: true,
        opacity: 0.5,
      }),
    [color],
  )

  useFrame((state, delta) => {
    if (!group.current) return
    const t = state.clock.elapsedTime
    group.current.rotation.y += delta * rotationSpeed
    group.current.rotation.x = Math.sin(t * 0.2) * 0.08
    // Gentle float of the whole cluster
    group.current.position.y = position[1] + Math.sin(t * floatSpeed) * 0.18
    group.current.position.x = position[0]
    group.current.position.z = position[2]
  })

  return (
    <group ref={group} position={position}>
      {voxels.map((v, i) => (
        <Voxel key={i} {...v} material={material} edgesMaterial={edgesMaterial} />
      ))}
      {/* Core glow sphere */}
      <mesh>
        <sphereGeometry args={[0.18 * scale, 16, 16]} />
        <meshBasicMaterial color={color} transparent opacity={0.35} />
      </mesh>
    </group>
  )
}

function Voxel({
  pos,
  size,
  rot,
  phase,
  material,
  edgesMaterial,
}: {
  pos: [number, number, number]
  size: number
  rot: [number, number, number]
  phase: number
  material: THREE.Material
  edgesMaterial: THREE.Material
}) {
  const mesh = useRef<THREE.Mesh>(null)
  const edges = useRef<THREE.LineSegments>(null)

  useFrame((state) => {
    if (!mesh.current || !edges.current) return
    const t = state.clock.elapsedTime
    mesh.current.rotation.x = rot[0] + t * 0.1
    mesh.current.rotation.y = rot[1] + t * 0.12
    mesh.current.position.y = pos[1] + Math.sin(t * 0.6 + phase) * 0.06
    edges.current.rotation.copy(mesh.current.rotation)
    edges.current.position.copy(mesh.current.position)
  })

  return (
    <group position={pos} rotation={rot}>
      <mesh ref={mesh} material={material}>
        <boxGeometry args={[size, size, size]} />
      </mesh>
      <lineSegments ref={edges} material={edgesMaterial}>
        <edgesGeometry args={[new THREE.BoxGeometry(size, size, size)]} />
      </lineSegments>
    </group>
  )
}
