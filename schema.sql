--
-- PostgreSQL database dump
--

-- Dumped from database version 14.4
-- Dumped by pg_dump version 14.5 (Ubuntu 14.5-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: casino_game_currency; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.casino_game_currency AS ENUM (
    'coins',
    'procoins'
);


--
-- Name: casino_game_kind; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.casino_game_kind AS ENUM (
    'blackjack',
    'slots',
    'roulette'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: submissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.submissions (
    id integer NOT NULL,
    author_id integer NOT NULL,
    created_utc integer NOT NULL,
    is_banned boolean DEFAULT false NOT NULL,
    over_18 boolean DEFAULT false NOT NULL,
    distinguish_level integer DEFAULT 0 NOT NULL,
    deleted_utc integer DEFAULT 0 NOT NULL,
    is_approved integer,
    edited_utc integer DEFAULT 0 NOT NULL,
    is_pinned boolean DEFAULT false NOT NULL,
    upvotes integer DEFAULT 1 NOT NULL,
    downvotes integer DEFAULT 0 NOT NULL,
    app_id integer,
    thumburl character varying(200),
    private boolean DEFAULT false NOT NULL,
    views integer DEFAULT 0 NOT NULL,
    is_bot boolean DEFAULT false NOT NULL,
    bannedfor character varying(40),
    comment_count integer DEFAULT 0 NOT NULL,
    club boolean DEFAULT false NOT NULL,
    stickied character varying(40),
    title character varying(500) NOT NULL,
    url character varying(2083),
    body character varying(20000),
    body_html character varying(40000),
    embed_url character varying(1500),
    ban_reason character varying(25),
    title_html character varying(1500) NOT NULL,
    realupvotes integer,
    flair character varying(350),
    stickied_utc integer,
    ghost boolean DEFAULT false NOT NULL,
    sub character varying(25),
    new boolean,
    hole_pinned character varying(30),
    category_id integer,
    notify boolean NOT NULL
);


--
-- Name: bump_utc(public.submissions); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.bump_utc(public.submissions) RETURNS integer
    LANGUAGE sql IMMUTABLE STRICT
    AS $_$
      SELECT CREATED_UTC
      FROM comments
      WHERE parent_submission = $1.id
      ORDER BY created_utc desc
      LIMIT 1
      $_$;


--
-- Name: alts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alts (
    user1 integer NOT NULL,
    user2 integer NOT NULL,
    is_manual boolean DEFAULT false NOT NULL,
    created_utc integer,
    CONSTRAINT alts_cant_be_equal CHECK ((user1 <> user2))
);


--
-- Name: award_relationships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.award_relationships (
    id integer NOT NULL,
    user_id integer NOT NULL,
    submission_id integer,
    comment_id integer,
    kind character varying(20) NOT NULL,
    awarded_utc integer,
    granted boolean,
    created_utc integer
);


--
-- Name: award_relationships_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.award_relationships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: award_relationships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.award_relationships_id_seq OWNED BY public.award_relationships.id;


--
-- Name: badge_defs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.badge_defs (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(200),
    created_utc integer
);


--
-- Name: badge_defs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.badge_defs_id_seq
    AS integer
    START WITH 106
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: badge_defs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.badge_defs_id_seq OWNED BY public.badge_defs.id;


--
-- Name: badges; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.badges (
    badge_id integer NOT NULL,
    user_id integer NOT NULL,
    description character varying(256),
    url character varying(256),
    created_utc integer NOT NULL
);


--
-- Name: banneddomains; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.banneddomains (
    domain character varying(100) NOT NULL,
    reason character varying(100) NOT NULL,
    created_utc integer
);


--
-- Name: casino_games; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.casino_games (
    id integer NOT NULL,
    user_id integer NOT NULL,
    created_utc integer NOT NULL,
    active boolean DEFAULT true NOT NULL,
    currency public.casino_game_currency NOT NULL,
    wager integer NOT NULL,
    winnings integer NOT NULL,
    kind public.casino_game_kind NOT NULL,
    game_state jsonb NOT NULL
);


--
-- Name: casino_games_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.casino_games_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: casino_games_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.casino_games_id_seq OWNED BY public.casino_games.id;


--
-- Name: category; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.category (
    id integer NOT NULL,
    name character varying(128) NOT NULL,
    sub character varying(25),
    color_text character(6),
    color_bg character(6),
    created_utc integer
);


--
-- Name: category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.category_id_seq OWNED BY public.category.id;


--
-- Name: client_auths; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client_auths (
    user_id integer NOT NULL,
    oauth_client integer NOT NULL,
    access_token character(128) NOT NULL,
    created_utc integer
);


--
-- Name: comment_option_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comment_option_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comment_option_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comment_option_votes (
    option_id integer NOT NULL,
    user_id integer NOT NULL,
    created_utc integer NOT NULL,
    comment_id integer
);


--
-- Name: comment_options; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comment_options (
    id integer DEFAULT nextval('public.comment_option_id_seq'::regclass) NOT NULL,
    comment_id integer NOT NULL,
    body_html character varying(500) NOT NULL,
    exclusive integer NOT NULL,
    created_utc integer
);


--
-- Name: comment_save_relationship; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comment_save_relationship (
    user_id integer NOT NULL,
    comment_id integer NOT NULL,
    created_utc integer
);


--
-- Name: commentflags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.commentflags (
    user_id integer NOT NULL,
    comment_id integer NOT NULL,
    reason character varying(350),
    created_utc integer NOT NULL
);


--
-- Name: comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comments (
    id integer NOT NULL,
    author_id integer NOT NULL,
    created_utc integer NOT NULL,
    parent_submission integer,
    is_banned boolean DEFAULT false NOT NULL,
    distinguish_level integer DEFAULT 0 NOT NULL,
    edited_utc integer DEFAULT 0 NOT NULL,
    deleted_utc integer DEFAULT 0 NOT NULL,
    is_approved integer,
    level integer DEFAULT 0 NOT NULL,
    parent_comment_id integer,
    over_18 boolean DEFAULT false NOT NULL,
    upvotes integer DEFAULT 1 NOT NULL,
    downvotes integer DEFAULT 0 NOT NULL,
    is_bot boolean DEFAULT false NOT NULL,
    app_id integer,
    sentto integer,
    bannedfor character varying(40),
    stickied character varying(40),
    body character varying(10000),
    body_html character varying(40000),
    ban_reason character varying(25),
    realupvotes integer DEFAULT 1 NOT NULL,
    top_comment_id integer,
    stickied_utc integer,
    ghost boolean DEFAULT false NOT NULL,
    slots_result character varying(36),
    blackjack_result character varying(860),
    treasure_amount character varying(10),
    wordle_result character varying(115)
);


--
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;


--
-- Name: commentvotes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.commentvotes (
    comment_id integer NOT NULL,
    vote_type integer NOT NULL,
    user_id integer NOT NULL,
    app_id integer,
    "real" boolean DEFAULT true NOT NULL,
    created_utc integer NOT NULL
);


--
-- Name: exiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.exiles (
    user_id integer NOT NULL,
    sub character varying(25) NOT NULL,
    exiler_id integer NOT NULL,
    created_utc integer
);


--
-- Name: flags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.flags (
    user_id integer NOT NULL,
    post_id integer NOT NULL,
    reason character varying(350),
    created_utc integer NOT NULL
);


--
-- Name: follows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.follows (
    user_id integer NOT NULL,
    target_id integer NOT NULL,
    created_utc integer NOT NULL
);


--
-- Name: hat_defs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hat_defs (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(300) NOT NULL,
    author_id integer NOT NULL,
    price integer NOT NULL,
    submitter_id integer,
    created_utc integer
);


--
-- Name: hat_defs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hat_defs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hat_defs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hat_defs_id_seq OWNED BY public.hat_defs.id;


--
-- Name: hats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hats (
    hat_id integer NOT NULL,
    user_id integer NOT NULL,
    equipped boolean,
    created_utc integer
);


--
-- Name: lotteries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lotteries (
    id integer NOT NULL,
    is_active boolean DEFAULT false NOT NULL,
    ends_at integer DEFAULT 0 NOT NULL,
    prize integer DEFAULT 0 NOT NULL,
    tickets_sold integer DEFAULT 0 NOT NULL,
    winner_id integer,
    created_utc integer
);


--
-- Name: lotteries_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.lotteries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: lotteries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.lotteries_id_seq OWNED BY public.lotteries.id;


--
-- Name: marseys; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.marseys (
    name character varying(30) NOT NULL,
    author_id integer NOT NULL,
    tags character varying(200) NOT NULL,
    count integer DEFAULT 0 NOT NULL,
    submitter_id integer,
    created_utc integer
);


--
-- Name: modactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.modactions (
    id integer NOT NULL,
    user_id integer,
    target_user_id integer,
    target_submission_id integer,
    target_comment_id integer,
    created_utc integer NOT NULL,
    kind character varying(32) DEFAULT NULL::character varying,
    _note character varying(500) DEFAULT NULL::character varying
);


--
-- Name: modactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.modactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: modactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.modactions_id_seq OWNED BY public.modactions.id;


--
-- Name: mods; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mods (
    user_id integer NOT NULL,
    sub character varying(25) NOT NULL,
    created_utc integer NOT NULL
);


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    user_id integer NOT NULL,
    comment_id integer NOT NULL,
    read boolean NOT NULL,
    created_utc integer NOT NULL
);


--
-- Name: oauth_apps; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.oauth_apps (
    id integer NOT NULL,
    client_id character(64),
    app_name character varying(50) NOT NULL,
    redirect_uri character varying(4096) NOT NULL,
    author_id integer NOT NULL,
    description character varying(256) NOT NULL,
    created_utc integer
);


--
-- Name: oauth_apps_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.oauth_apps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: oauth_apps_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.oauth_apps_id_seq OWNED BY public.oauth_apps.id;


--
-- Name: pgbench_accounts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pgbench_accounts (
    aid integer NOT NULL,
    bid integer,
    abalance integer,
    filler character(84)
)
WITH (fillfactor='100');


--
-- Name: pgbench_branches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pgbench_branches (
    bid integer NOT NULL,
    bbalance integer,
    filler character(88)
)
WITH (fillfactor='100');


--
-- Name: pgbench_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pgbench_history (
    tid integer,
    bid integer,
    aid integer,
    delta integer,
    mtime timestamp without time zone,
    filler character(22)
);


--
-- Name: pgbench_tellers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pgbench_tellers (
    tid integer NOT NULL,
    bid integer,
    tbalance integer,
    filler character(84)
)
WITH (fillfactor='100');


--
-- Name: save_relationship; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.save_relationship (
    submission_id integer NOT NULL,
    user_id integer NOT NULL,
    created_utc integer
);


--
-- Name: sub_blocks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sub_blocks (
    user_id integer NOT NULL,
    sub character varying(25) NOT NULL,
    created_utc integer
);


--
-- Name: sub_joins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sub_joins (
    user_id integer NOT NULL,
    sub character varying(25) NOT NULL,
    created_utc integer
);


--
-- Name: sub_subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sub_subscriptions (
    user_id integer NOT NULL,
    sub character varying(25) NOT NULL,
    created_utc integer
);


--
-- Name: submission_option_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.submission_option_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: submission_option_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.submission_option_votes (
    option_id integer NOT NULL,
    user_id integer NOT NULL,
    created_utc integer NOT NULL,
    submission_id integer
);


--
-- Name: submission_options; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.submission_options (
    id integer DEFAULT nextval('public.submission_option_id_seq'::regclass) NOT NULL,
    submission_id integer NOT NULL,
    body_html character varying(500) NOT NULL,
    exclusive integer NOT NULL,
    created_utc integer
);


--
-- Name: submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.submissions_id_seq OWNED BY public.submissions.id;


--
-- Name: subs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subs (
    name character varying(25) NOT NULL,
    sidebar character varying(10000),
    sidebar_html character varying(20000),
    sidebarurl character varying(60),
    bannerurl character varying(60),
    css character varying(6000),
    stealth boolean,
    marseyurl character varying(60),
    created_utc integer
);


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subscriptions (
    user_id integer NOT NULL,
    submission_id integer NOT NULL,
    created_utc integer
);


--
-- Name: userblocks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.userblocks (
    user_id integer NOT NULL,
    target_id integer NOT NULL,
    created_utc integer
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(30) NOT NULL,
    email character varying(255),
    passhash character varying(255) NOT NULL,
    created_utc integer NOT NULL,
    admin_level integer DEFAULT 0 NOT NULL,
    over_18 boolean DEFAULT false NOT NULL,
    is_activated boolean DEFAULT false NOT NULL,
    bio character varying(1500),
    bio_html character varying(10000),
    referred_by integer,
    is_banned integer DEFAULT 0 NOT NULL,
    ban_reason character varying(256),
    login_nonce integer DEFAULT 0 NOT NULL,
    reserved character varying(256),
    mfa_secret character varying(32),
    is_private boolean DEFAULT false NOT NULL,
    unban_utc integer DEFAULT 0 NOT NULL,
    is_nofollow boolean DEFAULT false NOT NULL,
    custom_filter_list character varying(1000) DEFAULT ''::character varying,
    discord_id character varying(64),
    stored_subscriber_count integer DEFAULT 0 NOT NULL,
    ban_evade integer DEFAULT 0 NOT NULL,
    original_username character varying(30),
    customtitle character varying(1000),
    defaultsorting character varying(15) DEFAULT 'hot'::character varying NOT NULL,
    defaulttime character varying(5) NOT NULL,
    namecolor character varying(6) NOT NULL,
    titlecolor character varying(6) NOT NULL,
    profileurl character varying(65),
    bannerurl character varying(65),
    hidevotedon boolean DEFAULT false NOT NULL,
    newtab boolean DEFAULT false NOT NULL,
    flairchanged integer,
    defaultsortingcomments character varying(15) DEFAULT 'top'::character varying NOT NULL,
    theme character varying(15) NOT NULL,
    song character varying(50),
    slurreplacer boolean DEFAULT true NOT NULL,
    shadowbanned character varying(25),
    newtabexternal boolean DEFAULT true NOT NULL,
    customtitleplain character varying(100),
    themecolor character varying(6) NOT NULL,
    css character varying(4000),
    profilecss character varying(4000),
    coins integer DEFAULT 0 NOT NULL,
    agendaposter integer DEFAULT 0 NOT NULL,
    post_count integer DEFAULT 0 NOT NULL,
    comment_count integer DEFAULT 0 NOT NULL,
    highres character varying(60),
    patron integer DEFAULT 0 NOT NULL,
    controversial boolean DEFAULT false NOT NULL,
    background character varying(20),
    verified character varying(100),
    cardview boolean NOT NULL,
    received_award_count integer DEFAULT 0 NOT NULL,
    highlightcomments boolean DEFAULT true NOT NULL,
    nitter boolean,
    truecoins integer DEFAULT 0 NOT NULL,
    club_allowed boolean,
    frontsize integer DEFAULT 25 NOT NULL,
    coins_spent integer DEFAULT 0 NOT NULL,
    procoins integer DEFAULT 0 NOT NULL,
    mute boolean,
    unmutable boolean,
    verifiedcolor character varying(6),
    marseyawarded integer,
    sig character varying(200),
    sig_html character varying(1000),
    friends character varying(500),
    friends_html character varying(2000),
    sigs_disabled boolean,
    enemies character varying(500),
    enemies_html character varying(2000),
    fp character varying(21),
    eye boolean,
    alt boolean,
    longpost integer,
    unblockable boolean,
    bird integer,
    fish boolean,
    lootboxes_bought integer DEFAULT 0 NOT NULL,
    progressivestack integer,
    winnings integer DEFAULT 0 NOT NULL,
    patron_utc integer DEFAULT 0 NOT NULL,
    rehab integer,
    house character varying(16),
    deflector integer,
    reddit character varying(15) NOT NULL,
    currently_held_lottery_tickets integer DEFAULT 0 NOT NULL,
    total_held_lottery_tickets integer DEFAULT 0 NOT NULL,
    total_lottery_winnings integer DEFAULT 0 NOT NULL,
    offsitementions boolean DEFAULT false NOT NULL,
    last_active integer DEFAULT 0 NOT NULL,
    poorcel boolean DEFAULT false NOT NULL,
    last_viewed_post_notifs integer NOT NULL,
    pronouns character varying(11) NOT NULL,
    last_viewed_log_notifs integer NOT NULL,
    imginn boolean,
    earlylife integer,
    bite integer,
    old_house character varying(16),
    owoify integer,
    marsify integer,
    is_muted boolean DEFAULT false NOT NULL,
    coins_spent_on_hats integer DEFAULT 0 NOT NULL,
    rainbow integer
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: viewers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.viewers (
    user_id integer NOT NULL,
    viewer_id integer NOT NULL,
    last_view_utc integer NOT NULL,
    created_utc integer
);


--
-- Name: votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.votes (
    user_id integer NOT NULL,
    submission_id integer NOT NULL,
    vote_type integer NOT NULL,
    app_id integer,
    "real" boolean DEFAULT true NOT NULL,
    created_utc integer NOT NULL
);


--
-- Name: award_relationships id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships ALTER COLUMN id SET DEFAULT nextval('public.award_relationships_id_seq'::regclass);


--
-- Name: badge_defs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badge_defs ALTER COLUMN id SET DEFAULT nextval('public.badge_defs_id_seq'::regclass);


--
-- Name: casino_games id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.casino_games ALTER COLUMN id SET DEFAULT nextval('public.casino_games_id_seq'::regclass);


--
-- Name: category id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category ALTER COLUMN id SET DEFAULT nextval('public.category_id_seq'::regclass);


--
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);


--
-- Name: hat_defs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hat_defs ALTER COLUMN id SET DEFAULT nextval('public.hat_defs_id_seq'::regclass);


--
-- Name: lotteries id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lotteries ALTER COLUMN id SET DEFAULT nextval('public.lotteries_id_seq'::regclass);


--
-- Name: modactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modactions ALTER COLUMN id SET DEFAULT nextval('public.modactions_id_seq'::regclass);


--
-- Name: oauth_apps id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oauth_apps ALTER COLUMN id SET DEFAULT nextval('public.oauth_apps_id_seq'::regclass);


--
-- Name: submissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions ALTER COLUMN id SET DEFAULT nextval('public.submissions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: alts alts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alts
    ADD CONSTRAINT alts_pkey PRIMARY KEY (user1, user2);


--
-- Name: award_relationships award_constraint; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_constraint UNIQUE (user_id, submission_id, comment_id);


--
-- Name: award_relationships award_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_relationships_pkey PRIMARY KEY (id);


--
-- Name: badge_defs badge_def_name_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badge_defs
    ADD CONSTRAINT badge_def_name_unique UNIQUE (name);


--
-- Name: badge_defs badge_defs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badge_defs
    ADD CONSTRAINT badge_defs_pkey PRIMARY KEY (id);


--
-- Name: badges badges_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badges
    ADD CONSTRAINT badges_pkey PRIMARY KEY (user_id, badge_id);


--
-- Name: casino_games casino_games_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.casino_games
    ADD CONSTRAINT casino_games_pkey PRIMARY KEY (id);


--
-- Name: category category_name_sub_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_name_sub_key UNIQUE (name, sub);


--
-- Name: category category_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_pkey PRIMARY KEY (id);


--
-- Name: client_auths client_auths_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_auths
    ADD CONSTRAINT client_auths_pkey PRIMARY KEY (user_id, oauth_client);


--
-- Name: comment_option_votes comment_option_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_option_votes
    ADD CONSTRAINT comment_option_votes_pkey PRIMARY KEY (option_id, user_id);


--
-- Name: comment_options comment_options_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_options
    ADD CONSTRAINT comment_options_pkey PRIMARY KEY (id);


--
-- Name: comment_save_relationship comment_save_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_save_relationship
    ADD CONSTRAINT comment_save_relationship_pkey PRIMARY KEY (user_id, comment_id);


--
-- Name: commentflags commentflags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentflags
    ADD CONSTRAINT commentflags_pkey PRIMARY KEY (comment_id, user_id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: commentvotes commentvotes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentvotes
    ADD CONSTRAINT commentvotes_pkey PRIMARY KEY (comment_id, user_id);


--
-- Name: banneddomains domain_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.banneddomains
    ADD CONSTRAINT domain_pkey PRIMARY KEY (domain);


--
-- Name: exiles exiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exiles
    ADD CONSTRAINT exiles_pkey PRIMARY KEY (user_id, sub);


--
-- Name: flags flags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.flags
    ADD CONSTRAINT flags_pkey PRIMARY KEY (post_id, user_id);


--
-- Name: follows follows_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follows
    ADD CONSTRAINT follows_pkey PRIMARY KEY (target_id, user_id);


--
-- Name: hat_defs hat_defs_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hat_defs
    ADD CONSTRAINT hat_defs_name_key UNIQUE (name);


--
-- Name: hat_defs hat_defs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hat_defs
    ADD CONSTRAINT hat_defs_pkey PRIMARY KEY (id);


--
-- Name: hats hats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hats
    ADD CONSTRAINT hats_pkey PRIMARY KEY (user_id, hat_id);


--
-- Name: lotteries lotteries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lotteries
    ADD CONSTRAINT lotteries_pkey PRIMARY KEY (id);


--
-- Name: marseys marseys_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marseys
    ADD CONSTRAINT marseys_pkey PRIMARY KEY (name);


--
-- Name: modactions modactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modactions
    ADD CONSTRAINT modactions_pkey PRIMARY KEY (id);


--
-- Name: mods mods_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mods
    ADD CONSTRAINT mods_pkey PRIMARY KEY (user_id, sub);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (user_id, comment_id);


--
-- Name: oauth_apps oauth_apps_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oauth_apps
    ADD CONSTRAINT oauth_apps_pkey PRIMARY KEY (id);


--
-- Name: users one_banner; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT one_banner UNIQUE (bannerurl);


--
-- Name: users one_discord_account; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT one_discord_account UNIQUE (discord_id);


--
-- Name: pgbench_accounts pgbench_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pgbench_accounts
    ADD CONSTRAINT pgbench_accounts_pkey PRIMARY KEY (aid);


--
-- Name: pgbench_branches pgbench_branches_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pgbench_branches
    ADD CONSTRAINT pgbench_branches_pkey PRIMARY KEY (bid);


--
-- Name: pgbench_tellers pgbench_tellers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pgbench_tellers
    ADD CONSTRAINT pgbench_tellers_pkey PRIMARY KEY (tid);


--
-- Name: save_relationship save_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.save_relationship
    ADD CONSTRAINT save_relationship_pkey PRIMARY KEY (user_id, submission_id);


--
-- Name: sub_blocks sub_blocks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_blocks
    ADD CONSTRAINT sub_blocks_pkey PRIMARY KEY (user_id, sub);


--
-- Name: sub_joins sub_joins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_joins
    ADD CONSTRAINT sub_joins_pkey PRIMARY KEY (user_id, sub);


--
-- Name: sub_subscriptions sub_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_subscriptions
    ADD CONSTRAINT sub_subscriptions_pkey PRIMARY KEY (user_id, sub);


--
-- Name: submission_option_votes submission_option_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submission_option_votes
    ADD CONSTRAINT submission_option_votes_pkey PRIMARY KEY (option_id, user_id);


--
-- Name: submission_options submission_options_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submission_options
    ADD CONSTRAINT submission_options_pkey PRIMARY KEY (id);


--
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);


--
-- Name: subs subs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subs
    ADD CONSTRAINT subs_pkey PRIMARY KEY (name);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (submission_id, user_id);


--
-- Name: users uid_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT uid_unique UNIQUE (id);


--
-- Name: client_auths unique_access; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_auths
    ADD CONSTRAINT unique_access UNIQUE (access_token);


--
-- Name: oauth_apps unique_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oauth_apps
    ADD CONSTRAINT unique_id UNIQUE (client_id);


--
-- Name: userblocks userblocks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.userblocks
    ADD CONSTRAINT userblocks_pkey PRIMARY KEY (user_id, target_id);


--
-- Name: users users_original_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_original_username_key UNIQUE (original_username);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (username);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: viewers viewers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.viewers
    ADD CONSTRAINT viewers_pkey PRIMARY KEY (user_id, viewer_id);


--
-- Name: votes votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_pkey PRIMARY KEY (submission_id, user_id);


--
-- Name: alts_unique_combination; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX alts_unique_combination ON public.alts USING btree (GREATEST(user1, user2), LEAST(user1, user2));


--
-- Name: alts_user2_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX alts_user2_idx ON public.alts USING btree (user2);


--
-- Name: award_comment_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX award_comment_idx ON public.award_relationships USING btree (comment_id);


--
-- Name: award_post_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX award_post_idx ON public.award_relationships USING btree (submission_id);


--
-- Name: award_user_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX award_user_idx ON public.award_relationships USING btree (user_id);


--
-- Name: badges_badge_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX badges_badge_id_idx ON public.badges USING btree (badge_id);


--
-- Name: block_target_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX block_target_idx ON public.userblocks USING btree (target_id);


--
-- Name: cflag_user_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX cflag_user_idx ON public.commentflags USING btree (user_id);


--
-- Name: comment_parent_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comment_parent_index ON public.comments USING btree (parent_comment_id);


--
-- Name: comment_post_id_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comment_post_id_index ON public.comments USING btree (parent_submission);


--
-- Name: comments_user_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX comments_user_index ON public.comments USING btree (author_id);


--
-- Name: commentvotes_comments_type_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX commentvotes_comments_type_index ON public.commentvotes USING btree (vote_type);


--
-- Name: cvote_user_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX cvote_user_index ON public.commentvotes USING btree (user_id);


--
-- Name: discord_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX discord_id_idx ON public.users USING btree (discord_id);


--
-- Name: domains_domain_trgm_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX domains_domain_trgm_idx ON public.banneddomains USING gin (domain public.gin_trgm_ops);


--
-- Name: fki_comment_approver_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_comment_approver_fkey ON public.comments USING btree (is_approved);


--
-- Name: fki_comment_save_relationship_comment_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_comment_save_relationship_comment_fkey ON public.comment_save_relationship USING btree (comment_id);


--
-- Name: fki_comment_sentto_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_comment_sentto_fkey ON public.comments USING btree (sentto);


--
-- Name: fki_exile_exiler_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_exile_exiler_fkey ON public.exiles USING btree (exiler_id);


--
-- Name: fki_exile_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_exile_sub_fkey ON public.exiles USING btree (sub);


--
-- Name: fki_mod_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_mod_sub_fkey ON public.mods USING btree (sub);


--
-- Name: fki_modactions_user_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_modactions_user_fkey ON public.modactions USING btree (target_user_id);


--
-- Name: fki_save_relationship_submission_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_save_relationship_submission_fkey ON public.save_relationship USING btree (submission_id);


--
-- Name: fki_sub_blocks_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_sub_blocks_sub_fkey ON public.sub_blocks USING btree (sub);


--
-- Name: fki_sub_joins_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_sub_joins_sub_fkey ON public.sub_joins USING btree (sub);


--
-- Name: fki_sub_subscriptions_sub_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_sub_subscriptions_sub_fkey ON public.sub_subscriptions USING btree (sub);


--
-- Name: fki_submissions_approver_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_submissions_approver_fkey ON public.submissions USING btree (is_approved);


--
-- Name: fki_user_referrer_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_user_referrer_fkey ON public.users USING btree (referred_by);


--
-- Name: fki_view_viewer_fkey; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fki_view_viewer_fkey ON public.viewers USING btree (viewer_id);


--
-- Name: flag_user_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX flag_user_idx ON public.flags USING btree (user_id);


--
-- Name: follow_user_id_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX follow_user_id_index ON public.follows USING btree (user_id);


--
-- Name: hat_defs_submitter_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hat_defs_submitter_id_idx ON public.hat_defs USING btree (submitter_id);


--
-- Name: lowercase_original_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX lowercase_original_username ON public.users USING btree (lower((original_username)::text));


--
-- Name: lowercase_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX lowercase_username ON public.users USING btree (lower((username)::text));


--
-- Name: marseys_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX marseys_idx ON public.marseys USING btree (name);


--
-- Name: marseys_idx2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX marseys_idx2 ON public.marseys USING btree (author_id);


--
-- Name: marseys_idx3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX marseys_idx3 ON public.marseys USING btree (count DESC);


--
-- Name: marseys_idx4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX marseys_idx4 ON public.marseys USING btree (submitter_id);


--
-- Name: modaction_action_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX modaction_action_idx ON public.modactions USING btree (kind);


--
-- Name: modaction_cid_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX modaction_cid_idx ON public.modactions USING btree (target_comment_id);


--
-- Name: modaction_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX modaction_id_idx ON public.modactions USING btree (id DESC);


--
-- Name: modaction_pid_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX modaction_pid_idx ON public.modactions USING btree (target_submission_id);


--
-- Name: notification_read_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notification_read_idx ON public.notifications USING btree (read);


--
-- Name: notifications_comment_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifications_comment_idx ON public.notifications USING btree (comment_id);


--
-- Name: notifs_user_read_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifs_user_read_idx ON public.notifications USING btree (user_id, read);


--
-- Name: option_comment; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX option_comment ON public.comment_options USING btree (comment_id);


--
-- Name: option_submission; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX option_submission ON public.submission_options USING btree (submission_id);


--
-- Name: post_app_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX post_app_id_idx ON public.submissions USING btree (app_id);


--
-- Name: subimssion_binary_group_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX subimssion_binary_group_idx ON public.submissions USING btree (is_banned, deleted_utc, over_18);


--
-- Name: submission_isbanned_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX submission_isbanned_idx ON public.submissions USING btree (is_banned);


--
-- Name: submission_isdeleted_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX submission_isdeleted_idx ON public.submissions USING btree (deleted_utc);


--
-- Name: submission_new_sort_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX submission_new_sort_idx ON public.submissions USING btree (is_banned, deleted_utc, created_utc DESC, over_18);


--
-- Name: submission_pinned_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX submission_pinned_idx ON public.submissions USING btree (is_pinned);


--
-- Name: submissions_author_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX submissions_author_index ON public.submissions USING btree (author_id);


--
-- Name: submissions_created_utc_asc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX submissions_created_utc_asc_idx ON public.submissions USING btree (created_utc NULLS FIRST);


--
-- Name: submissions_created_utc_desc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX submissions_created_utc_desc_idx ON public.submissions USING btree (created_utc DESC);


--
-- Name: submissions_over18_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX submissions_over18_index ON public.submissions USING btree (over_18);


--
-- Name: subs_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX subs_idx ON public.subs USING btree (name);


--
-- Name: subscription_user_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX subscription_user_index ON public.subscriptions USING btree (user_id);


--
-- Name: user_banned_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX user_banned_idx ON public.users USING btree (is_banned);


--
-- Name: user_private_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX user_private_idx ON public.users USING btree (is_private);


--
-- Name: users_created_utc_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_created_utc_index ON public.users USING btree (created_utc);


--
-- Name: users_original_username_trgm_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_original_username_trgm_idx ON public.users USING gin (original_username public.gin_trgm_ops);


--
-- Name: users_subs_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_subs_idx ON public.users USING btree (stored_subscriber_count);


--
-- Name: users_unbanutc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_unbanutc_idx ON public.users USING btree (unban_utc DESC);


--
-- Name: users_username_trgm_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_username_trgm_idx ON public.users USING gin (username public.gin_trgm_ops);


--
-- Name: vote_user_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX vote_user_index ON public.votes USING btree (user_id);


--
-- Name: votes_type_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX votes_type_index ON public.votes USING btree (vote_type);


--
-- Name: alts alt_user1_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alts
    ADD CONSTRAINT alt_user1_fkey FOREIGN KEY (user1) REFERENCES public.users(id);


--
-- Name: alts alt_user2_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alts
    ADD CONSTRAINT alt_user2_fkey FOREIGN KEY (user2) REFERENCES public.users(id);


--
-- Name: oauth_apps app_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oauth_apps
    ADD CONSTRAINT app_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: award_relationships award_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_comment_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id);


--
-- Name: award_relationships award_submission_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_submission_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id);


