import functools
import bleach
from bs4 import BeautifulSoup
from bleach.css_sanitizer import CSSSanitizer
from bleach.linkifier import LinkifyFilter
from functools import partial
from .get import *
from os import path, environ
import re
from mistletoe import markdown
from json import loads, dump
from random import random, choice
import signal
import time
import requests

TLDS = ('aaa','aarp','abarth','abb','abbott','abbvie','abc','able','abogado','abudhabi','ac','academy','accenture','accountant','accountants','aco','actor','ad','adac','ads','adult','ae','aeg','aero','aetna','af','afl','africa','ag','agakhan','agency','ai','aig','airbus','airforce','airtel','akdn','al','alfaromeo','alibaba','alipay','allfinanz','allstate','ally','alsace','alstom','am','amazon','americanexpress','americanfamily','amex','amfam','amica','amsterdam','analytics','android','anquan','anz','ao','aol','apartments','app','apple','aq','aquarelle','ar','arab','aramco','archi','army','arpa','art','arte','as','asda','asia','associates','at','athleta','attorney','au','auction','audi','audible','audio','auspost','author','auto','autos','avianca','aw','aws','ax','axa','az','azure','ba','baby','baidu','banamex','bananarepublic','band','bank','bar','barcelona','barclaycard','barclays','barefoot','bargains','baseball','basketball','bauhaus','bayern','bb','bbc','bbt','bbva','bcg','bcn','bd','be','beats','beauty','beer','bentley','berlin','best','bestbuy','bet','bf','bg','bh','bharti','bi','bible','bid','bike','bing','bingo','bio','biz','bj','black','blackfriday','blockbuster','blog','bloomberg','blue','bm','bms','bmw','bn','bnpparibas','bo','boats','boehringer','bofa','bom','bond','boo','book','booking','bosch','bostik','boston','bot','boutique','box','br','bradesco','bridgestone','broadway','broker','brother','brussels','bs','bt','bugatti','build','builders','business','buy','buzz','bv','bw','by','bz','bzh','ca','cab','cafe','cal','call','calvinklein','cam','camera','camp','cancerresearch','canon','capetown','capital','capitalone','car','caravan','cards','care','career','careers','cars','casa','case','cash','casino','cat','catering','catholic','cba','cbn','cbre','cbs','cc','cd','center','ceo','cern','cf','cfa','cfd','cg','ch','chanel','channel','charity','chase','chat','cheap','chintai','christmas','chrome','church','ci','cipriani','circle','cisco','citadel','citi','citic','city','cityeats','ck','cl','claims','cleaning','click','clinic','clinique','clothing','cloud','club','clubmed','cm','cn','co','coach','codes','coffee','college','cologne','com','comcast','commbank','community','company','compare','computer','comsec','condos','construction','consulting','contact','contractors','cooking','cookingchannel','cool','coop','corsica','country','coupon','coupons','courses','cpa','cr','credit','creditcard','creditunion','cricket','crown','crs','cruise','cruises','cu','cuisinella','cv','cw','cx','cy','cymru','cyou','cz','dabur','dad','dance','data','date','dating','datsun','day','dclk','dds','de','deal','dealer','deals','degree','delivery','dell','deloitte','delta','democrat','dental','dentist','desi','design','dev','dhl','diamonds','diet','digital','direct','directory','discount','discover','dish','diy','dj','dk','dm','dnp','do','docs','doctor','dog','domains','dot','download','drive','dtv','dubai','dunlop','dupont','durban','dvag','dvr','dz','earth','eat','ec','eco','edeka','edu','education','ee','eg','email','emerck','energy','engineer','engineering','enterprises','epson','equipment','er','ericsson','erni','es','esq','estate','et','etisalat','eu','eurovision','eus','events','exchange','expert','exposed','express','extraspace','fage','fail','fairwinds','faith','family','fan','fans','farm','farmers','fashion','fast','fedex','feedback','ferrari','ferrero','fi','fiat','fidelity','fido','film','final','finance','financial','fire','firestone','firmdale','fish','fishing','fit','fitness','fj','fk','flickr','flights','flir','florist','flowers','fly','fm','fo','foo','food','foodnetwork','football','ford','forex','forsale','forum','foundation','fox','fr','free','fresenius','frl','frogans','frontdoor','frontier','ftr','fujitsu','fun','fund','furniture','futbol','fyi','ga','gal','gallery','gallo','gallup','game','games','gap','garden','gay','gb','gbiz','gd','gdn','ge','gea','gent','genting','george','gf','gg','ggee','gh','gi','gift','gifts','gives','giving','gl','glass','gle','global','globo','gm','gmail','gmbh','gmo','gmx','gn','godaddy','gold','goldpoint','golf','goo','goodyear','goog','google','gop','got','gov','gp','gq','gr','grainger','graphics','gratis','green','gripe','grocery','group','gs','gt','gu','guardian','gucci','guge','guide','guitars','guru','gw','gy','hair','hamburg','hangout','haus','hbo','hdfc','hdfcbank','health','healthcare','help','helsinki','here','hermes','hgtv','hiphop','hisamitsu','hitachi','hiv','hk','hkt','hm','hn','hockey','holdings','holiday','homedepot','homegoods','homes','homesense','honda','horse','hospital','host','hosting','hot','hoteles','hotels','hotmail','house','how','hr','hsbc','ht','hu','hughes','hyatt','hyundai','ibm','icbc','ice','icu','id','ie','ieee','ifm','ikano','il','im','imamat','imdb','immo','immobilien','in','inc','industries','infiniti','info','ing','ink','institute','insurance','insure','int','international','intuit','investments','io','ipiranga','iq','ir','irish','is','ismaili','ist','istanbul','it','itau','itv','jaguar','java','jcb','je','jeep','jetzt','jewelry','jio','jll','jm','jmp','jnj','jo','jobs','joburg','jot','joy','jp','jpmorgan','jprs','juegos','juniper','kaufen','kddi','ke','kerryhotels','kerrylogistics','kerryproperties','kfh','kg','kh','ki','kia','kids','kim','kinder','kindle','kitchen','kiwi','km','kn','koeln','komatsu','kosher','kp','kpmg','kpn','kr','krd','kred','kuokgroup','kw','ky','kyoto','kz','la','lacaixa','lamborghini','lamer','lancaster','lancia','land','landrover','lanxess','lasalle','lat','latino','latrobe','law','lawyer','lb','lc','lds','lease','leclerc','lefrak','legal','lego','lexus','lgbt','li','lidl','life','lifeinsurance','lifestyle','lighting','like','lilly','limited','limo','lincoln','linde','link','lipsy','live','living','lk','llc','llp','loan','loans','locker','locus','loft','lol','london','lotte','lotto','love','lpl','lplfinancial','lr','ls','lt','ltd','ltda','lu','lundbeck','luxe','luxury','lv','ly','ma','macys','madrid','maif','maison','makeup','man','management','mango','map','market','marketing','markets','marriott','marshalls','maserati','mattel','mba','mc','mckinsey','md','me','med','media','meet','melbourne','meme','memorial','men','menu','merckmsd','mg','mh','miami','microsoft','mil','mini','mint','mit','mitsubishi','mk','ml','mlb','mls','mm','mma','mn','mo','mobi','mobile','moda','moe','moi','mom','monash','money','monster','mormon','mortgage','moscow','moto','motorcycles','mov','movie','mp','mq','mr','ms','msd','mt','mtn','mtr','mu','museum','music','mutual','mv','mw','mx','my','mz','na','nab','nagoya','name','natura','navy','nba','nc','ne','nec','net','netbank','netflix','network','neustar','new','news','next','nextdirect','nexus','nf','nfl','ng','ngo','nhk','ni','nico','nike','nikon','ninja','nissan','nissay','nl','no','nokia','northwesternmutual','norton','now','nowruz','nowtv','np','nr','nra','nrw','ntt','nu','nyc','nz','obi','observer','office','okinawa','olayan','olayangroup','oldnavy','ollo','om','omega','one','ong','onl','online','ooo','open','oracle','orange','org','organic','origins','osaka','otsuka','ott','ovh','pa','page','panasonic','paris','pars','partners','parts','party','passagens','pay','pccw','pe','pet','pf','pfizer','pg','ph','pharmacy','phd','philips','phone','photo','photography','photos','physio','pics','pictet','pictures','pid','pin','ping','pink','pioneer','pizza','pk','pl','place','play','playstation','plumbing','plus','pm','pn','pnc','pohl','poker','politie','porn','post','pr','pramerica','praxi','press','prime','pro','prod','productions','prof','progressive','promo','properties','property','protection','pru','prudential','ps','pt','pub','pw','pwc','py','qa','qpon','quebec','quest','racing','radio','re','read','realestate','realtor','realty','recipes','red','redstone','redumbrella','rehab','reise','reisen','reit','reliance','ren','rent','rentals','repair','report','republican','rest','restaurant','review','reviews','rexroth','rich','richardli','ricoh','ril','rio','rip','ro','rocher','rocks','rodeo','rogers','room','rs','rsvp','ru','rugby','ruhr','run','rw','rwe','ryukyu','sa','saarland','safe','safety','sakura','sale','salon','samsclub','samsung','sandvik','sandvikcoromant','sanofi','sap','sarl','sas','save','saxo','sb','sbi','sbs','sc','sca','scb','schaeffler','schmidt','scholarships','school','schule','schwarz','science','scot','sd','se','search','seat','secure','security','seek','select','sener','services','ses','seven','sew','sex','sexy','sfr','sg','sh','shangrila','sharp','shaw','shell','shia','shiksha','shoes','shop','shopping','shouji','show','showtime','si','silk','sina','singles','site','sj','sk','ski','skin','sky','skype','sl','sling','sm','smart','smile','sn','sncf','so','soccer','social','softbank','software','sohu','solar','solutions','song','sony','soy','spa','space','sport','spot','sr','srl','ss','st','stada','staples','star','statebank','statefarm','stc','stcgroup','stockholm','storage','store','stream','studio','study','style','su','sucks','supplies','supply','support','surf','surgery','suzuki','sv','swatch','swiss','sx','sy','sydney','systems','sz','tab','taipei','talk','taobao','target','tatamotors','tatar','tattoo','tax','taxi','tc','tci','td','tdk','team','tech','technology','tel','temasek','tennis','teva','tf','tg','th','thd','theater','theatre','tiaa','tickets','tienda','tiffany','tips','tires','tirol','tj','tjmaxx','tjx','tk','tkmaxx','tl','tm','tmall','tn','to','today','tokyo','tools','top','toray','toshiba','total','tours','town','toyota','toys','tr','trade','trading','training','travel','travelchannel','travelers','travelersinsurance','trust','trv','tt','tube','tui','tunes','tushu','tv','tvs','tw','tz','ua','ubank','ubs','ug','uk','unicom','university','uno','uol','ups','us','uy','uz','va','vacations','vana','vanguard','vc','ve','vegas','ventures','verisign','versicherung','vet','vg','vi','viajes','video','vig','viking','villas','vin','vip','virgin','visa','vision','viva','vivo','vlaanderen','vn','vodka','volkswagen','volvo','vote','voting','voto','voyage','vu','vuelos','wales','walmart','walter','wang','wanggou','watch','watches','weather','weatherchannel','webcam','weber','website','wed','wedding','weibo','weir','wf','whoswho','wien','wiki','williamhill','win','windows','wine','winners','wme','wolterskluwer','woodside','work','works','world','wow','ws','wtc','wtf','xbox','xerox','xfinity','xihuan','xin','xxx','xyz','yachts','yahoo','yamaxun','yandex','ye','yodobashi','yoga','yokohama','you','youtube','yt','yun','za','zappos','zara','zero','zip','zm','zone','zuerich','zw')

