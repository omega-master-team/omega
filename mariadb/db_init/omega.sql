
CREATE TABLE IF NOT EXISTS coa (
	campus_id	INTEGER NOT NULL,
	intra_id	INTEGER NOT NULL,
	guild_id	INTEGER NOT NULL,
	discord_id	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS cursus (
	campus_id	INTEGER NOT NULL,
	intra_id	INTEGER NOT NULL,
	guild_id	INTEGER NOT NULL,
	discord_id	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS groups (
	campus_id	INTEGER NOT NULL,
	intra_id	INTEGER NOT NULL,
	guild_id	INTEGER NOT NULL,
	discord_id	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
	omega_id	INTEGER NOT NULL AUTO_INCREMENT,
	discord_id	INTEGER NOT NULL,
	intra_id	TEXT NOT NULL,
	PRIMARY KEY(omega_id)
);
CREATE TABLE IF NOT EXISTS years (
	campus_id	INTEGER NOT NULL,
	intra_id	INTEGER NOT NULL,
	guild_id	INTEGER NOT NULL,
	discord_id	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS nick (
	campus_id	INTEGER NOT NULL,
	guild_id	INTEGER NOT NULL,
	format	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS project (
	campus_id	INTEGER NOT NULL,
	intra_id	INTEGER NOT NULL,
	in_progress	INTEGER NOT NULL,
	finished	INTEGER NOT NULL,
	validated	INTEGER NOT NULL,
	discord_id	INTEGER NOT NULL,
	guild_id	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS temp_auth (
	discord_id	INTEGER NOT NULL,
	code	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS new_users (
	discord_id	INTEGER NOT NULL,
	intra_id	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS maintenance (
	part	TEXT NOT NULL,
	status	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ticket (
	user_id	INTEGER NOT NULL,
	channel_id	INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS status (
	name	TEXT NOT NULL
);
INSERT INTO maintenance VALUES ('status','off');
INSERT INTO maintenance VALUES ('login','off');
INSERT INTO maintenance VALUES ('sync_config','off');
INSERT INTO maintenance VALUES ('sync_task','off');
INSERT INTO maintenance VALUES ('reaction_role','off');
INSERT INTO maintenance VALUES ('admin_utils','off');
INSERT INTO maintenance VALUES ('admin_sync','off');
INSERT INTO maintenance VALUES ('base','off');
INSERT INTO maintenance VALUES ('ticket','off');
