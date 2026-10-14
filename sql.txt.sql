-- CREATE TABLE "client" (
-- 	"id"	INTEGER NOT NULL UNIQUE,
-- 	"pref_name"	TEXT,
-- 	"fname"	TEXT,
-- 	"mname"	TEXT,
-- 	"lname"	TEXT,
-- 	"ename"	TEXT,
-- 	"suf_name"	TEXT,
-- 	"gender"	TEXT,
-- 	"dob"	TEXT,
-- 	"datecreated"	TEXT,
-- 	"addr"	TEXT,
-- 	"status"	INTEGER,
-- 	"addedby"	TEXT,
-- 	PRIMARY KEY("id" AUTOINCREMENT)
-- )


-- CREATE TABLE "user" (
-- 	"id"	INTEGER NOT NULL UNIQUE,
-- 	"name"	TEXT,
-- 	"username"	TEXT,
-- 	"password"	TEXT,
-- 	"role"	INTEGER,
-- 	"roles"	TEXT,
-- 	PRIMARY KEY("id" AUTOINCREMENT)
-- );

-- -- create admin account
-- -- 1 for admin
-- INSERT INTO user (id, name, username, password, role) VALUES('1', 'Administrator', 'admin', '21232f297a57a5a743894a0e4a801fc3', '1')


card -> 

-- bank_ada
CREATE TABLE "bank_ada" (
	"ada_no"	TEXT,
	"refid"	TEXT,
	"fund"	TEXT,
	"list_ada"	TEXT,
	"createdby"	TEXT,
	"datecreated"	TEXT,
	PRIMARY KEY("ada_no")
);