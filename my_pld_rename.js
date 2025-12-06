const jsonld = require('jsonld');
const fs = require('fs').promises;

async function expandJsonLd() {
  // Load JSON-LD from file
  const fileContent = await fs.readFile('opendata-uredni-deska (2).jsonld', 'utf8');
  const loadedJsonLd = JSON.parse(fileContent);

  // expand a document, removing its context
  const expanded = await jsonld.expand(loadedJsonLd);
  console.log('Expanded:', JSON.stringify(expanded, null, 2));

  // Save expanded JSON-LD to file
  await fs.writeFile('expanded.jsonld', JSON.stringify(expanded, null, 2), 'utf8');
  console.log('Saved expanded JSON-LD to expanded.jsonld');
}

expandJsonLd().catch(console.error);