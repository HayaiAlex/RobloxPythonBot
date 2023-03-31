DROP TABLE IF EXISTS users;
CREATE TABLE users (
    User_ID int(11) NOT NULL,
    User_Name varchar(11) NOT NULL,
    Raids int(11) NOT NULL,
    Defenses int(11) NOT NULL,
    Defense_Training int(11) NOT NULL,
    Prism_Trainings int(11) NOT NULL,
    CONSTRAINT PK_users PRIMARY KEY (User_ID)
) ENGINE = InnoDB DEFAULT CHARSET = latin1