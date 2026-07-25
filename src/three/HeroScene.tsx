import { Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { AdaptiveDpr, AdaptiveEvents, Preload } from '@react-three/drei'
import { EffectComposer, Bloom, Vignette, ChromaticAberration } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'
import * as THREE from 'three'
import VoxelCluster from './VoxelCluster'
import DataStreams from './DataStreams'

const MC_POS: [number, number, number] = [-3.2, 0.2, 0]
const MNW_POS: [number, number, number] = [3.2, 0.2, 0]

function Rig() {
  // Slow camera orbit + mouse parallax (uses R3F normalized pointer state)
  useFrame((state) => {
    const px = state.pointer.x
    const py = state.pointer.y
    state.camera.position.x += (px * 1.5 - state.camera.position.x) * 0.04
    state.camera.position.y += (0.6 + py * 0.6 - state.camera.position.y) * 0.04
    state.camera.lookAt(0, 0, 0)
    const t = state.clock.elapsedTime
    state.camera.position.z = 7 + Math.sin(t * 0.08) * 0.4
  })
  return null
}

function Lights() {
  return (
    <>
      <ambientLight intensity={0.35} color="#8fa8ff" />
      <hemisphereLight args={['#9ad8ff', '#1a0f1d', 0.4]} />
      <directionalLight position={[5, 8, 6]} intensity={1.1} color="#ffffff" />
      <pointLight position={[-3, 1, 3]} intensity={2.4} color="#3ddc97" distance={12} />
      <pointLight position={[3, 1, 3]} intensity={2.4} color="#f5b942" distance={12} />
      <pointLight position={[0, 2.5, 1.5]} intensity={1.6} color="#22d3ee" distance={10} />
    </>
  )
}

interface HeroSceneProps {
  className?: string
  enablePostprocessing?: boolean
}

export default function HeroScene({
  className,
  enablePostprocessing = true,
}: HeroSceneProps) {
  const isMobile =
    typeof window !== 'undefined' &&
    (window.matchMedia('(max-width: 768px)').matches ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches)

  return (
    <div className={className} aria-hidden="true">
      <Canvas
        dpr={[1, isMobile ? 1.5 : 2]}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: 'high-performance',
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.1,
        }}
        camera={{ position: [0, 0.6, 7], fov: 42, near: 0.1, far: 100 }}
        style={{ width: '100%', height: '100%' }}
      >
        <fog attach="fog" args={['#07090d', 8, 18]} />
        <Suspense fallback={null}>
          <Lights />
          <VoxelCluster
            position={MC_POS}
            color="#3ddc97"
            count={isMobile ? 18 : 30}
            seed={7}
            scale={1.05}
            rotationSpeed={0.08}
            floatSpeed={0.5}
          />
          <VoxelCluster
            position={MNW_POS}
            color="#f5b942"
            count={isMobile ? 18 : 30}
            seed={21}
            scale={1.05}
            rotationSpeed={-0.08}
            floatSpeed={0.45}
          />
          <DataStreams
            from={MC_POS}
            to={MNW_POS}
            color="#22d3ee"
            count={isMobile ? 120 : 240}
            arcHeight={1.8}
          />
          <DataStreams
            from={MNW_POS}
            to={MC_POS}
            color="#9ad8ff"
            count={isMobile ? 80 : 160}
            arcHeight={1.2}
          />
          <Rig />
          {enablePostprocessing && !isMobile && (
            <EffectComposer multisampling={2} enableNormalPass={false}>
              <Bloom
                intensity={0.85}
                luminanceThreshold={0.18}
                luminanceSmoothing={0.5}
                mipmapBlur
                radius={0.7}
              />
              <ChromaticAberration
                offset={new THREE.Vector2(0.0006, 0.0009)}
                radialModulation={false}
                modulationOffset={0}
                blendFunction={BlendFunction.NORMAL}
              />
              <Vignette eskil={false} offset={0.18} darkness={0.85} />
            </EffectComposer>
          )}
          <Preload all />
          <AdaptiveDpr pixelated />
          <AdaptiveEvents />
        </Suspense>
      </Canvas>
    </div>
  )
}