allowed_tags = ('b','blockquote','br','code','del','em','h1','h2','h3','h4','h5','h6','hr','i',
	'li','ol','p','pre','strong','sub','sup','table','tbody','th','thead','td','tr','ul',
	'marquee','a','span','ruby','rp','rt','spoiler','img','lite-youtube','video','source','audio','g')

allowed_styles = ['color', 'background-color', 'font-weight', 'text-align', 'filter',]

def allowed_attributes(tag, name, value):

	if name == 'style': return True

	if tag == 'marquee':
		if name in ['direction', 'behavior', 'scrollamount']: return True
		if name in {'height', 'width'}:
			try: value = int(value.replace('px', ''))
			except: return False
			if 0 < value <= 250: return True
		return False

	if tag == 'a':
		if name == 'href' and '\\' not in value and 'xn--' not in value:
			return True
		if name == 'rel' and value == 'nofollow noopener noreferrer': return True
		if name == 'target' and value == '_blank': return True
		return False

	if tag == 'img':
		if name in ['src','data-src']: return is_safe_url(value)
		if name == 'loading' and value == 'lazy': return True
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name in ['g','b','glow'] and not value: return True
		if name in ['alt','title']: return True
		if name == 'referrerpolicy' and value == 'no-referrer': return True
		return False

	if tag == 'lite-youtube':
		if name == 'params' and value.startswith('autoplay=1&modestbranding=1'): return True
		if name == 'videoid': return True
		return False

	if tag == 'video':
		if name == 'controls' and value == '': return True
		if name == 'preload' and value == 'none': return True
		return False

	if tag == 'source':
		if name == 'src': return is_safe_url(value)

	if tag == 'audio':
		if name == 'src': return is_safe_url(value)
		if name == 'controls' and value == '': return True
		if name == 'preload' and value == 'none': return True
		return False

	if tag == 'p':
		if name == 'class' and value == 'mb-0': return True
		return False

	if tag == 'span':
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name == 'title': return True
		if name == 'alt': return True
		return False


