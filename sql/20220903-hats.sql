CREATE TABLE public.hat_defs (
    id integer PRIMARY KEY,
    name character varying(50) NOT NULL UNIQUE,
    description character varying(300) NOT NULL,
    author_id integer NOT NULL,
    price integer NOT NULL
);

CREATE SEQUENCE public.hat_defs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.hat_defs_id_seq OWNED BY public.hat_defs.id;

ALTER TABLE ONLY public.hat_defs ALTER COLUMN id SET DEFAULT nextval('public.hat_defs_id_seq'::regclass);

ALTER TABLE ONLY public.hat_defs
    ADD CONSTRAINT hat_defs_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);





CREATE TABLE public.hats (
    hat_id integer NOT NULL,
    user_id integer NOT NULL
);

ALTER TABLE ONLY public.hats
    ADD CONSTRAINT hats_pkey PRIMARY KEY (user_id, hat_id);

ALTER TABLE ONLY public.hats
    ADD CONSTRAINT hats_hat_id_fkey FOREIGN KEY (hat_id) REFERENCES public.hat_defs(id);

ALTER TABLE ONLY public.hats
    ADD CONSTRAINT hats_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

alter table users add column coins_spent_on_hats integer DEFAULT 0 NOT NULL;
alter table users add column equipped_hat_id integer;
ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_equipped_hat_id_fkey FOREIGN KEY (equipped_hat_id) REFERENCES public.hat_defs(id);

