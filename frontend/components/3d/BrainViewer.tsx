"use client";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { Sparkles, Info } from "lucide-react";

export function BrainViewer() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeLobe, setActiveLobe] = useState<string>("Frontal Lobe");
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth || 450;
    const height = container.clientHeight || 450;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 8.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.innerHTML = "";
    container.appendChild(renderer.domElement);

    // Anatomical Brain Particle Cloud & Network
    // Generates a recognizable anatomical dual-hemisphere brain geometry
    const brainGroup = new THREE.Group();
    scene.add(brainGroup);

    const particleCount = 2400;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const cyan = new THREE.Color("#11B9D4");
    const violet = new THREE.Color("#7867F5");
    const blue = new THREE.Color("#3B82F6");

    let pIdx = 0;
    for (let i = 0; i < particleCount; i++) {
      // Hemisphere selection: left (-1) or right (+1)
      const hemisphere = Math.random() > 0.5 ? 1 : -1;
      
      // Ellipsoidal brain coordinates with cortex folds
      const u = Math.random() * Math.PI;
      const v = Math.random() * 2 * Math.PI;
      
      // Modulate shape for realistic cerebral lobes
      const rX = 2.1 * (1 + 0.15 * Math.sin(5 * u) * Math.cos(3 * v));
      const rY = 1.7 * (1 + 0.12 * Math.cos(4 * u));
      const rZ = 2.5 * (1 + 0.18 * Math.sin(3 * v));

      const x = hemisphere * (0.35 + Math.abs(rX * Math.sin(u) * Math.cos(v) * (0.8 + 0.2 * Math.random())));
      const y = rY * Math.cos(u) * (0.85 + 0.15 * Math.random());
      const z = rZ * Math.sin(u) * Math.sin(v) * (0.85 + 0.15 * Math.random());

      positions[pIdx] = x;
      positions[pIdx + 1] = y;
      positions[pIdx + 2] = z;

      // Color gradient based on anatomical region
      const t = (z + 2.5) / 5.0;
      const c = new THREE.Color();
      if (y > 0.3) {
        c.lerpColors(cyan, violet, t);
      } else {
        c.lerpColors(violet, blue, Math.random());
      }

      colors[pIdx] = c.r;
      colors[pIdx + 1] = c.g;
      colors[pIdx + 2] = c.b;

      pIdx += 3;
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

    // Particle Material
    const pMaterial = new THREE.PointsMaterial({
      size: 0.075,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
      blending: THREE.NormalBlending,
    });

    const particles = new THREE.Points(geometry, pMaterial);
    brainGroup.add(particles);

    // Add neural synaptic connection lines between proximal points
    const linePositions: number[] = [];
    const lineColors: number[] = [];
    const maxConnections = 600;
    let connections = 0;

    for (let i = 0; i < particleCount && connections < maxConnections; i += 4) {
      for (let j = i + 1; j < Math.min(i + 15, particleCount) && connections < maxConnections; j++) {
        const dx = positions[i * 3] - positions[j * 3];
        const dy = positions[i * 3 + 1] - positions[j * 3 + 1];
        const dz = positions[i * 3 + 2] - positions[j * 3 + 2];
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

        if (dist < 0.65) {
          linePositions.push(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]);
          linePositions.push(positions[j * 3], positions[j * 3 + 1], positions[j * 3 + 2]);

          lineColors.push(0.06, 0.72, 0.83); // Cyan
          lineColors.push(0.47, 0.40, 0.96); // Violet
          connections++;
        }
      }
    }

    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute("position", new THREE.Float32BufferAttribute(linePositions, 3));
    lineGeometry.setAttribute("color", new THREE.Float32BufferAttribute(lineColors, 3));

    const lineMaterial = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.35,
    });

    const neuralWeb = new THREE.LineSegments(lineGeometry, lineMaterial);
    brainGroup.add(neuralWeb);

    // Anatomical landmarks markers
    const landmarkPositions = [
      { name: "Frontal Lobe", pos: [0, 1.2, 1.8], color: 0x11b9d4 },
      { name: "Parietal Lobe", pos: [0, 1.5, -0.6], color: 0x7867f5 },
      { name: "Occipital Lobe", pos: [0, 0.2, -2.2], color: 0x3b82f6 },
      { name: "Temporal Lobe", pos: [1.8, -0.5, 0.3], color: 0x10b981 },
      { name: "Pituitary Region", pos: [0, -0.9, 0.5], color: 0xf59e0b },
    ];

    const markersGroup = new THREE.Group();
    landmarkPositions.forEach((lm) => {
      const markerGeo = new THREE.SphereGeometry(0.12, 16, 16);
      const markerMat = new THREE.MeshBasicMaterial({
        color: lm.color,
        wireframe: true,
      });
      const mesh = new THREE.Mesh(markerGeo, markerMat);
      mesh.position.set(lm.pos[0], lm.pos[1], lm.pos[2]);
      markersGroup.add(mesh);
    });
    brainGroup.add(markersGroup);

    // Mouse movement interaction
    let mouseX = 0;
    let mouseY = 0;
    let targetRotationX = 0;
    let targetRotationY = 0;

    const handleMouseMove = (event: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = event.clientX - rect.left - width / 2;
      const y = event.clientY - rect.top - height / 2;
      mouseX = (x / width) * 2;
      mouseY = (y / height) * 2;
      targetRotationY = mouseX * 0.7;
      targetRotationX = mouseY * 0.5;
    };

    container.addEventListener("mousemove", handleMouseMove);

    // Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      // Gentle continuous rotation
      brainGroup.rotation.y += 0.004;

      // Parallax smooth interpolation
      brainGroup.rotation.x += (targetRotationX - brainGroup.rotation.x) * 0.05;
      brainGroup.position.y = Math.sin(elapsed * 1.5) * 0.12;

      // Pulse markers
      const scale = 1 + 0.2 * Math.sin(elapsed * 3);
      markersGroup.children.forEach((child) => child.scale.set(scale, scale, scale));

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const newW = container.clientWidth || 450;
      const newH = container.clientHeight || 450;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      container.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
      geometry.dispose();
      pMaterial.dispose();
      lineGeometry.dispose();
      lineMaterial.dispose();
    };
  }, []);

  return (
    <div className="relative w-full max-w-[500px] h-[480px] mx-auto flex items-center justify-center">
      {/* Soft Ambient Light Gradient Background Glow */}
      <div className="absolute inset-0 bg-gradient-to-tr from-[#11B9D4]/10 via-[#7867F5]/5 to-transparent rounded-full filter blur-3xl pointer-events-none"></div>

      {/* 3D Canvas Container */}
      <div 
        ref={containerRef} 
        className="w-full h-full cursor-grab active:cursor-grabbing z-10"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      />

      {/* Interactive Floating Badge */}
      <div className="absolute bottom-3 left-4 right-4 z-20 flex items-center justify-between px-3 py-2 bg-[#FFFFFF]/90 backdrop-blur-md rounded-xl border border-[#E5EAF1] shadow-sm text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-[#11B9D4] animate-ping"></span>
          <span className="font-semibold text-[#15243A]">3D Neural Spatial Geometry</span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-[#68758A]">
          <span>Rotate & explore lobes</span>
        </div>
      </div>
    </div>
  );
}
