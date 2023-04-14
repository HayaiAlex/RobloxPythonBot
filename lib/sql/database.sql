DROP TABLE IF EXISTS users;
CREATE TABLE users (
    User_ID bigint(11) NOT NULL,
    Rank_ID int(11) NOT NULL,
    Raids int(11) NOT NULL,
    Defenses int(11) NOT NULL,
    Defense_Trainings int(11) NOT NULL,
    Prism_Trainings int(11) NOT NULL,
    CONSTRAINT PK_users PRIMARY KEY (User_ID)
) ENGINE = InnoDB DEFAULT CHARSET = latin1;

DROP TABLE IF EXISTS rank_requirements;
CREATE TABLE rank_requirements (
    Rank_ID int(11) NOT NULL,
    Rank_Name varchar(255) NOT NULL,
    Role_ID int(11) NOT NULL,
    Raids int(11) NOT NULL,
    Defenses int(11) NOT NULL,
    Defense_Trainings int(11) NOT NULL,
    Prism_Trainings int(11) NOT NULL,
    CONSTRAINT PK_ranks PRIMARY KEY (Rank_ID)
) ENGINE = InnoDB DEFAULT CHARSET = latin1;

INSERT INTO rank_requirements
VALUES (1, "[1] First", 96346577, 0, 0, 0, 0),
    (2, "[2] 2nd", 96346586, 1, 1, 1, 1),
    (3, "[3] 3rd Rank", 96346587, 3, 3, 3, 3);