def build_url_re(tlds, protocols):
	"""Builds the url regex used by linkifier

	If you want a different set of tlds or allowed protocols, pass those in
	and stomp on the existing ``url_re``::

		from bleach import linkifier

		my_url_re = linkifier.build_url_re(my_tlds_list, my_protocols)

		linker = LinkifyFilter(url_re=my_url_re)

	"""
	return re.compile(
		r"""\(*# Match any opening parentheses.
		\b(?<![@.])(?:(?:{0}):/{{0,3}}(?:(?:\w+:)?\w+@)?)?# http://
		([\w-]+\.)+(?:{1})(?:\:[0-9]+)?(?!\.\w)\b# xx.yy.tld(:##)?
		(?:[/?][^#\s\{{\}}\|\\\^\[\]`<>"]*)?
			# /path/zz (excluding "unsafe" chars from RFC 1738,
			# except for ~, which happens in practice)
		(?:\#[^#\s\|\\\^\[\]`<>"]*)?
			# #hash (excluding "unsafe" chars from RFC 1738,
			# except for ~, which happens in practice)
		""".format(
			"|".join(sorted(protocols)), "|".join(sorted(tlds))
		),
		re.IGNORECASE | re.VERBOSE | re.UNICODE,
	)

url_re = build_url_re(tlds=TLDS, protocols=['http', 'https'])

