import { getStore } from '@netlify/blobs';

export const handler = async (event) => {
  const jobId = event.queryStringParameters?.job;
  if (!jobId) return { statusCode: 400, body: 'Missing job ID' };

  const store = getStore('clip-jobs');

  // get blob data
  const blobInfo = await store.getWithMetadata(`${jobId}:output`, { type: 'arrayBuffer' });
  if (!blobInfo || !blobInfo.data) {
      return { statusCode: 404, body: 'File not found or expired' };
  }

  const mimeType = blobInfo.metadata?.mimeType || 'audio/mpeg';
  const ext = blobInfo.metadata?.extension || 'mp3';

  return {
    statusCode: 200,
    headers: {
      'Content-Type': mimeType,
      'Content-Disposition': `attachment; filename="clip-${jobId.slice(0,8)}.${ext}"`,
    },
    body: Buffer.from(blobInfo.data).toString('base64'),
    isBase64Encoded: true,
  };
};