DROP TABLE IF EXISTS medals;
CREATE TABLE medals (
    Medal_ID int(11) NOT NULL,
    Name varchar(255) NOT NULL,
    Description varchar(255) NOT NULL,
    Emote varchar(255),
    Role_ID bigint,
    Created timestamp NOT NULL,
    CONSTRAINT PK_medals PRIMARY KEY (Medal_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO medals
VALUES 
(1, "Frostarian War Commendation - LSE War", "War commendation given to medal recipients for the LSE war", "🎖️", NULL, FROM_UNIXTIME(1612824854)),
(2, "2021 Frostarian Easter Egg Hunt", "Found all the eggs during the Frostarian 2021 Egg Hunt at Grand Celeste", "🥚", NULL, FROM_UNIXTIME(1617320834)),
(3, "Voice of the Vanguard - Snow Core War", "Hosted the most raid wins on Aurora's Dam during the Snow Core war", "❄️", NULL, FROM_UNIXTIME(1623373111)),
(4, "Bulwark of Celeste - Snow Core War", "Hosted the most defense wins at Celeste 2 during the Snow Core wwar", "❄️", NULL, FROM_UNIXTIME(1623373123)),
(5, "Invader Inquisitor - Snow Core War", "Attended the most Aurora's Dam raids during the Snow Core war", "❄️", NULL, FROM_UNIXTIME(1623373135)),
(6, "Celeste Protector - Snow Core War", "Attended the most Celeste 2 defenses during the Snow Core war", "❄️", NULL, FROM_UNIXTIME(1623373148)),
(7, "Frequent Flyer - Snow Core War", "Attended the most events overall throughout the Snow Core war", "❄️", NULL, FROM_UNIXTIME(1623373156)),
(8, "Soldier's Savior - Snow Core War", "Accumulated the most overall heals throughout the Snow Core war", "❄️", NULL, FROM_UNIXTIME(1623373164)),
(9, "Into the Breach - Snow Core War", "Accumulated the most overall damage throughout the Snow Core war", "❄️", NULL, FROM_UNIXTIME(1623373172)),
(10, "May 2021 Frostarian Video Montage", "Participated in the May 2021 Frostarian Video Montage Competitio", "📹", NULL, FROM_UNIXTIME(1623375138)),
(11, "Best Hoster 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791308)),
(12, "Best Aimer 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791609)),
(13, "Best Defender 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791622)),
(14, "Most likely to throw a defense 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791635)),
(15, "Cult Leader 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791646)),
(16, "Funniest Frostarian 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791654)),
(17, "Frostarian Legend 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791664)),
(18, "Most Active 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791673)),
(19, "Most Productive Officer 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791689)),
(20, "Most Epik 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791710)),
(21, "Most likely to rage quit 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791731)),
(22, "Most likely to get moderated 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791740)),
(23, "Loudest on the Mic 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791753)),
(24, "Worst Aimer 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791762)),
(25, "The Stinkiest Poop Man 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791771)),
(26, "Most Toxic 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791779)),
(27, "Most likely to be demoted 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791788)),
(28, "Best Dresser 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791796)),
(29, "Worst Dresser 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791802)),
(30, "The Ultimate Femboy 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791812)),
(31, "Biggest Weeb 2021", "N/A", "🎖️", NULL, FROM_UNIXTIME(1625791830)),
(32, "Doomspire Tournament Winner Summer 2021", "N/A", "🏆", NULL, FROM_UNIXTIME(1628312053)),
(33, "Developer Award", "N/A", "🎖️", NULL, FROM_UNIXTIME(1628380681)),
(34, "Top Moderator", "N/A", "🎖️", NULL, FROM_UNIXTIME(1628380692)),
(35, "Frostarian Times Pulitzer", "N/A", "🎖️", NULL, FROM_UNIXTIME(1628380708)),
(36, "Most Nominations", "Nominated for the most amount of awards but didn't win anything during the Frostarian Choice Awards hosted 8/7/2021", "🎖️", NULL, FROM_UNIXTIME(1628380862)),
(37, "Voice of the Vanguard - WARCOM War", "Hosted the most raid wins on WARCOM during the WARCOM war", "<:WARCOM:914332814672035891>", NULL, FROM_UNIXTIME(1661619014)),
(38, "Bulwark of Frostaria - WARCOM War", "Hosted the most defense wins during the WARCOM war", "<:WARCOM:914332814672035891>", NULL, FROM_UNIXTIME(1661619028)),
(39, "Invader Inquisitor - WARCOM War", "Attended the most raids during the WARCOM war", "<:WARCOM:914332814672035891>", NULL, FROM_UNIXTIME(1661619052)),
(40, "Frostaria Protector - WARCOM War", "Attended the most defenses during the WARCOM war", "<:WARCOM:914332814672035891>", NULL, FROM_UNIXTIME(1661619083)),
(41, "Frequent Flyer - WARCOM War", "Attended the most events overall throughout the WARCOM warr", "<:WARCOM:914332814672035891>", NULL, FROM_UNIXTIME(1661619099)),
(42, "Soldier's Savior - WARCOM War", "Accumulated the most overall heals throughout the WARCOM warr", "<:WARCOM:914332814672035891>", NULL, FROM_UNIXTIME(1661619109)),
(43, "Into the Breach - WARCOM War", "Accumulated the most overall damage throughout the WARCOM war", "<:WARCOM:914332814672035891>", NULL, FROM_UNIXTIME(1661619125)),
(44, "Frostarian Leadership", "Given to those who helped lead defenses and raids during the WARCOM war", "<:WARCOM:914332814672035891>", NULL, FROM_UNIXTIME(1661619864)),
(45, "Frostarian War Hero", "Attended at least 3 events during the WARCOM war", "<:WARCOM:914332814672035891>", NULL, FROM_UNIXTIME(1661619924)),
(46, "Frostarian 2022 Winter Present Hunt Top 10", "N/A", "🎖️", "1058866590621384824", FROM_UNIXTIME(1672524563));


CREATE TABLE user_medals (
    User_ID bigint NOT NULL,
    Medal_ID int(11) NOT NULL,
    CONSTRAINT PK_user_medal PRIMARY KEY (User_ID, Medal_ID),
    CONSTRAINT FK_user FOREIGN KEY (User_ID) REFERENCES users(User_ID),
    CONSTRAINT FK_medal FOREIGN KEY (Medal_ID) REFERENCES medals(Medal_ID)
);

