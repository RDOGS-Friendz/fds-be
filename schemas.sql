-- public.account definition

-- Drop table

-- DROP TABLE public.account;

CREATE TABLE public.account (
	id serial4 NOT NULL,
	username varchar NOT NULL,
	pass_hash varchar NOT NULL,
	real_name varchar NOT NULL,
	email varchar NOT NULL,
	gender gender_type NOT NULL,
	is_real_name_private bool NOT NULL DEFAULT false,
	is_superuser bool NOT NULL DEFAULT false,
	is_deleted bool NOT NULL DEFAULT false,
	is_verified bool NOT NULL DEFAULT false,
	CONSTRAINT account_pkey PRIMARY KEY (id),
	CONSTRAINT account_username_key UNIQUE (username)
);


-- public.category definition

-- Drop table

-- DROP TABLE public.category;

CREATE TABLE public.category (
	id serial4 NOT NULL,
	"name" varchar NOT NULL,
	CONSTRAINT category_name_key UNIQUE (name),
	CONSTRAINT category_pkey PRIMARY KEY (id)
);


-- public.department definition

-- Drop table

-- DROP TABLE public.department;

CREATE TABLE public.department (
	id serial4 NOT NULL,
	school varchar NOT NULL,
	department_name varchar NOT NULL,
	CONSTRAINT department_pkey PRIMARY KEY (id),
	CONSTRAINT department_school_department_name_key UNIQUE (school, department_name)
);


-- public."location" definition

-- Drop table

-- DROP TABLE public."location";

CREATE TABLE public."location" (
	id serial4 NOT NULL,
	"name" varchar NOT NULL,
	"type" location_type NULL DEFAULT 'NONE'::location_type,
	lat float8 NULL,
	lng float8 NULL,
	CONSTRAINT location_pkey PRIMARY KEY (id)
);

-- public.email_verification definition

-- Drop table

-- DROP TABLE public.email_verification;

CREATE TABLE public.email_verification (
	id serial4 NOT NULL,
	code uuid NOT NULL DEFAULT gen_random_uuid(),
	email varchar NOT NULL,
	account_id int4 NOT NULL,
	is_consumed bool NOT NULL DEFAULT false,
	CONSTRAINT email_verification_pkey PRIMARY KEY (id),
	CONSTRAINT email_verification_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id)
);


-- public."event" definition

-- Drop table

-- DROP TABLE public."event";

CREATE TABLE public."event" (
	id serial4 NOT NULL,
	title varchar NOT NULL,
	is_private bool NOT NULL DEFAULT false,
	location_id int4 NULL,
	category_id int4 NULL,
	intensity intensity_type NULL DEFAULT 'INTERMEDIATE'::intensity_type,
	create_time timestamp NOT NULL,
	start_time timestamp NOT NULL,
	end_time timestamp NOT NULL,
	max_participant_count int4 NULL,
	creator_account_id int4 NULL,
	description varchar NULL,
	CONSTRAINT event_pkey PRIMARY KEY (id),
	CONSTRAINT positive_max_participants CHECK ((max_participant_count >= 0)),
	CONSTRAINT event_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.category(id),
	CONSTRAINT event_creator_account_id_fkey FOREIGN KEY (creator_account_id) REFERENCES public.account(id),
	CONSTRAINT event_location_id_fkey FOREIGN KEY (location_id) REFERENCES public."location"(id)
);


-- public.event_account_reaction definition

-- Drop table

-- DROP TABLE public.event_account_reaction;

CREATE TABLE public.event_account_reaction (
	id serial4 NOT NULL,
	event_id int4 NOT NULL,
	"content" varchar NOT NULL,
	author_id int4 NOT NULL,
	CONSTRAINT event_account_reaction_pkey PRIMARY KEY (id),
	CONSTRAINT event_account_reaction_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.account(id),
	CONSTRAINT event_account_reaction_event_id_fkey FOREIGN KEY (event_id) REFERENCES public."event"(id)
);


-- public.event_bookmark definition

-- Drop table

-- DROP TABLE public.event_bookmark;

CREATE TABLE public.event_bookmark (
	id serial4 NOT NULL,
	account_id int4 NOT NULL,
	event_id int4 NOT NULL,
	CONSTRAINT event_bookmark_event_id_account_id_key UNIQUE (event_id, account_id),
	CONSTRAINT event_bookmark_pkey PRIMARY KEY (id),
	CONSTRAINT event_bookmark_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id),
	CONSTRAINT event_bookmark_event_id_fkey FOREIGN KEY (event_id) REFERENCES public."event"(id)
);


-- public.event_participant definition

-- Drop table

-- DROP TABLE public.event_participant;

CREATE TABLE public.event_participant (
	account_id int4 NOT NULL,
	event_id int4 NOT NULL,
	CONSTRAINT event_participant_pkey PRIMARY KEY (account_id, event_id),
	CONSTRAINT event_participant_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id),
	CONSTRAINT event_participant_event_id_fkey FOREIGN KEY (event_id) REFERENCES public."event"(id)
);


