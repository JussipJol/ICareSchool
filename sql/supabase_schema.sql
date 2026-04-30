-- Extension for UUID generation
create extension if not exists "uuid-ossp";

-- 1. Regions Table
create table regions (
  id serial primary key,
  name text not null
);

-- 2. Cities Table
create table cities (
  id serial primary key,
  region_id int references regions(id) on delete cascade,
  name text not null
);

-- 3. Schools Table
create table schools (
  id serial primary key,
  city_id int references cities(id) on delete cascade,
  name text not null,
  address text
);

-- 4. Complaints Table
create table complaints (
  id uuid default uuid_generate_v4() primary key,
  short_id text unique not null, -- e.g., ADGS-8291
  region_id int references regions(id),
  city_id int references cities(id),
  school_id int references schools(id),
  category text not null, -- 'Bullying', 'Corruption', 'Violence', 'Negligence', 'Extortion', 'Power Abuse'
  target_person text,
  description text not null,
  attachment_url text, -- Storage link
  status text default 'New', -- 'New', 'Under Review', 'Audited', 'Closed'
  urgency int default 1, -- 3 for Violence/Corruption, 1 for others
  created_at timestamp with time zone default now()
);

-- RLS: Allow anonymous inserts
alter table complaints enable row level security;
create policy "Anonymous can report" on complaints for insert with check (true);
create policy "Anonymous can view own status" on complaints for select using (true); -- Usually restricted by short_id in app logic

-- 5. Seed Data (Kazakhstan Regions)
insert into regions (name) values 
('г. Астана'), ('г. Алматы'), ('г. Шымкент'),
('Абайская область'), ('Акмолинская область'), ('Актюбинская область'), ('Алматинская область'),
('Атырауская область'), ('Восточно-Казахстанская область'), ('Жамбылская область'), ('Жетысуская область'),
('Западно-Казахстанская область'), ('Карагандинская область'), ('Костанайская область'), ('Кызылординская область'),
('Мангистауская область'), ('Павлодарская область'), ('Северо-Казахстанская область'), ('Туркестанская область'),
('Улытауская область');

-- Example Cities for major regions
insert into cities (region_id, name) values 
(1, 'Район Алматы'), (1, 'Район Есиль'), (1, 'Район Байконур'), (1, 'Район Сарыарка'),
(2, 'Алмалинский район'), (2, 'Бостандыкский район'), (2, 'Медеуский район'),
(4, 'г. Семей'), (5, 'г. Кокшетау'), (6, 'г. Актобе');

-- Example Schools
insert into schools (city_id, name, address) values 
(1, 'Школа-лицей №1', 'ул. Достык, 5'), (1, 'Школа-гимназия №3', 'пр. Республики, 12'),
(2, 'Haileybury Astana', 'ул. Панфилова, 4'), (5, 'НИШ ФМН Алматы', 'мкр. Калкаман');
