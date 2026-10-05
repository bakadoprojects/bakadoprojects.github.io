from pathlib import Path
import re
from collections import Counter

path = Path('index.html')
original = path.read_text(encoding='utf-8')
assert 'id="hakkimizda"' not in original, 'About section already exists'
assert '<title>BAKADO PROJE</title>' in original
nav_old = '<nav class="menu"><a href="#hizmetler">'
assert original.count(nav_old) == 1
start = '<!-- PARTNERS-INTEGRATED-START -->'
end = '<!-- PARTNERS-INTEGRATED-END -->'
assert original.count(start) == 1 and original.count(end) == 1
pstart = original.index(start)
pend = original.index(end, pstart) + len(end)
partners = original[pstart:pend]
assert '<section id="cozum-ortaklari">' in partners
updated = original[:pstart] + original[pend:]
anchor = '<section id="teklif" class="inquiry">'
assert updated.count(anchor) == 1
updated = updated.replace(anchor, partners + '\n' + anchor, 1)
updated = updated.replace(nav_old, '<nav class="menu"><a href="#hakkimizda">Hakkımızda</a><a href="#hizmetler">', 1)
hero_image = re.search(r'url\("(data:image/[^\"]+)"\)', original).group(1)
about = '''<section id="hakkimizda" class="section bakado-about">
  <div class="w bakado-about-grid">
    <div class="bakado-about-copy">
      <div class="tag">Hakkımızda</div>
      <h2>Mekâna karakter.</h2>
      <p><strong>BAKADO PROJE</strong>, Antalya merkezli iç mekan tasarımı, özel mobilya ve uygulama markasıdır. Estetiği işlevle buluşturarak ihtiyaçlarınıza ve yaşamınıza uygun mekânlar tasarlarız. Keşiften uygulamaya kadar her aşamada detaylara ve açık iletişime önem veririz.</p>
    </div>
    <div class="bakado-about-image"><img src="HERO_SOURCE" alt="BAKADO mekan tasarımından bir detay" loading="lazy"></div>
  </div>
</section>'''.replace('HERO_SOURCE', hero_image)
main_start = updated.index('<main>')
hero_end = updated.index('</section>', main_start) + len('</section>')
updated = updated[:hero_end] + '\n' + about + '\n' + updated[hero_end:]
css = '''
/* BAKADO ABOUT ADDITION: scoped to the new section and menu fit only */
.bakado-about{background:var(--p);color:var(--i)}
.bakado-about-grid{display:grid;grid-template-columns:1.2fr .8fr;gap:80px;align-items:center}
.bakado-about-copy .tag{color:var(--g);margin-bottom:20px}
.bakado-about-copy h2{font-size:clamp(38px,4.5vw,58px);line-height:1.06;letter-spacing:-.045em;margin:0 0 25px}
.bakado-about-copy p{font-size:16px;line-height:1.85;color:var(--m);max-width:580px;margin:0}
.bakado-about-copy strong{color:var(--i)}
.bakado-about-image{position:relative;isolation:isolate;margin-right:14px}
.bakado-about-image img{height:320px;object-fit:cover;object-position:75% center}
.bakado-about-image:after{content:"";position:absolute;inset:14px -14px -14px 14px;border:1px solid var(--g);z-index:-1}
.nav .menu{gap:clamp(12px,1.7vw,24px);flex-wrap:nowrap}
.nav .menu a{white-space:nowrap}
@media(min-width:761px) and (max-width:1000px){.nav .menu{font-size:10px;gap:12px;letter-spacing:.05em}}
@media(max-width:760px){.bakado-about-grid{grid-template-columns:1fr;gap:32px}.bakado-about-copy p{font-size:15px}.bakado-about-image img{height:260px}}
/* BAKADO ABOUT ADDITION END */
'''
assert updated.count('</style>') == 1
updated = updated.replace('</style>', css + '</style>', 1)
old_sections = re.findall(r'<section\b.*?</section>', original, re.S)
assert len(old_sections) == 8, f'Unexpected original section count: {len(old_sections)}'
for section in old_sections:
    assert updated.count(section) == 1, 'An original section was altered or lost'
for script in re.findall(r'<script\b.*?</script>', original, re.S):
    assert script in updated, 'An original script changed'
old_style = re.search(r'<style>(.*?)</style>', original, re.S).group(1)
new_style = re.search(r'<style>(.*?)</style>', updated, re.S).group(1)
assert new_style == old_style + css
assert re.findall(r'<meta\b[^>]*>', original) == re.findall(r'<meta\b[^>]*>', updated)
assert re.findall(r'<title>.*?</title>', original) == re.findall(r'<title>.*?</title>', updated)
old_images = Counter(re.findall(r'data:image/[^\s\"\x27<>]+', original))
new_images = Counter(re.findall(r'data:image/[^\s\"\x27<>]+', updated))
expected = old_images.copy(); expected[hero_image] += 1
assert new_images == expected, 'Existing image data changed'
ids = re.findall(r'<section\b[^>]*\bid="([^"]+)"', updated)
assert ids == ['hakkimizda','hizmetler','projeler','surec','cozum-ortaklari','teklif','iletisim'], ids
menu = re.search(r'<nav class="menu">(.*?)</nav>', updated, re.S).group(1)
assert re.findall(r'href="#([^\"]+)"', menu) == ids
path.write_text(updated, encoding='utf-8')
print('Added short About section; aligned menu and section order.')
print('Preserved all 8 original sections, all original CSS/JS/SEO/image data.')
print('Section order:', ids)