-- public.friendship definition

-- Drop table

-- DROP TABLE public.friendship;

CREATE TABLE public.friendship (
	requester_id int4 NOT NULL,
	addressee_id int4 NOT NULL,
	status friendship_type NOT NULL DEFAULT 'PENDING'::friendship_type,
	CONSTRAINT friendship_pkey PRIMARY KEY (requester_id, addressee_id),
	CONSTRAINT friendship_addressee_id_fkey FOREIGN KEY (addressee_id) REFERENCES public.account(id),
	CONSTRAINT friendship_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.account(id)
);


-- public.profile definition

-- Drop table

-- DROP TABLE public.profile;

CREATE TABLE public.profile (
	id serial4 NOT NULL,
	account_id int4 NULL,
	is_birthday_private bool DEFAULT false,
	tagline varchar NULL,
	department_id int4 NULL,
	social_media_link varchar NULL,
	birthday timestamp NULL,
	about varchar NULL,
	CONSTRAINT profile_account_id_key UNIQUE (account_id),
	CONSTRAINT profile_pkey PRIMARY KEY (id),
	CONSTRAINT profile_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id),
	CONSTRAINT profile_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id)
);


-- public.profile_category definition

-- Drop table

-- DROP TABLE public.profile_category;

CREATE TABLE public.account_category (
	account_id int4 NOT NULL,
	category_id int4 NOT NULL,
	CONSTRAINT profile_category_pkey PRIMARY KEY (account_id, category_id),
	CONSTRAINT profile_category_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.account(id),
	CONSTRAINT profile_category_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.category(id)
);


-- functions

CREATE OR REPLACE FUNCTION get_account_friend(account_id INTEGER)
 RETURNS INTEGER[]
 LANGUAGE plpgsql
AS $function$
   DECLARE
     friend_ids INTEGER[];
   BEGIN
     SELECT ARRAY_AGG(friend_id) FROM
     ( SELECT DISTINCT UNNEST(ARRAY[requester_id, addressee_id]) AS friend_id
     		INTO friend_ids
	     	FROM friendship
     		WHERE (status='ACCEPTED')
      		AND (requester_id = account_id OR addressee_id = account_id) ) AS t;
      RETURN friend_ids;
   END;
  $function$
;


CREATE OR REPLACE FUNCTION public.event_joined_by_friend(viewer_id INTEGER)
 RETURNS INTEGER[]
 LANGUAGE plpgsql
AS $function$
   DECLARE
     event_ids INTEGER[];
   BEGIN
     SELECT distinct array_agg(event_id) FROM event_participant
     INTO event_ids
		     WHERE account_id IN (
		           SELECT * FROM (SELECT DISTINCT UNNEST(ARRAY[requester_id, addressee_id]) AS friend_id
			     	FROM friendship
		     		WHERE (status='ACCEPTED')
		      		AND (requester_id = viewer_id OR addressee_id = viewer_id) ) AS t
		      		WHERE friend_id != viewer_id);
      RETURN event_ids;
   END;
  $function$
;


-- view for event

-- public.view_event source

CREATE OR REPLACE VIEW public.view_event
AS SELECT t.id,
    t.title,
    t.is_private,
    t.location_id,
    t.category_id,
    t.intensity,
    t.create_time,
    t.start_time,
    t.end_time,
    t.max_participant_count,
    t.creator_account_id,
    t.description,
    t.duration,
    t.day_time,
    t.participant_id,
    t.start_date
   FROM ( SELECT event.id,
            event.title,
            event.is_private,
            event.location_id,
            event.category_id,
            event.intensity,
            event.create_time,
            event.start_time,
            event.end_time,
            event.max_participant_count,
            event.creator_account_id,
            event.description,
                CASE
                    WHEN (event.end_time - event.start_time) < '00:30:00'::interval THEN 'SHORT'::text
                    WHEN (event.end_time - event.start_time) >= '00:30:00'::interval AND (event.end_time - event.start_time) < '01:30:00'::interval THEN 'MEDIUM'::text
                    ELSE 'LONG'::text
                END AS duration,
                CASE
                    WHEN date_part('hour'::text, event.start_time) >= 5::double precision AND date_part('hour'::text, event.start_time) <= 12::double precision THEN 'MORNING'::text
                    WHEN date_part('hour'::text, event.start_time) >= 12::double precision AND date_part('hour'::text, event.start_time) <= 18::double precision THEN 'AFTERNOON'::text
                    WHEN date_part('hour'::text, event.start_time) >= 18::double precision AND date_part('hour'::text, event.start_time) <= 23::double precision THEN 'EVENING'::text
                    ELSE 'NIGHT'::text
                END AS day_time,
            ( SELECT DISTINCT array_agg(ep.account_id) AS array_agg
                   FROM event e
                     LEFT JOIN event_participant ep ON ep.event_id = e.id
                  WHERE ep.account_id IS NOT NULL AND event.id = ep.event_id) AS participant_id,
            event.start_time::date AS start_date
           FROM event) t;