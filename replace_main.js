const fs = require('fs');
const f = 'src/styles/main.css';

let content = fs.readFileSync(f, 'utf8');

// Replace specific colored alphas with black
['232,184,75','155,127,245','62,212,196','255,107,107','93,219,146'].forEach(c => {
  content = content.replace(new RegExp(`rgba\\(${c},([\\d.]+)\\)`, 'g'), 'rgba(0,0,0,$1)');
});

// Replace old hex colors with black
content = content.replace(/#(e8b84b|9b7ff5|3ed4c4|ff6b6b|5ddb92)/gi, '#000000'); // 

// Fix root variables to monochrome exactly
content = content.replace(/--bg: #080809;/g, '--bg: #ffffff;');
content = content.replace(/--bg2: #0f0f12;/g, '--bg2: #fafafa;');
content = content.replace(/--bg3: #161619;/g, '--bg3: #f5f5f5;');
content = content.replace(/--surface: #1c1c21;/g, '--surface: #ffffff;');
content = content.replace(/--border: #252530;/g, '--border: #eaeaea;');
content = content.replace(/--border2: #333340;/g, '--border2: #dddddd;');
content = content.replace(/--text: #ece8e0;/g, '--text: #000000;');
content = content.replace(/--muted: #888699;/g, '--muted: #666666;');
content = content.replace(/--dim: #4a4858;/g, '--dim: #999999;');
content = content.replace(/--gold: #e8b84b;/g, '--gold: #000000;');
content = content.replace(/--gold2: #f5d584;/g, '--gold2: #333333;');
content = content.replace(/--gold3: #c99b2e;/g, '--gold3: #111111;');
content = content.replace(/--violet: #9b7ff5;/g, '--violet: #000000;');
content = content.replace(/--violet2: #bfaaff;/g, '--violet2: #222222;');
content = content.replace(/--teal: #3ed4c4;/g, '--teal: #000000;');
content = content.replace(/--teal2: #85ede5;/g, '--teal2: #222222;');
content = content.replace(/--coral: #ff6b6b;/g, '--coral: #000000;');
content = content.replace(/--green: #5ddb92;/g, '--green: #000000;');

// Make Outfit the primary typography
content = content.replace(/--ff-display: 'Inter', 'Outfit', sans-serif;/g, "--ff-display: 'Outfit', 'Inter', sans-serif;");
content = content.replace(/--ff-body: 'Inter', 'Outfit', sans-serif;/g, "--ff-body: 'Outfit', 'Inter', sans-serif;");

// Invert white alpha to black alpha for readability on white bg
content = content.replace(/rgba\(255,255,255,([\d.]+)\)/g, 'rgba(0,0,0,$1)');

fs.writeFileSync(f, content);
console.log('Main.css colors replaced successfully!');
