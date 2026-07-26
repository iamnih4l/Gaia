"use client";

import * as React from "react";
import * as THREE from "three";
import { TIPPING_ELEMENTS } from "@/constants";
import { useGlobalStore } from "@/store";
import { cn } from "@/lib/utils";

interface Globe3DProps {
  onSelectElement?: (id: string) => void;
  className?: string;
  interactive?: boolean;
}

export function Globe3D({ onSelectElement, className, interactive = true }: Globe3DProps) {
  const mountRef = React.useRef<HTMLDivElement>(null);
  const { selectedElementId } = useGlobalStore();
  const [hoveredId, setHoveredId] = React.useState<string | null>(null);

  React.useEffect(() => {
    const currentMount = mountRef.current;
    if (!currentMount) return;

    const width = currentMount.clientWidth || 600;
    const height = currentMount.clientHeight || 600;

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 2.8;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    currentMount.appendChild(renderer.domElement);

    // Lights
    const ambientLight = new THREE.AmbientLight(0x48cae4, 0.6);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight1.position.set(5, 3, 5);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x7209b7, 0.8);
    dirLight2.position.set(-5, -3, -5);
    scene.add(dirLight2);

    // Earth Sphere
    const earthGeometry = new THREE.SphereGeometry(1, 64, 64);
    
    // Procedural wireframe / grid tech material
    const earthMaterial = new THREE.MeshPhongMaterial({
      color: 0x0b132b,
      emissive: 0x141e37,
      specular: 0x00b4d8,
      shininess: 25,
      wireframe: true,
      transparent: true,
      opacity: 0.85,
    });
    const earthMesh = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earthMesh);

    // Solid inner core sphere for depth
    const coreGeometry = new THREE.SphereGeometry(0.98, 32, 32);
    const coreMaterial = new THREE.MeshBasicMaterial({
      color: 0x070c1b,
    });
    const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial);
    earthMesh.add(coreMesh);

    // Atmospheric Glow Halo
    const atmosphereGeometry = new THREE.SphereGeometry(1.08, 64, 64);
    const atmosphereMaterial = new THREE.MeshBasicMaterial({
      color: 0x00b4d8,
      transparent: true,
      opacity: 0.12,
      side: THREE.BackSide,
    });
    const atmosphereMesh = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    scene.add(atmosphereMesh);

    // Convert lat/lon to 3D Cartesian coordinates
    const latLonToVector3 = (lat: number, lon: number, radius = 1.02): THREE.Vector3 => {
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (lon + 180) * (Math.PI / 180);
      const x = -(radius * Math.sin(phi) * Math.cos(theta));
      const z = radius * Math.sin(phi) * Math.sin(theta);
      const y = radius * Math.cos(phi);
      return new THREE.Vector3(x, y, z);
    };

    // Hotspot Markers
    const markerGroup = new THREE.Group();
    earthMesh.add(markerGroup);

    const markerObjects: { id: string; mesh: THREE.Mesh; ring: THREE.Mesh }[] = [];

    TIPPING_ELEMENTS.forEach((el) => {
      const pos = latLonToVector3(el.coordinates[0], el.coordinates[1], 1.02);
      
      let colorHex = 0x00b4d8; // default cyan
      if (el.status === "CRITICAL") colorHex = 0xf77f00; // orange
      if (el.status === "WARNING") colorHex = 0xfcbf49; // yellow
      if (el.id === selectedElementId) colorHex = 0x7209b7; // purple highlight

      // Inner sphere marker
      const markerGeo = new THREE.SphereGeometry(0.035, 16, 16);
      const markerMat = new THREE.MeshBasicMaterial({ color: colorHex });
      const markerMesh = new THREE.Mesh(markerGeo, markerMat);
      markerMesh.position.copy(pos);
      markerMesh.userData = { id: el.id, name: el.name };
      markerGroup.add(markerMesh);

      // Outer pulsating ring
      const ringGeo = new THREE.RingGeometry(0.045, 0.06, 32);
      const ringMat = new THREE.MeshBasicMaterial({
        color: colorHex,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.6,
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.position.copy(pos);
      ringMesh.lookAt(new THREE.Vector3(0, 0, 0));
      markerGroup.add(ringMesh);

      markerObjects.push({ id: el.id, mesh: markerMesh, ring: ringMesh });
    });

    // Starfield particles in background
    const starGeo = new THREE.BufferGeometry();
    const starCount = 500;
    const starPos = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount * 3; i += 3) {
      starPos[i] = (Math.random() - 0.5) * 20;
      starPos[i + 1] = (Math.random() - 0.5) * 20;
      starPos[i + 2] = (Math.random() - 0.5) * 20;
    }
    starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
    const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.02, transparent: true, opacity: 0.5 });
    const starPoints = new THREE.Points(starGeo, starMat);
    scene.add(starPoints);

    // Mouse interactivity (Raycaster)
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handlePointerMove = (event: MouseEvent) => {
      if (!interactive) return;
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(markerObjects.map((m) => m.mesh));

      if (intersects.length > 0) {
        const id = intersects[0].object.userData.id;
        setHoveredId(id);
        renderer.domElement.style.cursor = "pointer";
      } else {
        setHoveredId(null);
        renderer.domElement.style.cursor = "default";
      }
    };

    const handleClick = () => {
      if (!interactive) return;
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(markerObjects.map((m) => m.mesh));
      if (intersects.length > 0) {
        const id = intersects[0].object.userData.id;
        onSelectElement?.(id);
      }
    };

    const domEl = renderer.domElement;
    domEl.addEventListener("mousemove", handlePointerMove);
    domEl.addEventListener("click", handleClick);

    // Animation Loop
    let animationFrameId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const elapsedTime = clock.getElapsedTime();

      // Gentle continuous rotation
      earthMesh.rotation.y += 0.15 * delta;
      starPoints.rotation.y -= 0.02 * delta;

      // Pulse rings
      markerObjects.forEach((item) => {
        const scale = 1.0 + 0.3 * Math.sin(elapsedTime * 3);
        item.ring.scale.set(scale, scale, scale);
        (item.ring.material as THREE.MeshBasicMaterial).opacity = 0.4 + 0.3 * Math.cos(elapsedTime * 3);
      });

      renderer.render(scene, camera);
    };
    animate();

    // Resize handler
    const handleResize = () => {
      if (!currentMount) return;
      const w = currentMount.clientWidth;
      const h = currentMount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      domEl.removeEventListener("mousemove", handlePointerMove);
      domEl.removeEventListener("click", handleClick);
      cancelAnimationFrame(animationFrameId);
      if (currentMount && renderer.domElement) {
        currentMount.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [interactive, onSelectElement, selectedElementId]);

  const hoveredElement = TIPPING_ELEMENTS.find((e) => e.id === hoveredId);

  return (
    <div ref={mountRef} className={cn("relative w-full h-full min-h-[400px] flex items-center justify-center overflow-hidden", className)}>
      {/* Hover Tooltip Overlay */}
      {hoveredElement && (
        <div className="absolute top-6 left-6 z-10 rounded-xl border border-white/20 bg-slate-900/90 p-3 shadow-2xl backdrop-blur-md max-w-xs animate-in fade-in duration-150">
          <div className="flex items-center gap-2 font-bold text-white text-sm">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{
                backgroundColor:
                  hoveredElement.status === "CRITICAL"
                    ? "#F77F00"
                    : hoveredElement.status === "WARNING"
                    ? "#FCBF49"
                    : "#00B4D8",
              }}
            />
            {hoveredElement.name}
          </div>
          <div className="mt-1 text-xs text-slate-300 font-mono">
            Risk: {(hoveredElement.riskScore * 100).toFixed(0)}% • Lead time: ~{hoveredElement.leadTimeMonths} mo
          </div>
          <div className="mt-1 text-[11px] text-cyan-400 font-semibold">Click to inspect region →</div>
        </div>
      )}
    </div>
  );
}