def callback(attrs, new=False):
	if (None, "href") not in attrs:
		return # Incorrect <a> tag

	href = attrs[(None, "href")]

	# \ in href right after / makes most browsers ditch site hostname and allows for a host injection bypassing the check, see <a href="/\google.com">cool</a>
	if "\\" in href or not ascii_only_regex.fullmatch(href):
		attrs["_text"] = href # Laugh at this user
		del attrs[(None, "href")] # Make unclickable and reset harmful payload
		return attrs

	if not href.startswith('/') and not href.startswith(f'{SITE_FULL}/'):
		attrs[(None, "target")] = "_blank"
		attrs[(None, "rel")] = "nofollow noopener noreferrer"

	return attrs


def render_emoji(html, regexp, edit, marseys_used, b=False):
	emojis = list(regexp.finditer(html))
	captured = set()

	for i in emojis:
		if i.group(0) in captured: continue
		captured.add(i.group(0))

		emoji = i.group(1).lower()
		attrs = ''
		if b: attrs += ' b'
		if not edit and len(emojis) <= 20 and ('marsey' in emoji or emoji in marseys_const2):
			if random() < 0.0025: attrs += ' g'
			elif random() < 0.00125: attrs += ' glow'

		old = emoji
		emoji = emoji.replace('!','').replace('#','')
		if emoji == 'marseyrandom': emoji = choice(marseys_const2)

		emoji_partial_pat = '<img loading="lazy" alt=":{0}:" src="{1}"{2}>'
		emoji_partial = '<img loading="lazy" data-bs-toggle="tooltip" alt=":{0}:" title=":{0}:" src="{1}"{2}>'
		emoji_html = None

		if emoji.endswith('pat') and emoji != 'marseyunpettablepat':
			if path.isfile(f"files/assets/images/emojis/{emoji.replace('pat','')}.webp"):
				emoji_html = f'<span data-bs-toggle="tooltip" alt=":{old}:" title=":{old}:"><img src="/i/hand.webp">{emoji_partial_pat.format(old, f"/e/{emoji[:-3]}.webp", attrs)}</span>'
			elif emoji.startswith('@'):
				if u := get_user(emoji[1:-3], graceful=True):
					emoji_html = f'<span data-bs-toggle="tooltip" alt=":{old}:" title=":{old}:"><img src="/i/hand.webp">{emoji_partial_pat.format(old, f"/pp/{u.id}", attrs)}</span>'
		elif path.isfile(f'files/assets/images/emojis/{emoji}.webp'):
			emoji_html = emoji_partial.format(old, f'/e/{emoji}.webp', attrs)


		if emoji_html:
			marseys_used.add(emoji)
			html = re.sub(f'(?<!"){i.group(0)}', emoji_html, html)
	return html


