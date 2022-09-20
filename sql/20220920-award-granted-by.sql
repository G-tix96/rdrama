alter table award_relationships add column granted_by int;
ALTER TABLE ONLY public.award_relationships
    ADD CONSTRAINT award_granted_by_fkey FOREIGN KEY (granted_by) REFERENCES public.users(id);
update award_relationships set granted_by=1 where granted=true;
alter table award_relationships drop column granted;
