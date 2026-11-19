const fs = require('fs');
const html = fs.readFileSync('frontend/index.html', 'utf8');
// Extract the babel script
const startMarker = 'type="text/babel">';
const startIdx = html.indexOf(startMarker);
if (startIdx === -1) { console.error('No babel script found!'); process.exit(1); }
const scriptStart = startIdx + startMarker.length;
const scriptEnd = html.lastIndexOf('</script>');
const script = html.slice(scriptStart, scriptEnd);

console.log('Script length:', script.length, 'chars');
console.log('Script lines:', script.split('\n').length);

// Check backtick balance
let bt = 0;
for (let c of script) if (c === '`') bt++;
console.log('Backtick count:', bt, bt % 2 === 0 ? '✓ EVEN' : '✗ ODD!');

// Check for suspicious patterns
const lines = script.split('\n');
let issues = [];

for (let i = 0; i < lines.length; i++) {
  const l = lines[i];
  // Multi-word unquoted object keys
  if (l.match(/^\s+[A-Z][a-z]+ [A-Z][a-z]+\s*:/)) {
    issues.push('Line ' + (i + 1) + ': possible unquoted compound key: ' + l.trim());
  }
}

if (issues.length > 0) {
  console.log('\nPotential issues:');
  issues.forEach(i => console.log(' ', i));
} else {
  console.log('✓ No suspicious patterns found');
}

// Count function and class balance
let opens = (script.match(/\{/g) || []).length;
let closes = (script.match(/\}/g) || []).length;
console.log('Braces: { =', opens, ', } =', closes, opens === closes ? '✓ BALANCED' : '✗ UNBALANCED! diff=' + (opens - closes));

let parens_o = (script.match(/\(/g) || []).length;
let parens_c = (script.match(/\)/g) || []).length;
console.log('Parens: ( =', parens_o, ', ) =', parens_c, parens_o === parens_c ? '✓ BALANCED' : '✗ UNBALANCED! diff=' + (parens_o - parens_c));

console.log('\nAll checks complete!');
