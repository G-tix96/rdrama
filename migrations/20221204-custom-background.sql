alter table users alter column background type varchar(30);
update users set background='/i/backgrounds/' || background || '.webp' where background is not null;
