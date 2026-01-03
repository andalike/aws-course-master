/**
 * AWS Lambda S3 Event Processor - Node.js
 *
 * This Lambda function demonstrates:
 * - S3 event handling
 * - Processing uploaded files
 * - Image metadata extraction
 * - Generating thumbnails (conceptual)
 * - Cross-service integration (S3 to DynamoDB)
 *
 * Use Case: Processing files uploaded to S3 (images, documents, data files)
 */

const { S3Client, GetObjectCommand, PutObjectCommand, HeadObjectCommand } = require('@aws-sdk/client-s3');
const { DynamoDBClient, PutItemCommand } = require('@aws-sdk/client-dynamodb');
const { marshall } = require('@aws-sdk/util-dynamodb');
const { Readable } = require('stream');

// Initialize AWS clients
const s3Client = new S3Client({});
const dynamoClient = new DynamoDBClient({});

// Configuration from environment variables
const METADATA_TABLE = process.env.METADATA_TABLE || 'file-metadata';
const PROCESSED_PREFIX = process.env.PROCESSED_PREFIX || 'processed/';

/**
 * Convert a readable stream to a buffer
 */
async function streamToBuffer(stream) {
    const chunks = [];
    for await (const chunk of stream) {
        chunks.push(chunk);
    }
    return Buffer.concat(chunks);
}

/**
 * Get file metadata from S3
 */
async function getFileMetadata(bucket, key) {
    const command = new HeadObjectCommand({
        Bucket: bucket,
        Key: key
    });

    const response = await s3Client.send(command);

    return {
        contentType: response.ContentType,
        contentLength: response.ContentLength,
        lastModified: response.LastModified,
        eTag: response.ETag,
        metadata: response.Metadata || {}
    };
}

/**
 * Download file from S3
 */
async function downloadFile(bucket, key) {
    const command = new GetObjectCommand({
        Bucket: bucket,
        Key: key
    });

    const response = await s3Client.send(command);
    const buffer = await streamToBuffer(response.Body);

    return {
        buffer,
        contentType: response.ContentType,
        contentLength: response.ContentLength
    };
}

/**
 * Upload processed file to S3
 */
async function uploadFile(bucket, key, body, contentType, metadata = {}) {
    const command = new PutObjectCommand({
        Bucket: bucket,
        Key: key,
        Body: body,
        ContentType: contentType,
        Metadata: metadata
    });

    return s3Client.send(command);
}

/**
 * Store file metadata in DynamoDB
 */
async function storeMetadata(fileInfo) {
    const item = {
        id: fileInfo.key,
        bucket: fileInfo.bucket,
        filename: fileInfo.filename,
        contentType: fileInfo.contentType,
        size: fileInfo.size,
        processedAt: new Date().toISOString(),
        eventTime: fileInfo.eventTime,
        status: 'processed',
        metadata: JSON.stringify(fileInfo.customMetadata || {})
    };

    const command = new PutItemCommand({
        TableName: METADATA_TABLE,
        Item: marshall(item)
    });

    return dynamoClient.send(command);
}

/**
 * Process an image file (placeholder for actual image processing)
 * In production, you would use sharp, jimp, or another image library
 */
async function processImage(buffer, contentType) {
    console.log('Processing image...');

    // Placeholder: In production, you would:
    // 1. Use sharp or jimp to resize/optimize
    // 2. Generate thumbnails
    // 3. Extract EXIF data

    // For this example, we just return the original buffer
    return {
        processed: buffer,
        thumbnail: null, // Would be a resized version
        metadata: {
            originalSize: buffer.length,
            format: contentType.split('/')[1]
        }
    };
}

/**
 * Process a text/JSON file
 */
async function processTextFile(buffer, contentType) {
    console.log('Processing text file...');

    const content = buffer.toString('utf8');

    return {
        lineCount: content.split('\n').length,
        wordCount: content.split(/\s+/).filter(w => w.length > 0).length,
        charCount: content.length,
        isJson: isValidJson(content)
    };
}

/**
 * Check if string is valid JSON
 */
function isValidJson(str) {
    try {
        JSON.parse(str);
        return true;
    } catch {
        return false;
    }
}

/**
 * Determine file type and process accordingly
 */
