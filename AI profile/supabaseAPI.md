API keys:
public key:
your-supabase-anon-key-here
secret key:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh0cnhyY2x4aW5wbWJ0aWduam9qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODgyMjcyNCwiZXhwIjoyMDY0Mzk4NzI0fQ.hPyHoFK7Lbx4-SS_zfjGB8Tj1G9fGy03rMWQzfpwNZ0


publishable key:sb_publishable_vgn3lE_BBH7lJPP43jeOIA_1VWP-GBH


1.profile's table:
(1)in javascript
Columns

Name	Format	Type	Description
id	
uuid

string	
name	
text

string	
email	
text

string	
company_id	
uuid

string	
created_at	
timestamp with time zone

string	
updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: profiles, error } = await supabase
  .from('profiles')
  .select('*')
Read specific columns

let { data: profiles, error } = await supabase
  .from('profiles')
  .select('some_column,other_column')
Read referenced tables

let { data: profiles, error } = await supabase
  .from('profiles')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: profiles, error } = await supabase
  .from('profiles')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: profiles, error } = await supabase
  .from('profiles')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('profiles')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('profiles')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('profiles')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('profiles')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('profiles')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'profiles' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'profiles' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'profiles' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'profiles' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'profiles', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

(2)in bash:
Columns

Name	Format	Type	Description
id	
uuid

string	
name	
text

string	
email	
text

string	
company_id	
uuid

string	
created_at	
timestamp with time zone

string	
updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

curl 'https://your-project-id.supabase.co/rest/v1/profiles?select=*' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
Read specific columns

curl 'https://your-project-id.supabase.co/rest/v1/profiles?select=some_column,other_column' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
Read referenced tables

curl 'https://your-project-id.supabase.co/rest/v1/profiles?select=some_column,other_table(foreign_key)' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
With pagination

curl 'https://your-project-id.supabase.co/rest/v1/profiles?select=*' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Range: 0-9"
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

curl --get 'https://your-project-id.supabase.co/rest/v1/profiles' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Range: 0-9" \
-d "select=*" \
\
`# Filters` \
-d "column=eq.Equal+to" \
-d "column=gt.Greater+than" \
-d "column=lt.Less+than" \
-d "column=gte.Greater+than+or+equal+to" \
-d "column=lte.Less+than+or+equal+to" \
-d "column=like.*CaseSensitive*" \
-d "column=ilike.*CaseInsensitive*" \
-d "column=is.null" \
-d "column=in.(Array,Values)" \
-d "column=neq.Not+equal+to" \
\
`# Arrays` \
-d "array_column=cs.{array,contains}" \
-d "array_column=cd.{contained,by}" \
\
`# Logical operators` \
-d "column=not.like.Negate+filter" \
-d "or=(some_column.eq.Some+value,other_column.eq.Other+value)"
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

curl -X POST 'https://your-project-id.supabase.co/rest/v1/profiles' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-H "Prefer: return=minimal" \
-d '{ "some_column": "someValue", "other_column": "otherValue" }'
Insert many rows

curl -X POST 'https://your-project-id.supabase.co/rest/v1/profiles' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-d '[{ "some_column": "someValue" }, { "other_column": "otherValue" }]'
Upsert matching rows

curl -X POST 'https://your-project-id.supabase.co/rest/v1/profiles' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-H "Prefer: resolution=merge-duplicates" \
-d '{ "some_column": "someValue", "other_column": "otherValue" }'
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

curl -X PATCH 'https://your-project-id.supabase.co/rest/v1/profiles?some_column=eq.someValue' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-H "Prefer: return=minimal" \
-d '{ "other_column": "otherValue" }'
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

curl -X DELETE 'https://your-project-id.supabase.co/rest/v1/profiles?some_column=eq.someValue' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

# Realtime streams are only supported by our client libraries
Subscribe to inserts

# Realtime streams are only supported by our client libraries
Subscribe to updates

# Realtime streams are only supported by our client libraries
Subscribe to deletes

