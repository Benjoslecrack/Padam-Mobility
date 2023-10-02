-- DROP TABLE IF EXISTS public.entity;
create table if not exists public.entity
(
    entity_id bigserial,
    created_at timestamp without time zone not null,
    value double precision not null,
    constraint entity_pkey primary key(entity_id)
)

tablespace pg_default
;

alter table if exists public.entity
owner to postgres
;

-- DROP INDEX IF EXISTS public.index_entity_id;
create unique index if not exists index_entity_id on public.entity using btree
(entity_id asc nulls last)
tablespace pg_default
;

-- DROP INDEX IF EXISTS public.index_entity_created_at;
create index if not exists index_entity_created_at on public.entity using btree
(entity_id asc nulls last)
tablespace pg_default
;
