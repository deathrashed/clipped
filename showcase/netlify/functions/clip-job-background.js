import { getStore } from '@netlify/blobs';
import { execFile, exec } from 'child_process';
import { promisify } from 'util';
import { readFile, unlink, chmod, mkdir } from 'fs/promises';
import path from 'path';
import fs from 'fs';

const execFileAsync = promisify(execFile);
const execAsync = promisify(exec);

// Binary configuration
// We download binaries to /tmp to avoid Netlify's 50MB zipped Lambda limit
const BIN_DIR = '/tmp/bin';
const FFMPEG = path.join(BIN_DIR, 'ffmpeg');
const YTDLP = path.join(BIN_DIR, 'yt-dlp');

const BINARIES = {
    ffmpeg: {
        url: 'https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/linux-x64',
        path: FFMPEG
    },
    ytdlp: {
        url: 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp',
        path: YTDLP
    }
};

async function ensureBinaries() {
    if (!fs.existsSync(BIN_DIR)) {
        await mkdir(BIN_DIR, { recursive: true });
    }

    for (const [name, info] of Object.entries(BINARIES)) {
        if (!fs.existsSync(info.path)) {
            console.log(`Downloading ${name}...`);
            await execAsync(`curl -L -o "${info.path}" "${info.url}"`);
            await chmod(info.path, 0o755);
            console.log(`${name} ready.`);
        }
    }
}

export const handler = async (event) => {
  const { jobId } = JSON.parse(event.body || '{}');
  if (!jobId) return { statusCode: 400 };

  const store = getStore('clip-jobs');
  await store.set(`${jobId}:status`, 'Initializing Environment...', { ttl: 3600 });

  try {
    await ensureBinaries();

    const paramsJson = await store.get(`${jobId}:params`, { type: 'text' });
    if (!paramsJson) throw new Error("Job params not found");

    const params = JSON.parse(paramsJson);
    const { url, start, end, format, template, fade, platform } = params;

    const fadeDur = fade ? parseFloat(fade) : 0.3;
    const tmpRaw = `/tmp/${jobId}_raw`;

    // Determine if we are rendering video or just audio
    const isVideo = format === 'video' || template;
    const finalExt = isVideo ? 'mp4' : 'mp3';
    const tmpClip = `/tmp/${jobId}_clip.${finalExt}`;

    let sourceFile;

    if (url === 'local') {
        throw new Error("Local file upload directly to background jobs is not supported yet.");
    } else if (url.match(/youtube\.com|youtu\.be/)) {
        await store.set(`${jobId}:status`, 'Extracting audio from YouTube...', { ttl: 3600 });

        // Use node executable context to bypass yt-dlp node limits
        const nodePath = process.execPath;
        const ytdlpCmd = `${YTDLP} --js-runtimes "node:${nodePath}" -x --audio-format mp3 --audio-quality 0 --ffmpeg-location ${BIN_DIR} --no-playlist -o "${tmpRaw}.%(ext)s" "${url}"`;

        await execAsync(ytdlpCmd);
        sourceFile = `${tmpRaw}.mp3`;
    } else {
        await store.set(`${jobId}:status`, 'Downloading source file...', { ttl: 3600 });

        // Use curl to download direct file
        const downloadCmd = `curl -L -o "${tmpRaw}.mp3" "${url}"`;
        await execAsync(downloadCmd);
        sourceFile = `${tmpRaw}.mp3`;
    }

    if (!fs.existsSync(sourceFile)) {
        throw new Error("Failed to download source audio");
    }

    await store.set(`${jobId}:status`, isVideo ? 'Rendering Video...' : 'Extracting Audio Clip...', { ttl: 3600 });

    // Build FFmpeg command
    let ffmpegArgs = ['-i', sourceFile];

    const startTime = start ? parseFloat(start) : 0;
    ffmpegArgs.push('-ss', String(startTime));

    let duration = null;
    if (end) {
        duration = parseFloat(end) - startTime;
        if (duration <= 0) duration = 10;
        ffmpegArgs.push('-t', String(duration));
    }

    if (!isVideo) {
        // Just extract MP3
        ffmpegArgs.push(
            '-af', `afade=t=in:d=${fadeDur},afade=t=out:st=${Math.max(0, (duration||60) - fadeDur)}:d=${fadeDur}`,
            '-c:a', 'libmp3lame', '-q:a', '2',
            tmpClip, '-y'
        );
    } else {
        // Fast Video render using static image + waveform
        ffmpegArgs.push(
            '-filter_complex', `[0:a]showwaves=s=1080x1920:mode=cline:colors=white,format=yuv420p[v];[0:a]afade=t=in:d=${fadeDur},afade=t=out:st=${Math.max(0, (duration||60) - fadeDur)}:d=${fadeDur}[a]`,
            '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            '-c:a', 'aac', '-b:a', '128k',
            tmpClip, '-y'
        );
    }

    await execFileAsync(FFMPEG, ffmpegArgs);

    if (!fs.existsSync(tmpClip)) {
        throw new Error("FFmpeg failed to generate the output file");
    }

    // Store in Blobs
    await store.set(`${jobId}:status`, 'Finalizing...', { ttl: 3600 });
    const outData = await readFile(tmpClip);

    await store.set(`${jobId}:output`, outData, {
        metadata: { mimeType: isVideo ? 'video/mp4' : 'audio/mpeg', extension: finalExt },
        ttl: 3600 // Expire after 1 hour
    });

    await store.set(`${jobId}:status`, 'done', { ttl: 3600 });

    // Cleanup
    if (fs.existsSync(sourceFile)) await unlink(sourceFile);
    if (fs.existsSync(tmpClip)) await unlink(tmpClip);

  } catch (err) {
    console.error(`Job ${jobId} failed:`, err);
    await store.set(`${jobId}:status`, 'error: ' + err.message.slice(0, 200), { ttl: 3600 });
  }

  return { statusCode: 202 }; // Background functions should return 202
};