def with_sigalrm_timeout(timeout: int):
	'Use SIGALRM to raise an exception if the function executes for longer than timeout seconds'

	# while trying to test this using time.sleep I discovered that gunicorn does in fact do some
	# async so if we timeout on that (or on a db op) then the process is crashed without returning
	# a proper 500 error. Oh well.
	def sig_handler(signum, frame):
		print("Timeout!", flush=True)
		raise Exception("Timeout")

	def inner(func):
		@functools.wraps(func)
		def wrapped(*args, **kwargs):
			signal.signal(signal.SIGALRM, sig_handler)
			signal.alarm(timeout)
			try:
				return func(*args, **kwargs)
			finally:
				signal.alarm(0)
		return wrapped
	return inner


@with_sigalrm_timeout(2)
def sanitize(sanitized, edit=False, limit_pings=0, showmore=True, marsified=False, torture=False):
	sanitized = sanitized.strip()

	if torture:
		sanitized = torture_ap(sanitized, g.v.username)
		sanitized += '\n:#trumpjaktalking:'

	sanitized = normalize_url(sanitized)

	if '```' not in sanitized and '<pre>' not in sanitized:
		sanitized = linefeeds_regex.sub(r'\1\n\n\2', sanitized)

	sanitized = greentext_regex.sub(r'\1<g>\>\2</g>', sanitized)

	sanitized = image_regex.sub(r'\1![](\2)\5', sanitized)

	sanitized = image_check_regex.sub(r'\1', sanitized)

	sanitized = link_fix_regex.sub(r'\1https://\2', sanitized)

	if FEATURES['MARKUP_COMMANDS']:
		sanitized = command_regex.sub(command_regex_matcher, sanitized)

	sanitized = markdown(sanitized)

	sanitized = strikethrough_regex.sub(r'\1<del>\2</del>', sanitized)

	sanitized = sanitized.replace('‎','').replace('​','').replace("\ufeff", "").replace("𒐪","")

	sanitized = reddit_regex.sub(r'\1<a href="https://old.reddit.com/\2" rel="nofollow noopener noreferrer" target="_blank">/\2</a>', sanitized)
	sanitized = sub_regex.sub(r'\1<a href="/\2">/\2</a>', sanitized)

	v = getattr(g, 'v', None)

	names = set(m.group(2) for m in mention_regex.finditer(sanitized))
	if limit_pings and len(names) > limit_pings and not v.admin_level: abort(406)
	users_list = get_users(names, graceful=True)
	users_dict = {}
	for u in users_list:
		users_dict[u.username.lower()] = u
		if u.original_username:
			users_dict[u.original_username.lower()] = u

	def replacer(m):
		u = users_dict.get(m.group(2).lower())
		if not u:
			return m.group(0)
		return f'{m.group(1)}<a href="/id/{u.id}"><img loading="lazy" src="/pp/{u.id}">@{u.username}</a>'

	sanitized = mention_regex.sub(replacer, sanitized)

	soup = BeautifulSoup(sanitized, 'lxml')

	for tag in soup.find_all("img"):
		if tag.get("src") and not tag["src"].startswith('/pp/'):
			if not is_safe_url(tag["src"]):
				a = soup.new_tag("a", href=tag["src"], rel="nofollow noopener noreferrer", target="_blank")
				a.string = tag["src"]
				tag.replace_with(a)
				continue

			tag["loading"] = "lazy"
			tag["data-src"] = tag["src"]
			tag["src"] = "/i/l.webp"
			tag['alt'] = f'![]({tag["data-src"]})'

			if not is_site_url(tag["data-src"]):
				tag['referrerpolicy'] = "no-referrer"

			if tag.parent.name != 'a':
				a = soup.new_tag("a", href=tag["data-src"])
				if not is_site_url(a["href"]):
					a["rel"] = "nofollow noopener noreferrer"
					a["target"] = "_blank"
				tag = tag.replace_with(a)
				a.append(tag)

	for tag in soup.find_all("a"):
		if not tag.contents or not str(tag.contents[0]).strip():
			tag.extract()
		if tag.get("href") and fishylinks_regex.fullmatch(str(tag.string)):
			tag.string = tag["href"]


	sanitized = str(soup)

	sanitized = spoiler_regex.sub(r'<spoiler>\1</spoiler>', sanitized)

	marseys_used = set()

	emojis = list(emoji_regex.finditer(sanitized))
	if len(emojis) > 20: edit = True

	captured = []
	for i in emojis:
		if i.group(0) in captured: continue
		captured.append(i.group(0))

		old = i.group(0)
		if 'marseylong1' in old or 'marseylong2' in old or 'marseyllama1' in old or 'marseyllama2' in old: new = old.lower().replace(">", " class='mb-0'>")
		else: new = old.lower()

		new = render_emoji(new, emoji_regex2, edit, marseys_used, True)

		sanitized = sanitized.replace(old, new)

	emojis = list(emoji_regex2.finditer(sanitized))
	if len(emojis) > 20: edit = True

	sanitized = render_emoji(sanitized, emoji_regex2, edit, marseys_used)

	sanitized = sanitized.replace('&amp;','&')

	if "https://youtube.com/watch?v=" in sanitized: sanitized = sanitized.replace("?t=", "&t=")

	captured = []
	for i in youtube_regex.finditer(sanitized):
		if i.group(0) in captured: continue
		captured.append(i.group(0))

		params = parse_qs(urlparse(i.group(2)).query, keep_blank_values=True)
		t = params.get('t', params.get('start', [0]))[0]
		if isinstance(t, str): t = t.replace('s','')

		htmlsource = f'{i.group(1)}<lite-youtube videoid="{i.group(3)}" params="autoplay=1&modestbranding=1'
		if t: htmlsource += f'&start={t}'
		htmlsource += '"></lite-youtube>'

		sanitized = sanitized.replace(i.group(0), htmlsource)

	sanitized = video_sub_regex.sub(r'\1<video controls preload="metadata"><source src="\2"></video>', sanitized)
	sanitized = audio_sub_regex.sub(r'\1<audio controls preload="metadata" src="\2"></audio>', sanitized)

	if not edit and not marsified:
		for marsey in g.db.query(Marsey).filter(Marsey.submitter_id==None, Marsey.name.in_(marseys_used)).all():
			marsey.count += 1
			g.db.add(marsey)

	sanitized = sanitized.replace('<p></p>', '')
	sanitized = utm_regex.sub('', sanitized)
	sanitized = utm_regex2.sub('', sanitized)

	sanitized = sanitized.replace('<html><body>','').replace('</body></html>','')

	css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_styles)
	sanitized = bleach.Cleaner(tags=allowed_tags,
								attributes=allowed_attributes,
								protocols=['http', 'https'],
								css_sanitizer=css_sanitizer,
								filters=[partial(LinkifyFilter, skip_tags=["pre"],
									parse_email=False, callbacks=[callback], url_re=url_re)]
								).clean(sanitized)

	soup = BeautifulSoup(sanitized, 'lxml')

	links = soup.find_all("a")

	domain_list = set()

	for link in links:

		href = link.get("href")
		if not href: continue

		url = urlparse(href)
		domain = url.netloc
		url_path = url.path
		domain_list.add(domain+url_path)

		parts = domain.split(".")
		for i in range(len(parts)):
			new_domain = parts[i]
			for j in range(i + 1, len(parts)):
				new_domain += "." + parts[j]
				domain_list.add(new_domain)

	bans = g.db.query(BannedDomain.domain).filter(BannedDomain.domain.in_(list(domain_list))).all()

	if bans: abort(403, description=f"Remove the banned domains {bans} and try again!")

	if '<pre>' not in sanitized:
		sanitized = sanitized.replace('\n','')

	if showmore and len(sanitized) > 5000:
		sanitized = showmore_regex.sub(r'\1<p><button class="showmore" onclick="showmore()">SHOW MORE</button></p><d class="d-none">\2</d>', sanitized, count=1)

	return sanitized.strip()