# Realtime streams are only supported by our client libraries
Subscribe to specific rows

# Realtime streams are only supported by our client libraries
2.notes's table:
(1)in javascript
Columns

Name	Format	Type	Description
id	
uuid

string	
whiteboard_id	
uuid

string	
content	
text

string	
position_x	
integer

number	
position_y	
integer

number	
width	
integer

number	
height	
integer

number	
color	
text

string	
image_url	
text

string	
views	
integer

number	
created_at	
timestamp with time zone

string	
updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

let { data: notes, error } = await supabase
  .from('notes')
  .select('*')
Read specific columns

let { data: notes, error } = await supabase
  .from('notes')
  .select('some_column,other_column')
Read referenced tables

let { data: notes, error } = await supabase
  .from('notes')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination

let { data: notes, error } = await supabase
  .from('notes')
  .select('*')
  .range(0, 9)
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

let { data: notes, error } = await supabase
  .from('notes')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

const { data, error } = await supabase
  .from('notes')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows

const { data, error } = await supabase
  .from('notes')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows

const { data, error } = await supabase
  .from('notes')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

const { data, error } = await supabase
  .from('notes')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

const { error } = await supabase
  .from('notes')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

const channels = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'notes' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts

const channels = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'notes' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates

const channels = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'notes' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes

const channels = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'notes' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows

const channels = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'notes', filter: 'some_column=eq.some_value' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()


(2)in bash:
Columns

Name	Format	Type	Description
id	
uuid

string	
whiteboard_id	
uuid

string	
content	
text

string	
position_x	
integer

number	
position_y	
integer

number	
width	
integer

number	
height	
integer

number	
color	
text

string	
image_url	
text

string	
views	
integer

number	
created_at	
timestamp with time zone

string	
updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

curl 'https://your-project-id.supabase.co/rest/v1/notes?select=*' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
Read specific columns

curl 'https://your-project-id.supabase.co/rest/v1/notes?select=some_column,other_column' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
Read referenced tables

curl 'https://your-project-id.supabase.co/rest/v1/notes?select=some_column,other_table(foreign_key)' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
With pagination

curl 'https://your-project-id.supabase.co/rest/v1/notes?select=*' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Range: 0-9"
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

curl --get 'https://your-project-id.supabase.co/rest/v1/notes' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Range: 0-9" \
-d "select=*" \
\
`# Filters` \
-d "column=eq.Equal+to" \
-d "column=gt.Greater+than" \
-d "column=lt.Less+than" \
-d "column=gte.Greater+than+or+equal+to" \
-d "column=lte.Less+than+or+equal+to" \
-d "column=like.*CaseSensitive*" \
-d "column=ilike.*CaseInsensitive*" \
-d "column=is.null" \
-d "column=in.(Array,Values)" \
-d "column=neq.Not+equal+to" \
\
`# Arrays` \
-d "array_column=cs.{array,contains}" \
-d "array_column=cd.{contained,by}" \
\
`# Logical operators` \
-d "column=not.like.Negate+filter" \
-d "or=(some_column.eq.Some+value,other_column.eq.Other+value)"
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

curl -X POST 'https://your-project-id.supabase.co/rest/v1/notes' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-H "Prefer: return=minimal" \
-d '{ "some_column": "someValue", "other_column": "otherValue" }'
Insert many rows

curl -X POST 'https://your-project-id.supabase.co/rest/v1/notes' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-d '[{ "some_column": "someValue" }, { "other_column": "otherValue" }]'
Upsert matching rows

curl -X POST 'https://your-project-id.supabase.co/rest/v1/notes' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-H "Prefer: resolution=merge-duplicates" \
-d '{ "some_column": "someValue", "other_column": "otherValue" }'
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

curl -X PATCH 'https://your-project-id.supabase.co/rest/v1/notes?some_column=eq.someValue' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-H "Prefer: return=minimal" \
-d '{ "other_column": "otherValue" }'
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