insert into hat_defs (name, description, author_id, price) values
('Ushanka', 'The People''s Hat', 2, 500), 
('Fur Hat', 'The first step on your path to fursuit ownership', 2, 500), 
('Cat Ears I', 'Mew :3', 2, 500),
('Cat Ears II', 'Meow :3', 2, 500),
('Playboy Bunny', 'Will this bring daddy back?', 2, 500),
('Macaroni', 'Get it? Like the song lol', 2, 500),
('Pirate', 'BUTT pirate', 2, 500),
('Pirate Captain', 'Like a regular butt pirate, but for tops only', 2, 500),
('Dreads', 'Finally, an excuse for poor hygiene', 2, 500),
('The XXXTentacion', 'Pay homage to your favorite dead criminal!', 2, 500),
('the 6ix9ine', 'The finest piece of snitch couture on the market', 2, 500),
('The Elvis', 'Remember when this dude nailed a 13-year-old?', 2, 500),
('Gussy Hat', 'Let everyone know that you''re NOT a rapist. Honest.', 2, 500),
('Riveter', 'Can you do it? Really?', 2, 500),
('Top Hat (leprechaun)', 'LLM but Irish', 2, 500),
('Drinky Beer Hat', 'I actually didn''t know these were real things until I made this', 2, 500),
('Viking', 'Rape, pillage, never bathe. Live the dream.', 2, 500),
('Nonspecific Military Officer Hat', '[removed]', 2, 500),
('Soviet Officer I', 'OUR hat', 2, 500),
('Nonspecific Military Officer Hat II', '[removed]', 2, 500),
('Soviet Officer II', 'High fashion war criminal chic', 2, 500),
('Southern Gentleman', 'Slaveowner? Fried chicken chain founder? You decide!', 2, 500),
('Cowboy I', 'Make him wish he could quit you', 2, 500),
('Cowboy II', 'You''re my favorite deputy!', 2, 500),
('Halo', 'Dramamine criticized this one and now I''m too self-conscious about it to write a description', 2, 500),
('Fedora I', 'M''arsey', 2, 500),
('Bowler', 'Why would you need a hat to go bowling?', 2, 500),
('Du Rag (black)', 'Shitty bandana 1/6', 2, 500),
('Du Rag (red)', 'Shitty bandana 2/6', 2, 500),
('Du Rag (blue)', 'Shitty bandana 3/6', 2, 500),
('Du Rag (purple)', 'Shitty bandana 4/6', 2, 500),
('Du Rag (green)', 'Shitty bandana 5/6', 2, 500),
('Du Rag (yellow)', 'Shitty bandana 6/6', 2, 500),
('Ash Ketchum', 'You''re not so different, you and he', 2, 500),
('The Hotep', 'Traditional kangwear. POC ONLY.', 2, 500),
('Roman', 'Reddit delenda est', 2, 500),
('Confederate Soldier Cap', 'Basically the Gryffindor of American history', 2, 500),
('Northern Aggressor Soldier Cap', 'Slytherin irl', 2, 500),
('Rhodesian Light Infantry Beret', 'Rhodesians never die. Immortality guaranteed!', 2, 500),
('Magyar Headdress', 'Channel your inner QuadNarca and join Orban''s elite cavalry', 2, 500),
('The Senator Warren', 'heya heya heya heya heya heya heya heya heya heya heya', 2, 500),
('Please Be Patient I Have Autism', 'The OFFICIAL hat of rDrama.net', 2, 500),
('Samurai Helmet', 'Never be mistaken for a baka gaijin again', 2, 500),
('Watermelmet', 'Hydration and head protection all rolled into one stylish headpiece', 2, 500),
('Frankenstein', 'Akshually, Frankenstein was the scientist. The monster didn''t have a name.', 2, 500),
('The Drumpf', 'Orange hair bad', 2, 500),
('Tinfoil Hat', 'Keep Bill Gates'' 5G vaccine OUT of your precious brain!', 2, 500),
('Fez', 'Isn''t it CUTE?', 2, 500),
('Ching Chong', 'Me Chinese Me No Dumb Me Stick Finger In Daddy''s Bum', 2, 500),
('Octopus Friend', 'Awwwwwww!', 2, 500),
('In The Navy', 'It''s not gay', 2, 500),
('Seaman', 'semen lol', 2, 500),
('Flower Crown I', 'oh god i have to write descriptions for 15 flower crowns', 2, 500),
('Flower Crown II', 'A very cute flower crown', 2, 500),
('Flower Crown III', 'A super cute flower crown', 2, 500),
('Flower Crown IV', 'A really cute flower crown', 2, 500),
('Flower Crown V', 'The cutest flower crown?', 2, 500),
('Flower Crown VI', 'An extremely cute flower crown', 2, 500),
('Flower Crown VII', 'A flower crown that''s just so cute', 2, 500),
('Flower Crown VIII', 'A majorly cute flower crown', 2, 500),
('Flower Crown IX', 'A mega cute flower crown', 2, 500),
('Flower Crown X', 'An ultra cute flower crown', 2, 500),
('Flower Crown XI', 'Definitely the cutest flower crown', 2, 500),
('Flower Crown XII', 'A hella cute flower crown', 2, 500),
('Flower Crown XIII', 'An experimental anti-gravity cute flower crown', 2, 500),
('Flower Crown XIV', 'An adorably cute flower crown', 2, 500),
('Flower Crown XV', 'The final cute flower crown', 2, 500),
('Bow', 'What a cute little bow omg', 2, 500),
('BIPOCsmoke', 'It''s a Newport. You know it''s a Newport.', 2, 500),
('Gigachin', 'Aw yeah, this user definitely supports trans rights', 2, 500),
('Queensguard', 'A bear died for this', 2, 500),
('Queen Crown', 'Don''t be a drag', 2, 500),
('King Crown', 'King is like the n word, only racists and black people should be allowed to say it', 2, 500),
('Pope Hat', 'Matthew 16:18', 2, 500),
('Heebhead', 'Do NOT google the Lavon Affair', 2, 500),
('Zoomie Zoom Zoom', 'Underage user, do not interact', 2, 500),
('Sombrero I', 'El Autistico', 2, 500),
('Sombrero II', 'El Autistico Grandisimo', 2, 500),
('Crypto Billionaire', 'Sorry about the ice cream machine', 2, 500),
('Burger King Crown', 'I''m gonna say it', 2, 500),
('Burger King', 'You can have it your way and you still chose this', 2, 500),
('Wendys', 'Sassy social media intern', 2, 500),
('KFC', 'Popeyes is too far away', 2, 500),
('In-N-Out', 'Kill the commiefornian', 2, 500),
('Carls Jr', 'Purveyor of literally the finest food in the world', 2, 500),
('Whataburger', 'Texans don''t know any better', 2, 500),
('Five Guys', 'I love having 5 guys in my mouth', 2, 500),
('Taco Bell', 'Enabler of drunken mistakes', 2, 500),
('Marsey-In-A-Box', 'Awww you''re playing make-believe!', 2, 500),
('Orthodox Hood', 'User is a schismatic lunatic', 2, 500),
('Afro', 'Pool''s closed motherlover', 2, 500),
('Top Hat (black)', 'Traditional. Classy. Elegant.', 2, 500),
('Wizard I', 'Three decades a KHHV', 2, 500),
('Wizard II', 'Avada kedavra ✨', 2, 500),
('Witch I', 'Hex the patriarchy', 2, 500),
('Witch II', 'Bardfinn cosplay gear', 2, 500),
('Sun Hat', 'Tradwife simplicity', 2, 500),
('Obey Snapback', 'The timeless classic', 2, 500),
('Thug Life Snapback', 'User confirmed mayo', 2, 500),
('Supreme Snapback', 'Drip so hard omg', 2, 500),
('Make America Great Again', 'The official headgear of stochastic terrorists everywhere', 2, 500),
('Born To Feel', 'Do you pee standing up?', 2, 500),
('Fortunate Son', 'BORN TO SHIT FORCED TO WIPE', 2, 500),
('WWI', 'How is this supposed to offer any meaningful protection??', 2, 500),
('Pickelhaube', 'Inarguably the most fashionable of all contemporary military headgear ', 2, 500),
('Wehrmacht', 'What a cool helmet, I bet the people who wore it were real classy folks ', 2, 500),
('Chair Force', 'Yeah I''m a combat veteran, I''ve seen shit you wouldn''t believe. One time the wifi was out for almost an hour. ', 2, 500),
('Helmet w Dog Tags', 'More like dog fags lol', 2, 500),
('Urban Camo Helmet', 'Man urban camo is cool', 2, 500),
('Nightvision Helmet', 'Four-eyed freak', 2, 500),
('Helmet w Mesh', 'Sexy fishnet stocking helmet', 2, 500),
('Tojo Helmet', 'Artifact from Weeb War II', 2, 500),
('Officers Cap', 'Get fragged bozo', 2, 500),
('Jailbird Cap', 'The apex of prison fashion. Why did we stop using this?', 2, 500),
('P-Hat (green)', 'Zezima fanboy', 2, 500),
('P-Hat (red)', 'おれはPigAmericanですおれはばか i am average american man i enjoy bad game runescape', 2, 500),
('P-Hat (yellow)', 'PISS HAT PISS HAT', 2, 500),
('P-Hat (blue)', 'Ughhhh coming up with different descriptions for RuneScape party hats', 2, 500),
('P-Hat (pink)', 'It''s pink.', 2, 500),
('P-Hat (rainbow)', 'LGBTscape 😍', 2, 500),
('Newsboy', 'Or newsgirl. It''s okay, the hat is actually gender-neutral.', 2, 500),
('Whirly Tard Hat I', 'Wouldn''t it be neat if they could make one that like uses body heat or whatever to keep the propeller in a state of constant motion', 2, 500),
('Dunce Cap', 'You retard. Imbecile. Utter buffoon. Oaf. Nincompoop. Idiot. Moron. CLOWN.', 2, 500),
('Beret', 'Literally the most basic possible hat choice. Please do better. ', 2, 500),
('Mario', 'BING BING WAHOO ', 2, 500),
('Luigi', 'LING LING LAHOO', 2, 500),
('Wing Cap', 'If the hat''s wings are what provide the thrust necessary for flight then how does it stay on and let YOU fly with it huh', 2, 500),
('Metal Mario', 'Mario hat but with yelling and lots of double bass and distorted guitars and shit heck yeah', 2, 500),
('Cappy', 'A sentient hat-creature that''s actually a pretty horrifying parasite if you think about it', 2, 500),
('Wario', 'For the fat, yellow, extremely flatulent dramautist (in loving memory of Bidpots)', 2, 500),
('Waluigi', 'Coming soon to Smash for sure', 2, 500),
('Top Hat (kek)', 'Technically a top hat, shut up', 2, 500),
('Top Hat (white)', 'Oh, how dignified', 2, 500),
('Top Hat (striped)', 'Tim Burton''s take on the top hat', 2, 500),
('Top Hat (checkered)', 'Actually chessed, but that''s not really a word.', 2, 500),
('Top Hat (march hare)', 'April hare, May hare, June hare, July hare,', 2, 500),
('Top Hat (mad hatter)', 'Hatters mad [x24]', 2, 500),
('Top Hat (red)', 'Top hat, menstrual edition', 2, 500),
('Top Hat (uncle sam)', 'THIS HAT WAS FACT-CHECKED BY TRUE AMERICAN PATRIOTS', 2, 500),
('Fireperson I', 'In loving memory of r/HateForFirefighters', 2, 500),
('Constable', 'Useless bong cop nonsense', 2, 500),
('NYPD Officer', 'This user is authorized to stop, frisk and cavity search you at any time for any reason', 2, 500),
('Crossing Guard', 'We love Officer Marsey!', 2, 500),
('Paper Sailor', 'As idle as a paper ship, upon a paper ocean. Paper, paper, everywhere.', 2, 500),
('FBI', 'Federal Bussy Inspector', 2, 500),
('CIA', 'Cisgender Incineration Agency', 2, 500),
('ATF', 'Ass-Tickling Faggot. HIDE YOUR DOG!', 2, 500),
('Graduate', 'This hat signifies that the bearer has completed four (4) years of pan-african gender studies coursework', 2, 500),
('Nurse', 'Minor TikTok celebrity, OnlyFans top 91%', 2, 500),
('Farmer', 'Feed & Seed shopper', 2, 500),
('Farmette', 'Feed & Seed shoppette', 2, 500),
('Kung Lao', 'Why did I make a Kung Lao hat', 2, 500),
('Top Hat (steampunk)', 'Like a regular top hat but with goggles and gears', 2, 500),
('Brain Hat', 'Peter Griffin''s dog', 2, 500),
('The TED_SIMP', 'Wear this hat to express your undying adoration for carp', 2, 500),
('The Brandon', 'Listen here fat', 2, 500),
('The Brandon II', 'LISTEN HERE FAT', 2, 500),
('The King George', 'Proto-drag if you think about it', 2, 500),
('The Mao', 'Our hair!', 2, 500),
('The Young Stalin', 'Pockmarks not included', 2, 500),
('The Ripe Stalin', 'An homage to the #1 most prolific killer of commies in world history', 2, 500),
('The Austrian Painter', 'For aficionados of mid-20th century fine artists slash authors', 2, 500),
('Kenny I', 'User''s life insurance claim was rejected', 2, 500),
('Modern Major General', 'For my military knowledge, though I''m plucky and adventury / Has only been brought down to the beginning of the century / But still, in matters vegetable, animal, and mineral / I am the very model of a modern Major-General', 2, 500),
('Red Star Cap', 'Cannon fodder', 2, 500),
('Cartman', 'Fat antisemite - the archetypal rDrama user', 2, 500),
('Cheesehead', 'For fans of the Green Gay Fudge Packers', 2, 500),
('Kyle', 'ngl I don''t watch South Park so idk the difference between this and Stan', 2, 500),
('Stan', 'ngl I don''t watch South Park so idk the difference between this and Kyle', 2, 500),
('Kenny II', 'Like Kenny I except it shows more of your ugly face', 2, 500),
('The Cleopatra', 'Did you know she was actually white?', 2, 500),
('Pimp Hat I', 'Women are objects', 2, 500),
('Devil Horns', 'Satan is so cool and quirky!!!', 2, 500),
('Nooticer', 'THIS USER IS ENGAGED IN THOUGHTCRIME. DO NOT INTERACT.', 2, 500),
('Airpods', 'oh god oh fuck he cant hear us', 2, 500),
('Maskmaxxer', 'Why aren''t there two? Are you trying to kill us?', 2, 500),
('The Tupac', 'dead nigger storage', 2, 500),
('Media Executive', 'despite making up just 2% of the population,', 2, 500),
('Surgeon', 'Lobotomize me daddy', 2, 500),
('Mouseketeer', 'please don''t sue please don''t sue please don''t sue please don''t sue please don''t sue', 2, 500),
('Karen', 'Let me speak to your manager', 2, 500),
('Badass Fighter Ace', ' Top Gun™ Maverick® Now Showing In Theaters!', 2, 500),
('Taqiyah', 'It''s not a yarmulke I swear', 2, 500),
('Cock', 'DM me yours!', 2, 500),
('Nervous, Sweating', '>mfw', 2, 500),
('The Cat', 'does this really need a description', 2, 500),
('Noose', 'Cope or rope', 2, 500),
('The Penny', 'This shower cap bonnet is perfect for hiding nappy, alopecia-ridden hair', 2, 500),
('Hard Hat (yellow)', 'A rock hard, throbbing, veiny hat. Check out the girth on this thing', 2, 500),
('Hard Hat (white)', 'The mayo variant of the hard hat, used to signify someone of importance, or a visitor, at a job site', 2, 500),
('Beret (TF2)', 'Stylish vidya-variant of the beret', 2, 500),
('Texas Ten Gallon', 'Yeehaw!', 2, 500),
('Demoman', 'KaBOOM', 2, 500),
('Fireperson II', 'For extinguishing hot threads', 2, 500),
('Miners Hat', 'Please don''t touch minors', 2, 500),
('Old Man Hat', 'AKA the Wizdumb', 2, 500),
('Pimp Hat II', 'Women are people and they deserve respect just kidding they should suck my penis', 2, 500),
('Whirly Tard Hat II', 'Propeller go brrrrrrrrrr', 2, 500),
('Family Man Free Hat', 'It''s a good show!', 2, 500),
('Engineer', 'Choo choo!', 2, 500),
('Vexillaurius Helmet', 'Degenerates like you belong on rDrama', 2, 500),
('Astronaut Helmet', 'See you, space marsey', 2, 500);