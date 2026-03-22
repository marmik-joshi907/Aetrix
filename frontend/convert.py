import re

with open('stitch_output.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<!-- Sidebar / NavigationDrawer (Desktop) -->')
end = html.find('</main>') + 7

if start == -1 or end < 7:
    print("Could not find start/end")
    exit(1)

jsx = html[start:end]

# Convert HTML comments to JSX comments
jsx = jsx.replace('<!--', '{/*').replace('-->', '*/}')

# Convert class= to className=
jsx = jsx.replace('class=', 'className=')

# Fix self-closing tags (input, img, hr, br)
jsx = re.sub(r'<(input[^>]*?(?<!/))>', r'<\1 />', jsx)
jsx = re.sub(r'<(img[^>]*?(?<!/))>', r'<\1 />', jsx)
jsx = re.sub(r'<(hr[^>]*?(?<!/))>', r'<\1 />', jsx)
jsx = re.sub(r'<(br[^>]*?(?<!/))>', r'<\1 />', jsx)

code = f"""import React from 'react';

export default function SettingsView() {{
  return (
    <div className="flex w-full min-h-screen relative z-0">
      {{/* Wrapper for Stitch UI to isolate it from App.js default layout */}}
      <div className="w-full text-on-background bg-background font-body">
        {jsx}
      </div>
    </div>
  );
}}
"""

with open('src/components/SettingsView.js', 'w', encoding='utf-8') as f:
    f.write(code)
    print("Successfully wrote SettingsView.js")
