
CREATE TABLE IF NOT EXISTS coa (
	campus_id	BIGINT NOT NULL,
	intra_id	BIGINT NOT NULL,
	guild_id	BIGINT NOT NULL,
	discord_id	BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS cursus (
	campus_id	BIGINT NOT NULL,
	intra_id	BIGINT NOT NULL,
	guild_id	BIGINT NOT NULL,
	discord_id	BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS groups (
	campus_id	BIGINT NOT NULL,
	intra_id	BIGINT NOT NULL,
	guild_id	BIGINT NOT NULL,
	discord_id	BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
	omega_id	BIGINT NOT NULL AUTO_INCREMENT,
	discord_id	BIGINT NOT NULL,
	intra_id	TEXT NOT NULL,
	PRIMARY KEY(omega_id)
);
CREATE TABLE IF NOT EXISTS years (
	id BIGINT NOT NULL AUTO_INCREMENT,
	campus_id	BIGINT NOT NULL,
	intra_id	BIGINT NOT NULL,
	guild_id	BIGINT NOT NULL,
	discord_id	BIGINT NOT NULL,
	PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS nick (
	campus_id	BIGINT NOT NULL,
	guild_id	BIGINT NOT NULL,
	format	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS project (
	campus_id	BIGINT NOT NULL,
	intra_id	BIGINT NOT NULL,
	in_progress	BIGINT NOT NULL,
	finished	BIGINT NOT NULL,
	validated	BIGINT NOT NULL,
	discord_id	BIGINT NOT NULL,
	guild_id	BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS temp_auth (
	discord_id	BIGINT NOT NULL,
	code	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS new_users (
	discord_id	BIGINT NOT NULL,
	intra_id	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS maintenance (
	part	TEXT NOT NULL,
	status	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ticket (
	user_id	BIGINT NOT NULL,
	channel_id	BIGINT NOT NULL
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
