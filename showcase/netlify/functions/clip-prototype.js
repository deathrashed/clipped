import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs';

const execAsync = promisify(exec);

// Cold start initialization
let isInitialized = false;

async function ensureBinaries() {
  if (isInitialized) return;
  const binDir = '/tmp/bin';
  
  if (!fs.existsSync(binDir)) {
    fs.mkdirSync(binDir, { recursive: true });
  }

  const ytdlpPath = path.join(binDir, 'yt-dlp');
  const ffmpegPath = path.join(binDir, 'ffmpeg');

  // Download yt-dlp if not exists
  if (!fs.existsSync(ytdlpPath)) {
    console.log("Downloading yt-dlp...");
    await execAsync(`curl -sL https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux -o ${ytdlpPath}`);
    await execAsync(`chmod +x ${ytdlpPath}`);
  }

  // Download ffmpeg static build if not exists
  if (!fs.existsSync(ffmpegPath)) {
    console.log("Downloading static ffmpeg...");
    await execAsync(`curl -sL https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffmpeg-linux-x64 -o ${ffmpegPath}`);
    await execAsync(`chmod +x ${ffmpegPath}`);
  }

  isInitialized = true;
}

export const handler = async (event, context) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  let body;
  try {
    body = JSON.parse(event.body);
  } catch (err) {
    return { statusCode: 400, body: 'Invalid JSON' };
  }

  const { url, start = 0, end = 30 } = body;
  if (!url) {
    return { statusCode: 400, body: 'Missing YouTube URL' };
  }

  try {
    // Ensure binaries are downloaded (runs only on cold start)
    await ensureBinaries();

    const binDir = '/tmp/bin';
    const ytdlp = path.join(binDir, 'yt-dlp');
    const ffmpeg = path.join(binDir, 'ffmpeg');
    const id = Math.random().toString(36).substring(7);
    const outPath = `/tmp/clip_${id}.mp3`;

    console.log(`Downloading audio from ${url} (start: ${start}, end: ${end})`);
    
    // First, get the direct stream URL
    const nodePath = process.execPath;
    const ytdlpCmd = `export PATH="$PATH:${binDir}" && ${ytdlp} --js-runtimes "node:${nodePath}" -x -g "${url}"`;
    
    const { stdout: streamUrlRaw } = await execAsync(ytdlpCmd, { timeout: 10000 });
    const streamUrl = streamUrlRaw.trim();
    
    if (!streamUrl) {
        throw new Error('Could not extract direct stream URL');
    }

    // Now pipe the stream into ffmpeg
    const ffmpegCmd = `export PATH="$PATH:${binDir}" && ${ffmpeg} -ss ${start} -to ${end} -i "${streamUrl}" -vn -c:a libmp3lame -q:a 2 -y "${outPath}"`;
    
    await execAsync(ffmpegCmd, { timeout: 15000 }); // Netlify functions max timeout is 10-26s
    
    if (!fs.existsSync(outPath)) {
      throw new Error('Output file was not created');
    }

    const audioBuffer = fs.readFileSync(outPath);
    const base64Audio = audioBuffer.toString('base64');
    fs.unlinkSync(outPath);

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'audio/mpeg',
        'Content-Disposition': `attachment; filename="clip_${id}.mp3"`,
      },
      body: base64Audio,
      isBase64Encoded: true,
    };
  } catch (error) {
    console.error('Extraction failed:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to process clip', details: error.message }),
    };
  }
};
