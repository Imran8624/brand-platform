const fs = require('fs');
const html = fs.readFileSync('frontend/index.html', 'utf8');
const start = html.indexOf('type="text/babel"');
const scriptStart = html.indexOf('>', start) + 1;
const scriptEnd = html.lastIndexOf('</script>');
const script = html.slice(scriptStart, scriptEnd);
const lines = script.split('\n');

console.log('=== Scanning for potential issues ===\n');

// 1. Check for JSX comments that use // inside JSX (should use {/* */})
// 2. Check for unmatched backticks
let backtickCount = 0;
let inStr = false;
let strChar = '';
for (let i = 0; i < script.length; i++) {
  const c = script[i];
  if (!inStr && (c === '"' || c === "'")) { inStr = true; strChar = c; }
  else if (inStr && c === strChar && script[i-1] !== '\\') { inStr = false; }
  else if (!inStr && c === '`') backtickCount++;
}
console.log('Backtick count (should be even):', backtickCount, backtickCount % 2 === 0 ? '✓ EVEN' : '✗ ODD - UNCLOSED TEMPLATE LITERAL!');

// 3. Check for arrow functions with TypeScript type annotations that might fail
let tsAnnotations = [];
for (let i = 0; i < lines.length; i++) {
  const l = lines[i];
  if (l.match(/\([\w,\s]*:\s*(string|number|boolean|any|React\.)/)) {
    tsAnnotations.push({ line: i+1, text: l.trim() });
  }
}
console.log('\nTypeScript parameter annotations found:', tsAnnotations.length);
tsAnnotations.slice(0, 5).forEach(a => console.log('  Line', a.line, ':', a.text.substring(0, 80)));

// 4. Check for JSX with angle brackets that might be misread
let typeGenerics = [];
for (let i = 0; i < lines.length; i++) {
  const l = lines[i];
  if (l.match(/useState<[A-Z]/) || l.match(/useRef<[A-Z]/)) {
    typeGenerics.push({ line: i+1, text: l.trim() });
  }
}
console.log('\nTypeScript generics (useState<T>, useRef<T>) found:', typeGenerics.length);
typeGenerics.slice(0, 10).forEach(a => console.log('  Line', a.line, ':', a.text.substring(0, 80)));

// 5. Look for interface/type declarations
let interfaces = [];
for (let i = 0; i < lines.length; i++) {
  const l = lines[i];
  if (l.match(/^\s*(interface|type\s+\w+\s*=|enum\s)/)) {
    interfaces.push({ line: i+1, text: l.trim() });
  }
}
console.log('\nTypeScript interfaces/types found:', interfaces.length);
interfaces.forEach(a => console.log('  Line', a.line, ':', a.text.substring(0, 80)));

// 6. Check for async/await issues
let asyncIssues = [];
for (let i = 0; i < lines.length; i++) {
  const l = lines[i];
  if (l.match(/^\s*async\s+\w+\s*\(/) && !l.match(/function|=>/)) {
    asyncIssues.push({ line: i+1, text: l.trim() });
  }
}
console.log('\nAsync function declarations:', asyncIssues.length);
asyncIssues.slice(0, 5).forEach(a => console.log('  Line', a.line, ':', a.text.substring(0, 80)));

// 7. Check for <> fragment shorthand that might cause issues
let fragments = 0;
for (let i = 0; i < lines.length; i++) {
  if (lines[i].includes('<>') || lines[i].includes('</>')) fragments++;
}
console.log('\nLines with <> fragment shorthand:', fragments);

// 8. Check balanced JSX braces in JSX expressions
console.log('\n=== Done ===');
