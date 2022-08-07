CREATE TABLE category (
	id serial PRIMARY KEY,
	name character varying(128) NOT NULL,
	sub character varying(20) REFERENCES subs(name),
	color_text char(6),
	color_bg char(6),
	UNIQUE (name, sub)
);

ALTER TABLE submissions ADD COLUMN category_id integer REFERENCES category(id) ON DELETE SET NULL;