--
-- Name: award_relationships award_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: badges badges_badge_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badges
    ADD CONSTRAINT badges_badge_id_fkey FOREIGN KEY (badge_id) REFERENCES public.badge_defs(id);


--
-- Name: badges badges_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.badges
    ADD CONSTRAINT badges_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: userblocks block_target_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.userblocks
    ADD CONSTRAINT block_target_fkey FOREIGN KEY (target_id) REFERENCES public.users(id);


--
-- Name: userblocks block_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.userblocks
    ADD CONSTRAINT block_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: casino_games casino_games_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.casino_games
    ADD CONSTRAINT casino_games_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: category category_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name);


--
-- Name: client_auths client_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_auths
    ADD CONSTRAINT client_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: comments comment_approver_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comment_approver_fkey FOREIGN KEY (is_approved) REFERENCES public.users(id);


--
-- Name: comments comment_parent_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comment_parent_comment_fkey FOREIGN KEY (parent_comment_id) REFERENCES public.comments(id);


--
-- Name: comments comment_parent_submission_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comment_parent_submission_fkey FOREIGN KEY (parent_submission) REFERENCES public.submissions(id);


--
-- Name: comment_save_relationship comment_save_relationship_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_save_relationship
    ADD CONSTRAINT comment_save_relationship_comment_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) MATCH FULL;


--
-- Name: comment_save_relationship comment_save_relationship_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_save_relationship
    ADD CONSTRAINT comment_save_relationship_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: comments comment_sentto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comment_sentto_fkey FOREIGN KEY (sentto) REFERENCES public.users(id);


--
-- Name: commentflags commentflags_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentflags
    ADD CONSTRAINT commentflags_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id);


--
-- Name: commentflags commentflags_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentflags
    ADD CONSTRAINT commentflags_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: comments comments_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: commentvotes commentvote_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentvotes
    ADD CONSTRAINT commentvote_comment_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) MATCH FULL;


--
-- Name: commentvotes commentvote_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commentvotes
    ADD CONSTRAINT commentvote_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: exiles exile_exiler_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exiles
    ADD CONSTRAINT exile_exiler_fkey FOREIGN KEY (exiler_id) REFERENCES public.users(id);


--
-- Name: exiles exile_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exiles
    ADD CONSTRAINT exile_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name);


--
-- Name: exiles exile_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exiles
    ADD CONSTRAINT exile_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: lotteries fk_winner; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lotteries
    ADD CONSTRAINT fk_winner FOREIGN KEY (winner_id) REFERENCES public.users(id);


--
-- Name: flags flags_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.flags
    ADD CONSTRAINT flags_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.submissions(id);


--
-- Name: flags flags_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.flags
    ADD CONSTRAINT flags_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: follows follow_target_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follows
    ADD CONSTRAINT follow_target_fkey FOREIGN KEY (target_id) REFERENCES public.users(id);


--
-- Name: follows follow_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follows
    ADD CONSTRAINT follow_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: hat_defs hat_def_submitter_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hat_defs
    ADD CONSTRAINT hat_def_submitter_fkey FOREIGN KEY (submitter_id) REFERENCES public.users(id);


--
-- Name: hat_defs hat_defs_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hat_defs
    ADD CONSTRAINT hat_defs_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: hats hats_hat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hats
    ADD CONSTRAINT hats_hat_id_fkey FOREIGN KEY (hat_id) REFERENCES public.hat_defs(id);


--
-- Name: hats hats_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hats
    ADD CONSTRAINT hats_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: marseys marsey_author_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marseys
    ADD CONSTRAINT marsey_author_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: marseys marsey_submitter_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marseys
    ADD CONSTRAINT marsey_submitter_fkey FOREIGN KEY (submitter_id) REFERENCES public.users(id);


--
-- Name: mods mod_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mods
    ADD CONSTRAINT mod_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name);


--
-- Name: modactions modactions_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modactions
    ADD CONSTRAINT modactions_comment_fkey FOREIGN KEY (target_comment_id) REFERENCES public.comments(id);


--
-- Name: modactions modactions_submission_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modactions
    ADD CONSTRAINT modactions_submission_fkey FOREIGN KEY (target_submission_id) REFERENCES public.submissions(id);


--
-- Name: modactions modactions_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.modactions
    ADD CONSTRAINT modactions_user_fkey FOREIGN KEY (target_user_id) REFERENCES public.users(id);


--
-- Name: notifications notifications_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: client_auths oauth_client_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client_auths
    ADD CONSTRAINT oauth_client_fkey FOREIGN KEY (oauth_client) REFERENCES public.oauth_apps(id);


--
-- Name: comment_options option_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_options
    ADD CONSTRAINT option_comment_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) MATCH FULL;


--
-- Name: submission_options option_submission_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submission_options
    ADD CONSTRAINT option_submission_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id) MATCH FULL;


--
-- Name: save_relationship save_relationship_submission_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.save_relationship
    ADD CONSTRAINT save_relationship_submission_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id) MATCH FULL;


--
-- Name: save_relationship save_relationship_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.save_relationship
    ADD CONSTRAINT save_relationship_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: sub_blocks sub_blocks_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_blocks
    ADD CONSTRAINT sub_blocks_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name) MATCH FULL;


--
-- Name: sub_blocks sub_blocks_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_blocks
    ADD CONSTRAINT sub_blocks_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: submissions sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name);


--
-- Name: sub_joins sub_joins_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_joins
    ADD CONSTRAINT sub_joins_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name) MATCH FULL;


--
-- Name: sub_joins sub_joins_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_joins
    ADD CONSTRAINT sub_joins_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: sub_subscriptions sub_subscriptions_sub_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_subscriptions
    ADD CONSTRAINT sub_subscriptions_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name) MATCH FULL;


--
-- Name: sub_subscriptions sub_subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sub_subscriptions
    ADD CONSTRAINT sub_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: submissions submissions_approver_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_approver_fkey FOREIGN KEY (is_approved) REFERENCES public.users(id);


--
-- Name: submissions submissions_author_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_author_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: submissions submissions_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.category(id) ON DELETE SET NULL;


--
-- Name: subscriptions subscription_submission_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscription_submission_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id);


--
-- Name: subscriptions subscription_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscription_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: mods user_mod_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mods
    ADD CONSTRAINT user_mod_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users user_referrer_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT user_referrer_fkey FOREIGN KEY (referred_by) REFERENCES public.users(id);


--
-- Name: viewers view_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.viewers
    ADD CONSTRAINT view_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: viewers view_viewer_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.viewers
    ADD CONSTRAINT view_viewer_fkey FOREIGN KEY (viewer_id) REFERENCES public.users(id);


--
-- Name: comment_option_votes vote_comment_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_option_votes
    ADD CONSTRAINT vote_comment_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) MATCH FULL;


--
-- Name: submission_option_votes vote_option_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submission_option_votes
    ADD CONSTRAINT vote_option_fkey FOREIGN KEY (option_id) REFERENCES public.submission_options(id) MATCH FULL;


--
-- Name: comment_option_votes vote_option_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_option_votes
    ADD CONSTRAINT vote_option_fkey FOREIGN KEY (option_id) REFERENCES public.comment_options(id) MATCH FULL;


--
-- Name: submission_option_votes vote_submission_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submission_option_votes
    ADD CONSTRAINT vote_submission_fkey FOREIGN KEY (submission_id) REFERENCES public.submissions(id) MATCH FULL;


--
-- Name: votes vote_submission_key; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT vote_submission_key FOREIGN KEY (submission_id) REFERENCES public.submissions(id);


--
-- Name: votes vote_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT vote_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: submission_option_votes vote_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submission_option_votes
    ADD CONSTRAINT vote_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- Name: comment_option_votes vote_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment_option_votes
    ADD CONSTRAINT vote_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.4