def allowed_attributes_emojis(tag, name, value):

	if tag == 'img':
		if name == 'src' and value.startswith('/') and '\\' not in value: return True
		if name == 'loading' and value == 'lazy': return True
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name in ['g','glow'] and not value: return True
		if name in ['alt','title']: return True

	if tag == 'span':
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name == 'title': return True
		if name == 'alt': return True
		return False
	return False


@with_sigalrm_timeout(1)
def filter_emojis_only(title, edit=False, graceful=False, torture=False):
	title = title.strip()

	if torture:
		title = torture_ap(title, g.v.username)

	title = title.replace('‎','').replace('​','').replace("\ufeff", "").replace("𒐪","").replace("\n", "").replace("\r", "").replace("\t", "").replace("&", "&amp;").replace('<','&lt;').replace('>','&gt;').replace('"', '&quot;').replace("'", "&#039;").strip()

	marseys_used = set()

	title = render_emoji(title, emoji_regex3, edit, marseys_used)

	if not edit:
		for marsey in g.db.query(Marsey).filter(Marsey.submitter_id==None, Marsey.name.in_(marseys_used)).all():
			marsey.count += 1
			g.db.add(marsey)

	title = strikethrough_regex.sub(r'\1<del>\2</del>', title)

	title = bleach.clean(title, tags=['img','del','span'], attributes=allowed_attributes_emojis, protocols=['http','https'])

	if len(title) > 1500 and not graceful: abort(400)
	else: return title.replace('\n','').strip()

