const jsonld = require('jsonld');
const fs = require('fs').promises;
const path = require('path');
const ProgressBar = require('progress');


const START_DIR = './data/nkod/distributions'; 
const FILE_PREFIX = 'distribution';
const ERROR_LOG_FILE = 'failed_files_log.txt';

/**
 * Processes a single JSON-LD file by loading it, expanding it,
 * and saving the expanded result to a new file.
 * @param {string} filePath - The full path to the JSON-LD file.
 */
async function processJsonLdFile(filePath) {
  try {
    const fileContent = await fs.readFile(filePath, 'utf8');
    const loadedJsonLd = JSON.parse(fileContent);
    const expanded = await jsonld.expand(loadedJsonLd);

    const dirName = path.dirname(filePath);
    const baseName = path.basename(filePath, path.extname(filePath));
    const outputFileName = `${baseName}_expanded.jsonld`;
    const outputFilePath = path.join(dirName, outputFileName);
    await fs.writeFile(outputFilePath, JSON.stringify(expanded, null, 2), 'utf8');
    
    return { success: true, filePath: filePath }; 

  } catch (error) {
    const logEntry = `${filePath}\n`;
    await fs.appendFile(ERROR_LOG_FILE, logEntry, 'utf8');
    
    return { success: false, filePath: filePath, error: error.message };
  }
}

/**
 * Traverses directories, finds files, and processes them sequentially with a progress bar.
 */
async function expandJsonLdSequentiallyWithProgress() {
  console.log(`Starting sequential search in: ${START_DIR}`);
  
  try {
    const allFiles = await fs.readdir(START_DIR, { 
      recursive: true, 
      withFileTypes: true 
    });

    const jsonLdFilesToProcess = [];

    for (const dirent of allFiles) {
      if (dirent.isFile() && 
          dirent.name.startsWith(FILE_PREFIX) && 
          dirent.name.endsWith('.jsonld')) {
        
        const fullPath = path.join(dirent.path || START_DIR, dirent.name);
        jsonLdFilesToProcess.push(fullPath);
      }
    }
    
    const totalFiles = jsonLdFilesToProcess.length;
    console.log(`\nFound ${totalFiles} files matching the criteria.`);
    if (totalFiles === 0) return;

    const bar = new ProgressBar('Processing [:bar] :current/:total :percent :etas | File: :file', {
      total: totalFiles,
      width: 40,
      clear: true
    });

    let failedCount = 0;
    
    for (const filePath of jsonLdFilesToProcess) {
      bar.render({ file: path.basename(filePath) }); 
      const result = await processJsonLdFile(filePath);
      
      if (result.success) {
        // console.log(`\n✅ Success: ${path.basename(filePath)}`);
      } else {
        console.error(`\n❌ Failed: ${path.basename(filePath)}. Logged to ${ERROR_LOG_FILE}`);
        failedCount++;
      }
      
      bar.tick({ file: path.basename(filePath) });
    }

    console.log('\n---');
    if (failedCount > 0) {
      console.log(`⚠️ Completed with ${failedCount} failures. Check ${ERROR_LOG_FILE} for details.`);
    }
    console.log('✨ All file processing complete.');

  } catch (err) {
    console.error(`An error occurred during directory traversal or setup:`, err);
  }
}


expandJsonLdSequentiallyWithProgress().catch(console.error);
