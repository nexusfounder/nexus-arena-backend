/* ============================================================
   login-wave.js — Full-Bleed 3D WebGL Particle Wave Background
   Faithful port of the three.js particle wave field from alldeputations.com
   Custom-tuned for Nexus Gaming Arena Login & Gateway View
   ============================================================ */

(function () {
    'use strict';

    function initHeroWave() {
        if (typeof THREE === 'undefined') {
            console.warn('[HeroWave] THREE not ready yet, retrying in 50ms...');
            setTimeout(initHeroWave, 50);
            return;
        }

        const canvas = document.getElementById("heroWaveCanvas");
        if (!canvas) {
            console.warn('[HeroWave] Canvas #heroWaveCanvas not found, retrying in 50ms...');
            setTimeout(initHeroWave, 50);
            return;
        }

        // Prevent double initialization
        if (canvas.__waveInitialized) return;
        canvas.__waveInitialized = true;

        const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        let renderer;
        try {
            renderer = new THREE.WebGLRenderer({
                canvas: canvas,
                antialias: true,
                alpha: true,
                powerPreference: "high-performance"
            });
        } catch (err) {
            console.error('[HeroWave] Failed to create WebGLRenderer:', err);
            return;
        }

        const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
        renderer.setPixelRatio(pixelRatio);
        renderer.autoClear = false;

        const scene = new THREE.Scene();

        // Dual Camera Perspective (Faithful to alldeputations.com):
        // camTop looks DOWN  -> wave horizon rides high at the top behind branding/header
        // camBottom looks UP -> wave sea rolls at the bottom of viewport
        const initialAspect = window.innerWidth / (window.innerHeight || 1);
        const camTop = new THREE.PerspectiveCamera(55, initialAspect, 0.1, 100);
        const camBottom = new THREE.PerspectiveCamera(55, initialAspect, 0.1, 100);
        const CAM = {
            top: { y: 7.0, lookY: -1.5, z: 14.0 },
            bottom: { y: 2.4, lookY: 6.0, z: 15.0 }
        };

        function placeCameras(mx, my) {
            camTop.position.set(mx * 0.5, CAM.top.y + my * 0.25, CAM.top.z);
            camTop.lookAt(0, CAM.top.lookY, 0);
            camBottom.position.set(mx * 0.5, CAM.bottom.y + my * 0.25, CAM.bottom.z);
            camBottom.lookAt(0, CAM.bottom.lookY, 0);
        }
        placeCameras(0, 0);

        // Density grid tuned for silky 60fps across mobile and desktop
        const isMobile = window.innerWidth <= 768;
        const COLS = isMobile ? 120 : 200;
        const ROWS = isMobile ? 130 : 210;
        const W = 46.0;
        const H = 40.0;
        const count = COLS * ROWS;
        const positions = new Float32Array(count * 3);
        const seeds = new Float32Array(count);

        let idx = 0;
        for (let y = 0; y < ROWS; y++) {
            for (let x = 0; x < COLS; x++) {
                positions[idx * 3 + 0] = (x / (COLS - 1) - 0.5) * W;
                positions[idx * 3 + 1] = 0;
                positions[idx * 3 + 2] = (y / (ROWS - 1) - 0.5) * H;
                seeds[idx] = Math.random();
                idx++;
            }
        }

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute("aSeed", new THREE.BufferAttribute(seeds, 1));

        const uniforms = {
            uTime: { value: 0 },
            uMouse: { value: new THREE.Vector2(0, 0) },
            uScroll: { value: 0 },
            uPixelRatio: { value: pixelRatio },
            // Atmospheric brand palette: dark void ink + electric cyan, radiant sky, violet, and neon teal
            uColInk: { value: new THREE.Color("#0a1020") },
            uColA: { value: new THREE.Color("#00f2fe") },   // Electric Cyan
            uColB: { value: new THREE.Color("#38bdf8") },   // Radiant Sky Cyan
            uColC: { value: new THREE.Color("#a855f7") },   // Neon Violet
            uColD: { value: new THREE.Color("#00ffcc") }    // Neon Emerald / Teal
        };

        const VERT = `
            uniform float uTime;
            uniform vec2 uMouse;
            uniform float uScroll;
            uniform float uPixelRatio;
            attribute float aSeed;
            varying float vElev;
            varying float vSeed;
            varying vec2 vUvPos;

            void main() {
                vec3 p = position;

                // Layered traveling wave functions (alldeputations.com)
                float t = uTime * 0.55;
                float e = 0.0;
                e += sin(p.x * 0.55 + t) * 0.75;
                e += sin(p.z * 0.85 + t * 1.4) * 0.5;
                e += sin((p.x + p.z) * 0.35 + t * 0.8) * 0.6;

                // Interactive swell that follows the mouse/touch cursor
                float mDist = distance(p.xz, uMouse * vec2(23.0, 20.0));
                e += smoothstep(5.5, 0.0, mDist) * 1.4;

                // Ease waves down slightly as user scrolls
                e *= (1.0 - uScroll * 0.35);

                p.y = e;
                vElev = e;
                vSeed = aSeed;
                vUvPos = vec2(position.x / 46.0 + 0.5, position.z / 40.0 + 0.5);

                vec4 mv = modelViewMatrix * vec4(p, 1.0);
                gl_Position = projectionMatrix * mv;

                // Generously sized luminous circular particles (2.5px - 6px)
                gl_PointSize = min((3.2 + aSeed * 2.8) * uPixelRatio * (15.0 / -mv.z), 24.0 * uPixelRatio);
            }
        `;

        const FRAG = `
            uniform vec3 uColInk;
            uniform vec3 uColA;
            uniform vec3 uColB;
            uniform vec3 uColC;
            uniform vec3 uColD;
            varying float vElev;
            varying float vSeed;
            varying vec2 vUvPos;

            void main() {
                // Circular particle shape
                float d = length(gl_PointCoord - 0.5);
                if (d > 0.5) discard;

                // Cyan gradient on left, violet/teal on right
                vec3 warm = mix(uColA, uColB, vUvPos.y);
                vec3 cool = mix(uColC, uColD, vUvPos.y);
                vec3 hue = mix(warm, cool, smoothstep(0.15, 0.85, vUvPos.x));

                // Colorize from displacement so crests blaze brightly across the whole field
                float energy = smoothstep(0.02, 0.7, abs(vElev));
                vec3 col = mix(mix(uColInk, hue, 0.45), hue, energy);

                // Luminous radial glow bead
                float glow = smoothstep(0.5, 0.08, d);
                float alpha = (0.55 + energy * 0.45) * (0.7 + vSeed * 0.3) * glow;
                gl_FragColor = vec4(col, alpha);
            }
        `;

        const material = new THREE.ShaderMaterial({
            uniforms: uniforms,
            transparent: true,
            depthWrite: false,
            vertexShader: VERT,
            fragmentShader: FRAG
        });

        const points = new THREE.Points(geometry, material);
        scene.add(points);

        function resize() {
            const w = window.innerWidth;
            const h = window.innerHeight;
            if (w === 0 || h === 0) return;
            canvas.style.width = '100%';
            canvas.style.height = '100%';
            renderer.setSize(w, h, false);
            const aspect = w / h;
            camTop.aspect = aspect;
            camTop.updateProjectionMatrix();
            camBottom.aspect = aspect;
            camBottom.updateProjectionMatrix();
            uniforms.uPixelRatio.value = Math.min(window.devicePixelRatio || 1, 2);
        }
        resize();
        window.addEventListener("resize", resize);

        function renderAll() {
            renderer.clear();
            renderer.render(scene, camTop);
            renderer.render(scene, camBottom);
        }

        // Mouse & Touch pointer tracking for interactive swell
        const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
        function updatePointer(clientX, clientY) {
            mouse.tx = (clientX / (window.innerWidth || 1)) * 2 - 1;
            mouse.ty = -((clientY / (window.innerHeight || 1)) * 2 - 1);
        }

        window.addEventListener("pointermove", (e) => {
            updatePointer(e.clientX, e.clientY);
        }, { passive: true });

        window.addEventListener("touchmove", (e) => {
            if (e.touches && e.touches[0]) {
                updatePointer(e.touches[0].clientX, e.touches[0].clientY);
            }
        }, { passive: true });

        // Scroll listener (both window and #gateway-landing-view container)
        let ticking = false;
        function readScroll() {
            const landingEl = document.getElementById("gateway-landing-view");
            const scrollY = landingEl ? landingEl.scrollTop : window.scrollY;
            const heroZone = window.innerHeight || 1;
            uniforms.uScroll.value = Math.min(Math.max(scrollY / heroZone, 0), 1);
            ticking = false;
        }

        window.addEventListener("scroll", () => {
            if (!ticking) {
                ticking = true;
                requestAnimationFrame(readScroll);
            }
        }, { passive: true });

        const landingContainer = document.getElementById("gateway-landing-view");
        if (landingContainer) {
            landingContainer.addEventListener("scroll", () => {
                if (!ticking) {
                    ticking = true;
                    requestAnimationFrame(readScroll);
                }
            }, { passive: true });
        }
        readScroll();

        const clock = new THREE.Clock();
        let isTabActive = !document.hidden;
        let isEnginePaused = false;

        document.addEventListener("visibilitychange", () => {
            isTabActive = !document.hidden;
            if (isTabActive && !isEnginePaused) {
                renderAll();
            }
        });

        // Paint immediately so canvas is never blank
        renderAll();

        // 60fps Animation Loop
        renderer.setAnimationLoop(() => {
            if (!isTabActive || isEnginePaused) return;

            const t = clock.getElapsedTime();
            uniforms.uTime.value = reducedMotion ? 0 : t;

            mouse.x += (mouse.tx - mouse.x) * 0.05;
            mouse.y += (mouse.ty - mouse.y) * 0.05;
            uniforms.uMouse.value.set(mouse.x, mouse.y);

            placeCameras(mouse.x, mouse.y);
            renderAll();
        });

        // Global controller for app integration
        window.heroWaveEngine = {
            pause() {
                isEnginePaused = true;
            },
            resume() {
                if (isEnginePaused) {
                    isEnginePaused = false;
                    clock.start();
                    resize();
                    renderAll();
                }
            },
            resize: resize
        };

        console.log('%c[HeroWave] 🌊 3D Particle Wave Background Active!', 'color:#00f2fe;font-weight:bold;font-size:13px;');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initHeroWave);
    } else {
        initHeroWave();
    }
})();
