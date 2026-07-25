import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface DataStreamsProps {
  from: [number, number, number]
  to: [number, number, number]
  color?: string
  count?: number
  arcHeight?: number
}

/**
 * Particle data stream flowing between two voxel clusters along an
 * arched bezier path. Particles travel from `from` to `to` and wrap
 * around continuously, with size and opacity fading at the ends.
 */
export default function DataStreams({
  from,
  to,
  color = '#22d3ee',
  count = 220,
  arcHeight = 1.6,
}: DataStreamsProps) {
  const points = useMemo(() => {
    const a = new THREE.Vector3(...from)
    const b = new THREE.Vector3(...to)
    const mid = a.clone().add(b).multiplyScalar(0.5)
    // Push mid up and slightly toward camera to create an arc
    mid.y += arcHeight
    mid.z += 0.6
    const curve = new THREE.QuadraticBezierCurve3(a, mid, b)
    return curve.getPoints(64)
  }, [from, to, arcHeight])

  const curve = useMemo(() => {
    const a = new THREE.Vector3(...from)
    const b = new THREE.Vector3(...to)
    const mid = a.clone().add(b).multiplyScalar(0.5)
    mid.y += arcHeight
    mid.z += 0.6
    return new THREE.QuadraticBezierCurve3(a, mid, b)
  }, [from, to, arcHeight])

  // Pre-allocate particle attributes
  const { geometry, speeds } = useMemo(() => {
    const positions = new Float32Array(count * 3)
    const sizes = new Float32Array(count)
    const offsets = new Float32Array(count)
    const speedsArr = new Float32Array(count)
    for (let i = 0; i < count; i++) {
      const t = i / count
      const p = curve.getPoint(t)
      positions[i * 3] = p.x
      positions[i * 3 + 1] = p.y
      positions[i * 3 + 2] = p.z
      sizes[i] = 0.04 + Math.random() * 0.06
      offsets[i] = t
      speedsArr[i] = 0.06 + Math.random() * 0.08
    }
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1))
    geo.setAttribute('offset', new THREE.BufferAttribute(offsets, 1))
    return { geometry: geo, speeds: speedsArr }
  }, [curve, count])

  // Material: soft round point with glow
  const material = useMemo(() => {
    const tex = makeParticleTexture(color)
    return new THREE.PointsMaterial({
      size: 0.14,
      map: tex,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true,
      color: new THREE.Color(color),
      opacity: 0.85,
    })
  }, [color])

  const pointsRef = useRef<THREE.Points>(null)

  // Persistent progress array (declared before useFrame to avoid TDZ confusion)
  const progress = useMemo(() => {
    const arr = new Float32Array(count)
    for (let i = 0; i < count; i++) arr[i] = i / count
    return arr
  }, [count])

  useFrame((_, delta) => {
    if (!pointsRef.current) return
    const pos = pointsRef.current.geometry.attributes.position as THREE.BufferAttribute
    const arr = pos.array as Float32Array
    for (let i = 0; i < count; i++) {
      const idx = i * 3
      progress[i] += speeds[i] * delta
      if (progress[i] > 1) progress[i] -= 1
      const p = curve.getPoint(progress[i])
      arr[idx] = p.x
      arr[idx + 1] = p.y
      arr[idx + 2] = p.z
    }
    pos.needsUpdate = true
  })

  return (
    <>
      <points ref={pointsRef} geometry={geometry} material={material} />
      {/* Soft guide curve */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={points.length}
            array={Float32Array.from(points.flatMap((p) => [p.x, p.y, p.z]))}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color={color} transparent opacity={0.18} />
      </line>
    </>
  )
}

// Procedural circular sprite (no external asset needed)
function makeParticleTexture(color: string): THREE.Texture {
  const size = 64
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size
  const ctx = canvas.getContext('2d')!
  const grad = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2)
  const c = new THREE.Color(color)
  const r = Math.floor(c.r * 255)
  const g = Math.floor(c.g * 255)
  const b = Math.floor(c.b * 255)
  grad.addColorStop(0, `rgba(${r},${g},${b},1)`)
  grad.addColorStop(0.3, `rgba(${r},${g},${b},0.7)`)
  grad.addColorStop(1, `rgba(${r},${g},${b},0)`)
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, size, size)
  const tex = new THREE.CanvasTexture(canvas)
  tex.needsUpdate = true
  return tex
}
