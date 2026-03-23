const fs = require('fs');
const files = [
  'src/styles/components.css',
  'src/styles/animations.css',
  'src/styles/learn.css',
  'index.html'
];
files.forEach(f => {
  let content = fs.readFileSync(f, 'utf8');
  // Replace specific colored alphas with black
  ['232,184,75','155,127,245','62,212,196','255,107,107','93,219,146'].forEach(c => {
    content = content.replace(new RegExp(`rgba\\(${c},([\\d.]+)\\)`, 'g'), 'rgba(0,0,0,$1)');
  });
  // Replace old hex colors with black
  content = content.replace(/#(e8b84b|9b7ff5|3ed4c4|ff6b6b|5ddb92)/gi, '#000000');
  // Invert white alpha to black alpha for readability on white bg
  content = content.replace(/rgba\(255,255,255,([\d.]+)\)/g, 'rgba(0,0,0,$1)');
  
  // Specific backgrounds in components.css
  content = content.replace(/background: linear-gradient\(135deg, var\(--gold\), var\(--violet\)\);/g, 'background: #000000;');
  content = content.replace(/background: linear-gradient\(135deg, var\(--violet\), #7c5cdb\);/g, 'background: #000000;');
  
  fs.writeFileSync(f, content);
});
console.log('Colors replaced successfully!');