def normalize_url(url):
	url = reddit_domain_regex.sub(r'\1https://old.reddit.com/\3/', url)

	url = url.replace("https://youtu.be/", "https://youtube.com/watch?v=") \
			 .replace("https://music.youtube.com/watch?v=", "https://youtube.com/watch?v=") \
			 .replace("https://www.youtube.com", "https://youtube.com") \
			 .replace("https://youtube.com/shorts/", "https://youtube.com/watch?v=") \
			 .replace("https://youtube.com/v/", "https://youtube.com/watch?v=") \
			 .replace("https://mobile.twitter.com", "https://twitter.com") \
			 .replace("https://m.facebook.com", "https://facebook.com") \
			 .replace("https://m.wikipedia.org", "https://wikipedia.org") \
			 .replace("https://m.youtube.com", "https://youtube.com") \
			 .replace("https://www.twitter.com", "https://twitter.com") \
			 .replace("https://www.instagram.com", "https://instagram.com") \
			 .replace("https://www.tiktok.com", "https://tiktok.com") \
			 .replace("https://www.streamable.com", "https://streamable.com") \
			 .replace("https://streamable.com/", "https://streamable.com/e/") \
			 .replace("https://streamable.com/e/e/", "https://streamable.com/e/") \
			 .replace("https://search.marsey.cat/#", "https://camas.unddit.com/#") \
			 .replace("https://imgur.com/", "https://i.imgur.com/")

	url = imgur_regex.sub(r'\1_d.webp?maxwidth=9999&fidelity=high', url)
	url = giphy_regex.sub(r'\1.webp', url)

	return url

def validate_css(css):
	if '@import' in css:
		return False, "@import statements not allowed."

	for i in css_url_regex.finditer(css):
		url = i.group(1)
		if not is_safe_url(url):
			domain = tldextract.extract(url).registered_domain
			return False, f"The domain '{domain}' is not allowed, please use one of these domains\n\n{approved_embed_hosts}."

	return True, ""