curl -X DELETE 'https://your-project-id.supabase.co/rest/v1/notes?some_column=eq.someValue' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

# Realtime streams are only supported by our client libraries
Subscribe to inserts

# Realtime streams are only supported by our client libraries
Subscribe to updates

# Realtime streams are only supported by our client libraries
Subscribe to deletes

# Realtime streams are only supported by our client libraries
Subscribe to specific rows

# Realtime streams are only supported by our client libraries

3.business_cards's table


Columns

Name	Format	Type	Description
id	
uuid

string	
user_id	
uuid

string	
what_i_am_doing	
text

string	
people_i_want_to_meet	
text

string	
profession_education	
text

string	
personal_links	
jsonb

json	
created_at	
timestamp with time zone

string	
updated_at	
timestamp with time zone

string	
Read rows
Documentation
To read rows in this table, use the select method.

Read all rows

curl 'https://your-project-id.supabase.co/rest/v1/business_cards?select=*' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
Read specific columns

curl 'https://your-project-id.supabase.co/rest/v1/business_cards?select=some_column,other_column' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
Read referenced tables

curl 'https://your-project-id.supabase.co/rest/v1/business_cards?select=some_column,other_table(foreign_key)' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
With pagination

curl 'https://your-project-id.supabase.co/rest/v1/business_cards?select=*' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Range: 0-9"
Filtering
Documentation
Supabase provides a wide range of filters

With filtering

curl --get 'https://your-project-id.supabase.co/rest/v1/business_cards' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Range: 0-9" \
-d "select=*" \
\
`# Filters` \
-d "column=eq.Equal+to" \
-d "column=gt.Greater+than" \
-d "column=lt.Less+than" \
-d "column=gte.Greater+than+or+equal+to" \
-d "column=lte.Less+than+or+equal+to" \
-d "column=like.*CaseSensitive*" \
-d "column=ilike.*CaseInsensitive*" \
-d "column=is.null" \
-d "column=in.(Array,Values)" \
-d "column=neq.Not+equal+to" \
\
`# Arrays` \
-d "array_column=cs.{array,contains}" \
-d "array_column=cd.{contained,by}" \
\
`# Logical operators` \
-d "column=not.like.Negate+filter" \
-d "or=(some_column.eq.Some+value,other_column.eq.Other+value)"
Insert rows
Documentation
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Insert a row

curl -X POST 'https://your-project-id.supabase.co/rest/v1/business_cards' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-H "Prefer: return=minimal" \
-d '{ "some_column": "someValue", "other_column": "otherValue" }'
Insert many rows

curl -X POST 'https://your-project-id.supabase.co/rest/v1/business_cards' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-d '[{ "some_column": "someValue" }, { "other_column": "otherValue" }]'
Upsert matching rows

curl -X POST 'https://your-project-id.supabase.co/rest/v1/business_cards' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-H "Prefer: resolution=merge-duplicates" \
-d '{ "some_column": "someValue", "other_column": "otherValue" }'
Update rows
Documentation
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Update matching rows

curl -X PATCH 'https://your-project-id.supabase.co/rest/v1/business_cards?some_column=eq.someValue' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY" \
-H "Content-Type: application/json" \
-H "Prefer: return=minimal" \
-d '{ "other_column": "otherValue" }'
Delete rows
Documentation
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Delete matching rows

curl -X DELETE 'https://your-project-id.supabase.co/rest/v1/business_cards?some_column=eq.someValue' \
-H "apikey: SUPABASE_CLIENT_ANON_KEY" \
-H "Authorization: Bearer SUPABASE_CLIENT_ANON_KEY"
Subscribe to changes
Documentation
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Subscribe to all events

# Realtime streams are only supported by our client libraries
Subscribe to inserts

# Realtime streams are only supported by our client libraries
Subscribe to updates

# Realtime streams are only supported by our client libraries
Subscribe to deletes

# Realtime streams are only supported by our client libraries
Subscribe to specific rows

# Realtime streams are only supported by our client libraries