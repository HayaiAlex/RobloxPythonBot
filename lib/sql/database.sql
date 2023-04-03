DROP TABLE IF EXISTS users;
CREATE TABLE users (
    User_ID int(11) NOT NULL,
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
    CONSTRAINT PK_users PRIMARY KEY (Rank_ID)
) ENGINE = InnoDB DEFAULT CHARSET = latin1;
INSERT INTO rank_requirements
VALUES (1, "[1] First", 96346577, 0, 0, 0, 0),
    (2, "[2] 2nd", 96346586, 1, 1, 1, 1),
    (3, "[3] 3rd Rank", 96346587, 3, 3, 3, 3);