async function processFile(bucket, key, contentType) {
    console.log(`Processing file: ${key} (${contentType})`);

    // Download the file
    const file = await downloadFile(bucket, key);

    let processingResult = {};

    // Process based on content type
    if (contentType.startsWith('image/')) {
        processingResult = await processImage(file.buffer, contentType);
    } else if (contentType.startsWith('text/') || contentType === 'application/json') {
        processingResult = await processTextFile(file.buffer, contentType);
    } else {
        console.log(`Unsupported content type: ${contentType}, storing metadata only`);
        processingResult = { type: 'unsupported' };
    }

    return {
        originalSize: file.contentLength,
        contentType,
        processingResult
    };
}

/**
 * Main Lambda handler
 */
exports.handler = async (event, context) => {
    console.log('Received event:', JSON.stringify(event, null, 2));
    console.log('Function:', context.functionName);
    console.log('Request ID:', context.awsRequestId);

    const results = [];
    const errors = [];

    // Process each S3 event record
    for (const record of event.Records) {
        try {
            // Skip non-S3 events
            if (record.eventSource !== 'aws:s3') {
                console.log('Skipping non-S3 event:', record.eventSource);
                continue;
            }

            // Extract S3 event details
            const bucket = record.s3.bucket.name;
            const key = decodeURIComponent(record.s3.object.key.replace(/\+/g, ' '));
            const size = record.s3.object.size;
            const eventTime = record.eventTime;
            const eventName = record.eventName;

            console.log(`Processing: s3://${bucket}/${key}`);
            console.log(`Event: ${eventName}, Size: ${size} bytes`);

            // Skip if file is already in processed folder (prevent loops)
            if (key.startsWith(PROCESSED_PREFIX)) {
                console.log('Skipping already processed file');
                continue;
            }

            // Skip delete events
            if (eventName.startsWith('ObjectRemoved')) {
                console.log('Skipping delete event');
                continue;
            }

            // Get file metadata
            const metadata = await getFileMetadata(bucket, key);
            console.log('File metadata:', JSON.stringify(metadata, null, 2));

            // Process the file
            const processingResult = await processFile(bucket, key, metadata.contentType);

            // Store metadata in DynamoDB
            const fileInfo = {
                bucket,
                key,
                filename: key.split('/').pop(),
                contentType: metadata.contentType,
                size,
                eventTime,
                customMetadata: {
                    ...metadata.metadata,
                    ...processingResult.processingResult
                }
            };

            await storeMetadata(fileInfo);
            console.log('Metadata stored in DynamoDB');

            // Optionally copy processed file to processed folder
            // This is useful for triggering downstream processes
            const processedKey = `${PROCESSED_PREFIX}${key}`;
            // await uploadFile(bucket, processedKey, processedBuffer, metadata.contentType);

            results.push({
                key,
                status: 'success',
                size,
                contentType: metadata.contentType,
                processingResult
            });

            console.log(`Successfully processed: ${key}`);

        } catch (error) {
            console.error(`Error processing record:`, error);
            errors.push({
                record: record.s3?.object?.key || 'unknown',
                error: error.message
            });
        }
    }

    // Return summary
    const response = {
        statusCode: errors.length === 0 ? 200 : 207,
        body: {
            message: 'Processing complete',
            processed: results.length,
            errors: errors.length,
            results,
            errors: errors.length > 0 ? errors : undefined
        }
    };

    console.log('Response:', JSON.stringify(response, null, 2));
    return response;
};

// For local testing
if (require.main === module) {
    // Mock S3 event
    const mockEvent = {
        Records: [
            {
                eventSource: 'aws:s3',
                eventName: 'ObjectCreated:Put',
                eventTime: new Date().toISOString(),
                s3: {
                    bucket: {
                        name: 'test-bucket'
                    },
                    object: {
                        key: 'uploads/test-file.json',
                        size: 1024
                    }
                }
            }
        ]
    };

    const mockContext = {
        functionName: 's3-processor-nodejs',
        awsRequestId: 'test-request-id'
    };

    console.log('Local test - mock event:');
    console.log(JSON.stringify(mockEvent, null, 2));
    console.log('\nNote: Actual processing requires AWS credentials and real S3 bucket');
}