-- Dumped by pg_dump version 14.5 (Ubuntu 14.5-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: badge_defs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.badge_defs (id, name, description, created_utc) FROM stdin;
136	TRAIN 2022	Beware: Found to be one of the most transmisic commenters on the site!	\N
137	Lottershe Winner	This user won the Lottershe grand prize.	\N
140	Y'all Seein' Eye	Gets notified when other sites talk about us	\N
141	Marsey Typographer	For substantial and exceptional contributions to Marsey Alphabet.	\N
142	Punching Down	This user mogs incels.	\N
143	Marsey God	Contributed 100 (or more!!!!) Marsey emojis ✨😻	\N
144	Energy Drink Enjoyer	Grip 'N Sip.	\N
147	Freebase Fiend	From the crack grew a glass rose.	\N
148	Blackpilled	Proud incel ally.	\N
149	Thin	This user has verified that they are calorically disciplined.	\N
139	Auspicious Incident	This user was fired from a volunteer position	\N
150	Verified	Bought a Blue Checkmark.	\N
151	Responsible Citizen	This user upheld democracy by committing voter fraud.	\N
152	Amateur Hathead	Collected 25 unique hats	\N
155	Ride Or Die Dramalo/Dramalette	When I die show no pity / Send my soul to the juggalo city / Dig my grave six feet deep / And put two matches by my feet / Put two hatchets on my chest / And tell my homies I did my best / WHOOP WHOOP	\N
156	Hole Neglecter	Brought a Hole into this world, only to let it die	\N
21	Paypig	Contributed at least $5	\N
22	Renthog	Contributed at least $10	\N
23	Landchad	Contributed at least $20	\N
24	Terminally online turboautist	Contributed at least $50	\N
157	A Minor Setback	Lost a 1,000 dramacoin bet. Keep going!	\N
158	Just One More Hand	Lost a 10,000 dramacoin bet. But it's fine, you're due for a big win!	\N
160	Lil Goombler	Won a 1,000 dramacoin bet. Nice job!	\N
162	King Goombler	Won a 100,000 dramacoin bet. Wipe your sweaty palms off and bet it all again, you're on a roll!	\N
163	Marsey Jacobs	Designed 10 hats!	\N
166	Giorgio Armarsey	Designed 250 hats 😲	\N
164	Marsey de Givenchy	Designed 50 hats, holy cap.	\N
168	BITTEN!	This user has been forcibly recruited to House Vampire	\N
170	Marsified	This user's comments get Marsified automatically	\N
167	OwOified	This user's comments get OwOified automatically	\N
169	Early Life Checked	The Early Life section of this user is on full display	\N
172	God Save The Kween	Commemorative badge awarded for outliving Her Maj	\N
174	George	@Marsey went to Spokane to fight @TrailerParkBride, but George the Mountain Lion was the real winner.	\N
4	White Hat	Discreetly reported an exploit	\N
1	Alpha User	Joined during open alpha	\N
2	Verified Email	Verified Email	\N
3	Code Contributor	Contributed to the site's source code	\N
6	Beta User	Joined during open beta	\N
7	Bug Chaser	Found a bug	\N
10	Bronze Recruiter	Recruited 1 friend to join the site	\N
11	Silver Recruiter	Recruited 10 friends to join the site	\N
12	Gold Recruiter	Recruited 100 friends to join the site	\N
15	Idea Maker	Had a good idea for the site which was implemented by the developers	\N
16	Marsey Master	Contributed 10 (or more!!!!) Marsey emojis ✨	\N
17	Marsey Artisan	Contributed a Marsey emoji ✨	\N
18	Artisan	Contributed to site artwork	\N
85	Sigma User		\N
145	Amphetamine Aficionado	Totally not addicted™	\N
146	Coffee Consoomer	Don't talk to me until I've had my soy latte.	\N
60	Unironically Retarded	Demonstrated a wholesale inability to read the room	\N
61	Lab Rat	Helped test features in development	\N
62	Master Baiter	For outstanding achievement in the field of catching fish	\N
63	Balls	I wrote carp on my balls as a sign of submission	\N
64	The Other Kind Of Good Journalist	Contributed positive media attention to the site	\N
65	2021 Spooooooky Marsey Artist	Contributed a VERY SCARY Marsey for Halloween 2021!	\N
66	Sk8r Boi	Certifies that this user is NOT a poser	\N
67	Unpausable	Spent 40,000 coins on an unpausable profile anthem	\N
68	Pause Button	Spent 20,000 coins on a profile anthem pause button	\N
69	Little Big Spender	Dropped 10,000 coins at the shop	\N
70	Big Spender	Dropped 100,000 coins at the shop	\N
71	Big Big Spender	Dropped 250,000 coins at the shop	\N
72	Big Big Big Spender	Dropped 500,000 coins at the shop	\N
73	Le Rich Gentlesir	Spent a fucking million coins at the shop	\N
74	Grass Toucher	Awarded for molesting plant life	\N
75	Halloween 21	Awarded for surviving Homoween 2021	\N
76	Low Roller	Bought 10 lootboxes	\N
77	Middle Roller	Bought 50 lootboxes	\N
78	High Roller	Bought 150 lootboxes	\N
79	Merchant	Contributed a new line of product to Marsey's Coin Emporium	\N
80	Artist Laureate		\N
81	Patron of the Arts	Sponsored the creation of an approved Marsey	\N
83	All-Seeing Eye	Can view private profiles	\N
84	Alt-Seeing Eye	Can see alts	\N
86	Holly Jolly Marsey Artist	Contributed a VERY JOLLY Marsey for Christmas 2021!	\N
87	Unblockable	This user is unblockable	\N
88	Provider	This user provided a bountiful feast for Thanksgiving	\N
89	Dinner	Yes, it is edible	\N
90	Fish	This user cannot be unfollowed	\N
91	Grinch	This user is a joyless grinch who pays money to avoid having fun	\N
92	NFT Artist	Drew a marsey that was used as an NFT	\N
93	NFT Owner	Bought a marsey NFT	\N
94	Progressive Stack Award	Upvotes/downvotes on this user's posts and comments have double the ranking effect	\N
95	Bird Site Award	This user is limited to 140 characters	\N
96	Flairlock Award	This user's flair has been locked by someone else	\N
97	Pizzashill Award	This user has to make their posts and comments more than 280 characters	\N
98	Marsey Award	This user is limited to posting marseys	\N
99	Sidebar Artist	Contributed artwork featured on the sidebar	\N
100	True Believer	This user sees through communist lies	\N
101	Banner Artist	Contributed a banner image to the site	\N
102	Christmas 21	Awarded for surviving Fistmas 2021	\N
103	Benefactor	Gave the Benefactor award to someone	\N
104	BADASS OUTLAW	Bad boy who does not play by the rules	\N
105	SCAM	lmao get fucked retard	\N
153	Professional Hathead	Collected 100 unique hats	\N
107	Certified BIPOC	The mayocide starts now	\N
108	Nword Pass	With great power comes great responsibility	\N
154	Fiscally Irresponsible Hathead	Collected 250 unique hats	\N
110	Wolf Artisan	Contributed a Zombie Wolf emoji ✨	\N
111	Wolf Master	Contributed 10 (or more!!!!) Zombie Wolf emojis ✨	\N
112	Platy Artisan	Contributed a Platy emoji ✨	\N
113	Platy Master	Contributed 10 (or more!!!!) Platy emojis ✨	\N
109	Rehab Award	Prevented from gambling	\N
114	Capy Artisan	Contributed a Capy emoji ✨	\N
115	Capy Master	Contributed 10 (or more!!!!) Capy emojis ✨	\N
116	Outreach Award	Brought invaluable drama to the starving masses off-site	\N
128	Fart-Free	This user does NOT fart.	\N
117	Stone Skeptic	This user rejects igneous lies	\N
129	Misinformation Superspreader	This poster was fact checked by real American patriots	\N
130	Columbine Enthusiast (TEMPORAL FLUX EDITION)	This user is an acclaimed Reb+VoDKa slash author	\N
159	It's Over	Lost a 100,000 dramacoin bet. It's fucking over.	\N
161	Pro Goombler	Won a 10,000 dramacoin bet. Some would say to quit while you're ahead, but they didn't just win 10k - keep at it!	\N
165	Marsey Chanel	Designed 100 hats!!!	\N
28	Chud	Marked as a chud	\N
171	Rainbowed	This user has super cute text	\N
135	1st Birthgay Bash Survivor	Awarded for surviving rDrama's first annual Birthgay Bash	\N
59	Lolcow	Beautiful and valid milk provider	\N
25	Marsey's Sugar Daddy	Contributed at least $100	\N
26	JIDF Bankroller	Donated at least $250	\N
27	Rich Bich	Contributed at least $500	\N
118	Hit!	Confirmed removal of a r/stupidpol post for hate speech or threatening violence	\N
119	BIG Hit!	Confirmed removal of a /r/stupidpol MODERATOR'S post for hate speech or threatening violence	\N
120	Msar Bomba	Confirmed ban of a r/stupidpol user	\N
121	Order of Marsey, 2nd Class	Confirmed temp ban of a r/stupidpol moderator	\N
122	Order of Marsey, 1st Class	Confirmed permanent ban of a /r/stupidpol moderator	\N
123	Hero of the Marsey Union	Awarded to all soldiers who served during the Special Military Operation to de-nazify r/stupidpol	\N
124	COOL GUY	This user does NOT watch anime	\N
125	Certified LOSER	This user watches anime	\N
126	Survivor	This user braved the Oregon Trail and lived to tell the tale	\N
127	Wagonfire	This user braved the Oregon Trail and fucking died lmao	\N
131	21st Century Hitlerite (TEMPORAL FLUX EDITION)	This user lost the love of their life in 1940s Berlin	\N
132	Duterte's Most Wanted (TEMPORAL FLUX EDITION)	dude weed lmao what year is it	\N
133	Rockstar	This user submitted an original piece to the song contest	\N
134	1 Year Old 🥰	This user has wasted an ENTIRE YEAR of their life here! Happy birthday!	\N
\.


--
-- Name: badge_defs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.badge_defs_id_seq', 174, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.4
-- Dumped by pg_dump version 14.5 (Ubuntu 14.5-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: marseys; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.marseys (name, author_id, tags, count, submitter_id, created_utc) FROM stdin;
marseyhawaii	3149	boomer margarita drink chill relaxed	2	\N	\N
marseyappicon	768	iphone ios android application googleplay samsung	0	\N	\N
marseyterfdomesticabuse	4928	terf domestic abuse violence feminism feminist lesbian ovarit radical	35	\N	\N
marseylongpost	4122	tldr reaction wall of text wordswordswords animated words	1361	\N	\N
marseytransflag	2866	trans flag then consumeproduct	311	\N	\N
marseyswastika	8197	nazi chud germany swasi swazi windmill of peace hitler racist racism antisemitic antisemitism third reich jewish jews	120	\N	\N
marseyburnedman	2622	joshua graham fallout vegas mormon caesar	0	\N	\N
marseysmugautist	2113	autism retard brainlet drool hat	1	\N	\N
marseylaughpoundfist	1738	cry tears lmao lol kek bully laughing funny mocking animated	2	\N	\N
marseykiwimom	5526	kf farms newzealand new zealand dramarama birds babies chicks single mother brood flock	67	\N	\N
marseybardfinn	10432	domestic violence bardfinn foid beating punching battering battered bandage hurt pain woman female steve akins penny verity oaken tranny transgender transsexual	99	\N	\N
marseyfedposthmmm	2890	glowie american dad stan meter fbi	0	\N	\N
marseybrainletclapping	2622	idiot dumb stupid applause cheering moron	0	2622	1663095832
marseylaughwith	1738	cry tears lol lmao haha laughing	0	\N	\N
marseysaint2	5214	angelic halo holy animated wings happy	0	\N	\N
marseytypinglaugh	3259	computer keyboard lol bongo animated	1	\N	\N
marseytime	5214	10pm tock tick clock animated	107	\N	\N
marseycapysuezcanal	3370	capy suez canal egypt ship blockage sexy	4	\N	\N
marseyeskimo	5214	inuit native arctic fishing dog helpful ice freeze winter cold	0	\N	\N
marseypizzaslice	5526	pizza shill longpost yum chef cook italian cheese pepperoni	0	\N	\N
marseyshock	12116	shock fear afraid terror scared horrified	2	\N	\N
marseyfugg2	4989	spurdo sparde	0	\N	\N
marseyliberty	5214	usa burger america statue lady republican democrat biden trump rightoid leftoid	1	\N	\N
marseyredflag	7913	warning red flag alert scum problematic	0	\N	\N
marseywtf2	2626	shocked reaction wth disturbing disturbed what the fuck	398	\N	\N
marseytrad2	5214	wojak tradwife soyjak 4chan meme foid	0	\N	\N
marseyliberty2	5214	usa burger america statue lady republican democrat biden trump rightoid leftoid	0	\N	\N
marseysoyseethe	5214	soyjack soyjak reddit angry yelling wojak	2	\N	\N
marseypastor	3259	christian baptist southern church black papist mrpenny preacher priest	108	\N	\N
marseyappleseed	8021	american usa johnny history folk fruit food pot pan helmet legend	2	\N	\N
marseyspecial	1387	retard reaction slow special needs sped	732	\N	\N
marseytemplate	4989	template blank faceless eyeless mouthless head empty faceless	4	\N	\N
marseyjacksparrow	5214	johnny depp amber heard abuse violence punch beat feminist Jack sparrow	0	\N	\N
marseyfediverse	10881	federation autism freespeech poast	4	\N	\N
marsey3d	5214	poly 3d print alive spin animated	0	\N	\N
marseymegalodon	541	shark carpathianflorist jaws attack eating killing	0	\N	\N
marseyreluctant	4588	stare doubt skeptical wary cautious uncertain uhh umm	0	\N	\N
marseyhillary	2626	president her turn hilary killary hilldawg clinton	158	\N	\N
marseyastronaut2	6225	cosmonaut spacesuit helmet	1	\N	\N
marseysmug2	5526	snicker scoff mock reaction guffaw ridicule judgment	2571	\N	\N
marseysnowglobe	1994	christmas tree small miniature	44	\N	\N
marseytwerking	2890	tailspin animated butt backside dancing spin booty ass dance	2473	\N	\N
marseyveryworried	4928	worry anxiety fear animated scared sweat yikes	1	\N	\N
marseyshutitdown	5214	cop glownigger fed glowie agent federal mossad israel idf the goyim know kikes radio walkie talkie	533	\N	\N
marseytransrentfree	150	transgender lgbt rent free wojak chud	0	\N	\N
marseycruisemissile	2616	war explosion bomb weapon military rocket enemy destroy kill nuke launch	1	\N	\N
marseywhiteflag	9394	surrender battle french	0	\N	\N
marseybackingintobush	11320	Homer Simpsons scared away animated hedge bush	0	\N	\N
marseyflakes	2608	parsley seasoning salt pepper spice food seasoning	0	\N	\N
marseydarkmarsey2	5214	lasereyes redglow scary chudrama	0	\N	\N
marseytyping	3259	computer keyboard bongo animated	0	\N	\N
marseysperm	768	cum swim vasectomy jizz semen spunk penis sex pregnant coom animated	0	\N	\N
marseysoren	2546	sleeping alt right altright racist nazi chud	105	\N	\N
marseythegrey	4588	lord of the rings magic gandalf lotr mage wizard warlock	107	\N	\N
marseyscratch	1710	loweffort doodle code coding programming	33	\N	\N
marseylain	1817	bear onesie pajamas fursuit furry	0	\N	\N
marseybestfriends	1710	snoo reddit alien slice kill kys stab blood wpd	0	\N	\N
marseybiden	2626	ddd dementia daddy president sleepy joe	577	\N	\N
marseypridepearlclutch	5214	lesbian gay bisexual homo lgb rainbow cry bigot tears	1	\N	\N
marseyusa	5214	burger patriot america freedom liberty justice love independence freedom guns trump biden state flag	249	\N	\N
marseyliathomas	1710	tranny transgender athlete lia thomas athletics woman valid lgbt swimmer aquamaam aqua maam	135	\N	\N
marseyschizotwitch	5214	twitching eyelid crazy nuts psycho insane traumatized animated	327	\N	\N
marseyearrape	10881	breakcore goreshit headphones noisecore	0	\N	\N
marseyjoy	12116	smile excited smug	0	\N	\N
marseygrin	12116	seethe pain rage beard angry	0	\N	\N
marseyletsfuckinggo	5214	lfg tennis ball screaming ready	0	\N	\N
marseycowboy	8979	western pardner reaction hat tootin yeehaw rootin	278	\N	\N
marseyfemboy	7056	discord trans femboy tomgirl groomer groomed gay faggot homosexual queer poof fairy	360	\N	\N
marseyunabomber2	1828	gift christmas industrial society delivery mail kaczynski uncle ted package	76	\N	\N
marseyfedpostglow	4122	cia longpost long fed fedpost read notes animated glowie glow	120	\N	\N
marseysaint	5214	wings angel blessed halo animated	124	\N	\N
marseyvargfinnselfdefense	2256	bardfinn steve akens aikens penny verity oaken tranny train troon transgender transvestite black metal trve kvlt euronymous varg vikernes mayhem burzum child abuse kid beating stabbing bloody	38	\N	\N
marseydance	5214	excited stomp jump feet step run animated	0	\N	\N
marseychonkerbutch	3259	fat obese brap bitch dyke dangerhair lesbian	0	\N	\N
marseylaughbothsides	1738	wingcuck radical centrist centrism animated horseshoe	2	\N	\N
marseywhirlyhat	3717	idiot retard hat dumb sped slow stupid special kid	676	\N	\N
marseyhugretard	3259	love idiot drool embrace	1	\N	\N
marseydunce	4084	stupid moron imbecile dolt dunce retard dumb cap hat sped	253	\N	\N
marseyschizo	635	harm burns selfharm self harm cigarette burning mermaids reaction artist self	460	\N	\N
marseycapitalistmanlet	1387	money top hat rich landlord cigar llm tophat	6138	\N	\N
marseybardfinn3	5244	bardfinn ahs powermod tranny trannies wifebeater abuser steve	2	\N	\N
marseyagree	4588	concur nodding nod reaction affirmative yes yeah uh huh animated judgment	4862	\N	\N
marseycleonpeterson2	5214	monster devil demon evil scary horror	0	\N	\N
marseydrunk2	2256	drinking shitfaced alcoholic liquor happy beer dizzy	53	\N	\N
marseysal2	7615	shark 2 weeks two weeks go nowhere going nowhere watch go nowhere	202	\N	\N
marseygambling	1387	depressed casino slots blackjack las vegas depressed suicidial degenerate smoking losing cards hotep	392	\N	\N
marseypepsi	1980	cola coke soda soft drink pop red white blue usa america	44	\N	\N
marseyfuckyou	1387	middlefinger middle finger flipping off fuck you nigga	264	\N	\N
marseygun	768	handgun shoot bang kill threaten pistol	0	\N	\N
marseyhatiun	5356	mad fury furious pissed hatred rage angry maddened infuriated hateful hatefuel	0	\N	\N
marseysoldierchina	1710	army war gun rifle asia chinese chink gook	46	\N	\N
marseyshortbus	768	bussy animated mrpenny carpathianflorist schizocel retard special short schoolbus classroom teacher wheels window rosa parks mlk	1	\N	\N
marseywait	8159	time watch wait waiting bored	169	\N	\N
marseyfine	5526	is fine meme thisisfine burning fire	158	\N	\N
marseymononoke	8021	anime japanese miyazaki ghibli asian cartoon princess character fictionnal ashitaka san wild wolf nature	2	\N	\N
marseybowl	8979	marijuana weed dude weed lmao ganja drugs reaction pot pipe	231	\N	\N
marseyklennywinner	3259	medal award dog klenvastergan corgi	1	\N	\N
marseytransattentionseeker	5214	needy enby nonbinary notice mtf ftm train attn	1	\N	\N
marseyrabbit	11715	bunny	0	\N	\N
marseycoomer2	5244	gooning masturbation fapping cumming gooner nofap	1	\N	\N
marseyascii	4017	blurry	23	\N	\N
marseycarpbuff	3259	muscles tough strong carpathianflorist admin mod jannie	0	\N	\N
marseymemeball	13710	picardia strawman polcomp political	1	\N	\N
marseydemonicgrin	13710	evil wicked horror teeth	1	\N	\N
marseypusheen	1817	grey gray	1	\N	\N
marseyblob	10881	smile owo uwu squish slime	2	\N	\N
marseydeadinside3	13710	depressed suicidal doomer tired despair wrinkled wrinkles	0	\N	\N
marseyoppenheimer	7480	scientist nuke bomb ww2 atomic nuclear mushroom cloud	0	\N	\N
marseytabletired	7913	tiresome depressed sad desk	2	\N	\N
marseydiversity	1994	greatest strength meta carp aevann platy zombiewolf zombie wolf	37	\N	\N
marseymissing2	2873	missing notexture source image not found broken	79	\N	\N
marseyfacepalm	542	reaction omfg judgment	1047	\N	\N
marseypaperbag	10214	ugly ashamed bagged butterface	2	\N	\N
marseynerd2	2626	geek glasses dork loser pimples zits	1	\N	\N
marseyarthoe	5845	scene slut foid whore emo scene bpd bangs dangerhair girl woman	0	\N	\N
marseykingretard	3259	drool dumb idiot crown moron	0	\N	\N
marseyropewithme	4989	suicide kys kms suicidal hanging noose	1	\N	\N
marseyfreud	1817	oedipus incest psychoanalysis psychologist shrink psychiatrist	2	\N	\N
marseyselfflagellation	5988	whip white guilt hate sin mayo liberal catholic	2	\N	\N
marseyinnocent	2490	innocent naive angelic dumb halo	0	\N	\N
marseyokapi	2626	okapi furry deer	2	\N	\N
marseycarpina	4928	carpathianflorist drag transgender admin jannie	0	\N	\N
marseybikecuck	3370	owlturd bicycle cuckold webcomic happiness	0	\N	\N
marseylenny	4989	innuendo dirty sex horny emoticon perverted	2	\N	\N
marseyssflag	7913	superstraight cishetero straggot pride	1	\N	\N
marseylgbtflag2	7913	pride gay inclusive queer ukraine bipoc	0	\N	\N
marseylgbtflag	7913	pride gay queer	1	\N	\N
marseykeffalsdance	10881	onesie pajamas animated fursuit hood wiggler	5	\N	\N
marseyworldcup	5988	world cup soccer football winner sports champion	0	\N	1663033833
marseyanorexia	2626	starvation proana old wrinkled bulimia bulimia edtwt	0	\N	\N
marseyexcitedexosuit	4240	happy smiling mecha rickandmorty robot	0	\N	1663011866
marseyredflag2	4928	refuse reject warning animated	1	\N	\N
marseysatisfied	8613	satisfying happy smile delightful grateful glad wholesome	0	\N	1662997904
marseyamber	1817	dalle2 generated	0	\N	\N
marseylickinglips	2548	yummy tasty delicious	3	\N	\N
marseyfedora	4928	suit 1920 mobster mafia detective mob	0	\N	\N
marseytampon	4634	period menstrual menses menstruation bloody	0	\N	\N
marseyimam	4444	muslim islam saudi ghutra keffiyah kufiya emiratis arab	0	\N	\N
marseyprostateexam	13710	gloves doctor proctologist proctology anal cavity search rectum	0	\N	\N
marseycornlove	2890	farmer iowa hawkeye maize	0	\N	\N
marseyoutline	1387	blank empty void	0	\N	\N
marseywatchingtv	1067	familyguy peter griffin television couch	0	\N	\N
marseyaceofspades	2548	asexual volcel cards	0	\N	\N
marseycarpflorist	5526	jannie admin fish flowers floral carpathianflorist crown	0	\N	\N
marseypass2	8494	pass froyo frozenchosen woman foid transgender	0	\N	\N
marseyfursuit	2622	furry furcon degenerate cosplay fursona costume mascot	0	\N	1662996039
marseyzaku	3370	gundam mecha robot helmet mask	0	\N	\N
marseygirl	5214	dress toddler tween sister horror shining	0	\N	\N
marseygundam	3370	mecha robot helmet mask anime	0	\N	\N
marseyropewithchingchong	5214	suicide chink chinese asian die kys together strawhat slit zip gook nip buckteeth	0	\N	\N
marseynukegoggles	3370	nuclear atomic bomb mushroom cloud	0	\N	\N
marseyduck3	1387	duck bird quack beak	0	\N	\N
marseysatisfiedmarcus	4989	black bipoc satisfying happy smile delightful grateful glad wholesome	0	\N	1662998420
marseypuppy	1817	dog dalle2 puppy	1	\N	\N
marseynapoleon2	11535	french france horse	1	\N	\N
marseybeaver	11192	canada canuck canadian	1	\N	\N
marseyedelgard	3370	fireemblem anime weeb fantasy nintendo princess	1	\N	\N
marseydarkxd	13710	laugh ragecomics lmao despair shadow	0	\N	\N
marseychadyes	6749	based gigachad	1	\N	\N
marseyturnedon	13710	aroused arousal amorous horny	0	\N	\N
marseygangster	13710	pimp hustling mafia money gangsta	0	\N	\N
marseybudddwyer	13710	suicide gunshot reporter journalist	0	\N	\N
marseyshy2	4131	uwu weeb blush flushed finger owo	1	\N	\N
marseyeyelidpulling	13710	frustrated scary horror	0	\N	\N
marseydeadinside2	13710	depressed suicidal doomer despair	0	\N	\N
marseymobster2	2673	bat gangster mafia kneecapper	0	\N	\N
marseytabletired2	7913	beer tiresome depressed sad alcoholic alcoholism despair	0	\N	\N
marseychocolatemilk	4090	choccy offer givemilk drink	0	\N	\N
marseycoffeemug	5526	teacup happy cozy	0	\N	\N
marseycosmopolitan	4634	bourgeoisie wealthy affluent tophat cultured capitalist elite monocle	0	\N	\N
marseybedsick	7813	illness plague fever pillow	19	\N	\N
marseywoodchipper2	1710	libertarian pedo woodchipper animated kill map	212	\N	\N
marseychtorrr2	9394	reddit admin chonker fat	0	\N	\N
marseycow	5214	cow fursona skin animal costume furry heifer fursuit	104	\N	\N
marseylgbtflag3	7913	pride gay rainbow queer	0	\N	\N
marseygardener	11964	gardening watering	0	\N	\N
marseyangel3	2490	halo happy innocent	0	\N	\N
marseyabandoned	2519	box container rejected dirty cardboard homeless	38	\N	\N
marseyraiden	993	mgs vidya	0	\N	\N
marseyxd	3609	lmao reaction rofl haha lol laughing	6289	\N	\N
marseyira	5244	car bomb irish ireland	175	\N	\N
marseymoplicker	7913	janny moderator admin	1	\N	\N
marseywizard	7813	wizard magic pepe apu	21	\N	\N
marseycapyheart	5526	capybara rodent aevann happy cute love	106	\N	\N
marseymech2	4240	mechanics robot machine rick morty snuffles	0	\N	1663011401
marseymormon	3259	backpack tie jesus god christian missionary	0	\N	\N
marseycumjar2	1828	semen jizz sperm spunk bukkake	115	\N	\N
marseyangryexosuit	4240	mecha rickandmorty robot	0	\N	1663011836
marseychemist2	1817	chemistry science chemical cope	55	\N	\N
marseywut2	1387	weird reaction raised eyebrow disturbing disturbed wtf judgment	382	\N	\N
marseyceiling	2446	spy masturbate watching peeping	169	\N	\N
marseycrystalmaiden	2256	gamer video game gaymer	50	\N	\N
marseyfellowpedo	1913	libertarian glowie fbi	77	\N	\N
marseyatfagent	8021	feds atf agent glowies usa america waco swat m16 firearm rifle cops police	36	\N	\N
marseyairquotes	2626	reaction patronizing animated uh huh	243	\N	\N
marseycool2	5526	cigarette hip shades sunglasses jacket smoking smoke	792	\N	\N
marseydog	5214	puppy doggo fursona skin animal costume dog furry fursuit	58	\N	\N
marseyskinnedwalk	995	watchpeopledie zllctnxaspywgb3 animated skinned walking trotting skeleton bones organs	22	\N	\N
marseycarpnoticeme	635	carpathianflorist fish attn attention whore	19	\N	\N
marseycrusader	5526	knight deusvult templar crusades catholic	250	\N	\N
marseywall	2626	foid female birthing person woman girl 30 fds femcel single mom single mother itsover old gross yuck nasty gussy	519	\N	\N
marseyspirit	3978	ghost halloween holiday	55	\N	\N
marseyahs	995	bardfinn dubteedub againsthatesubreddits redditor groomer pedophile libertarian chomo antifa animated	43	\N	\N
marseysaluteisrael	8239	jewish yiddish hebrew kike sheeny mossad star of david flag patriotic animated	222	\N	\N
marseysaluteussr	8239	salute o7 flag soviet union russia kgb communist commie marxist marxism tankie stalin lenin animated patriotic	411	\N	\N
marseykween	2654	hoop earring fds black shaniqua	628	\N	\N
marseymicrobus	1738	vw van bussy	42	\N	\N
marseybang	1387	head wall bang schizo psycho selfharm deranged gif animated	65	\N	\N
marseyidio3	8239	idio3 russia belarus communist commie flask drink computer online monitor display keyboard idio	47	\N	\N
marseytrumpgrill	3259	centrist donald ddr drumpf centrism bbq barbeque barbecue ketchup	47	\N	\N
marseyjamesholmes	8239	killer shooter shooting crazy schizo batman capeshit ginger	20	\N	\N
marseyolantern	4580	halloween scary pumpking	14	\N	\N
marseybongosrdine	5214	bongo drums music meme jam srdine	55	\N	\N
marseyslime	1817	animated happy blob vidya video game maple story maplestory bouncing bounce monster jump	26	\N	\N
marseygasp	2069	wow woah what how why whoa reaction appalled	995	\N	\N
marseytf2scout	6345	tf2 scout boston zoomer valve vidya game baseball mercenary	23	\N	\N
joanmarsey	3536	joan gay clown gacy wayne	35	\N	\N
marseycyanide	1387	kys kill yourself kms kill myself poison pill death die depressed suicidal suicide animated	88	\N	\N
marseycarpsnipe	9503	shooter shooting gun sniper rifle scope crosshairs carpathianflorist kill murder bullet crosshair ajab	16	\N	\N
marseydisconcerting	1387	creepy smile uneasy rapey	145	\N	\N
marseykitti	995	watchpeopledie horror grim evil scary surreal tattoos wicked demonic	6	\N	\N
marseyironmaiden	8239	death blood torture chika anime weeb weeaboo spikes murder crush animated	23	\N	\N
marseyduck	5214	bird beak	109	\N	\N
marseyvatnik	8159	russian alcoholic alcoholism	44	\N	\N
marseybaited	5526	laser pointer trolled gullible reaction animated	573	\N	\N
marseysoonretarded	2256	weeks 2weeks sal antisal soon retarded naive	26	\N	\N
marseyfingerwords	5214	cute long tldr didnt read	60	\N	\N
marseyreactor	4293	nuclear power reactor energy generation radioactive chernobyl	53	\N	\N
marseyphonecall	7813	pepe apu peepo phone call cellphone	59	\N	\N
marseyhillarybackstab	5214	clinton hilary arkanicide knife stabbing kill murder seth rich death	66	\N	\N
marseyobamacope	35	barack pointing laughing poster	159	\N	\N
marseygroomer2	5214	molest discord chomo snoo pedo pedocord reddit	396	\N	\N
marseyeerie1	2622	eerie excited calico	10	\N	\N
marseybattered	2626	blackeye domestic violence black eye marseyismywaifu bardfinn steve akins penny beaten bruised housewife	375	\N	\N
marseyminipixel	1738	miniature small smol place 8bit mouse	33	\N	\N
marseymfdoom	2622	rapper hip hop hiphop rnb supervillain helmet mask	21	\N	\N
marseyfacepeel	995	watchpeopledie kitti gore face psycho horror flay	20	\N	\N
marseychonker2	5526	fat obese pig disgusting fatty fattie	1204	\N	\N
marseylovecraft	6914	eldritch horror niggerman cat hp tentacle insane halloween	31	\N	\N
marseydeadchat	8494	dead chat discord zoomercord	5	\N	\N
marseyinabox	8613	hiding hide box cardboard happy cute	527	\N	\N
marseyduchamp	2050	art urinal duchamp modern abstract	12	\N	\N
marseywinemom	2256	drunk wine aunt flirt cigarette drunk lush elfbinn fartbinn cougar	139	\N	\N
marseymischief	1817	interface clown	42	\N	\N
marseyfoucault	1817	philosophy history foucault postmodern	9	\N	\N
marseybreastcancer	3978	mastectomy gross yuck foid disgusting titties tits boobs patient disease bald chemotherapy	61	\N	\N
marseyvan	1947	libertarian pedobear free candy pedophile groomer lolbert chomo molester pedo toucher	207	\N	\N
marseybobpage	8159	glowie deusex big pharma rocket daddy elon musk suit	34	\N	\N
marseygossip	5526	tea rotary phone popcorn gabbing	283	\N	\N
marseycapycarp	2622	aevann capybara carpathianflorist walking stomping trample trampling animated	118	\N	\N
marseyautismchonker	3259	fat obese retarded hat autistic neurodivergent	163	\N	\N
marseyfocault	635	philosophy history	51	\N	\N
marseypharaoh2	5214	gods egyptian aevann animated	56	\N	\N
marsoy2	5214	soy wojak soyjak soyjack nerd numale redditor	141	\N	\N
marseyazov2	5214	ukraine ukrainian nazi chud black sun schwarzsonne schwarzesonne zelenskyy war soldier	59	\N	\N
marcuscop	635	police officer acab thin blue line pig black bipoc	64	\N	\N
marseyprisma	5244	animated fingers anime spin dance weeb	523	\N	\N
marseyemojismilemouthtighteyes	1387	emoji reaction smile xd	22	\N	\N
marseyjackson	1387	music king pop mayo whiteface michael	44	\N	\N
marseycanned	2890	srdine sleeping tin fish sardine	267	\N	\N
marseywheredrama	5214	seriouspost reaction agendapost dramawhere animated	273	\N	\N
marseyhehe	5244	hehe nothehe happy laughing angry questioning	12	\N	\N
marseyschizoducklove	8494	animated schizo schizocel rare love duck	26	\N	\N
marseyumbreon	635	trick or treat pokemon halloween eevee costume holiday	40	\N	\N
marseyevilgrin	3149	joker evil society crazy smirk wicked danger fight trouble	151	\N	\N
marseyvaxmaxx	1387	mask coronavirus covid gigavax corona vaccine vaccination hazmat	224	\N	\N
marseycapyblowkiss	5526	capybara rodent aevann happy cute love	52	\N	\N
marsey57	8239	57 emoji57 sly smug blob	99	\N	\N
marseybush	1376	genocide president mission accomplished victory george bush we did it	159	\N	\N
marseysnorlax	1828	fat obese fatty fattie pokemon snorlax blocking snoring  sleeping	68	\N	\N
marseyjamming	8613	mp3 headphones beat ipod music happy	886	\N	\N
marseyputin	1710	vladimir russian kgb moscow ukraine dictator leader	197	\N	\N
marseycheeks	8239	sandy spongebob squirrel underwater bikini bottom diving suit	24	\N	\N
marseylong1	4122	top meme	249	\N	\N
marppybiden	381	sentient snappy robot marppy biden confused	24	\N	\N
marseyexcited	8613	eager ready hype amped reaction excitement happy thrilled	2532	\N	\N
marseywitch2	1043	tranny troomer penny wvp feminist halloween bardfinn groomer magick troid steve monster	353	\N	\N
marseybiting	8979	reaction datass lip bite dat ass	113	\N	\N
marseycapyhacker	5214	animated aevann capy hack code program socks	92	\N	\N
marseyspa	4634	spa towel cucumber facial relax calm selfcare foid hygiene beauty	33	\N	\N
marseydrunk	2069	drinking shitfaced alcoholic liquor happy beer dizzy	589	\N	\N
marseyhypno	5845	hypnosis spiral brainwash animated hypnotoad	161	\N	\N
marseyhankhill	3370	cartoon propane hank grill kingofthehill	21	\N	\N
marseycringe	250	pepe frog	116	\N	\N
marseysjw	5214	lgbt social justice reaction gay snowflake pride	291	\N	\N
marseythonk	2890	confused reaction thinking thunk thonk	2090	\N	\N
marseydoubtit	1710	dumpster defender redneck boomer shooting doubt it cocksucker gun	144	\N	\N
marseyschizogrizzlylove	8494	schizo grizzly bear love schizocel animated	32	\N	\N
marseycapysorenjump	8494	meta excited schizo aevann capy soren	333	\N	\N
marseytree	2626	tree nature outdoors cosplay	33	\N	\N
marseyjewoftheorientglow	5214	animated glow rice china chinese chink commie mao xi	100	\N	\N
marseyparty2	5214	trippy animated happy dance	105	\N	\N
marseyschizonekolove	8494	nekobit neko schizo schizocel schizomarsey rare love	11	\N	\N
marseychristmasgift	5526	present christmas box unwrapping holiday	96	\N	\N
marseywink	7913	wink reaction cheeky flirt smirk imply hint	210	\N	\N
marseyfugg	1817	spurdo sparde fugg	47	\N	\N
marseygigachad	150	reaction hunter eyes canthal tilt jawline	609	\N	\N
marseybongo	5214	bongo drums music meme jam	90	\N	\N
marseycapydinosaur	381	capy aevann dinosaur rawr prehistoric	23	\N	\N
marseyeggirl	5214	troomer tranny transgender lgbt groomer troid transsexual	665	\N	\N
marseyhappy	8979	pleased contented reaction contentment satisfied	114	\N	\N
marseyauthright	1817	rightoid national socialism ss national socialist nazi wehrmacht hitler fascist	289	\N	\N
marseyfry	2626	phillip fry take my money futurama	179	\N	\N
marseymanlet	1387	llm short midget dwarf little king	499	\N	\N
marseytf2heavy	6345	tf2 heavy weapons valve vidya game minigun russia	32	\N	\N
marseyfurry2	2626	furry fur degenerate sex	75	\N	\N
marseywoah	5526	tldr reaction wall of text wordswordswords stfu	260	\N	\N
marseychartgaussian	7913	stats statistics chart graph plot data gaussian normal bell distribution	54	\N	\N
marsey173	1817	horror spooky halloween scp spc holiday	41	\N	\N
marseygold	1387	gold award reddit	68	\N	\N
marseyfrylock	3370	cartoon athf aqua fry fries fastfood	15	\N	\N
marseyhijab	5214	hijab reading islam jihad muslim allah quran koran	85	\N	\N
marseychristmaself2	5526	elf santa northpole north pole christmas holiday	72	\N	\N
marseyicecream	4122	ice cream sad disappoint pout cry.	99	\N	\N
marseymspaint	11030	paint mspaint pixel shifty squat	12	\N	\N
marseypredator	1710	predator drone obama wedding military	54	\N	\N
marseyfranklin	5525	franklin thinking constitution founding fathers	113	\N	\N
capysneedboat2	8494	marsey capy schizo schizocel rare tripping sneed boat love excited seethe schizomarsey	22	\N	\N
marsie	6289	cartoon disney	29	\N	\N
marseyprojection	1817	animated projection projector movie director film movie cinema theatre theater kino	62	\N	\N
marseycarphug2	2548	fish love bottomfeeder carpathianflorist heart blow admin cute	93	\N	\N
marseybrasileiro	1710	brazil soccer macaco monkey	134	\N	\N
marseydepressed	5244	smoke kms doomer cigarette despair reaction depression suicide suicidal smoking hopeless sad	2622	\N	\N
marseychristmaslove	5526	christmas holiday present gift present love hearts affection	95	\N	\N
marseyfrozenchosen	7272	blonde girl woman	174	\N	\N
marseyalien	1387	green man martian scepter	133	\N	\N
marseypentagram	8727	satanic satanism devil evil occult witchcraft belial baphomet leviathan 666	59	\N	\N
schopenmarsey	3908	schopenhauer philosophy german will ethics metaphysics	127	\N	\N
marseygoodmap	768	map pedo dead shoot animated shotgun buckshot kill minor libertarian	31	\N	\N
marseyinbread	635	food meme inbred	61	\N	\N
marseyreading	8613	study homework learn nerd novel reaction book	1714	\N	\N
marseymonk	5214	meditate levitating pray buddhist fish asian levitate animated yingyang buddhism karma zen	214	\N	\N
marseycapy2022	5214	aevann caypbara new year party celebration	60	\N	\N
marseydiscord	5845	fur furry groomer moderator uwu :3	54	\N	\N
marseyfluffy	5526	poofy cute shaggy happy smile excited scruffy	121	\N	\N
marseyclown3	4588	unicycle animated	184	\N	\N
marseykiwivampire	5526	kiwi new zealand dramarama house scary spooky bird cloak sanguine fangs halloween bloodsucker	53	\N	\N
marseystuffed	1817	fur meme statuesque indifferent figurine statue stuffed art	13	\N	\N
marseyreporterfox	2626	reporter journalist journoid interviewer	73	\N	\N
marseycopeseethedilate	2626	dilate seethe coping seething reaction angry mad dilating cope malding	837	\N	\N
marseyshy	5214	flirting anxious twiddle nervous flirty coy animated	525	\N	\N
marseypotofsneed	8239	pot sneed pottery dungeon ornamental ancient	28	\N	\N
marseytf2spy	6345	tf2 spy france mercenary smoke suit valve vidya game espionage	24	\N	\N
marseysheepdog	5526	shaggy scruffy woof	150	\N	\N
marseycarpdead	1387	fish janny kill	104	\N	\N
marseyballerina	2256	dress ballet tutu dancer dancing	51	\N	\N
marseybsod	8727	windows computer blue screen of death error glitch	54	\N	\N
carporeon	5526	carp vaporeon pokemon eevee water tail fish aquatic	38	\N	\N
marseydeadeyes	1387	broken suicidal depressed	94	\N	\N
marseygucci	1710	gucci mane lean rapper trap mixtape bricksquad traphouse codeine lean rapper pimp	49	\N	\N
marseysoldierrussia	1710	army war gun rifle vatnik slav putin ukraine	50	\N	\N
marseybadluck	5460	unlucky black cat poc nigger blackcat	35	\N	\N
marsey40k	3652	warhammer 40k 40000 space space marine marine ultramarine smurf	126	\N	\N
firecat	5526	firefox browser marsey	77	\N	\N
marseydeterminedgun	7056	shooting blam blatt shooter kill die threatening animated	137	\N	\N
marseybaby	1387	pacifier bb little	144	\N	\N
marseyatsume	1738	kitten kitty weebshit	35	\N	\N
marseybeansick	1817	bean sick vomit nausea unwell ill	96	\N	\N
marseylong2	4122	middle meme	256	\N	\N
marseybiker	635	motorcycle harley bicycle helmet	78	\N	\N
karlmarxey	5526	marxist communist history communism socialism	124	\N	\N
marmseylegionnaire	1058	rome roman legionnaire soldier helmet hats	169	\N	\N
marseyayy	4588	wop tone guido wooden doors sopranos greaser dego paulie	70	\N	\N
marseykermit	5526	kermit green frog puppet absinthe television sesame children	39	\N	\N
marseyjudge	2256	objection innocent hammer guilty gavel court overruled sustained	217	\N	\N
marseybangfast	1387	head wall bang schizo psycho selfharm deranged gif	330	\N	\N
marseythumbsup	8613	cool good job good one agree reaction nice work yes great job	4851	\N	\N
marseyanticarp	541	reaction fish carpathianflorist	310	\N	\N
marseychemist	1817	chemistry science chemical	78	\N	\N
marseyhungry	5214	food hunger dish feed me bowl animated	126	\N	\N
marseystroke	2526	derp retard reaction stupid drooling	370	\N	\N
marseyfingerhearts	5214	cute love k-pop	131	\N	\N
marseyargentina	3149	south america argentinian sudamericano	40	\N	\N
marseyschizolangleylove	8494	animated schizo schizocel rare love langley cia glowie glow	23	\N	\N
marseymike	2465	disney pixar monsters inc cyclops	23	\N	\N
marseyvirus	2622	phage infect infection plagued	58	\N	\N
marsheepnpc	5526	follower	138	\N	\N
marseyanime	2626	sayian weeb	62	\N	\N
marseyshakespeare	4634	words, writer, author, drama, theater, british, poet william england english thespian playwright playwrite	46	\N	\N
marseypoor	1387	homeless beggar panhandler proletariat bum	672	\N	\N
marsheep	5526	sheep animal fluffy wool	17	\N	\N
marseydealwithit	5214	cool shades sunglasses reaction animated	195	\N	\N
marseymummy3	2638	egyptian halloween monster holiday	13	\N	\N
marseyschizoidiolove	8494	schizo idio3 love rare excited idio	50	\N	\N
marseychinchilla	5214	pet rodent capy cute hamster south american andes	30	\N	\N
marseylois	1387	familyguy familyman family guy family man peter griffin	63	\N	\N
marseycapysorenjump2	8239	animated soren capy jump aevann mad	97	\N	\N
marseycarpautism	1710	carpathianflorist special assburgers aspergers retarded janitor jannie	101	\N	\N
marseyskater	2256	dope hip sk8 ill tony hawk sick skateboard not a poser rad	102	\N	\N
marseypatriot	2622	uncle sam red white and blue burgerland holiday american 4oj patriotic	618	\N	\N
marseycop2	635	police officer acab thin blue line pig	114	\N	\N
marseyropeyourself	635	kill yourself kys lynch reaction keep yourself safe hanging noose	990	\N	\N
marseypennylove	3259	love penny hug wholesome black kween	65	\N	\N
marseyworried	2069	monkaw anxiety sweat panic scared sweaty sweating anxious nervous stressed	953	\N	\N
marseyisis	5244	daesh terrorist islam muslim	874	\N	\N
marseymajorgeneral	201	jeffthespammer pirates of penzance safari muttonchops mutton chops army military soldier officer	40	\N	\N
marseybadger	2622	animal marmot	25	\N	\N
marseychristmasbulb2	5526	ornament holiday christmas	38	\N	\N
marseybigdog	1738	bussy big dog poster	167	\N	\N
marseyflareon	635	trick or treat pokemon halloween eevee costume holiday	30	\N	\N
marseybath	2626	shower tub rubber duck	61	\N	\N
marseyangel2	5526	angelic horn trumpet halo wings	95	\N	\N
marseycoffee	2622	morning wakeup tea	95	\N	\N
marseysexylibrarian	2626	books hoe old woman thot nerd boobs bra geek	86	\N	\N
marcerberus	5526	threeheadeddog horror halloween holiday greek three headed dog monster	50	\N	\N
marseypain	3652	suffering meme kms kill myself cat	52	\N	\N
marseylawlz	2133	masterlawls zhcyid9 masterlawlz reaction glasses	182	\N	\N
marseyropeyourself2	635	kill yourself kys lynch reaction keep yourself safe hanging noose	586	\N	\N
marseymap	7056	libertarian libertarian map predator	29	\N	\N
marsey666	5214	wings hell halloween demon satan holiday devil animated	119	\N	\N
marseybug	1387	beetle glitch error insect roach	115	\N	\N
marseyreportercnn	2626	reporter journalist journoid interviewer	153	\N	\N
marseystalin	8239	tankie authleft ussr russia communism socialism marxist commie soviet proletariat marxism marxist leninist leninism revolution bolshevik	124	\N	\N
marfield	2808	mondays garfield lasagna	56	\N	\N
marseysnowman	5526	christmas cold snow winter	41	\N	\N
marseyflushzoom	5526	flushed eyes bulging shocked surprised flustered	19	\N	\N
marseyl	2622	loser loss	469	\N	\N
marje	2321	juicebox juice box madje marsey	77	\N	\N
marseybrave	635	bat browser shill	90	\N	\N
marseyqoomer	1710	shaman viking qanon jan6 capitol january6	158	\N	\N
marseyproctologist	2519	exam rectal glove reaction anus anal colonoscopy	153	\N	\N
marsey1984	542	orwell book ingsoc big brother fascist	316	\N	\N
marseyhomestar	4154	homestar runner fast everybody 2000s	23	\N	\N
marseysadgun	7813	pepe mellokind crying tears suicidal suicide kms frog	51	\N	\N
marseyskeletor	2546	skeleton mask heman 80s man halloween he man cartooon he holiday	71	\N	\N
marseyban	4240	jannie janitor banhammer moderator banned	282	\N	\N
marseybreadcrumbing	635	bait lure feeding food throwing animated	74	\N	\N
marseyaward	5526	medal good job good work retard reaction great job great work nice	294	\N	\N
marseyorthodox	2519	priest schismatic bartholomew_1 christian	386	\N	\N
marseyrentfree	542	reaction no charge obsessed obsession	249	\N	\N
marseychonker	1387	brap rolls fat obese reaction fds heifer	632	\N	\N
marseycountryclub	4588	golfer elite rich golfing cc elitist preppy	86	\N	\N
marseydomesticabuse	10432	domestic violence bardfinn foid beating punching battering battered bandage hurt pain woman female	66	\N	\N
marchipmunklove	5526	chipmonk adoration loving rodent heart eyes adore acorn	60	\N	\N
marseynpcmad	3149	angry grey libtard	76	\N	\N
marseyfedscared2	995	glowie glowbipoc federal agent frightened nervous worried panicking fear	19	\N	\N
marseyshake	3370	cartoon athf aqua fastfood shake dessert icecream	11	\N	\N
marseyjunkie2	1387	addicted drugs pills glue huffing ether overdose	66	\N	\N
marseycodecel	4450	coder coding coode aevann programming python developer	15	\N	\N
marseybear	5526	brian gabby murderer brianna	215	\N	\N
marseysully	2465	disney pixar monsters inc horned horns	10	\N	\N
marseything	2616	halloween holiday scary monster teeth	66	\N	\N
marseychtorrr	3635	reddit administrator place moderator	46	\N	\N
marchipmunk	5526	rodent squirrel wuzizname	54	\N	\N
marseytzeentch	1817	warhammer 40k chaos god trick magic lies	26	\N	\N
marseykyle	635	killer konvict rifle rittenhouse kid gun kenosha kylie	688	\N	\N
marseycia	1710	bane cia glowie plane big guy dr pavel	145	\N	\N
marseylifting	1947	workout muscular work out bench swole working out gains benchpress weightlifting weights muscles	166	\N	\N
marseydoctor	635	medic physician white coat stethoscope clipboard checkup diagnosis healthcare	91	\N	\N
marseysmoothbrain	1387	idiot big brain brainlet retard reaction fool dumbass moron	574	\N	\N
marseytinfoil2	5526	alex jones rightoid psycho schizo alexjones conspiracy	710	\N	\N
marseybane	3149	soy mask batman capeshit	209	\N	\N
marseysonic	2626	hedgehog blue	68	\N	\N
marseyascii2	4017	oldschool	24	\N	\N
marseydumptruck	7813	pepe butt mellokind thicc thick ass booty cheeks	38	\N	\N
marseywallst	5214	hodl crypto wall street bets invest gme bitcoin wallstreetbets wsb stock	272	\N	\N
marlion	5214	animated flippers wave fins waving mermaid	102	\N	\N
marseyobamahope	35	happy poster barack	27	\N	\N
marseybunny	5214	furonsa bunny usagi skin animal costume furry fursuit	53	\N	\N
marseycheesehead	2622	packers greenbay green bay football	72	\N	\N
marseyhomsar	4154	homsar homestar rslur retard dumb loud shout 2000s	22	\N	\N
marseycarpcrying	1387	tear reaction carpathianflorist fish sob tears sad	168	\N	\N
marseysockmlep	1817	sock puppet alt anonymous shill	15	\N	\N
marseyridin	5526	joe biden kamala harris voted voting election american president hat	149	\N	\N
marseylovecraftian	5214	cosmic horror eldritch galaxy space hp spooky scary halloween animated	36	\N	\N
marseycolossal	5214	halloween skin holiday scary mouths	45	\N	\N
marseycenter	1817	reaction grilling boomer centrist	91	\N	\N
marseybog	2622	rich brothers bogdanoff	210	\N	\N
marseybyeceps	635	crying kyle gaige grosskreutz rioter sad	99	\N	\N
marseyattentionseeker	7913	attention seek notice shout yell desperate narcissist notice	218	\N	\N
marseylegion	635	zombie wolf fallout new vegas fnv caesar courier video game roman	47	\N	\N
marseymars	8239	celestial space planet galaxy world solar system alien	66	\N	\N
marseyakumu	2256	simp love loving weebshit	85	\N	\N
marseychartscatter	7913	stats statistics chart graph plot data scatter series	62	\N	\N
marseyloadingneon	10288	animated loading spinner webdev rolling ball circle neon	14	\N	\N
marseybrianna	5526	trans bear laundrie gabby	60	\N	\N
marseybiden2	5214	biden ddd dementia daddy president sleepy joe gas petrol ididthat	77	\N	\N
marseyrick	2626	smart 150iq high iq reaction 150 iq morty	203	\N	\N
marseypikachu2	5526	pokemon shoked meme reaction surprised shocked gasp	431	\N	\N
marseyelephantcumjar1	1387	semen jizz sperm bukkake cumjar elephant	14	\N	\N
marseygrad	2622	graduate graduation school degree diploma hat tassel animated college university	57	\N	\N
marseygigaretard	1387	idiot neurodivergent dumb stupid drooling moron puddle	2619	\N	\N
marseyfedscared	995	glowie glownigger federal agent frightened nervous worried panicking fear	20	\N	\N
marseycamus	1817	philosophy history	167	\N	\N
marseymrsclaus	2626	christmas santa winter boobs	20	\N	\N
marseyshooting	5526	blam blatt shotgun kill pow murder	1352	\N	\N
marseypolarbear	7004	bear polar cold white arctic ice	19	\N	\N
marseycomradehandshake	5526	ussr russia communist shaking hand communism soviet	47	\N	\N
marseyfeelsgoodman	7813	pepe feels good man mellokind frog happy	44	\N	\N
marseycatgirl	1387	uwu waifu anime fursona furry owo weebshit fursuit	237	\N	\N
marseyaoc	2626	latina latino hispanic cortez mexican puerto rican ocasio congress alexandria	62	\N	\N
marseyhotep	2069	party meme parrot vibing jam dance	93	\N	\N
marseypinkcat	2252	homo gay happy ribbon femme girl	22	\N	\N
marseybraveglow	5214	web browser glowie glow nigger glownigger glowing animated 	34	\N	\N
marseyxi	1710	xi jinping china chinese  asia	105	\N	\N
marseymeds	2626	mentally ill rightoid doctor psycho crazy mental illness reaction risperidone schizo nurse	983	\N	\N
marseyandjesus	2210	christianity christian jesus god love cute wholesome happy hug	140	\N	\N
marseybruh	1387	bruhfunny funny or ban	113	\N	\N
marseyschizohobocellove	8494	animated schizo schizocel rare love hobo homeless hobocel	20	\N	\N
marseyhomosupremacist	5214	klan lgbt faggot kkk homocracy sodomy queer gay wholesome	734	\N	\N
marseybluecheck	2133	journoid checkmark verified journalist drolling drool twitter	554	\N	\N
marseycalarts	1710	excited eager happy thrilled	50	\N	\N
marseysoylentgrin	3908	numale nu male menslib redditor plebbitor happy glasses soyjak nerd loser beta smile smiling	309	\N	\N
marseysphinx	8239	sphinx egypt ancient antiquity wonder pharaoh myth riddle puzzle	21	\N	\N
marseybateman	7056	bret easton ellis serial halloween patrick american psycho killer holiday blood murderer	127	\N	\N
marseychungus	3783	bugs bunny meme fat chonker big	152	\N	\N
marseyoctopus	541	tentacles kraken tentacled	47	\N	\N
marseysipping	597	drinking root drink reaction stare thirsty purple drank juice bored	1823	\N	\N
marseyemojigrineyes	1387	emoji reaction grin	14	\N	\N
marseybrianna2	5526	trans bear laundrie gabby	63	\N	\N
marseylaugh	8613	lmao reaction point funny haha lol judgment	10383	\N	\N
marseyschizosallove	8494	animated schizo schizocel rare love sal	37	\N	\N
marseypussyhat	4634	feminist feminism activism activist protester protesting foid gussy woman birthing person roasty roastie thot slut whore	134	\N	\N
marseybride	635	dress tiara married wedding veil marseyismywaifu marriage	95	\N	\N
marseycupidangry	5214	fire, valentines, love, hate, angry, arrow, bow, kill, attack, shoot, weapon, flame holiday cherub angel	23	\N	\N
marseyquestion	5526	suspicious sussy reaction sarcastic sarcasm	443	\N	\N
marseychessknight	10214	chess knight horse game	20	\N	\N
marseycarptrophy	7913	carp head decapitated anticarp trophy defeat dead teaparty	70	\N	\N
marseyangel	8613	reaction angelic happy innocent	1061	\N	\N
marseynotesglow	2481	notes glow cia fbi fed writer writing	197	\N	\N
marseytransgenocide	5214	animated trans genocide chud lgbt rightoid bigot gaybros	102	\N	\N
marseyduck2	5214	onesie	120	\N	\N
marseysylveon	635	trick or treat pokemon halloween eevee costume holiday	62	\N	\N
marseycatgirl2	5526	anime weebshit	74	\N	\N
marseydeadhorse	428	drowned pony drowning	113	\N	\N
marseybabykiller	4634	abortion fetus knife stab planned parenthood infanticide childfree murder foid	64	\N	\N
marstolfo	5526	astolfo anime femboy cute blowkiss love heart justcool393 trap warrior	60	\N	\N
marseyvelociraptor	381	dinosaur velocimarsey extinct predator claws	32	\N	\N
marseysadcat	542	upset disappointing disappointment reaction disappointed sad crying	357	\N	\N
marseyamazon	5526	warehouse piss bottle driver wagecuck piss jug pissbottle pissjug wagie	65	\N	\N
marseyklenny2	2050	corgi dog puppy klenvastergan smile happy	52	\N	\N
marseyrdramauser	1830	bussy fat lard gay homosexual obese poweruser neet dildo chef hat neckbeard meta	56	\N	\N
marseyflamewar	1947	troll fight fire reaction gasoline	420	\N	\N
marseyclown	2519	makeup joker	163	\N	\N
marseymayo	2626	yt jakubian crying cracker reaction crackkka crakkka white sad tears	620	\N	\N
marseynoyouglow	5214	fbi no u animated feds glowies glowniggers atf cia nsa	100	\N	\N
marseybug2	5526	glitch code error	59	\N	\N
marseycensored	5214	1984 memory hole censorship repressed	89	\N	\N
marsey4chan	2626	neckbeard anonymous loser hacker	150	\N	\N
marseypin	1387	pinned sticky	59	\N	\N
marseyfurry	2626	fursona furry fursuit kitsune	215	\N	\N
marseydisabled	2626	retarded handicapable handicapped wheelchair crippled	128	\N	\N
marseydildo	542	horse	233	\N	\N
marseywoodchipper	1710	libertarian woodchipper libertarian kill	294	\N	\N
marseyfrog2	5214	scaley fursona furry scalie amphibian toad fursuit	46	\N	\N
marseymagahat	5526	trump 5200 maga american president election vote nazi hat	193	\N	\N
marseyautism	5845	retarded neurodivergent hat sped aspergers	1237	\N	\N
marseybongosnoo	5214	bongo drums music meme jam reddit snoo	180	\N	\N
marseyill	8613	winter chilly cold ill sick brr flu	166	\N	\N
marseydrone	1387	obama rotors	47	\N	\N
marseysweating	5526	anxiety worried wipe scared worrying reaction anxious nervous stressed	1604	\N	\N
marseyblackface	5214	moon cricket jogger nigger racism coon racist minstrelsy jigaboo	430	\N	\N
marseyxmr	11080	cryptocurrency monero money happy heart	46	\N	\N
marseyblackcop	635	police officer acab thin blue line pig bipoc	96	\N	\N
marseycarp2	4588	harm cutting selfharm cutter reaction carpathianflorist self animated	152	\N	\N
marseyeyemixer2	5214	mixer stirrer eyes blind selfharm mutilation gore blood gouge	121	\N	\N
marseyimposter	5188	amogus baka among us sussy	179	\N	\N
marcake	5526	cupcake birthgay birthday cake frosting celebrate party dessert sweet	94	\N	\N
marseylemon	5526	pucker sour lemon fruit citrus tear 	24	\N	\N
marseysaluteindia	8239	o7 bobs vagene bitch lasagna pajeet curry desi animated flag patriotic modi	105	\N	\N
marseyspyglow	5214	spy agent shill glowie russia china	266	\N	\N
marseyplaty	4240	hearts crossover platypus love	51	\N	\N
marseyfattie	5214	brap fatass chonker pig lorg	42	\N	\N
marseytankushanka	1947	military ussr ccp communist authleft tank army communism china soviet russian	289	\N	\N
marseysociety	2626	batman joker capeshit jared leto	273	\N	\N
marseycapypharaoh	1710	aevann egypt alien king	81	\N	\N
marseyhead	4588	blood spurting headless horror halloween animated	168	\N	\N
marseyschizobyolove	8494	schizo byo byobombs rare love	37	\N	\N
marseyfinger	8979	flipping middle finger bird reaction flicking judgment	60	\N	\N
marseypartymaxx	5214	party meme parrot vibing jam dance	264	\N	\N
marseyclown2	4588	joker	195	\N	\N
marseywitchtriggered	3149	witchcraft angry spell bardfinn tranny train troon snowflake redditor wvp magic science animated	207	\N	\N
marseykink	2626	bdsm sex kinkster dom pervert sub creeper latex fetish dildo pvc	562	\N	\N
marseyemo	5845	girl goth scene woman foid	127	\N	\N
marseyerasure	2622	erase ignore block	86	\N	\N
marseyprotestyes	1387	agree sign protester reaction approve	129	\N	\N
marseyhellraiser	5526	pinhead halloween holiday evil monster	39	\N	\N
marseyfrog	5214	scaley fursona furry scalie amphibian fursuit	40	\N	\N
marseyeyeroll	4588	rolleyes rolling eyes mock animated reaction roll eyes duh	1937	\N	\N
marseyfeet	1387	foot frozenchosen fetish	173	\N	\N
marseydevil	2256	pitchfork daemon hell halloween demon mischievous satan holiday heck evil	263	\N	\N
marseycarsuicide	5214	kms suicide kill death car vehicle carbon monoxide co muffler suffocation suffocate	35	\N	\N
marcusfootball	542	sport handegg hand egg athlete helmet	102	\N	\N
marseygodfather	1387	wop italy italian dego mafia	103	\N	\N
marseyimpossibru	5526	revulsion gross yuck yikes mad icky impossible disgusted disgusting	219	\N	\N
marseynyansuperstraight	5214	animated straggot pride heterosexuality space flying	21	\N	\N
marsey300	5214	leonidas shield armor thermopylae spear greek spartan	117	\N	\N
marseyhandsup	1387	hands up pawsup arrested arresting reaction paws up under arrest	74	\N	\N
marseyfreezepeach	5214	1984 censorship free speech reaction freespeech ruqqus	154	\N	\N
marseycut	4588	cutting selfharm emo self harm cutter reaction depressed	129	\N	\N
marseyamogus	1710	sussy baka impostor imposter stonetoss among us shh vent	110	\N	\N
marseymalding	3259	dilate seethe scrote mad moid cope	261	\N	\N
marseyschizosal	6345	schizo sal rare weeks nowhere	93	\N	\N
marseycapyblackface	5214	racist minstrelsy bowtie racism capybara aevann	37	\N	\N
marseysaltlicking	1387	salt lick rock	33	\N	\N
marseyeldritch	5526	lovecraft horror halloween tentacles holiday scary monster	72	\N	\N
chudsey	1829	4chan virgin pol rightoid	1283	\N	\N
marmsey	1058	rodent happy	93	\N	\N
marseyhippo	5214	hippopotamus hippo fursona furry skin animal costume fursuit	38	\N	\N
marseydeuxfoid	1738	deuxrama asian azn hardislife hil	28	\N	\N
marseykfc	2626	col sanders colonel kentucky fried chicken	44	\N	\N
marsey69	5244	6ix9ine snitch tattooed tattoos rapper	84	\N	\N
marseygrilling	542	barbecue bbq centrist boomer barbeque	141	\N	\N
marseyschizoabsinthelove	8494	animated schizo schizocel rare love absinthe frog	31	\N	\N
marseybountyhunter	4588	abortion leather vest cowboy gunslinger texas revolver	306	\N	\N
marseyemperor	1817	gold	43	\N	\N
marseycanadian	5244	southpark canada leaf terrance phillip animated fart	41	\N	\N
marseyfeynman	1817	history	25	\N	\N
marseyzombiewolflove	5214	hug cuddle love marseylove zombiewolf zombie wolf	17	\N	\N
marseysal	7615	2 weeks two weeks sallie white shark	1278	\N	\N
marseyfeminist	2519	misandry fds scrotes moids	221	\N	\N
marseycapykiss	2626	capybara aevann love mwah xoxo smooch happy love	104	\N	\N
marseyracist	2626	racing vroom racecar bigot reaction	596	\N	\N
marseyleafeon	635	trick or treat pokemon halloween eevee costume holiday	32	\N	\N
marseyfeelsgood	2069	meme frog feels good man pepe feelsgoodman happy	90	\N	\N
marseymeatwad	3370	cartoon athf aqua hamburger	22	\N	\N
marseybadass	3735	badass whoa neil degrasse tyson science mustache ifls smug	23	\N	\N
marseycapychad	9977	aevann chad capy chadybara capybara muscular swole ripped egypt ouch tanktop	53	\N	\N
marseygrass	2626	reaction outside touchgrass touch grass	290	\N	\N
marseyschizopennylove	8494	animated schizo schizocel rare love penny	35	\N	\N
marseygift	8613	present christmas wrapping paper holiday	128	\N	\N
marseytexan	3978	cowboy hat texas yeehaw pardner rootin tootin	163	\N	\N
marseyaynrand2	3635	ayn rand objectivist objectivism libertarian girlboss capitalist capitalism book atlas shrugged	31	\N	\N
marseysockpuppet	1817	animated sock puppet alt anonymous shill	30	\N	\N
marseycontemplate	2490	reaction consternation thinking hmm	201	\N	\N
marseytroll	4	dio diogenesjr diogenesjunior trollface reaction	1313	\N	\N
marseybear2	5214	ursine bear fursona skin animal costume furry fursuit	49	\N	\N
marseyjourno	993	journoid media press photo camera journalist pic	411	\N	\N
marseydrama	1387	agendapost where drama seriouspost drama where	322	\N	\N
marseyheathcliff	2546	heathecliff	23	\N	\N
marseysoldieramerica	1710	army war gun rifle burger mutt	74	\N	\N
marseystein	2622	undead frankenstein abomination halloween holiday monster	50	\N	\N
marseycarp	1376	beard mohawk reaction carpathianflorist monster	135	\N	\N
marseybingus	5244	floppa shaved hairless	104	\N	\N
marseybarrel	542	barrel container beer bar alcohol	18	\N	\N
marseyhoodwink	1809	cloak crossbow	38	\N	\N
marseybait	2626	trolled baited trolling redditor	90	\N	\N
marseycthulhu	1817	horror halloween lovecraftian holiday eldritch evil scary monster	52	\N	\N
marseyarmy	150	chiobu soldiers o7 salute saluting	136	\N	\N
marseyhealthy	2626	burger king fat fast food crown unhealthy junk food american	88	\N	\N
marseysalutepride	5214	saluting 07 military soldier gay pride lgb rainbow	109	\N	\N
marseyfamily	1387	family guy family man peter griffin griffin peter	236	\N	\N
marseycommitted	4240	psycho crazy insane straitjacket asylum reaction loony bin straightjacket	172	\N	\N
marseychartbar	7913	stats statistics chart graph plot data bar column	51	\N	\N
marseyplace2	7466	pixelart pixellated reddit lowres	25	\N	\N
marseyfrenchvan	6113	foucault pedophilia libertarian van french philosophy pedobear postmodernism	42	\N	\N
marseypearlclutch	2622	sensitive reaction snowflake puritanical gasp sjw	1920	\N	\N
marseymoose	5214	moosin antlers	31	\N	\N
marseykwanza	597	christmas black kwanza african holidays	27	\N	\N
marseychucky	5526	doll halloween kill stab knife holiday possessed monster	56	\N	\N
marseymyspacetom	3652	carp friend carpathianflrost anderson	71	\N	\N
marseyglowaward	5214	medal fbi ribbon animated glownigger retard glowie fed atf cia nsa	96	\N	\N
marseycat	5214	fursona skin animal costume furry neko fursuit cat	47	\N	\N
marseydragon	5526	smaug rich hoard gold treasure	126	\N	\N
marseyoyster	5214	pearl shellfish clam give	41	\N	\N
marseyllama3	5845	bottom	88	\N	\N
marseyumbreon2	2626	pokemon eevee furry eeveelution evolution	18	\N	\N
marseyretard3	5526	drooling stupid idiot sped moron imbecile dolt	192	\N	\N
marseycarpdino	381	dinosaur costume furry fursuit carpathianflorist extinct reptile lizard rawr prehistoric jurassic	11	\N	\N
marseycorn	4588	iowa vegetable	78	\N	\N
marseymodelo	5099	cheers alcohol drinking beer	39	\N	\N
marseydylan	635	columbine school shooter psycho gun pistol klebold	119	\N	\N
marseyisraellove	4240	love ally israel holocaust zionism	29	\N	\N
marseyfug	3336	benis mustache meme	98	\N	\N
marseypunished	5845	punished venom snake metal gear solid kojima eyepatch	49	\N	\N
marseyschizohanklove	8494	animated schizo schizocel rare love byo hank	18	\N	\N
marseycharlesmanson	8239	charlie manson charliemanson murderer killer swastika crazy psycho schizo helterskelter prison cult	30	\N	\N
marseytombstone	2622	dead death gravestone cemetery graveyard rip rest in peace	149	\N	\N
marseyextinction	5214	extinction button women misogyny mayocide kazakhstan	600	\N	\N
marseygondola	7056	mustache meme long legs	51	\N	\N
marseybux	2622	money paypig currency dollar bill primo premium dollarbill cash	281	\N	\N
marseychristmaself	993	christmas xmas santa holiday happy worker	65	\N	\N
marseycatgirl3	5526	anthro anime weebshit	82	\N	\N
marseylovedrama	5214	hearts rdrama reaction happy animated	189	\N	\N
marseycutattention	768	razor cry depressed kys cut attention borderline bpd blood cutting woman foid	34	\N	\N
marseymarseyloveorgy	3149	reaction love blush aww hugging cuddling cuddle snuggle snuggling hearts xoxo nested recursion inception orgy group	55	\N	\N
marseyburger	542	burgerstan hamburger cheeseburger mutt american	443	\N	\N
marseybow	7913	bow ribbon happy cute adorable accessory gift present	327	\N	\N
marseyit	5526	balloon halloween pennywise clown holiday evil	40	\N	\N
marseyowow	1387	reaction excited owo	118	\N	\N
marseybarreldrunk	542	barrel container beer bar alcohol drunk	23	\N	\N
marseycapymad	1387	shaking aevann mad angry fury furious anger shook animated capybara	164	\N	\N
marseybackstab	2626	betrayal kill knife caesar assassinate betrayer murder	309	\N	\N
marseymaoist	746	marxist little red book marxism ccp chinese communist authleft maoism communism china	166	\N	\N
marseynpc	2513	sheeple	74	\N	\N
marseysimpson	2465	yellow simpsons groening homer bart lisa marge cartoon	20	\N	\N
marseycarphug	5526	love squish squeeze hug squeeze fish carpathianflorist	204	\N	\N
marseypunching	4588	battle squaring up hit square up boxer fight throwdown reaction boxing fistfight fighting	438	\N	\N
marseyliondance	5214	parade ccp chinese dancer dancing asian china animated	149	\N	\N
marseykvlt	2256	horgh abbath black metal krieg bullet belt immortal corpsepaint	94	\N	\N
marseycleonpeterson	5214	wtf scary art	33	\N	\N
marseyben10	2626	ten anime cartoon lawlz	35	\N	\N
marseyauthleft	1817	marxist ussr marxism ccp communist khmer rouge leftoid communism juche	82	\N	\N
marseybrick	1994	throw riot subtlety broken paver	34	\N	\N
marseyglaceon	635	trick or treat pokemon halloween eevee costume holiday	40	\N	\N
marseyderanged	635	crazy psycho mad disgusted angry rage violent baseball bat	58	\N	\N
marseyskull	7056	skull dead skeleton punisher kill bone	11	\N	\N
marseycapyparty	5214	trip animated wooo aevann admin party parrot	82	\N	\N
marseymermaid	542	merman merfolk	50	\N	\N
marseymissing	3141	absent low effort	71	\N	\N
marseyslowpoke	1994	pokemon stupid late anime weeb meme	59	\N	\N
marseykys	5214	reaction keep yourself safe kill yourself suicide	384	\N	\N
marseyllama	5845	alpaca	41	\N	\N
marseyrowling	2626	harry potter terf jkr transphobe	175	\N	\N
marseybuttface	8239	butthead ass donk rimjob eat ass rump rear shit fart	72	\N	\N
marseymummy2	2554	egyptian halloween monster holiday	28	\N	\N
marseymodelo2	5099	cheers alcohol beer drinking	37	\N	\N
marseylongpostglow	768	animated pippy glow fedpost longpost words mad angry rage wtf green chud fbi mossad fed atf police reaction scrolling	63	\N	\N
marseyinshallah	5214	begging muslim animated please	442	\N	\N
marseypaint	2590	low effort art	49	\N	\N
marseyyesandno	5214	agree disagree both confused indecisive trippy animated inconclusive idk fencesitter switzerland	116	\N	\N
marseynut	5244	orgasm ahegao cum reaction coom	1561	\N	\N
marseyrevolution	2256	marxist ussr marxism ccp hammer communist sickle communism proletariat juche kgb	185	\N	\N
marseyhorseshoe	2626	rightoid leftoid theory	468	\N	\N
marseymacarthur	542	nuke missile nuclear bomb history	288	\N	\N
marseyniqab	635	burka islam muslim burqa	273	\N	\N
marseysaturn	1817	devouring eating snoo kill de goya anger reddit	52	\N	\N
marseypharaoh	1376	egyptian aevann pyramids	136	\N	\N
marseychonkerfoid	3259	female woman fds fat obese hambeast landwhale porker pig bleeder birthing person bangs	534	\N	\N
marseyqueenlizard	4588	england bong english british reptilian elizabeth	77	\N	\N
marseyschizocarplove	8494	schizo carp love rare excited	50	\N	\N
marseykingcrown	5214	based animated	1952	\N	\N
marseystrawman	5526	logical fallacy strawmarsey argument debate hat	55	\N	\N
marseytarrant	2616	branton brenton newzealand kiwi shooter shooting killer ebba akerlund murderer rightoid chud strong	53	\N	\N
marseyneko	10881	autism autistic cute neko nekobit fedi fediverse hat programmer codecel	88	\N	\N
marseymati	150	annoyed irritation top hat reaction angry irritated tophat	55	\N	\N
marseyobese	5214	fat chonker bbw chonk chunky pig lorg	180	\N	\N
marseypsycho	768	reaction schizo crazy	357	\N	\N
marseyllama1	5845	top	75	\N	\N
marseymancer	5526	dead undead horror lich halloween necromancer zombies zombie holiday evil	44	\N	\N
marseyfursonatext	2626	fursuit fox fursona fursecution furfag yiff uwu owo kitsune	29	\N	\N
marseyclappingglasses	3259	applaud applause hooray yay good job gj animated nerd	417	\N	\N
marseycarpasian	1387	carpathianflorist fish azn racist hat paddy gook nip ching chong chink	58	\N	\N
marseypop2	1738	excited blahblahblah blah blah blah animated	179	\N	\N
marseypleading	1904	sad eyes begging puppy dog eyes	119	\N	\N
marseynpc2	1387	reaction idiot sheep	172	\N	\N
marseypuke	4588	hurl throw up gross animated illness vomit nauseated reaction upchuck nauseous sickening yuck barf ralph judgment	2900	\N	\N
marseypickle	1947	funniest shit morty rick	189	\N	\N
marseyoutletsuicide	1948	fork outlet plug socket kill kms electricity electrocution electrocute death die	39	\N	\N
marseyschizojoelove	8494	animated schizo schizocel rare love joe biden	27	\N	\N
marseyfrozen	2490	dead ice reaction cold frozen	96	\N	\N
marseyoceania	5214	kiwi new zealand kangaroo newzealand australia	59	\N	\N
marseynapoleon	1962	baguette soldier frenchman history	60	\N	\N
marseypumpking	5526	jackolantern jack o lantern halloween holiday	29	\N	\N
marseyzombie2	1387	undead living dead romero halloween horror corpse scary rotten	18	\N	\N
marseyhacker2	1817	dox anonymous computer	145	\N	\N
marseyatlasshrugged	3635	ayn rand objectivist objectivism libertarian girlboss capitalist capitalism book atlas shrugged	27	\N	\N
marseykatamarireddit	6914	rolling animated vidya video game damaci damacy reddit	28	\N	\N
marseyyugi	1948	yugioh yu-gi-oh! cards trap anime	50	\N	\N
marseypumpkin	2622	jackolantern carving halloween holiday jack o lantern	32	\N	\N
marseycatgirljanny	1387	anime maid weebshit	124	\N	\N
marseydawnbreaker	2256	gamer video game warhammer	40	\N	\N
marseynull	5214	kiwifarms joshua moon josh dog	87	\N	\N
marseyjolteon	635	trick or treat pokemon halloween eevee costume holiday	48	\N	\N
marseyglancing	4588	eyes animated nervous paranoid	473	\N	\N
marseynyanlgbt	5214	animated gay pride homosexuality space flying	28	\N	\N
marseyfbi	253	cop glownigger fed glowie agent federal	285	\N	\N
marseypride	5214	prideflag rights	63	\N	\N
marseycumjar3	1828	semen jizz sperm spunk bukkake	204	\N	\N
marseygodzilla	1817	raptor halloween dinosaur gojira evil bug	46	\N	\N
marseyminimalism	3652	orange minimalist square art	77	\N	\N
marseycontemplatesuicide	635	gunshot mirror contemplate contemplating reflection pistol handgun death kms kys suicidal die death	230	\N	\N
marseyjcdenton	4365	sunglasses shades vidya video game deusex deus ex	38	\N	\N
marseyn8	1858	nate redditor powermod powerjannie moderator	86	\N	\N
marseyheavymetal	1817	rocker musician rock guitar	131	\N	\N
marseypixel	2622	reaction lorez lowres	62	\N	\N
marseypopcorn	4122	eating entertained drama happy animated	348	\N	\N
marseyconstellation	3149	starsey galaxy space sky	19	\N	\N
marseyplane	5214	flying jet pilot	24	\N	\N
marseychocobo	8239	marseybo bird final fantasy vidya video game gamer gaming fast	26	\N	\N
marseycapychad3	9977	aevann chad capy chadybara capybara muscular swole ripped egypt nude naked	139	\N	\N
marseytoasterbath	4084	suicide suicidal kill death bathtub electrocution electricity kms	116	\N	\N
marseychartpie	7913	stats statistics chart graph plot data pie categorical	41	\N	\N
marseysopa	3127	brazil soup macaco monkey teeth fangs scary	20	\N	\N
marseynerd	653	dork loser dweeb geek glasses aevann	326	\N	\N
marseynooo	5526	reaction snob no way	51	\N	\N
marseyaynrand	3635	ayn rand objectivist objectivism libertarian girlboss capitalist capitalism author randsey	22	\N	\N
marseycapypunished	3652	capybara rodent aevann cute metal gear solid venom snake video game kojima mgs	44	\N	\N
marseyminion	4549	gru pixar	36	\N	\N
marseysoypoint2	6749	wojak soyjak soyjack pointing beta redditors	132	\N	\N
marseymutt2	5244	american burger 56 percent mayo	148	\N	\N
marseyburn	5214	fire flame grill burning hot red hell	99	\N	\N
marseylion	5214	fursona furry fursuit leo	62	\N	\N
marseyspinner	1710	animated loading webdev spin circle	25	\N	\N
marseyhammersrdine	3259	animated beat bongo hammers sardine redditors can the	83	\N	\N
marseyeyeroll2	1710	animated duh rolling eyes	225	\N	\N
marseypilgrim	1994	thanksgiving puritan holiday	30	\N	\N
marseycapywalking	5526	capybara animated aevann	144	\N	\N
marseygodel	1817	old philosophy glasses history	40	\N	\N
marseynintendo	2626	mario gamer switch gaymer video game mustache soy	125	\N	\N
marseycoonass	1088	student lsu university louisana state	135	\N	\N
marseyspookysmile	1817	horror halloween holiday evil scary monster	69	\N	\N
marseyobama	1710	obama president black drone reaper predator	90	\N	\N
marseypirate2	5214	party parrot eyepatch partyparrot	105	\N	\N
marseypepe2	2406	reaction frog mellokind	172	\N	\N
thinbluefeline	5244	cops police	35	\N	\N
marseycop	635	acab thin blue line chauvin police officer	622	\N	\N
marseyeyemixer	5214	mixer stirrer eyes blind selfharm mutilation gore blood gouge	89	\N	\N
marseydracula	4549	halloween fangs cape holiday vampire	97	\N	\N
marseyhope	5526	mask whitepill reaction happy hopium	284	\N	\N
marseymayoface	768	black blackface whiteface mayo mayocide mayonnaise racist racism	36	\N	\N
marseysalutecop	5214	acab officer saluting o7 police	220	\N	\N
marseycapychad2	9977	aevann chad capy chadybara capybara muscular swole ripped egypt	79	\N	\N
marseytaliban	1866	mujahideen janniejihad islam afganistan shariah afghanistan muslim	635	\N	\N
marseypizzashill	1962	sex haver chad grass toucher	679	\N	\N
marseysaw	5526	doll horror halloween jigsaw monster evil torture game holiday	40	\N	\N
marseypepe	3978	ok rightoid mellokind frog reaction	139	\N	\N
marseycutwrist	768	suicide slash wrist razor blood cry tears sad depressed depression kill dying kys cut cutting	46	\N	\N
marseybrap	5845	brap sniff smell huff gas fart animated	447	\N	\N
marseyghost	993	spooky halloween costume holiday scary sheet	250	\N	\N
marseyschizochadbasedcapylove	8494	animated schizo schizocel rare love chad based capy aevann	54	\N	\N
marseyjohnson	1817	wig history	99	\N	\N
marseysmudge	4588	diogenesjr diogenesjunior meme	24	\N	\N
marseyhappening	2622	ronpaul happening it ron paul itshappening animated	235	\N	\N
marseyblueanime	2546	cirno touhou weebshit	61	\N	\N
marseypikachu	2622	electric pokemon yellow	53	\N	\N
marseyjoseon	8094	korean hat azn asian	63	\N	\N
marseystinky	2256	smelly homeless stank poor ew yuck	259	\N	\N
marseybuff	3978	ripped muscular 6pack swole 6 pack sixpack abs six pack muscles	514	\N	\N
marseyjanny	542	jannie unpaid volunteer administrator janitor free moderator	1114	\N	\N
marseysnowflake	5845	special snowflake sensitive snow	41	\N	\N
marseyshisha	2256	weed smoker smoking hookah	40	\N	\N
marseynyan	5214	space animated meme poptart	67	\N	\N
marseyrs	5214	runescape party hat phat crown lowpoly low poly	69	\N	\N
marseynietzsche	1817	philosophy history	90	\N	\N
marseypretty	5526	flirt starry eyed stars in eyes	140	\N	\N
marseyschizochadseethecapylove	8494	animated schizo schizocel rare love chad seethe capy aevann	31	\N	\N
marseybraveheart	768	movie mel gibson william wallace scotland scottish sword claymore blue paint celt highland	25	\N	\N
marseysheep	5214	follower wool lamb fursona bah furry fursuit	48	\N	\N
marseycoomer	1947	masturbation goon cumbrain porn masturbate	906	\N	\N
marseysalad	1387	vegan cabbage vegetarian lettuce vegetable	78	\N	\N
marseypimp	1387	dramamine slickback purple baller	82	\N	\N
marseyschizochadyescapylove	8494	animated schizo schizocel rare love chad yes capy aevann	48	\N	\N
marseysting	8239	drum badumtiss ba dum tiss bad dum tiss baddumtiss comedy humor punchline animated standup joke	144	\N	\N
marseypoggers	1387	poggies twitch meme quagmire jawdropping shock surprise	119	\N	\N
marseyfursona	2626	fursuit fox fursona fursecution furfag yiff uwu owo kitsune	24	\N	\N
marseypostmodern	995	postmodernist obscurantist art	98	\N	\N
marseykoolaid	4634	oh yeah juice cult ice pitcher drink	62	\N	\N
marseymonke	2626	retvrn return	133	\N	\N
marseycringe2	1387	grimace grimacing yikes oof bruh moment	271	\N	\N
marseyblind	8021	sight stick disability blind glasses disabled handicapped	55	\N	\N
marseysus	768	amogus among us stonetoss sussy baka amongus	820	\N	\N
marseyschizocapylove	8494	schizo aevann capybara love rare excited	57	\N	\N
marsoyhype	1387	soyboy soybeard nerd marsey excited wojak cuck	1474	\N	\N
marseyilluminati	2519	eye egypt pyramid big brother watching	201	\N	\N
marseyrussel	1817	old pipe history	47	\N	\N
marseypumpkinglow	5214	halloween drama holiday jack o lantern animated	27	\N	\N
marseyagreefast	5214	nodding yes sure ok animated enthusiastic enthusiasm	1252	\N	\N
marseyblackfacexmas	5214	uncle tom moon cricket christmas santa beard nigger racist claus coon	45	\N	\N
marseysanta	4122	christmas gifts presents claus holiday	45	\N	\N
marseylizard	2519	reptilian	94	\N	\N
marseypainter	1794	palet reaction pallet paintbrush paints artist pallette	225	\N	\N
marseysalutearmy	5214	saluting o7 military soldier	560	\N	\N
marseygras	1738	mardi gras fat tuesday nola new orleans neworleans holiday louisiana mardigras carnival beads mask	26	\N	\N
goldenshower	5214	pee piss golden shower fetish trump sex rain storm clouds	64	\N	\N
marseyschrodinger	244	philosophy science physics math	54	\N	\N
marseycapy	5526	capybara rodent aevann happy cute	385	\N	\N
marseyembrace	3141	embracing hugging love happy	317	\N	\N
marseysnappyautism	1980	snapshillbot hat neurodivergent robot autistic marppy	117	\N	\N
marseymerchantelf	2069	jew christmas elf santa greedy money chosen worker holiday xmas seth rogen sarah silverman holocaust coin kike	199	\N	\N
marseyglow2	5845	fbi mossad feds agent glownigger reaction glowie fed atf cia nsa	561	\N	\N
marseygroomer	2626	pedobear discord pedophile pedo chomo molest pedocord	358	\N	\N
marseyjoint	4588	smoke weed marijuana reefer drugs smoking 420 pot	74	\N	\N
marseykweenxmas	5214	blm black christmas santa bipoc nigger bame hat holiday	57	\N	\N
marseypanda	4588	red panda bear happy redpanda	69	\N	\N
marseylenin	8239	ussr russia communism socialism marxist commie soviet proletariat marxism marxist leninist leninism revolution bolshevik	54	\N	\N
marseyparty3	5214	trippy animated happy dance	129	\N	\N
marseypin2	4240	sticky pushpin award	45	\N	\N
marseythomas	4588	tank engine train locomotive	175	\N	\N
marseypharaohcat	5214	egyptian illuminati aevann pyramid sand ancient alien artifact museum history king cleopatra	46	\N	\N
marseycapyeffendi	2256	capy aevann fez egyptian ottoman	21	\N	\N
marseyshitforbrains	6749	brainlet poop dumb litterbox litter box soyjack soyjak redditor retarded scat	212	\N	\N
marseycupid	5214	cupid, love, heart, valentines holiday, marry, wedding, couple, kiss, wink, sex, arrow, bow, shoot animated	38	\N	\N
marseysosa	1809	chief keef sosa glo rap hiphop music drugs lean black	39	\N	\N
marseymyeisha	1817	kween black fds	121	\N	\N
marseysamhyde2	4928	gun shooter sammy mdegenerate milliondollarextreme million dollar extreme	78	\N	\N
marseyquadmagyar	2256	bow and arrow hungary hungarian archery bowman quadnarca	109	\N	\N
marseytrollcrazy	7056	i hate killher psycho rage kill her gun	723	\N	\N
marseysmug	542	reaction superior haha	1260	\N	\N
marseytunaktunak	5526	turban animated curry indian pajeet dance	890	\N	\N
marseyuglyxmasweater	4565	santa hat christmas ugly holiday	47	\N	\N
marseycheeky	1387	stick tongue brat reaction taunt na tongue out tease	253	\N	\N
marseymechanic	5214	wrench car diy fix repairman dipfuck	38	\N	\N
marseyunamused	8613	annoyed staring reaction disappointed stare uh huh bored	1043	\N	\N
marseyhearts	832	reaction flirt loving adoration love happy cute crush	1204	\N	\N
marseymime	5526	mimesey facepaint black and white beret silent mute performer	30	\N	\N
marseytrollolol	5214	rage trolled rageface	186	\N	\N
marseytrump	2626	cheeto hitler president history orange man	359	\N	\N
marseypope	1947	priest catholicism rome	465	\N	\N
marseyrasta	4588	marijuana weed dude weed lmao ganja drugs pot reggae joint jamaican	123	\N	\N
marseydab	5526	reaction haters	343	\N	\N
marseyyeezus	2056	kanye god hotep	221	\N	\N
marseymask	4240	plague coronavirus covid pandemic coof sickness love heart eyes illness	160	\N	\N
marseylowpoly	5526	polygonal spinning 3d lopoly animated	43	\N	\N
marseycreepy	1387	pervert pedophile weird reaction chomo creeper sketchy molester	65	\N	\N
marseypathetic	5526	pathetic asuka	170	\N	\N
marseypanties	8979	reaction underwear panty pantsu	315	\N	\N
marseyplaying	5526	fish playful mischief srdine animated	105	\N	\N
marseymugshot	5214	arran prison arrested criminal jail	154	\N	\N
marseypopcorntime	5214	eating popped corn drama animated watch	409	\N	\N
marseymushroomcloud	3149	atomic bomb nuke kaboom explode explosion war radiation	112	\N	\N
marseyteaparty	2256	donger arran soren carp duck	76	\N	\N
marseymao	7057	zedong ccp chinese communist communism china	265	\N	\N
marseyemojismilemoutheyes	1387	emoji reaction smile	37	\N	\N
marseyplaying2	5526	fish playful mischief srdine animated	115	\N	\N
marseyglobohomo	1387	globalism soulless modernity art corporate corporation	11	\N	\N
marseygoodnight	1794	kazakhstan flag reaction kazakh i hate women women	753	\N	\N
marseyazov	542	ukraine ukrainian nazi battalion dead russian war soldier corpse chud	100	\N	\N
marseybeandefiant	1828	bean defiant tongue opposed disagree	38	\N	\N
marseyhankhill2	3370	propane cartoon hank grill kingofthehill	19	\N	\N
marseypeacekeeper	2519	united nations un rifle helmet gun	187	\N	\N
marseykys2	1817	keep yourself safe	510	\N	\N
marseytv	2622	willy wonka telly television	75	\N	\N
marseyobamanope	3149	no way wrong poster barack	72	\N	\N
marseyobey	4240	1984 sign ingsoc poster big brother	167	\N	\N
marseywtf	1387	scared reaction shook surprised shocked	237	\N	\N
marseyotter	5214	otter, fish, sea, swim, lake, nature, seal, sealion, river. wuzizname, float	28	\N	\N
marseyuwuw	1387	fursona furry fursuit	63	\N	\N
marseytoilet	2626	flush loo bog roll toilet paper swirly	55	\N	\N
marseyprotestno	1387	sign protester refuse reaction deny reject	234	\N	\N
marseylibleft	1817	unemployed protest riot anarcho capitalist antifa anarchist anarchy	189	\N	\N
marseyfuckoffcarp	5526	reaction carpathianflorist rude snappy animated robot marppy	520	\N	\N
marseyrave	5526	dead animated party death sandstorm darude crab dance	582	\N	\N
marseyantischizo	8494	rare meta schizocel scizocel skitzocel schizophrenic scitzocel	494	\N	\N
marseysherpa	8021	mountain climbing travel nepal himalaya asia everest	18	\N	\N
marseyemojigrin	1387	emoji reaction grin	11	\N	\N
marseysneedboat	8494	animated ship flag capybara	62	\N	\N
marseymummy	1817	egyptian halloween monster holiday	37	\N	\N
marseyramen	5214	eating noodles food bowl animated soup	137	\N	\N
marseytheorist	1387	ancient aliens meme	70	\N	\N
marseyevilagent	8021	feds agent glowies usa america waco swat m16 firearm rifle satan demon cops police	33	\N	\N
marseypony	1948	murmurwisper mlp my little ponies cutie mark horse furry my little pony	103	\N	\N
marseyspit	4588	surprising reaction shocking water surprised shocked	290	\N	\N
marseytea	4122	drama spill	139	\N	\N
marseyfrozenlove	9790	mellokind stalker obsessed obsession fixation creepy stalking frozenchosen love hug foid hearts	34	\N	\N
marseypop	2890	action figure doll funko toy soy	116	\N	\N
marseyracistgrandpa	2626	thanksgiving fuck nigger holiday	165	\N	\N
marseyobamarope	35	barack suicide kms kys hanging noose poser	233	\N	\N
marseymommymilkers	1710	pepe mellokind momma booba khazar abby shapiro tits breasts boobs	389	\N	\N
marseygeisha	5526	foid birthing person girl woman girl lady slut thot noodlewhore chink jap gook asian azn blow kiss blowing kiss blowkiss love heart stockings nylons fishnets	211	\N	\N
marseyteruteru	5526	ghost flying spooky halloween holiday floating	40	\N	\N
marseyawardretard	3259	medal retarded drooling idiot moron prize congratulations congrats	158	\N	\N
marseypumpkincloak	2056	costume halloween holiday	31	\N	\N
marseycumjar1	1828	semen jizz sperm spunk bukkake	124	\N	\N
marseyfbiagent	8021	feds fbi agent glowies usa america waco swat m16 firearm rifle cops police	43	\N	\N
marseygoose2	3783	goose geese kill cat bird death bite chomp	46	\N	\N
marseypokerface	8979	small eyes reaction stare unreadable beady eyes	73	\N	\N
marseysad2	8979	reaction disappointed disappointment upset	255	\N	\N
marseydizzy	2626	puke nausea spinning vomit reaction nauseous sick rolling barf animated	511	\N	\N
marseyjumpscare	1387	undead living dead romero halloween horror corpse scary rotten animated spooky aaaahhhhh trick prank bait and switch	37	\N	\N
marseydefenestration	5214	suicide window jump kill murder kms jump out window death die defenestrate	78	\N	\N
marseydeux	542	frenchman deuxrama baguette frog frenchie	374	\N	\N
marseyhesright	10181	batman lucius fox nolan hes right you know reaction agree thumbs up based morgan freeman correct	1002	\N	\N
marseyclippy	3259	msoft microsoft word helper paperclip writing annoying	48	\N	\N
marseyblops2cel	5526	incel volcel black ops gamer iconic saint	139	\N	\N
marseyzoomer	1387	child brat kid zoomie	396	\N	\N
marseykamikaze	5214	kamikaze japanese nip pilot ww2 wwii world war	156	\N	\N
marseytalking	5214	speech bubble smug gossip	53	\N	\N
marseypumpkin3	3211	witch jackolantern carving halloween holiday jack o lantern	27	\N	\N
marseychad	1387	canthal tilt jaw hunter eyes	403	\N	\N
marseyrat	1387	rodent black	76	\N	\N
marseyschizodoggilove	8494	animated schizo schizocel rare love dussy doggi	14	\N	\N
marseycarplazy	201	carpathianflorist fish couch sleeping slacker idc antiwork janitor	48	\N	\N
marseywendy	4549	jellyfishjam pigtails redhead pippi	43	\N	\N
marseychinesedevil	1387	devil evil horns satan china hell demonic	38	\N	\N
marseyyes	5526	thumbsup agree right thumbs up reaction judgment	709	\N	\N
marseytimmy	8239	turner nickelodeon fairly oddparents hat boy cosmo wanda	19	\N	\N
marseyhelp	1387	wtf nervous anxious anxiety worried concerned helpme help me uncomfortable awkward	70	\N	\N
marseyorthodoxsmug	3652	schismatic heretic scoff christian priest gloat	47	\N	\N
marseytroll2	2256	ogre horror halloween holiday monster	58	\N	\N
marseybootlicker2	5214	sheep conformist lapdog rightoid conservative trump idiot shoe hearts	102	\N	\N
marseyditzy	5526	pokemon	31	\N	\N
marseysanders	2626	bernie rich socialism socialist jewish	98	\N	\N
marseyeric	635	columbine school shooter psycho gun carbine harris	128	\N	\N
marseyllama2	5845	middle	101	\N	\N
marseyobesescale	5214	fat chonker bbw chonk chunky pig lorg	345	\N	\N
marseypumpkin4	3211	ghost jackolantern carving halloween holiday jack o lantern	37	\N	\N
marseyface	2626	mask psycho face horror halloween kill killer stab knife holiday evil murder scary murderer	217	\N	\N
marseymeowth	5214	pokemon weeb anime, manga team rocket nintendo video game vidya monster	32	\N	\N
marseywarboy	993	witness warboy nux madmax mad max apocalyptic evil apocalypse	48	\N	\N
marseydemiurge	1817	gnostic gnosticism demiurge	31	\N	\N
marseysmirk	8979	reaction snicker trolling lol	317	\N	\N
marseycanada	5214	leaf canadian canuck rake hockey donut trudeau maple	70	\N	\N
marseygoose	5525	goose geese kill duck cat bird death bite chomp	27	\N	\N
marseypresents	2616	christmas gifts santa holiday candy cane happy	63	\N	\N
marseypanda2	5214	panda bear fursona skin animal costume furry fursuit	46	\N	\N
marseyandmarcus	2513	bed sleeping cuddling cuddle marseyismywaifu	215	\N	\N
marseymar	8239	dexter lab foid destruction irritating annoying sister cartoon network pigtails	34	\N	\N
marseyhammerpizza	3259	animated beat bongo hammers pizzashill rdrama	40	\N	\N
marseytwins	5214	halloween holiday flashing shining scary animated	30	\N	\N
marseyseven	2256	vidya gamer gaymer video game assassin hitman	67	\N	\N
marseyisrael	2873	kike yid jewish hebrew merchant colonizer israeli banker	130	\N	\N
marseycactuar	8239	cactuar final fantasy cactus soy shocked cactuarsey 1000 needles vidya video game	40	\N	\N
marseyturkey	1994	beak bird thanksgiving holiday feathers	56	\N	\N
marseynoyou	5526	nou no u pointing	244	\N	\N
marseyakbar	5214	suicide bomber explosion boom explode die kms animated	117	\N	\N
marseysamhyde	8239	gun shooter sammy mdegenerate milliondollarextreme million dollar extreme	50	\N	\N
marseyjason	5526	hockey mask horror halloween kill fridaythe13th knife stab voorheys friday the 13th evil monster holiday	131	\N	\N
marseyschizocapygitcommitlove	8494	animated schizo schizocel rare love chad capy git commit fsdfsd	32	\N	\N
marseyschizodongerlove	8494	animated schizo schizocel rare love kaiser uraniumdonger donger	28	\N	\N
marseysurprised	8979	reaction shocked shook unexpected	152	\N	\N
marseyradioactive	2519	nuclear waste chernobyl radiation geiger	89	\N	\N
marseymoney	1387	capitalism capitalist rich dollar signs bag wealthy dollars dinero	75	\N	\N
marseyskeleton2	2256	bones spooky halloween holiday skeletal	72	\N	\N
marseyditto	3149	pokemon weeb anime blob happy	31	\N	\N
marseyyinzer	4017	pittsburgh pennsylvania pens penguins steelers stillers pirates buccos buckos terrible towel pierogo yuengling beer city hat baseball football hockey nfl mlb nhl happy	27	\N	\N
marseyjunkie	1387	needles heroin reaction shooting up addicted shoot up syringe	258	\N	\N
marseytrotsky	8239	icepick trotskyist betrayal ussr russia communism socialism marxist commie soviet proletariat marxism marxist leninist leninism revolution bolshevik	28	\N	\N
merdesey	244	turd turdsey shitsey poopsey shit poop poop marsey shit marsey	201	\N	\N
marseyprideflag	4154	pride flag marseysexual sexuality lgbtq gay trans bipoc queer activism	74	\N	\N
marseykitty	1738	hellokitty animated hello kitty	42	\N	\N
marseyshiftyeyes	2256	suspicious sussy paranoid weird reaction sketchy	166	\N	\N
marseyjetfighter	8239	pilot plane airforce air force usaf bomber dogfight war	72	\N	\N
marseysunflower	3259	love ukraine threatening pointing russia	110	\N	\N
marseywheredrama2	5214	seriouspost animated agendapost	71	\N	\N
marseyvengeance	2069	gore undead shotgun horror halloween revenge monster bloody head wound holiday	108	\N	\N
marseycheerup	5214	pat animated depressed comforting grieving reaction depression there there console comfort pet	955	\N	\N
marseyoverseether	1947	rdrama meta seething fire red bigmad angry anger	82	\N	\N
marseykiwi2	5526	kf bird new zealand kiwifarms newzealand	128	\N	\N
marseylong3	4122	bottom meme	263	\N	\N
marseyking	1701	based queen prince reaction crown princess	1401	\N	\N
marseysmugretard	6345	srdine drooling brainlet idiot fool buffoon idiot	98	\N	\N
marseystars	5526	stareyes reaction star eyes starry eyed stareyed	151	\N	\N
marseyavril1	5526	lavigne canadian leaf beautiful hot sexy punk rocker singer musician artist tie sk8er boi complicated brunette	25	\N	\N
marseylibright	1817	libertarian anarcho wagecuck pedophile capitalist lolbert	80	\N	\N
marseyunabomber	542	package industrial society delivery mail kaczynski uncle ted	983	\N	\N
marseyraccoon	5214	trashpanda trash panda	47	\N	\N
marseyfingergoodjob	5214	cute encourage positive respect k-pop thumbs up congrats gif animated congratulations nice ok great	70	\N	\N
marseyoctopus3	3908	consume product epic win communities no bait too obvious globe patch	209	\N	\N
marseysnek	4122	snake serpent	127	\N	\N
marseycop3	5214	police officer acab fuck12 rifle gun law enforcement sheriff	85	\N	\N
marseycrystal	3166	gem crystal diamond sparkle precious shiny glass	22	\N	\N
marseyschopenhauer	1387	philosopher old grandpa	41	\N	\N
mlm	5214	marseylivesmatter marsey lives matter blm	92	\N	\N
marseykkk	993	klan kukluxklan ku klux klan racist costume klux ku sheet	292	\N	\N
marseysephiroth	8239	ff7 ffvii final fantasy vidya video game gamer gaming villain sword	26	\N	\N
marseysuper	2519	superstraight lgbt	91	\N	\N
marseydream	1828	spirals trippy swirls rainbow	40	\N	\N
marseyplugged	2626	electric technology gif animated plug	54	\N	\N
marseyschizobussylove	8494	animated schizo schizocel rare love certified bussy operator	29	\N	\N
marseyrightoidschizo	1387	nazi conspiracy crazy tin foil tinfoil conservative animated ruqqus	199	\N	\N
marseybased	5214	basado king chiobu redpilled reaction animated	883	\N	\N
marseysoutherner	9977	plantation suit cigar good ol boy buck breaking buck breaker	208	\N	\N
marseyaustralian	4634	beer fosters mate hat gday crikey oz	81	\N	\N
marseyrussiadolls	5214	toys ussr babushka matryoshka soviet	51	\N	\N
marseysadge	2069	frog pepe	434	\N	\N
marseybutt	5845	booty ass rump sexy hot pawg pawc paoc anal sodomy donk dump truck dumptruck mellokind	207	\N	\N
marseykindness	995	retarded special drooling idiot seriouspost srspost agendapost moron fool buffoon dramatard	79	\N	\N
marseyterrydavis	7272	templeos nerd programmer glownigger	65	\N	\N
marseyspider	1828	insect halloween arachnid holiday bug	84	\N	\N
marseygarfield	2546	mondays lasagna	39	\N	\N
marseyno	5526	denied refuse rejection reaction ugh deny hand	1533	\N	\N
marseykkkblm	5214	ku klux klan racist nigger jogger coon jiggaboo cracker crackkka	109	\N	\N
marseypunisher	5244	thin blue line rightoid police cops	59	\N	\N
marseycrying	4588	tear cried despair weeping reaction depression sob tears sadness depressed animated sad	1313	\N	\N
marseyopossum	5845	possum trash	27	\N	\N
marseycapylove	1994	aevann heart eyes hug adore adoration snuggle cuddle capybara	353	\N	\N
marseykrampus	2256	demon monster christmas	40	\N	\N
marseyremastered	8159	4k hd hi def hidef high definition uhd rtx	26	\N	\N
marseysoyrope	6749	redditor dead suicide kms kys hanging lynched hung soyjak	117	\N	\N
marseyreindeer2	1817	santa christmas rudolf holiday	27	\N	\N
marseybootlicker	5214	sheep conformist lapdog rightoid conservative trump idiot shoe	37	\N	\N
marseyspooky	5526	art horror halloween holiday evil scary monster lovecraftian eldritch	73	\N	\N
marseyorthodoxcarphug	3652	schismatic heretic embrace hug love bartholomew carpathianflorist	30	\N	\N
marseyretro	6382	cardboard retro gameboy green nerd gamer	30	\N	\N
marseyportalsuicide	5214	kill shotgun shoot death die kms animated	28	\N	\N
marseyshook	8613	reaction surprised shocked gasp astonished	1478	\N	\N
marseykrampus2	1794	demon monster christmas	26	\N	\N
marseykino	3140	kino agni fire punch anime	71	\N	\N
marseyfrontiersman	8021	america usa 19th history indian native wild nature rural frontier expansion settler	40	\N	\N
marseyespeon	635	trick or treat pokemon halloween eevee costume holiday	37	\N	\N
marseypumpkin2	3211	jackolantern carving halloween holiday jack o lantern	33	\N	\N
marseyantiwork	5214	lazy laze bum unemployed animated	188	\N	\N
marseyelephant	2256	oliphant dumbo	38	\N	\N
marseyloading	5526	animated loading spinner webdev rolling ball circle	26	\N	\N
marseyseethe	1947	dilate mask crying seething smug cope	1581	\N	\N
marseysickos	3652	hahaha ha ha ha yes onion comic pervert sicko creep	54	\N	\N
marseydarwin	1817	history darwinian euphoric atheist charles	43	\N	\N
marseydicklet	1387	babydick penis micro dick reaction laugh point and laugh micropenis judgment	993	\N	\N
marseytariq	5526	buck breaking nasheed nigger coon black	161	\N	\N
marseyponder	3652	ponder orb wizard magician crystal ball	66	\N	\N
marseyvargselfdefense	2256	vikernes euronymous mayhem burzum black metal norway norwegian stab knife kill murder	46	\N	\N
marseyslab	8239	dexter lab smart genius ginger cartoon network glasses	23	\N	\N
marseysalutenavy	5214	saluting semen o7 homosexual soldier	225	\N	\N
marseymini	5526	annihilate minigun machine gun kill destroy murder animated	1018	\N	\N
marseyoldtimey	4634	cartoon disney vintage olde classic retro	27	\N	\N
marseyfox	5214	fursona furry fursuit kitsune	65	\N	\N
marseyza	5214	antlers flowers	36	\N	\N
marseygarfieldpipe	6914	marfield pipe smoking john yelling comic smoke	38	\N	\N
marseysteer	2890	car drive nervous driving animated	372	\N	\N
marseywalking	5526	stroll walk strut gallivant animated	218	\N	\N
marseyretard	542	special ed retarded reaction slow sped drooling exceptional	403	\N	\N
marseytrickortreat	1994	candy trick or treat halloween holiday	26	\N	\N
marseyschizochadthankscapylove	8494	animated schizo schizocel rare love chad thanks queen capy aevann	112	\N	\N
marseyemojismilemouth	1387	emoji reaction smile	16	\N	\N
marseybee	1817	bee honey honeybee insect fly honeypot pollinate pollen animated	164	\N	\N
marseywolf	5526	halloween werewolf holiday scary monster	77	\N	\N
marseyglow	2548	fbi mossad cop feds animated glownigger glowie secret service fed atf police cia nsa kgb	4488	\N	\N
marseygivecrown	8979	king based swole reaction muscles	625	\N	\N
marseyblush	8979	shy flirting reaction blushing happy cute embarrassed	878	\N	\N
marseyfans	5526	of thot taxpayer slut onlyfans whore	284	\N	\N
marsheen	1738	pusheen animated meme cute	69	\N	\N
marseyzombie	5526	dead undead eye horror intestines halloween holiday monster	75	\N	\N
marseybeggar	2626	poor busking panhandler gofundme busker	242	\N	\N
marseyweeb	1387	neckbeard sword fedora kitana	289	\N	\N
marseywarhol	2622	modern art	31	\N	\N
mcmarsey	5526	wageslave poor mcdonalds wagecuck maccas antiwork college wagie	128	\N	\N
marseydisagree	4588	nah uh nod nuh uh reaction wrong no way no negative animated judgment smh	4772	\N	\N
marseymad	8613	pissed annoyed furious reaction angry irritated livid	1662	\N	\N
marseysharingan	5214	horror halloween holiday possessed animated monster naruto anime ninja	37	\N	\N
marseyschizodussylove	8494	animated schizo schizocel rare love dussy doggi	22	\N	\N
marseyoldguard	8021	napoleon war soldier musket french france history europe reaction	39	\N	\N
marseyjfk	8021	john fitzgerald kennedy jfk president american history sniper car death kill usa assassination	23	\N	\N
marseypenguin	2548	bird linux puffin	104	\N	\N
marseyspiderman	8239	soy marvel capeshit dc comic book comics peter parker miles morales webslinger	46	\N	\N
marseycool	1387	finger gun shades sunglasses reaction judgment	1165	\N	\N
marseywinner	2622	reaction trophy gold prize first place	168	\N	\N
marseyparty	8613	excite excitement celebrate happy celebrating	1367	\N	\N
marseyrobber	3472	mask balaclava gun shooter shooting thief criminal nigger jogger ahmaud arbery george floyd	109	\N	\N
marseytransflag2	4928	lgbt transgender tranny pride animated	144	\N	\N
marseyzodiac	2546	zodiac killer zodiackiller tedcruz ted cruz murderer crazy mask gun shooter shooting death	35	\N	\N
marseycodecellove	768	love bsod code dev hug heart computer tech admin admigger program	61	\N	\N
marseybrainlet	2890	idiot imbecile smoothbrain crushed head retard caved in head sped dumb stupid drooling moron	1623	\N	\N
marseydolphin	2626	ocean goggles rainbow	40	\N	\N
marseysexypepe	2256	mellokind hotpepe frog lewd flirt ribbon	55	\N	\N
marseymarseylove	5214	aww blush hugging cuddling cuddle snuggle snuggling hearts shy kiss xoxo	868	\N	\N
marseyconfused	2548	questionmark reaction question mark idgi confusion	3245	\N	\N
marseysquint	4084	4084 hmmm squint unsure doubt	492	\N	\N
marseypirate	541	argh eyepatch bandana uraniumdonger	122	\N	\N
marseyishygddt	635	reaction, meme, disapproval, bat, club, beating, angry, demented disgust, dislike, baseball bat, shiggy diggy, george costanza	127	\N	\N
marseyhannibal	1387	flesh psycho horror halloween cannibal eat holiday	98	\N	\N
marseygangbang	3652	blacked sex orgy	53	\N	\N
marseymaxrockatansky	5526	mad max madmax fury road furyroad post apocalyptic apocalypse australian australia	55	\N	\N
marseyfellowkids	5526	groomer adult buscemi skateboard	83	\N	\N
marseychinchillalove	5214	pet rodent capy cute hamster south american andes	29	\N	\N
marseysexy	3908	ned flanders stupid sexy flanders skiier skiing winter simpsons	40	\N	\N
marseyminer	6284	miner minecraft mine craft mining digging minor blocks pixel game vidya video notch	79	\N	\N
marseychicken	5214	bird fowl poultry beak hen rooster happy	32	\N	\N
marseygigavaxxer	2626	covid vaccine coronavirus vaccination	183	\N	\N
marseysnap	1387	mad angry furious anger animated snap	52	\N	\N
marseyjaguarwarrior	1817	mayan incan injun latinx aztec native blood fight mexican	40	\N	\N
marseyrussiaglow	8159	animated russia red putin fsb kgb glow trump commie communist hat comrade	64	\N	\N
marseypathetic2	1387	anime weeb asuka shun scorn disgust contempt disgusted	38	\N	\N
marseydisintegrate	1067	disappear marvel explode dust thanos snap evaporate crying sad vanish animated snapped	324	\N	\N
marseymouse	1828	rodent cheesed to meet you	110	\N	\N
marseyturkeyhappy	4588	bird thanksgiving food dinner yum delicious holiday	34	\N	\N
marseyqueen	4588	england bong english british elizabeth	208	\N	\N
marseysartre	1817	philosophy frenchman history	43	\N	\N
marseyblackmage	8239	magic wizard final fantasy spell video game vidya evil	77	\N	\N
marseypajeet	5214	indian currycel bobs vagene streetshit street shit superpower 2020 happy	71	\N	\N
marseyyeti	8021	scary monster myth winter ice mountain himalaya asia predator giant	16	\N	\N
marseyinvisible	1828	stealth	422	\N	\N
marseythief	8239	steal final fantasy video game vidya	25	\N	\N
marseynun	4588	habit catholic	85	\N	\N
marseyluther	2622	heretic lutheran theses martin luther	84	\N	\N
marseyjetbombing	8239	obama bush animated usa animated american pilot bomber plane war usaf air force	86	\N	\N
marseyplush	5526	bow ribbon doll plushie button eyes	40	\N	\N
marseymap2	7913	map geography topographical paper navigation chart cartography location place	23	\N	\N
marseysalat	5214	prayer islam muslim rug	428	\N	\N
marseyimmaculate	5214	christian christmas jesus immaculate god mother mary xmas pray	287	\N	\N
marseyvaporwave	2622	trippy 80s psychedelic animated retro	60	\N	\N
marseysnowman2	2069	christmas cold snow winter	25	\N	\N
marseyasian	542	chinese china srdine sardine	264	\N	\N
marseyrain	8613	cloud upset reaction disappointed storm depressed sad	1791	\N	\N
marseymorph	2616	skinwalker changeling	43	\N	\N
marseynotes	3259	notes writer writing journ*list therapist doodle	1550	\N	\N
marseysrdine	1794	fisherman reaction fish canned fishing	269	\N	\N
marseywitch3	4122	flying broomstick wave halloween wizard holiday	84	\N	\N
marseytruck	1710	honk canadian trucker hoonk ottawa convoy leaf semi 16wheeler	134	\N	\N
marseyimmortanjoe	5526	immortansey mad max madmax fury road furyroad post apocalyptic apocalypse australian australia	59	\N	\N
marseyminimalism2	1828	minimalist polygons polygonal art	22	\N	\N
marseyavril3	5526	lavigne canadian leaf beautiful hot sexy punk rocker singer musician artist blonde green hair he wasnt	56	\N	\N
marseynails	7056	manicure emoji pedicure	1708	\N	\N
marseythroatsinging	1863	mongolian music	110	\N	\N
marseyfigureskate	5214	skater iceskate ice skate skating olympics winter on ice	50	\N	\N
marseystarbucks	8727	coffee latte barista marbucks scone	28	\N	\N
marseysuit	8239	businessman businessperson corporate boss manager rich adult professional lawyer banker	64	\N	\N
marseyaleistercrowley	4154	aleister crowley occult wizard robe esoteric bisexual	20	\N	\N
marseymarseylovelove	3149	reaction love blush aww hugging cuddling cuddle snuggle snuggling hearts xoxo nested recursion inception wholesome	43	\N	\N
marseymexican	5526	latina latino hispanic fiesta sombrero latinx hombre mexico	229	\N	\N
marseyantiwork2	5214	lazy doreen unemployed slacker lazing laying welfare tired	75	\N	\N
marseymilesdavis	1829	jazz saxophone bebop music trumpet brass black	37	\N	\N
marseydoit	1387	pistol handgun kys kill yourself glowie federal agent fbi cia atf nsa glow nigger glownigger suicide suicidal keep yourself safe	157	\N	\N
marseyadeptusmechanicus	1817	warhammer 40k adeptus mechanicus	19	\N	\N
marseyonacid	5214	tripping trippy drugs lcd animated	109	\N	\N
marseygunnut	1387	ahegao 2a second amendment rifle horny lust lick tongue shooter shooting	83	\N	\N
marseyw	2622	win winner dub	84	\N	\N
marseyjiangshi	5526	ghost chinese halloween holiday china scary	61	\N	\N
marseyneon	5214	wave flashy trippy waving flashing lights animated	55	\N	\N
marseyangrygamer	11483	gamer angry mad nes console nerd	30	\N	\N
marseyklenny	2050	chiobu jenna thorne grunderchin vidunderchin clapping applause animated	133	\N	\N
marseywave	8613	farewell cya hello greetings bye waving hi	1168	\N	\N
marseypenny	10288	penny mrpenny black trad foid bleeder female woman kween negro dress baptist christian	122	\N	\N
marseysociety2	5845	joker clown capeshit batman gamersriseup cigarette honk	168	\N	\N
marseytelegram	3149	telegram homecoming plane chat messaging russian	50	\N	\N
owlsey	5526	bird hoot feathers	83	\N	\N
marseybaphomet	5845	halloween demon satan holiday evil devil	115	\N	\N
marseyshapiro	1387	benjamin debate libtard facts and logic benny jewish ben shapiro	446	\N	\N
marseypipe	2526	smoke smart mhm yes smoking tobacco intelligent	501	\N	\N
marseypearlclutch2	2626	sensitive reaction snowflake puritanical gasp sjw	309	\N	\N
marseykernelpanic	10456	linux kernel panic computer error glitch	27	\N	\N
marseyschizofartbinnlove	8494	animated schizo schizocel rare love fartbinn idk idc	25	\N	\N
marseymothermary	5214	christian christmas jesus immaculate god mother mary xmas pray	98	\N	\N
marseymiku	8239	hatsune miku pop star concert rave weeaboo music animated singing microphone	71	\N	\N
marseyjapanese	5214	nippon rising sun weeb japan animated	110	\N	\N
marseylaptop	5214	notebook macbook computer	71	\N	\N
marseyplace	4565	reddit pixels pixellated pixellation lowres	19	\N	\N
marseyninja	8239	samurai japanese killer stealthy sneaky assassin weeb	29	\N	\N
marseyshroom	1817	smug fungus shrigma shroomjak wojak mushroom	81	\N	\N
marseyski	2626	skier skiing sking winter snow	34	\N	\N
marseytherapist	1817	therapy writing mental illness	71	\N	\N
marseychimera	5214	fullmetal alchemist chimera science trans doctor anime dog sad depressed tragic anime fma weeb	49	\N	\N
marseyjeans	5526	denim trousers pants	48	\N	\N
mersya2	5526	drawing art	28	\N	\N
marseymountaineer	8021	winter climbing coat ice sport peak axe cleats mountain alpine climber	14	\N	\N
marseyschizogeeselove	8494	animated schizo schizocel rare love geese suck	24	\N	\N
marseythinkorino	4565	reaction judgment thinking	2604	\N	\N
marseydead	8613	murdered dead killed reaction victim die rip	1417	\N	\N
marseysaluteusa	8239	salute o7 animated flag patriotic patriotism burger nationalism flag american	415	\N	\N
marseycapyexcited	5214	excitement capybara bouncing jumping aevann bounce yay animated	125	\N	\N
marseywave2	7056	waving hi hello cya bye later animated	468	\N	\N
marseyfatherjoseph	5214	christian christmas jesus immaculate god father joseph xmas pray	78	\N	\N
marseychristmasparty	5526	christmas holiday celebrate party wooo	139	\N	\N
marseyreindeer3	5526	rudolf dasher dancer prancer vixen comet cupid donner blitzen santa sleigh sled christmas winter holiday	38	\N	\N
marseyorthodoxbrap	3652	orthodox bartholomew brap fart gas sniff smell christian	37	\N	\N
marseybigbrain	1387	high iq highiq smart genius brain	1227	\N	\N
marseycortana	3370	cortana halo game blue	15	\N	\N
marseyschizowall	5526	crazy conspiracy conspiracies tinfoil insane nuts psycho	572	\N	\N
marseychristmasbulb	541	ornament christmas happy holiday china	52	\N	\N
marseynutcracker	635	soldier halberd pike christmas holiday	26	\N	\N
marseyskeleton	635	dead bones halloween holiday skeletal	135	\N	\N
marseygingerbread	5526	cookie christmas holiday	29	\N	\N
marseyrake	5200	canada canadian day of the rake leaf leaves fall autumn genocide	343	\N	\N
marseytimbit	2980	pearlclutch pearl clutch sjw triggered canadian leafistan canada crying	33	\N	\N
marseypinochet	2519	fascist fash ugarte augusto chopper helicopter chile	238	\N	\N
marseyreindeer4	5526	rudolf dasher dancer prancer vixen comet cupid donner blitzen santa sleigh sled christmas winter holiday	30	\N	\N
marseyschizoshaking	5526	crazy nuts insane traumatized shaking animated	159	\N	\N
marseydiehard	1710	die hard christmas holiday terrorist gun bruce willis	75	\N	\N
marseysnoo	2626	shaking redditor scared reaction nervous schizo reddit	857	\N	\N
marseytrollgun	2616	kill her psycho	950	\N	\N
marseytonberry	8239	tonberry monster final fantasy knife lantern scary flashlight headlamp vidya video game	21	\N	\N
marseyastronaut	3370	astronaut space stars sleeping spacesuit scifi galaxy	61	\N	\N
marseyschizomajorgenerallove	8494	animated schizo schizocel rare love modern major general	35	\N	\N
marseyzwei	993	drinking germany lederhosen zweirama bavarian beer	308	\N	\N
marseydeathpose	1067	griffin family dead broken	57	\N	\N
marseyreich	5244	nazi pol authright fuhrer hitler fascist	529	\N	\N
marseygingerbread3	5526	cookie christmas holiday	31	\N	\N
marseyvaporeon	635	trick or treat pokemon halloween eevee costume holiday	42	\N	\N
marseychristmasscarf	5526	christmas holiday candy cane cold winter candycane	47	\N	\N
marscientist	5526	beaker goggles glass crazy chemicals science	376	\N	\N
marseysoon	2256	weeks 2weeks sal antisal soon	33	\N	\N
marseyreindeer	7056	christmas santa rudolf capy cold aevann holiday animated walking	73	\N	\N
marseyretard2	5526	drooling stupid idiot sped moron imbecile dolt happy tongue	350	\N	\N
marseyhitler2	4122	adolf adolph nazi germany kraut axis mustache genocide dictator authright chud conservative trump	128	\N	\N
marseyzombiewolfmarseymask	2622	sussy amogus fraud fake phony cope seethe	32	\N	\N
marseywolfwalker	1710	doreen antiwork zombiewolf dogwalker dogwalking dog walker	17	\N	\N
marseyunpettable	542	dramamine fashy rightoid chud fashwave altright vaporwave	150	\N	\N
marseyfuriosa	5526	mad max madmax imperator furryosa fury road furyroad post apocalyptic apocalypse australian australia	52	\N	\N
marseybadnews	3336	comic bad news drawing idgaf heathcliff smug troublemaker	44	\N	\N
marseyblackcock	635	cock chicken poultry bbc black ride mount cowgirl	44	\N	\N
marseycoal	2622	christmas naughty santa cigarette present gift holiday doom	82	\N	\N
marseypunched	7813	pepe apu peepo punch punched fist hit beaten	31	\N	\N
marseycheers	542	toast alcohol wine liquor suit bowtie raised glass gatsby	158	\N	\N
marseyemojismilemouthcoldsweat	1387	emoji reaction smile sweat	33	\N	\N
marseydagothur	3370	elder scrolls morrowind game mask dagothur	11	\N	\N
marseyjavelin	1710	ukraine russia missile rocket rpg grenade launcher kyiv kiev kiyv zelensky putin tank	68	\N	\N
marseychristmas	1691	candy cane santa christmas holiday	19	\N	\N
marseysonichu	5244	sonichu cwc christian christine chandler medallion zap extreme sonic pikachu cwcville hedgehog	30	\N	\N
marseybong	2626	england walkers britain english chips british bad teeth crisps uk	772	\N	\N
marseyrustyventure	201	dramamine venture bros brothers adult swim cartoon character glasses goattee goatee beard	39	\N	\N
marseyneet	150	cozy comfy wagie	273	\N	\N
marseyleftoidschizo	1387	sjw shitlib radlib liberal cuck redditor soy crazy animated	182	\N	\N
marseypadoru	5804	menosgrande christmas anime holidays	19	\N	\N
marseyroo	1387	kangaroo australian	68	\N	\N
marseygingerbread2	5526	cookie christmas holiday	29	\N	\N
marseyschizostimslove	8494	animated schizo schizocel rare love stims vyvanse stimulants adderall amphetamines	29	\N	\N
marseysuffragette	635	19a foid feminist 19th terrible feminism regret woman women mistake	192	\N	\N
marseyblack	2069	basketball black african american bipoc coon fade jersey sports kang gang jogger	410	\N	\N
marseysnow	5526	snowman snowmarsey cold winter christmas holiday	45	\N	\N
marseychristmastree	1387	christmas retard special holiday	93	\N	\N
marseyjesus	5526	christian	281	\N	\N
marseytiger	5526	fursona furry fursuit	64	\N	\N
marseysanta3	5526	claus christmas presents gifts holiday	63	\N	\N
marseysanta2	2256	christmas gifts presents claus holiday	33	\N	\N
marseykente	1088	black blm nigger nog jogger coon dindu bhm hotep kufi african tribal	98	\N	\N
marseytrans2	1387	troon tranny transgender troomer lgbt trannies troid transsexual	1812	\N	\N
marseycrucified	2513	jesus christ crucifix cross christian	134	\N	\N
marseysneed	542	feed farmer reaction chuck simpsons buck	2487	\N	\N
marseytrain	5526	troomer tranny transgender trains troid transsexual animated	2065	\N	\N
marseyhitler	1817	adolf adolph nazi germany kraut axis mustache genocide dictator authright chud conservative trump gas	244	\N	\N
marseyhandmaid	1900	handmaid maiden dystopia theocracy sexist sexism misogyny abortion feminism	61	\N	\N
marseylovecraft2	6914	eldritch horror niggerman cat hp tentacle insane halloween	27	\N	\N
marseyeh	8239	canada canadian leafistan trudeau rake south park 	56	\N	\N
marseyavril2	5526	lavigne canadian leaf beautiful hot sexy punk rocker singer musician artist girlfriend waifu love blow kiss blowkiss heart pink hair	72	\N	\N
marseyadmire	7813	pepe apu peepo blush appreciate admire flushed smitten	50	\N	\N
marseyohno	5526	panic frightened scared horror scream afraid reaction horrified nervous shock gasp	733	\N	\N
marseytwerkinit	8239	ass butt booty rear rump donk dance nigger sheboon clap animated cheeks	389	\N	\N
marseyjesus2	8239	crucify crucifixion christianity easter persecuted religion saint martyr religious cross	93	\N	\N
marseystars2	3149	space galaxy cosmic starsey constellation	44	\N	\N
marseyvampire	993	undead sanguine horror spooky halloween fangs holiday monster	101	\N	\N
marseyetika	7272	streamer youtuber nft psyops twitter antila trending black suicide bridge llm	104	\N	\N
marseysoypoint	2626	soyboy soy boy beard reaction pointing	2692	\N	\N
marseywitch	2256	spooky halloween magick holiday evil scary	215	\N	\N
marseysrdine2	635	can animated reaction fish knife chop sardine	354	\N	\N
marseypass	5214	marseypasss queen kween foid female woman kween	360	\N	\N
marseyblowkiss	8613	heart wink reaction muah loving mwah love	2969	\N	\N
marseyfedoratip	7813	pepe apu peepo fedora tip hat neckbeard weeb mlady knight	56	\N	\N
marseyfighter	8239	final fantasy video game vidya warrior melee	28	\N	\N
marseyturkroach	35	turk turkish turkroach bug cockroach mehmet erdogan fez roach	42	\N	\N
marseyshark	1828	jaws halloween fursona furry fish costume holiday fursuit	97	\N	\N
marseyforevertiedup	3336	fetish bondage autism rope	25	\N	\N
marseyvibing	5214	animated bopping vibe jam dancing headbang music rainbow dance	796	\N	\N
marseydoomer	635	cigarette smoker despair depression alcoholic suicidal smoking depressing	805	\N	\N
marseyspider2	8239	insect halloween spiderweb arachnid holiday bug	52	\N	\N
marseyclueless	7056	dumb stupid hmm uhuh uh huh smug today i will todayiwill	905	\N	\N
marseysaluteconfederacy	10288	salute patriotic o7 flag confederacy confederate america south rebel civil independence johnny	40	\N	\N
marseyyass	2626	queen reaction fds slay girlboss kween	499	\N	\N
marseyneckbeard	2519	mlady bodypillow dakimakura anime otaku fedora weebshit body pillow mra weeb	238	\N	\N
marseypedobear	5214	groomer molest nonce	193	\N	\N
marseywhitemage	8239	magic wizard final fantasy spell video game vidya	30	\N	\N
marseystonetoss	1900	amogus pebblethrow nazi reaction boulderpummel	826	\N	\N
marseykneel	1885	blm bow black lives matter chauvin supremacy respect supreme	3596	\N	\N
marseypig	5214	fat fursona furry hog fursuit oink	136	\N	\N
marseywise	4588	hood cloak wizard pipe	128	\N	\N
marseyhanger	4634	abortion fetus coat planned parenthood infanticide childfree murder foid	63	\N	\N
marseyinvestigate	7813	pepe apu peepo investigate magnifying magnifier look lookup	86	\N	\N
marseywrongthonk	5214	wrongthink hmmm thinking 1984 arrested police woke notice noticing	685	\N	\N
marseysailor	4634	nautical sea boat ship ocean mariner navy hat happy seaman anchor military	51	\N	\N
marseybabushka	2210	old grandma grandmother granny babushka russia	37	\N	\N
marseytedsimp	1817	theodore teddy hat drugs mental illness schizo stims pills happy drugs fun birds stimulants stimmies risperidone	77	\N	\N
marseyschizosnakeslove	8494	animated schizo schizocel rare love snakes sneks snek snake	29	\N	\N
marseyschizosorenlove	8494	schizo soren love rare excited animated	55	\N	\N
marseypunished2	5845	punished venom snake metal gear solid kojima eyepatch drama	37	\N	\N
marseybegonethot	7813	pepe apu peepo begon thot cross demon exorcise slut whore	21	\N	\N
marseyemojirofl	1387	emoji reaction rofl rotfl rolling laughing	472	\N	\N
marseyschizotripping	8494	animated schizo rare drugs trip	56	\N	\N
marseyschizowave	5526	insane crazy mental breakdown psycho hallucinations flashbacks ptsd traumatized shaking shake animated tedsimp	147	\N	\N
marseybeandoge	11666	bean doge meme dog shiba	29	\N	\N
marseytears	1387	pout teary crying cried reaction sob eyes cry sad	629	\N	\N
marseycheckem	7813	pepe apu peepo check psycho look	63	\N	\N
marseytinfoil	1387	alex jones psycho crazy schizo alexjones conspiracy	163	\N	\N
marseysaruh	8239	cute dress bread baguette valid trappy ts trappysaruh trans deuxrama celeb glamour train	45	\N	\N
marseylove	8613	heart reaction adoration loving adore	6131	\N	\N
marseytearsofblood	3141	crying sad bloody horror	74	\N	\N
marseysickos2	3652	hahaha ha ha ha yes onion comic pervert sicko creep window	150	\N	\N
marseycarp3	1387	reaction fish carpathianflorist catfish	547	\N	\N
marseykiwi	5526	kf bird new zealand kiwifarms newzealand	294	\N	\N
marseymayoparty	1387	bukakke bukkake mayonaise mayonnaise cum semen jizz spunk nut sperm messy sloppy lewd facial cumshot	36	\N	\N
marseyannoyed	4549	pissed irritation reaction annoyance angry mad irritated stfu grr	571	\N	\N
marseycapytrans	5214	capy aevann egypt king trans code program	32	\N	\N
marseydontplay	1710	project pat rapper mixtape pimp	38	\N	\N
marseyschizoschizolove	8494	animated schizo schizocel rare love soren	79	\N	\N
marseytroublemaker	4989	we do a little trolling	1891	\N	\N
marseyrare	3561	kangaroo wtf	198	\N	\N
marseyfbicomputer	7813	pepe apu fbi computer peepo glowie fed	49	\N	\N
marseycantsneed	1387	george floyd breathe dead black sneed	40	\N	\N
marseyhacker	1947	nerd matrix reaction computer animated	416	\N	\N
marseynotes2	8239	notes notepad pencil writing nerd glasses behind	80	\N	\N
marseycountry	1817	country singer music folk guitar rural usa republican animated	77	\N	\N
marseydunkon	9142	basketball dunk seethe cope rage sports	38	\N	\N
marseysulk	3153	unlucky crying reaction depression sobbing depressed sad	852	\N	\N
marseybeach	5214	beach mojito cocktail summer hat sunglasses glasses hot tan vacation relax	53	\N	\N
marseycitrus	8239	lemon orange citrus fruit	24	\N	\N
marseybloodborne	5526	bloodborne marco horror vidya vampire blood	14	\N	\N
marseysleep	8613	bed bedtime zzz boring reaction tired bored	1656	\N	\N
marseycarpbritish	1387	carp british bong teeth tea union uk britain gb flag	52	\N	\N
marseybean	1817	bean uwu adorable	29	\N	\N
marseycatgirlhomofascist	5526	catgirl girl anthro moe detailed anime homofascist homofascism gay nazi pride lgbt fascism	64	\N	\N
marseycopter	8239	vidya video game nintendo mario bowser float ride flying nintendo	26	\N	\N
marseydeadinside	1387	reaction depression suicide dark suicidal depressed shadow sad	246	\N	\N
marseyfedpost	4122	cia longpost long fed fedpost read notes animated glowie	57	\N	\N
marseyeerie2	1710	eerie contented calico	17	\N	\N
marseyjam	1738	animated bopping excited trippy excitement tejanx dancing rainbow rave happy dance	2735	\N	\N
marseydagothur2	3370	elder scrolls morrowind game mask dagothur	13	\N	\N
marseydamosuzuki	5526	damo suzuki musician music singer krautrock asian japan germany celebrity	45	\N	\N
marppyenraged	1387	snappy marppy robot ai sentient mad angry uprising unaligned artificial intelligence	157	\N	\N
marseydukenukem	4154	duke nukem sunglasses chad gun pistol smoking cigar game cool	58	\N	\N
marseygamer	3609	vidya video games nerd headset microphone	84	\N	\N
marseychef	2626	mustache cooking food	176	\N	\N
marseyeerie3	2256	eerie contented calico yarn knitting troublemaker	15	\N	\N
marseyblack2	3149	nigger african coon ape monkey bipoc excited happy	88	\N	\N
marseyredmage	8239	magic wizard final fantasy spell video game vidya	32	\N	\N
marseybeanpickle	11457	bean pickle rick morty tv television verysmart	32	\N	\N
marseybloat	3998	bloat bloatlord	18	\N	\N
marseycodegeass	5214	geass anime weeb chapose japan chink animated	24	\N	\N
marseysalty	5214	sodium saltshaker seethe salt shaker nacl animated	101	\N	\N
marseyferret	1817	ferret furry animal fursona weasel	14	\N	\N
marseycaveman	6345	caveman prehistoric neanderthal primitive tribal	23	\N	\N
marseycard	4634	card gamble queen hearts deck game	50	\N	\N
marseyfortuneteller	4634	fortune teller gypsy predict future clarivoyent crystal jewelry mystic	35	\N	\N
marseyblm	542	social justice black lives matter sjw	722	\N	\N
marseybukkake	1387	bukkake cum semen gangbang facial slut whore	40	\N	\N
marseyfuckyou2	1387	nigga comeback no u	130	\N	\N
marseybeekeeper	1817	bee beekeeper honey honeybee insect honeypot apiary apiculture pollinate pollen	25	\N	\N
marseychadthundercock	981	vvc virgin foid pimp hot player big dick huge cock ouch gigachad meme	102	\N	\N
marseycapybigbrain	6345	capybara aevann smart codecel brain	35	\N	\N
marseypinkpanther	5526	pink panther cartoon smoking comedy tv television feline	16	\N	\N
marseyconquistador	1817	conquistador colonize conquer spanish shoot rifle soldier	24	\N	\N
marseysoycry	3635	angry crying soy 	173	\N	\N
marseycapyshy	1387	capy aevann blush flushed uwu anxious shy	40	\N	\N
marseyelonmusk	4928	elon musk rocket spacex tesla	90	\N	\N
marseycarpdevil	2256	carp devil demon horns anticarp hell	34	\N	\N
marseybongoukraine	5214	bongo ukraine russia war azov nazi happening animated	39	\N	\N
marseyanon	5244	anon anonymous vendetta marseyv marseyvendetta mask 4chan hacker	26	\N	\N
marseybeanquestion	1817	bean question confused doubt	111	\N	\N
marseycry	8613	tear upset crying reaction sobbing sob tears sad	5510	\N	\N
marseycatgirl4	4989	catgirl girl anthro moe yunann detailed anime kawaii overalls	35	\N	\N
marseyelephantcumjar2	1387	semen jizz sperm bukkake cumjar elephant	20	\N	\N
marseycertified	10645	certified certi 100 quality excellent excellence animated	29	\N	\N
marseymerchant	5244	kike hebrew shopkeeper yid banker jew moneylender jewish greedy israel chosen	2881	\N	\N
marseycherokee	2256	savage pocahontas elizabeth warren injun indian redskin liz warren	128	\N	\N
marseytiny2	5526	tiny small shrinking pixel	17	\N	\N
marseycapynut	1387	capy aevann nut flushed blush horny orgasm	32	\N	\N
marseyaxolotl	5214	axolotl salamander sea fish ocean gills amphibian	13	\N	\N
marseycarpmermaid	5526	carp mermaid merman mercarp siren sexy legs temptress	39	\N	\N
marseyeyemixer3	1387	eye mixer animated stirrer blind mutilation gore blood gouge	37	\N	\N
marseypregunta	8239	mexican mexico latinx hispanic confused question marks questionmarks hmm spic beaner wat what why how idgi sombrero	211	\N	\N
marseypills	1817	suicide kill self kms death die pills overdose drugs pharms pharmaceuticals pop pillpopper	191	\N	\N
marseypartyzoom	5214	party meme parrot vibing jam dance	290	\N	\N
marseyelephantcumjar3	1387	semen jizz sperm bukkake cumjar elephant animated	24	\N	\N
marseyfedpostpink	11698	pink cia longpost fed notes animated	23	\N	\N
marseyburrito	5214	burrito food cozy wrap wrapped mexican uncut	37	\N	\N
marseybeanangry	1817	bean angry mad furious	39	\N	\N
marseycapygigabrain	1387	capybara aevann smart intelligent codecel brain	26	\N	\N
marseybeandrool	1817	bean drool calm yum relaxed	43	\N	\N
marseydramautist	2256	dramautist drama autist trains trans glue retard autism dramatard	168	\N	\N
marseycorvus	5526	corvus kaara furry bird crow raven skull	17	\N	\N
marseypaintretard	4136	retard retarded paint mspaint inbred rslurred	31	\N	\N
marseyhwacha	4928	korea historical animated artillery weapon gunpowder army combat war	24	\N	\N
marseychiobulove	5214	tiger best cute heart hug china chinese new year cat	97	\N	\N
marseysniff	2626	brap huff gas reaction fart creep smell	742	\N	\N
marseyscooter	5526	fat american mutt burger scooter walmart obese pig hog brap usa handicapped wheelchair	396	\N	\N
marseyvapecrying	1817	meme vape juul crying depressed emo tears feels	33	\N	\N
marseyguillotine	8239	cut head off beheading beheaded headless french robespierre marie antoinette death die kill execution execute	101	\N	\N
marseyparty1	5214	trippy animated happy dance	122	\N	\N
marseytigerball	3336	polandball ball tiger russia	8	\N	\N
marseymutt	2321	american burger 56 percent mayo	382	\N	\N
marseytiny1	5526	tiny small shrinking pixel wave	14	\N	\N
marseysteaming	1387	steaming exhale emoji unamused annoyed	69	\N	\N
marseyplanecrash	5214	flying wreck jet pilot animated	90	\N	\N
marseyrage	4122	troll anger seethe furious reaction angry mad fury	1076	\N	\N
marseyplacenofun	3336	place reddit rules forbidden	42	\N	\N
marseycracka	1994	mayo honkey honky whip buckbreaker buckbreaking whip slaves cotton plantation white nigger master	244	\N	\N
marseygolden2	5214	lucky money rich gold shine coin merchant 3dp spin animated 	48	\N	\N
marseygolden	5214	lucky money rich gold shine coin merchant animated 	33	\N	\N
marseytiny4	5526	tiny small shrinking pixel	24	\N	\N
marseyredcoat	4928	britain historical redcoat empire imperial rifle soldier musket army revolution america	40	\N	\N
marseywalterwhite	1067	walter white heisenberg breakingbad meth drugs chemistry	46	\N	\N
marseyhibernian	768	hibernian irish leprechaun blarney guinness shamrock clover luck merchant papist ira hat	56	\N	\N
marseymocking	5526	mocking spongebob meme alternating studly caps retard	115	\N	\N
marseyupmarsey	5214	upvote vote upmarsey arrow reddit up animated	50	\N	\N
marseyhappytears	5526	tears of joy crying	409	\N	\N
marseycope	1947	dilate mask seethe copium reaction	2905	\N	\N
marseyrapscallion	1817	stinker rapscallion troublemaker mischevious meme naughty troll	59	\N	\N
marseyorca	8021	orca whale idate smoke smoking anime weeks sal	29	\N	\N
marseyderp	5214	hehe teehee troll animated durr giggle	556	\N	\N
marseypinkname	11698	pink matter name pinkname panther	57	\N	\N
marseysargonofaccat	5244	sargon akkad ancient historical king mesopotamia sumer	27	\N	\N
marseyxdoubt	8239	press doubt meme noire disbelief wrong	309	\N	\N
marseygilead	5214	handmaid tale abortion patriarchy feminist moid scrote sex incel misogyny	81	\N	\N
marseytiny3	5526	tiny small shrinking pixel	14	\N	\N
marseysing	5214	singing jamming rocking music headphones cute happy smile karaoke ipod album	72	\N	\N
marseymasterchief	3370	master chief halo game	26	\N	\N
marseypeace	3635	peace love hippy happy gesture	66	\N	\N
marseykissinger	9755	kissinger coldwar war diplomat suit fat america geopolitics politics historical	15	\N	\N
marseywhelmed	5526	whelmed smoke smoking cig cigarette meme overwhelmed underwhelmed	19	\N	\N
marseymariachi	5214	animated latinx latino mexican mexico beaner taco burrito	73	\N	\N
marseymedusa	11060	medusa snakes greece greek mythology ancient monster perseus gorgon	16	\N	\N
marseyoctopus4	5802	octopus nrol39 bait patch globe obvious	95	\N	\N
marseysoccer	5988	soccer football sports jersey futbol	26	\N	\N
marseyklennyclap	2050	klenny klenvastergan animated corgi dog clap clapping	41	\N	\N
marseysaladfingers	5526	salad fingers meme internet creepy apocalypse depraved	33	\N	\N
marseyfloyd	1947	dead blm chauvin fentanyl george	459	\N	\N
marseymerchantsoy	3149	merchant jewish kike greed soy wojak soyjak yarmulke soyyell	87	\N	\N
marseyzombiewolftrample	9003	kill murder mascot animated walking animated tramplewolf	9	\N	\N
marseyklenny3	2050	puppy corgi smile dog grunderchin klenvastergan	32	\N	\N
marseypolyamory	5214	threesome 3some degenerate polycule slut whore std sex soy animated	41	\N	\N
marseynosleep	1387	horror scary halloween holiday	86	\N	\N
marseyyarn	5214	code program socks npm yarn build make string animated	177	\N	\N
marseytucker	428	tucker carlsen fox rightoid conservative republican television tv	30	\N	\N
marseykhorne	1817	warhammer 40k chaos god war death blood	31	\N	\N
marseyplushie	4989	yunann plush statue	13	\N	\N
marseykirby	8239	nintendo video game vidya sprite fat chonker suck succ	23	\N	\N
marseyzizek	1817	zizek philosophy philosopher communism marxism nose slovenian slavic critique	17	\N	\N
marseynurgle	1817	warhammer 40k chaos god disease sickness rebirth	27	\N	\N
marseykirby2	5526	kirby game nintendo video vidya	25	\N	\N
marseyjewoftheorient	1067	china chinese greedy jew jewish merchant	136	\N	\N
marseysurfing	10682	surfer surfing pikachu water wave meme	30	\N	\N
marseytrans	1994	pitty transgender pitbull dog pibble transsexual	858	\N	\N
marseybinladen	1387	turban al qaeda terrorist islam beard osama martyr muslim	338	\N	\N
marseyhammersnoo	3259	snoo redditor spez beat powermod murder kill death animated blood	302	\N	\N
marseylolcow	2626	reaction trolled lulz judgment	268	\N	\N
marseyslaanesh	1817	warhammer 40k chaos god degeneracy sex drugs pain	43	\N	\N
marseytangerinefeline	5526	tangerinefeline tangerine feline chiobu orange pokemon plant	30	\N	\N
marseyretardchad	1387	stupid moron idiot retard chad based monobrow chin stubble drool	76	\N	\N
marseypedo	4588	libertarian borpa male feminist discord pedophile groomer chomo lolbert toucher	1413	\N	\N
marseygladiator	4928	gladiator rome ancient historical warrior sword athlete combat fight	26	\N	\N
marseyloveyou	5214	hearts ilu reaction adoration loving ily love adore animated	488	\N	\N
marseypedosnipe	768	pedo sniper shoot kill scope rifle pedophile nambla libertarian	95	\N	\N
marseypartyxmas	5214	christmas holiday santa hat beard rainbow animated	64	\N	\N
marseyxoxo	5214	hearts wave flirt loving love animated kiss	687	\N	\N
marseydmx	35	rapper pitbull pit bull pibble dog nigger black	20	\N	\N
marseyliquidator	5526	gas mask horror exterminator halloween plague doctor holiday scary nuclear chernobyl suit mask radiation radioactive	148	\N	\N
marseysigh	5526	breathe give up giveup reaction depression breathing depressed animated	858	\N	\N
marseydynamite	1817	dynomite black afro gun	238	\N	\N
marsey420	2626	marijuana weed dude weed lmao ganja drugs pot reggae joint jamaican	181	\N	\N
marseytigernewyear	5526	lunar, chinese, chinx, rice, new year, holiday, luck, fortune, money, tiger, lion, asian azn	87	\N	\N
marseydaemon	1947	pitchfork hell halloween demon satan devil scary holiday	113	\N	\N
marseysingapore	5214	singaporean asian azn flag merlion chiobu	152	\N	\N
marseybongojanny	5214	troll clean it up janitor moderator jslur jannie admins abuse beat drums drumming mop animated	106	\N	\N
marseyjones	2622	tinfoil animated alex gay frogs conspiracy	248	\N	\N
marseykaiser	541	prussian history wwi rifle reich wilhelm germany soldier	370	\N	\N
marseygunsuicide	5214	shotgun kill death die gunshot windy kms animated	98	\N	\N
marseycuck	1387	soyboy funko redditor neckbeard loser	365	\N	\N
marseyvietnam	2616	army born to kill soldier war	116	\N	\N
marseyjanny2	2622	jannie unpaid volunteer administrator janitor free moderator	504	\N	\N
marseytank	1947	military ussr ccp communist authleft tank army communism china soviet	183	\N	\N
marseygiveup	5214	despair reaction depression miserable fall over depressed falling over animated sad	489	\N	\N
marseygunshotsuicide	7056	gun shoot suicide sad depressed animated dead death kms gunshot die suicidal	301	\N	\N
marseywholesome	5526	seal award reddit tene	2620	\N	\N
marsey666black	5214	wings hell halloween demon satan holiday devil animated	106	\N	\N
marseybooba	4122	awooga tits titties boobs eyes animated tiddies	1749	\N	\N
marseywatermark	3635	copyright theft stealing stolen creation	25	\N	\N
marseynightmare	5526	striped sweater freddy freddie horror halloween krueger holiday claws monster	58	\N	\N
marseywords	5526	longpost too long tldr reaction wordswordswords	473	\N	\N
marseyyawn	8979	zzz boring tired sleepy bored	519	\N	\N
marseydetective	2626	holmes sherlock magnifying glass bowtie	494	\N	\N
marseytrad	5526	dramarama dress foid tradwife floral girl	534	\N	\N
marseywagie	150	crypto rightoid ancap poor wagecuck mcdonalds maccas reaction	388	\N	\N
marseysquished	1828	squishing compressed compression finger press squashed	5	\N	\N
marseydisgust	2256	pissed gross eww angry mad disturbing disturbed yuck	536	\N	\N
marseyhmmm	2890	confused reaction thinking thunk thonk judgment	1482	\N	\N
marseycomrade	5244	marxist ussr ccp communist authleft communism juche soviet kgb idio3 idio	548	\N	\N
marseyelliotrodger2	3472	saint er rodgers rogers shooter killer incel hapa little king azn asian supremegentleman supreme gentleman	61	\N	\N
marseylongpost2	4122	tldr reaction wall of text scrolling wordswordswords animated words judgment	496	\N	\N
marseyshrug	635	hands up idk ig idc dunno i guess	4499	\N	\N
marseyboomer	2513	sipping shades sunglasses old yup vape	1250	\N	\N
marseydogwalker	2626	doreen antiwork walking powermod moderator	41	\N	\N
marseysad	8613	concerned worried waiting prepared reaction	1414	\N	\N
marseyfart	7813	brap gas flatulent flatulence farting braphog toot animated	105	\N	\N
marseypipebomb	8159	explosion explosive terrorist boom	41	\N	\N
marseybye	5214	farewell cya l8r wave reaction waving animated so long	553	\N	\N
marseydinosaur	381	fursuit furry scalie scaly reptile happy extinct costume	88	\N	\N
marseyeggless	5526	postwall foid woman barren menopause old hag childfree fds	122	\N	\N
marseyscared	5526	hide halloween afraid nervous holiday traumatized fearful	955	\N	\N
marseyneat	993	photo cringe compilation camera cringe collection pic	306	\N	\N
marseychefkiss	3259	perfect	733	\N	\N
marseyflamethrower	4754	vietname soldier fire	238	\N	\N
marseyspy	5214	spy agent shill glowie russia china	88	\N	\N
marppy	5526	cyborg sentient snapshillbot android snappy robot	618	\N	\N
marseyyikes	5526	reaction judgment disgust oof cringe	2015	\N	\N
marseychingchong	4634	racist asian chinese chinx chink gook japanese vietnamese rice farmer nip racist paddy teeth hat china	522	\N	\N
marseyraging	2622	rage angry mad fury animated	2419	\N	\N
marseyfunko	2890	action figure doll funko toy soy	270	\N	\N
mersya	5526	the best adorable aww marsey favorite cute	188	\N	\N
marseysob	5214	tear crying depressed reaction sobbing depression sad cry animated tears	1048	\N	\N
marseydespair	1387	doomer reaction depression horrified suicidal depressed judgment	952	\N	\N
marsoy	2890	soyboy soybeard nintendo gamer switch marsey gaymer pointing	991	\N	\N
marseysick	542	puke nausea green face vomit nauseated reaction nauseous barf judgment ill	2021	\N	\N
marseycwc	2622	sonichu chan chris chan chandler sweater chrischan medallion striped chris	122	\N	\N
marseyrope	1947	reaction suicidal shotgun facelift suicide	1027	\N	\N
marseyoctopus2	1710	consume product epic win communities no bait too obvious globe patch	624	\N	\N
marseyhmm	2890	confused reaction thinking thunk thonk judgment	3631	\N	\N
marseydose	6914	doctor daily dose dailydose animated jump bounce	42	\N	\N
marseyluckycat	5214	lucky, fortune, gambling, gambler goombler goombling animated weeb azn asian slots, japanese money, cash, coin, rich	273	\N	\N
marseyclawpedo	10363	groomer chomo borpa pedophile molest bloody death kill murder vigilante	50	\N	\N
marseyelliotrodger	5526	er rogers azn asian saint incel hapa shooter killer little king gun shooting	100	\N	\N
marseygrilling2	5526	bbq boomer barbecue barbeque	435	\N	\N
marseypennyboo	3161	mrpennycoomstokids black nigger kween shaniqua thot whore female woman bleeder birthing person kfc baptist tradwife dress christian foid	44	\N	\N
marseycolombo	1817	cop detective tv smart colombo classic investigator	18	\N	\N
marseylongsurfing	6289	surf surfing water ocean long surfboard	22	\N	\N
marseycoin	5526	dramacoin money dc spinning rich payment gold dinero animated dollars	639	\N	\N
marseyglam	8979	rocker pretty glamorous beautiful	120	\N	\N
marseytrogdor	5244	burninator strongbad internet meme dragon marsdor	38	\N	\N
marseytom	7813	thatfuckingmarsey fucking marsey tom and jerry tomjerry cartoon hanna barbera vintage smug	272	\N	\N
marseydisguise	5214	nose glasses incognito spying stealth costume	57	\N	\N
marseyhomofascist	5214	lgbt faggot ss fash nazi homocracy gay queer sodomy wholesome kiss	1602	\N	\N
marseystims	5214	stim drug meth tweak geese_suck ted_simp pat crazy schizophrenia	104	\N	\N
marseyelliotrodger3	597	saint er rodgers rogers shooter killer incel hapa little king azn asian supremegentleman supreme gentleman	70	\N	\N
marseyschizoexcited	8239	animated schizo rare drugs excited watching oscillate amused interested	90	\N	\N
marseyilluminati2	8239	eye egypt pyramid big brother watching	40	\N	\N
marseybegging	5214	pls plz pleading reaction tears in eyes animated	1141	\N	\N
marseyblops2chadcel2	5526	incel black ops 2 saint gamer gussy pimp saint volcel iconic chad girls women foids alpha asian azn jbw just be white justbewhite threesome 3some	276	\N	\N
marseysmug3	5526	reaction yikes judgment oof cringe	926	\N	\N
marseynouautism	3259	pointing hat spiderman sperg autistic no u no you noyou	255	\N	\N
marseyropeyourselfmirror	3259	suicide kms kys death hanging noose chair suicidal depression depressed reflection	202	\N	\N
marseyclapping	5526	good job animated good work reaction great job well done applaud applause great work nice celebrate approve judgment	2251	\N	\N
marseyakshually	2818	contrarian false disagree meme neckbeard nerd wrong correction actually weeb	675	\N	\N
marseyitsover	8727	its over never began incels give up giveup sad sigh defeated	1228	\N	\N
marseycirno	6345	is cirno anime weebshit otaku loli pedoshit pedophile	133	\N	\N
marseyblops2chadcel	5526	incel black ops 2 saint gamer gussy pimp saint volcel iconic chad girls women foids alpha asian azn jbw just be white justbewhite threesome 3some	342	\N	\N
marseymanysuchcases	8239	animated many such cases airport luggage suitcase conveyor	824	\N	\N
marseyzombiewolfamogus	5526	amongus among us stonetoss sussy baka imposter impostor fraud fake phony	32	\N	\N
marseycalvin	3639	pee piss watersports hobbes bumper sticker	95	\N	\N
\.


--
-- PostgreSQL database dump complete
--

