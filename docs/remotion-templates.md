# Remotion Templates Collection

**A curated collection of production-ready Remotion video templates for AI coding agents and developers.**



## Template Categories

### Official Templates (remotion-dev)

| Template | Stars | Description | Best For |
|----------|-------|-------------|----------|
| [template-audiogram](https://github.com/remotion-dev/template-audiogram) | 237 | Podcast clips with waveforms & captions | Podcasts, audio content |
| [template-three](https://github.com/remotion-dev/template-three) | 82 | React Three Fiber 3D integration | Product showcases, 3D |
| [template-next-app-dir-tailwind](https://github.com/remotion-dev/template-next-app-dir-tailwind) | 41 | Next.js + Tailwind + Lambda SaaS | Video generation apps |
| [template-react-router](https://github.com/remotion-dev/template-react-router) | 27 | React Router 7 + Lambda | Multi-page video apps |
| [template-skia](https://github.com/remotion-dev/template-skia) | 21 | React Native Skia graphics | Advanced visual effects |
| template-music-visualization | - | Spectrum & waveform visualizers | Music videos |
| template-code-hike | - | Code syntax animations | Tutorials, tech content |

### Caption & Subtitle Libraries

| Template | Stars | Description | Features |
|----------|-------|-------------|----------|
| [remotion-subtitles](https://github.com/ahgsql/remotion-subtitles) | 76 | 17 animated caption styles | Bounce, Fire, Glitch, Neon, 3D, Lightning |
| [remotion-animation](https://github.com/ahgsql/remotion-animation) | 36 | CSS keyframes in Remotion | 80+ animate.css effects |
| [remotion-lottie](https://github.com/ahgsql/remotion-lottie) | 19 | Lottie/After Effects sync | Frame-perfect control |

### Audio Visualization

| Template | Stars | Description | Styles |
|----------|-------|-------------|--------|
| [remotion-audio-visualizers](https://github.com/marcusstenbeck/remotion-audio-visualizers) | 68 | Audio visualization components | Bars, spectrum, waveform |
| [remotion-audio-visualizer](https://github.com/satelllte/remotion-audio-visualizer) | 46 | Minimalistic audio viz | Clean, customizable |
| [remotion-audio-player-template](https://github.com/varunpbardwaj/remotion-audio-player-template) | 7 | Reusable audio player | Player UI component |

### Effects & Animations

| Template | Stars | Description | Effects |
|----------|-------|-------------|---------|
| [remotion-templates](https://github.com/reactvideoeditor/remotion-templates) | 60 | Free effects collection | Matrix rain, particles, glitch, waves |
| [fireship-remotion-intro](https://github.com/thecmdrunner/fireship-remotion-intro) | 16 | Fireship Code Report style | 3D camera, news feed |
| [remotion-fireship](https://github.com/wcandillon/remotion-fireship) | - | "Made with code" video | Meta video creation |

### Data Visualization

| Template | Stars | Description | Use Case |
|----------|-------|-------------|----------|
| [github-stats-remotion](https://github.com/LukasParke/github-stats-remotion) | 6 | GitHub profile video | Developer portfolios |
| [remotion-globegl](https://github.com/alexfernandez803/remotion-globegl) | 9 | 3D globe visualization | Geographic data |
| [mafs-remotion-animation](https://github.com/Octoframes/mafs-remotion-animation) | 1 | Math visualizations | Educational content |

### Social Media

| Template | Stars | Description | Platform |
|----------|-------|-------------|----------|
| [remotion-instagram](https://github.com/hardikmodi1/remotion-instagram) | 5 | Profile showcase | Instagram |
| [remotion-tiktok](https://github.com/heyirfanaziz/remotion-tiktok) | - | TikTok style | TikTok, Reels |
| [github-unwrapped](https://github.com/remotion-dev/github-unwrapped) | - | Year in review | Personalized recaps |

### Deployment & Infrastructure

| Template | Stars | Description | Stack |
|----------|-------|-------------|-------|
| [remotion-sst](https://github.com/karelnagel/remotion-sst) | 25 | AWS Lambda with SST/Pulumi | IaC deployment |
| [Remotion-Matrix-Renderer](https://github.com/yuvraj108c/Remotion-Matrix-Renderer) | 22 | GitHub Actions optimization | 6x faster CI rendering |
| [remotion-gtts-template](https://github.com/thecmdrunner/remotion-gtts-template) | 16 | Google TTS integration | Automated narration |

### 3D & Advanced Graphics

| Template | Stars | Description | Tech |
|----------|-------|-------------|------|
| [template-three](https://github.com/remotion-dev/template-three) | 82 | React Three Fiber | Phone mockups, 3D models |
| [remotion-three-gltf-example](https://github.com/remotion-dev/remotion-three-gltf-example) | 5 | GLTF model loading | 3D assets |
| [tldraw-remotion-animation](https://github.com/Octoframes/tldraw-remotion-animation) | 9 | Whiteboard animations | Explainer videos |

---

## Quick Installation

### Any Template
```bash
# Clone specific template
git clone https://github.com/[org]/[template-name]
cd [template-name]
npm install
npm run dev
```

### Official Templates (Recommended)
```bash
# Interactive template selection
npx create-video@latest

# Or specific template
npx create-video@latest --template=audiogram
npx create-video@latest --template=three
npx create-video@latest --template=next-tailwind
```

### Caption Libraries (NPM)
```bash
npm install @ahgsql/remotion-subtitles
npm install @ahgsql/remotion-animation
npm install remotion-audio-visualizers
```

---

## Template Selection Guide

### By Use Case

| I want to make... | Recommended Template |
|-------------------|---------------------|
| Podcast clips | template-audiogram |
| TikTok/Reels captions | remotion-subtitles |
| Music visualizer | remotion-audio-visualizers |
| Product demo (3D) | template-three |
| Video SaaS platform | template-next-app-dir-tailwind |
| Developer portfolio | github-stats-remotion |
| Code tutorial | template-code-hike |
| YouTube intro | fireship-remotion-intro |
| Data visualization | remotion-globegl |

### By Complexity

| Level | Templates |
|-------|-----------|
| Beginner | template-blank, template-helloworld |
| Intermediate | template-audiogram, remotion-subtitles |
| Advanced | template-three, template-skia |
| Production | template-next-app-dir-tailwind, remotion-sst |

---

## Featured Showcase

### 1. Animated Captions (remotion-subtitles)
17 viral-ready caption styles:
- **Bounce** - Letters pop in
- **Fire** - Burning text effect
- **Glitch** - Digital distortion
- **Neon** - Glowing effect
- **3D** - Depth perspective
- **Lightning** - Electric highlights
- **Typewriter** - Character by character
- **Explosive** - Burst animation

### 2. Audio Visualizers
- Spectrum analyzer bars
- Circular radial display
- Waveform oscilloscope
- Frequency response curves
- Beat-reactive animations

### 3. 3D Product Showcases
- Phone mockups with video screens
- Rotating product displays
- Camera orbits and zoom
- Material customization
- Environment lighting

---

## Resources

- [Remotion Docs](https://remotion.dev/docs)
- [Remotion Showcase](https://remotion.dev/showcase)
- [Remotion Discord](https://remotion.dev/discord)
- [API Reference](/Users/ali/Desktop/API-Docs/remotion/)

---

## License

This curation is MIT licensed. Individual templates have their own licenses - check each repo before commercial use.

---

**Built for the AI-assisted video creation era.**
